<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useToastStore } from '@/stores/toast'
import Mustache from 'mustache'
import { previewDataApiV1TemplatesTemplateIdPreviewDataPost } from '@/api/generated'
import type { PreviewDataResponse } from '@/api/generated'

const props = defineProps<{
  show: boolean
  templateId: string | null
  templateName: string | null
  htmlContent: string
  structureName?: string | null
}>()

const emit = defineEmits<{ 'update:show': [value: boolean] }>()

const toastStore = useToastStore()

const previewData = ref<Record<string, unknown>>({})
const loadingData = ref(false)
const exporting = ref(false)

const REPORT_STYLES = `
  @page { size: A4; margin: 10mm; }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; box-sizing: border-box; }
  body { margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; color: #212529; font-size: 14px; overflow-x: hidden; }
  .report-page { page-break-after: always; padding: 24px 28px; position: relative; max-width: 100%; overflow: hidden; }
  .report-page:last-child { page-break-after: auto; }
  h1, h2, h3 { color: #2d3e50; }
  h1 { font-weight: 700; }
  .report-tile { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 15px rgba(52,152,219,0.3); }
  .report-tile.tile-primary { background: linear-gradient(135deg, #2d3e50 0%, #34495e 100%); box-shadow: 0 4px 15px rgba(45,62,80,0.3); }
  .report-tile.tile-success { background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%); box-shadow: 0 4px 15px rgba(39,174,96,0.3); }
  .report-tile.tile-warning { background: linear-gradient(135deg, #f39c12 0%, #d68910 100%); box-shadow: 0 4px 15px rgba(243,156,18,0.3); }
  .report-tile.tile-danger { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); box-shadow: 0 4px 15px rgba(231,76,60,0.3); }
  .report-tile-title { font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px; }
  .report-tile-value { font-size: 2rem; font-weight: 700; }
  .report-table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
  .report-table thead { background: #2d3e50; color: white; }
  .report-table th { padding: 0.75rem 1rem; text-align: left; font-weight: 600; font-size: 0.875rem; }
  .report-table td { padding: 0.75rem 1rem; border-bottom: 1px solid #eee; }
  .chart-container { background: white; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #eee; overflow: hidden; }
  .chart-title { font-size: 1rem; font-weight: 600; color: #2d3e50; margin-bottom: 1rem; }
  .report-bar-chart, .report-pie-chart { position: relative; width: 100%; max-height: 300px; }
  .page-number { text-align: center; font-size: 0.75rem; color: #999; padding-top: 1.5rem; margin-top: auto; border-top: 1px solid #eee; }
  @media print {
    .row { display: flex !important; flex-wrap: wrap !important; }
    [class*="col-"] { flex-shrink: 0; }
    .col-3, .col-sm-3, .col-md-3, .col-lg-3 { width: 25% !important; }
    .col-4, .col-sm-4, .col-md-4, .col-lg-4 { width: 33.3333% !important; }
    .col-6, .col-sm-6, .col-md-6, .col-lg-6 { width: 50% !important; }
    .col-12, .col-sm-12, .col-md-12, .col-lg-12 { width: 100% !important; }
    .d-flex { display: flex !important; }
    .gap-2 { gap: 0.5rem !important; }
  }
`

const CHART_SCRIPT = `
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"><\/script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  var COLORS = ['rgba(52,152,219,0.8)','rgba(46,204,113,0.8)','rgba(155,89,182,0.8)','rgba(241,196,15,0.8)','rgba(231,76,60,0.8)','rgba(26,188,156,0.8)','rgba(230,126,34,0.8)'];
  var BORDERS = ['rgba(52,152,219,1)','rgba(46,204,113,1)','rgba(155,89,182,1)','rgba(241,196,15,1)','rgba(231,76,60,1)','rgba(26,188,156,1)','rgba(230,126,34,1)'];
  function parse(el) {
    var l = (el.getAttribute('data-labels')||'').replace(/^\\[|]$/g,'');
    var v = (el.getAttribute('data-values')||'').replace(/^\\[|]$/g,'');
    return { labels: l.split(',').map(function(s){return s.trim()}).filter(Boolean), values: v.split(',').map(function(s){return s.trim()}).filter(Boolean).map(Number) };
  }
  function render(sel, type) {
    document.querySelectorAll(sel).forEach(function(el) {
      var d = parse(el); if (!d.labels.length) return;
      var canvas = document.createElement('canvas'); canvas.style.maxHeight='300px'; el.innerHTML=''; el.appendChild(canvas);
      new Chart(canvas, { type: type, data: { labels: d.labels, datasets: [{ data: d.values, backgroundColor: COLORS.slice(0,d.values.length), borderColor: type==='pie'?'#fff':BORDERS.slice(0,d.values.length), borderWidth: type==='pie'?2:1 }] }, options: { responsive:true, maintainAspectRatio:false, animation:false, plugins:{ legend:{ display:type==='pie', position:'bottom' } }, scales: type==='bar'?{ y:{ beginAtZero:true } }:{} } });
    });
  }
  render('.report-bar-chart','bar'); render('.report-pie-chart','pie');
});
<\/script>`

function buildDocument(body: string, title: string): string {
  return `<!DOCTYPE html><html><head>
<meta charset="utf-8">
<title>${title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
<style>${REPORT_STYLES}</style>
</head><body>${body}${CHART_SCRIPT}</body></html>`
}

const renderedHtml = computed(() => {
  if (!props.htmlContent) return ''
  try { return Mustache.render(props.htmlContent, previewData.value) } catch { return '' }
})

const previewDocument = computed(() =>
  renderedHtml.value ? buildDocument(renderedHtml.value, props.templateName ?? 'Report') : ''
)

async function loadPreview() {
  if (!props.templateId) { previewData.value = {}; return }
  loadingData.value = true
  try {
    const result = (await previewDataApiV1TemplatesTemplateIdPreviewDataPost(
      props.templateId, { limit: 10 },
    )) as unknown as PreviewDataResponse
    previewData.value = result.data
  } catch {
    previewData.value = {}
  } finally {
    loadingData.value = false
  }
}

watch(() => props.show, (visible) => {
  if (visible) loadPreview()
})

async function exportToPdf() {
  if (!props.templateId) return
  exporting.value = true
  try {
    const result = (await previewDataApiV1TemplatesTemplateIdPreviewDataPost(
      props.templateId, { limit: 1000 },
    )) as unknown as PreviewDataResponse
    const fullHtml = Mustache.render(props.htmlContent, result.data)
    const doc = buildDocument(fullHtml, props.templateName ?? 'Report')
    const iframe = document.createElement('iframe')
    iframe.style.cssText = 'position:fixed;left:-9999px;top:0;width:794px;height:1123px;border:none;visibility:hidden;'
    document.body.appendChild(iframe)
    iframe.srcdoc = doc
    iframe.onload = () => {
      const win = iframe.contentWindow!
      let attempts = 0
      const waitForCharts = () => {
        const pending = win.document.querySelectorAll('.report-bar-chart:empty, .report-pie-chart:empty')
        if (pending.length > 0 && attempts < 20) { attempts++; setTimeout(waitForCharts, 150); return }
        win.focus(); win.print()
        setTimeout(() => { try { document.body.removeChild(iframe) } catch { /* removed */ } }, 2000)
      }
      setTimeout(waitForCharts, 1000)
    }
  } catch {
    toastStore.warning('Failed to generate PDF')
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="preview-modal-backdrop" @keydown.esc="emit('update:show', false)" tabindex="-1">
      <div class="preview-modal">

        <!-- Header -->
        <div class="preview-modal-header">
          <div class="d-flex align-items-center gap-3">
            <i class="bi bi-file-earmark-richtext text-danger fs-5"></i>
            <div>
              <div class="fw-semibold">{{ templateName ?? 'Preview & Export' }}</div>
              <div v-if="structureName" class="text-muted small">
                <i class="bi bi-diagram-3 me-1"></i>{{ structureName }}
              </div>
            </div>
          </div>
          <div class="d-flex align-items-center gap-2">
            <span v-if="loadingData" class="text-muted small">
              <span class="spinner-border spinner-border-sm me-1"></span> Loading data…
            </span>
            <span v-else class="text-muted small">Preview: 10 rows · Export: full dataset</span>
            <button
              class="btn btn-danger btn-sm"
              @click="exportToPdf"
              :disabled="!templateId || exporting || loadingData"
            >
              <span v-if="exporting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              <i v-else class="bi bi-file-earmark-pdf me-1"></i>
              {{ exporting ? 'Generating…' : 'Export PDF' }}
            </button>
            <button class="btn btn-outline-secondary btn-sm" @click="emit('update:show', false)" title="Close">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>

        <!-- Body -->
        <div class="preview-modal-body">
          <div v-if="!templateId" class="empty-state">
            <i class="bi bi-file-earmark-x d-block"></i>
            <p class="mt-2 text-muted">No template selected</p>
          </div>
          <div v-else-if="loadingData" class="d-flex justify-content-center align-items-center h-100">
            <div class="spinner-border text-primary" role="status"></div>
          </div>
          <iframe
            v-else-if="previewDocument"
            class="preview-iframe"
            :srcdoc="previewDocument"
          ></iframe>
          <div v-else class="empty-state">
            <i class="bi bi-file-earmark-x d-block"></i>
            <p class="mt-2 text-muted">Nothing to preview</p>
          </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.preview-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1050;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: stretch;
  justify-content: flex-end;
}

.preview-modal {
  width: min(900px, 90vw);
  height: 100vh;
  background: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.2);
  animation: slide-in 0.2s ease;
}

@keyframes slide-in {
  from { transform: translateX(100%); opacity: 0; }
  to   { transform: translateX(0);    opacity: 1; }
}

.preview-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
  flex-shrink: 0;
}

.preview-modal-body {
  flex: 1;
  min-height: 0;
  background: #e9ecef;
  position: relative;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
  background: white;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}
.empty-state i { font-size: 3rem; opacity: 0.5; }
</style>
