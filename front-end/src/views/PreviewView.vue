<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTemplatesStore } from '@/stores/templates'
import { useToastStore } from '@/stores/toast'
import Mustache from 'mustache'
import {
  useListStructuresApiV1StructuresGet,
  useListTemplatesApiV1TemplatesGet,
  previewDataApiV1TemplatesTemplateIdPreviewDataPost,
} from '@/api/generated'
import type { PreviewDataResponse } from '@/api/generated'

const templatesStore = useTemplatesStore()
const toastStore = useToastStore()

const { data: structures } = useListStructuresApiV1StructuresGet()
const { data: templates } = useListTemplatesApiV1TemplatesGet()

const activeTemplate = computed(() =>
  templates.value?.find((t) => t.id === templatesStore.activeTemplateId) ?? null
)

const previewDataResult = ref<Record<string, unknown>>({})
const loadingData = ref(false)
const exporting = ref(false)

async function loadPreview() {
  if (!activeTemplate.value) { previewDataResult.value = {}; return }
  loadingData.value = true
  try {
    const result = (await previewDataApiV1TemplatesTemplateIdPreviewDataPost(
      activeTemplate.value.id!, { limit: 10 },
    )) as unknown as PreviewDataResponse
    previewDataResult.value = result.data
  } catch {
    previewDataResult.value = {}
  } finally {
    loadingData.value = false
  }
}

watch(() => activeTemplate.value?.id, () => { loadPreview() }, { immediate: true })

const renderedHtml = computed(() => {
  if (!activeTemplate.value) return ''
  try {
    return Mustache.render(activeTemplate.value.html_content ?? '', previewDataResult.value)
  } catch {
    return ''
  }
})

const REPORT_STYLES = `
  @page { size: A4; margin: 10mm; }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; box-sizing: border-box; }
  body { margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; color: #212529; font-size: 14px; overflow-x: hidden; }

  .report-page {
    page-break-after: always;
    padding: 24px 28px;
    position: relative;
    max-width: 100%;
    overflow: hidden;
  }
  .report-page:last-child { page-break-after: auto; }

  h1, h2, h3 { color: #2d3e50; }
  h1 { font-weight: 700; }

  .report-tile {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
  }
  .report-tile.tile-primary {
    background: linear-gradient(135deg, #2d3e50 0%, #34495e 100%);
    box-shadow: 0 4px 15px rgba(45, 62, 80, 0.3);
  }
  .report-tile.tile-success {
    background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
    box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
  }
  .report-tile.tile-warning {
    background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
    box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
  }
  .report-tile.tile-danger {
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
  }
  .report-tile-title {
    font-size: 0.875rem;
    opacity: 0.9;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
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
    .col-1, .col-sm-1, .col-md-1, .col-lg-1 { width: 8.3333% !important; }
    .col-2, .col-sm-2, .col-md-2, .col-lg-2 { width: 16.6667% !important; }
    .col-3, .col-sm-3, .col-md-3, .col-lg-3 { width: 25% !important; }
    .col-4, .col-sm-4, .col-md-4, .col-lg-4 { width: 33.3333% !important; }
    .col-5, .col-sm-5, .col-md-5, .col-lg-5 { width: 41.6667% !important; }
    .col-6, .col-sm-6, .col-md-6, .col-lg-6 { width: 50% !important; }
    .col-7, .col-sm-7, .col-md-7, .col-lg-7 { width: 58.3333% !important; }
    .col-8, .col-sm-8, .col-md-8, .col-lg-8 { width: 66.6667% !important; }
    .col-9, .col-sm-9, .col-md-9, .col-lg-9 { width: 75% !important; }
    .col-10, .col-sm-10, .col-md-10, .col-lg-10 { width: 83.3333% !important; }
    .col-11, .col-sm-11, .col-md-11, .col-lg-11 { width: 91.6667% !important; }
    .col-12, .col-sm-12, .col-md-12, .col-lg-12 { width: 100% !important; }
    .d-flex { display: flex !important; }
    .gap-2 { gap: 0.5rem !important; }
    .g-3 { --bs-gutter-x: 1rem; --bs-gutter-y: 1rem; }
  }
`

const CHART_RENDER_SCRIPT = `
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"><\/script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  var COLORS = [
    'rgba(52,152,219,0.8)','rgba(46,204,113,0.8)','rgba(155,89,182,0.8)',
    'rgba(241,196,15,0.8)','rgba(231,76,60,0.8)','rgba(26,188,156,0.8)',
    'rgba(230,126,34,0.8)'
  ];
  var BORDERS = [
    'rgba(52,152,219,1)','rgba(46,204,113,1)','rgba(155,89,182,1)',
    'rgba(241,196,15,1)','rgba(231,76,60,1)','rgba(26,188,156,1)',
    'rgba(230,126,34,1)'
  ];

  function parse(el) {
    var l = (el.getAttribute('data-labels') || '').replace(/^\\[|]$/g, '');
    var v = (el.getAttribute('data-values') || '').replace(/^\\[|]$/g, '');
    return {
      labels: l.split(',').map(function(s){return s.trim()}).filter(Boolean),
      values: v.split(',').map(function(s){return s.trim()}).filter(Boolean).map(Number)
    };
  }

  function render(selector, type) {
    document.querySelectorAll(selector).forEach(function(el) {
      var d = parse(el);
      if (!d.labels.length) return;
      var canvas = document.createElement('canvas');
      canvas.style.maxHeight = '300px';
      el.innerHTML = '';
      el.appendChild(canvas);
      new Chart(canvas, {
        type: type,
        data: {
          labels: d.labels,
          datasets: [{
            data: d.values,
            backgroundColor: COLORS.slice(0, d.values.length),
            borderColor: type === 'pie' ? '#fff' : BORDERS.slice(0, d.values.length),
            borderWidth: type === 'pie' ? 2 : 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false,
          plugins: { legend: { display: type === 'pie', position: 'bottom' } },
          scales: type === 'bar' ? { y: { beginAtZero: true } } : {}
        }
      });
    });
  }

  render('.report-bar-chart', 'bar');
  render('.report-pie-chart', 'pie');
});
<\/script>`

function buildPrintDocument(bodyHtml: string, title = 'Report'): string {
  return `<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
<style>${REPORT_STYLES}</style>
</head>
<body>${bodyHtml}${CHART_RENDER_SCRIPT}</body></html>`
}

const previewDocument = computed(() => {
  if (!renderedHtml.value) return ''
  return buildPrintDocument(renderedHtml.value, activeTemplate.value?.name ?? 'Report')
})

function selectTemplate(id: string) {
  templatesStore.setActiveTemplate(id)
}

async function exportToPdf() {
  if (!activeTemplate.value) { toastStore.warning('No template selected'); return }

  exporting.value = true
  try {
    const result = (await previewDataApiV1TemplatesTemplateIdPreviewDataPost(
      activeTemplate.value.id!, { limit: 1000 },
    )) as unknown as PreviewDataResponse

    const fullHtml = Mustache.render(activeTemplate.value.html_content ?? '', result.data)
    const doc = buildPrintDocument(fullHtml, activeTemplate.value.name)

    const iframe = document.createElement('iframe')
    iframe.style.cssText = 'position:fixed;left:-9999px;top:0;width:794px;height:1123px;border:none;visibility:hidden;'
    document.body.appendChild(iframe)

    iframe.srcdoc = doc
    iframe.onload = () => {
      const win = iframe.contentWindow!
      const waitForCharts = () => {
        const pending = win.document.querySelectorAll('.report-bar-chart:empty, .report-pie-chart:empty')
        if (pending.length > 0 && attempts < 20) {
          attempts++
          setTimeout(waitForCharts, 150)
          return
        }
        win.focus()
        win.print()
        setTimeout(() => {
          try { document.body.removeChild(iframe) } catch { /* already removed */ }
        }, 2000)
      }
      let attempts = 0
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
  <div class="preview-view">
    <div class="toolbar mb-4 d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center gap-3">
        <h4 class="mb-0"><i class="bi bi-file-earmark-pdf me-2 text-danger"></i> Preview & Export</h4>
        <select
          :value="activeTemplate?.id || ''"
          class="form-select"
          style="width: 250px"
          @change="selectTemplate(($event.target as HTMLSelectElement).value)"
        >
          <option value="" disabled>Select Template</option>
          <option v-for="t in (templates ?? [])" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-export" @click="exportToPdf" :disabled="!activeTemplate || exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-1" role="status"></span>
          <i v-else class="bi bi-file-earmark-pdf me-1"></i>
          {{ exporting ? 'Generating PDF...' : 'Export PDF' }}
        </button>
      </div>
    </div>

    <div v-if="activeTemplate" class="alert alert-info mb-4 d-flex align-items-center">
      <i class="bi bi-info-circle me-2"></i>
      <div>
        <strong>{{ activeTemplate.name }}</strong> —
        <span v-if="loadingData">Loading data from Unity Catalog...</span>
        <span v-else>Preview shows first 10 rows. Export PDF generates the full report.</span>
      </div>
    </div>

    <div class="preview-container card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <span><i class="bi bi-file-richtext me-2"></i> Report Preview</span>
        <span v-if="activeTemplate" class="text-muted small">
          Structure: {{ structures?.find(s => s.id === activeTemplate!.structure_id)?.name }}
        </span>
      </div>
      <div class="card-body p-0">
        <div v-if="!activeTemplate" class="empty-state">
          <i class="bi bi-file-earmark-x d-block"></i>
          <p>Select a template to preview</p>
        </div>
        <div v-else-if="loadingData" class="d-flex justify-content-center align-items-center" style="min-height: 400px;">
          <div class="spinner-border" role="status"></div>
        </div>
        <iframe
          v-else-if="previewDocument"
          class="pdf-preview-frame"
          :srcdoc="previewDocument"
        ></iframe>
      </div>
    </div>
  </div>
</template>

<style scoped>
.preview-view { max-width: 1200px; margin: 0 auto; }
.preview-container { min-height: 600px; }
.preview-container .card-body {
  background: #e0e0e0;
  overflow: hidden;
  padding: 0 !important;
}
.pdf-preview-frame {
  width: 100%;
  height: calc(100vh - 280px);
  border: none;
  display: block;
  background: white;
}
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}
.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}
</style>
