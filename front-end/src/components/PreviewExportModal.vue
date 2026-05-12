<script setup lang="ts">
import { ref, computed, watch, shallowRef } from 'vue'
import { useToastStore } from '@/stores/toast'
import Mustache from 'mustache'
import { marked } from 'marked'
import { previewDataApiV1TemplatesTemplateIdPreviewDataPost } from '@/api/generated'
import type { PreviewDataResponse } from '@/api/generated'
import { renderChartsAsSvg, processLayoutMagic } from '@/utils/chartSvg'

const props = defineProps<{
  show: boolean
  templateId: string | null
  templateName: string | null
  htmlContent: string
  templateType?: 'html' | 'markdown'
  pageSize?: 'A4' | 'email'
  structureName?: string | null
}>()

const emit = defineEmits<{ 'update:show': [value: boolean] }>()

const toastStore = useToastStore()

const previewData = ref<Record<string, unknown>>({})
const loadingData = ref(false)
const exporting = ref(false)
const previewLimit = ref(50)

const _IMG_REF_RE = /src=(["'])img:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\1/gi
function expandImageRefs(html: string): string {
  return html.replace(_IMG_REF_RE, 'src=$1/api/v1/images/$2/data$1')
}

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
  .page-break { height: 0; margin: 0; padding: 0; border: none; display: block; page-break-after: always; break-after: page; }
  .page-break-before { height: 0; margin: 0; padding: 0; border: none; display: block; page-break-before: always; break-before: page; }
  .no-break { break-inside: avoid; page-break-inside: avoid; }
  .report-columns-2 { column-count: 2; column-gap: 2rem; }
  .report-columns-3 { column-count: 3; column-gap: 1.5rem; }
  .report-columns-4 { column-count: 4; column-gap: 1rem; }
  /* Report grid — media-query-free CSS Grid for reliable PDF output.
     Prefer these over Bootstrap col-* in templates. Keep in sync with _REPORT_STYLES
     in back-end/services/report_renderer.py. */
  .report-grid-2   { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
  .report-grid-3   { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
  .report-grid-4   { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
  .report-grid-1-2 { display: grid; grid-template-columns: 1fr 2fr; gap: 1rem; }
  .report-grid-2-1 { display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; }
  .report-grid-1-3 { display: grid; grid-template-columns: 1fr 3fr; gap: 1rem; }
  .report-grid-3-1 { display: grid; grid-template-columns: 3fr 1fr; gap: 1rem; }
  .report-global-header { border-bottom: 2px solid #2d3e50; padding-bottom: 1rem; margin-bottom: 1.5rem; }
  .report-global-footer { border-top: 1px solid #dee2e6; padding-top: 0.75rem; margin-top: 1.5rem; font-size: 0.8rem; color: #6c757d; }
  /* Bootstrap grid overrides — applied unconditionally so print mode and screen both render
     columns correctly without relying on @media breakpoints. Keep in sync with _REPORT_STYLES
     in back-end/services/report_renderer.py. */
  .row { display: flex !important; flex-wrap: wrap !important; margin-right: -0.75rem; margin-left: -0.75rem; }
  [class*="col-"] { flex-shrink: 0; padding-right: 0.75rem; padding-left: 0.75rem; box-sizing: border-box; }
  .col-1,  .col-sm-1,  .col-md-1,  .col-lg-1,  .col-xl-1,  .col-xxl-1  { width: 8.3333%  !important; }
  .col-2,  .col-sm-2,  .col-md-2,  .col-lg-2,  .col-xl-2,  .col-xxl-2  { width: 16.6667% !important; }
  .col-3,  .col-sm-3,  .col-md-3,  .col-lg-3,  .col-xl-3,  .col-xxl-3  { width: 25%      !important; }
  .col-4,  .col-sm-4,  .col-md-4,  .col-lg-4,  .col-xl-4,  .col-xxl-4  { width: 33.3333% !important; }
  .col-5,  .col-sm-5,  .col-md-5,  .col-lg-5,  .col-xl-5,  .col-xxl-5  { width: 41.6667% !important; }
  .col-6,  .col-sm-6,  .col-md-6,  .col-lg-6,  .col-xl-6,  .col-xxl-6  { width: 50%      !important; }
  .col-7,  .col-sm-7,  .col-md-7,  .col-lg-7,  .col-xl-7,  .col-xxl-7  { width: 58.3333% !important; }
  .col-8,  .col-sm-8,  .col-md-8,  .col-lg-8,  .col-xl-8,  .col-xxl-8  { width: 66.6667% !important; }
  .col-9,  .col-sm-9,  .col-md-9,  .col-lg-9,  .col-xl-9,  .col-xxl-9  { width: 75%      !important; }
  .col-10, .col-sm-10, .col-md-10, .col-lg-10, .col-xl-10, .col-xxl-10 { width: 83.3333% !important; }
  .col-11, .col-sm-11, .col-md-11, .col-lg-11, .col-xl-11, .col-xxl-11 { width: 91.6667% !important; }
  .col-12, .col-sm-12, .col-md-12, .col-lg-12, .col-xl-12, .col-xxl-12 { width: 100%     !important; }
  .col { flex: 1 0 0% !important; }
  .d-flex { display: flex !important; }
  .gap-1 { gap: 0.25rem !important; }
  .gap-2 { gap: 0.5rem !important; }
  .gap-3 { gap: 1rem !important; }
  .gap-4 { gap: 1.5rem !important; }
`


const MARKDOWN_STYLES = `
  @page { size: A4; margin: 15mm 20mm; }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 15px; line-height: 1.7; color: #212529; }
  .markdown-body { max-width: 100%; padding: 2.5rem 3rem; }
  h1, h2, h3, h4, h5, h6 { color: #2d3e50; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; }
  h1 { font-size: 2rem; font-weight: 700; border-bottom: 2px solid #2d3e50; padding-bottom: 0.5rem; }
  h2 { font-size: 1.5rem; border-bottom: 1px solid #dee2e6; padding-bottom: 0.25rem; }
  h3 { font-size: 1.25rem; }
  p { margin-bottom: 1rem; }
  table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
  thead { background: #2d3e50; color: white; }
  th { padding: 0.75rem 1rem; text-align: left; font-weight: 600; font-size: 0.875rem; }
  td { padding: 0.625rem 1rem; border-bottom: 1px solid #eee; }
  tbody tr:nth-child(even) { background: #f8f9fa; }
  code { background: #f3f3f3; padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.875em; color: #c0392b; }
  pre { background: #2d2d44; color: #f8f8f2; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }
  pre code { background: none; color: inherit; padding: 0; }
  blockquote { border-left: 4px solid #3498db; margin: 0 0 1rem; padding: 0.5rem 1rem; background: #f0f8ff; color: #555; border-radius: 0 4px 4px 0; }
  blockquote p { margin: 0; }
  ul, ol { margin-bottom: 1rem; padding-left: 1.5rem; }
  li { margin-bottom: 0.25rem; }
  hr { border: none; border-top: 1px solid #dee2e6; margin: 1.5rem 0; }
  del { color: #6c757d; }
`

function renderBody(mustacheOutput: string): string {
  if (props.templateType === 'markdown') {
    return `<div class="markdown-body">${marked.parse(mustacheOutput) as string}</div>`
  }
  return mustacheOutput
}

function buildDocument(body: string, title: string): string {
  const isMarkdown = props.templateType === 'markdown'
  return `<!DOCTYPE html><html><head>
<meta charset="utf-8">
<title>${title}</title>
${isMarkdown ? '' : '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">'}
<style>${isMarkdown ? MARKDOWN_STYLES : REPORT_STYLES}</style>
</head><body>${body}</body></html>`
}

const renderedHtml = computed(() => {
  if (!props.htmlContent) return ''
  try { return expandImageRefs(renderBody(Mustache.render(props.htmlContent, previewData.value))) } catch { return '' }
})

// Chart-rendered version of renderedHtml for the preview iframe.
// renderChartsAsSvg is async so we can't use a computed — use a ref updated by a watcher.
const previewHtmlWithCharts = shallowRef('')

watch(renderedHtml, async (html) => {
  if (!html) { previewHtmlWithCharts.value = ''; return }
  const tmp = document.createElement('div')
  tmp.innerHTML = html
  processLayoutMagic(tmp)
  await renderChartsAsSvg(tmp)
  previewHtmlWithCharts.value = tmp.innerHTML
}, { immediate: true })

const previewDocument = computed(() =>
  previewHtmlWithCharts.value ? buildDocument(previewHtmlWithCharts.value, props.templateName ?? 'Report') : ''
)

async function loadPreview() {
  if (!props.templateId) { previewData.value = {}; return }
  loadingData.value = true
  try {
    const result = (await previewDataApiV1TemplatesTemplateIdPreviewDataPost(
      props.templateId, { limit: previewLimit.value },
    )) as unknown as PreviewDataResponse
    previewData.value = result.data
  } catch {
    previewData.value = {}
    toastStore.error('Failed to load preview data')
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
    const bodyHtml = expandImageRefs(renderBody(Mustache.render(props.htmlContent, result.data)))
    const tmp = document.createElement('div')
    tmp.innerHTML = bodyHtml
    processLayoutMagic(tmp)
    await renderChartsAsSvg(tmp)
    const doc = buildDocument(tmp.innerHTML, props.templateName ?? 'Report')
    const iframe = document.createElement('iframe')
    iframe.style.cssText = 'position:fixed;left:-9999px;top:0;width:794px;height:1123px;border:none;visibility:hidden;'
    document.body.appendChild(iframe)
    iframe.srcdoc = doc
    iframe.onload = () => {
      const win = iframe.contentWindow!
      win.focus()
      win.print()
      setTimeout(() => { try { document.body.removeChild(iframe) } catch { /* removed */ } }, 2000)
    }
  } catch {
    toastStore.error('Failed to generate PDF')
  } finally {
    exporting.value = false
  }
}

function downloadHtml() {
  if (!props.templateId) return
  // Server sets Content-Disposition with the canonical filename; same-origin
  // browsers honour the response header, so no anchor download attribute needed.
  const a = document.createElement('a')
  a.href = `/api/v1/templates/${props.templateId}/render-output`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
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
            <template v-else>
              <label class="text-muted small mb-0 me-1">Preview rows</label>
              <input
                type="number"
                class="form-control form-control-sm"
                style="width: 72px;"
                v-model.number="previewLimit"
                min="1"
                max="1000"
                @change="loadPreview"
              />
            </template>
            <button
              v-if="pageSize !== 'email'"
              class="btn btn-danger btn-sm"
              @click="exportToPdf"
              :disabled="!templateId || exporting || loadingData"
            >
              <span v-if="exporting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              <i v-else class="bi bi-file-earmark-pdf me-1"></i>
              {{ exporting ? 'Generating…' : 'Export PDF' }}
            </button>
            <button
              v-else
              class="btn btn-outline-secondary btn-sm"
              @click="downloadHtml"
              :disabled="!templateId || loadingData"
            >
              <i class="bi bi-file-earmark-code me-1"></i>
              Download HTML
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
