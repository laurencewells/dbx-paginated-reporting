<script setup lang="ts">
import { ref, computed, watch, watchEffect, onMounted, onUnmounted, nextTick } from 'vue'
import DOMPurify from 'dompurify'
import { renderChartsAsSvg } from '@/utils/chartSvg'

const props = defineProps<{
  html: string
  pageSize?: 'A4' | 'email'
  templateType?: 'html' | 'markdown'
}>()

// Strip <style> blocks from the HTML before sanitising; they are injected
// into <head> directly via a managed DOM element (see watchEffect below).
const _IMG_REF_RE = /src=(["'])img:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\1/gi

const sanitizedHtml = computed(() => {
  const withImages = props.html.replace(_IMG_REF_RE, 'src=$1/api/v1/images/$2/data$1')
  const stripped = withImages.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
  return DOMPurify.sanitize(stripped, {
    ADD_ATTR: [
      'data-labels', 'data-values',
      'data-title', 'data-color-scheme', 'data-width', 'data-height',
      'data-x-title', 'data-y-title', 'data-sort', 'data-inner-radius',
    ],
  })
})

// Sanitize extracted CSS by stripping the vectors that can load external
// resources or execute code. Safe presentational properties are untouched.
function sanitizeCss(css: string): string {
  return css
    .replace(/@import\s[^;]+;?/gi, '')               // no external imports
    .replace(/url\s*\(\s*(['"]?)(?!data:image\/)[^)]*\1\s*\)/gi, 'none') // no external urls (data:image allowed)
    .replace(/expression\s*\([^)]*\)/gi, 'none')      // IE expression()
    .replace(/javascript\s*:/gi, '')                  // javascript: URIs
    .replace(/-moz-binding\s*:[^;]+/gi, '')           // Firefox XBL binding
}

// Inject template <style> blocks as a real <head> stylesheet so the browser
// always activates them. v-html / innerHTML injection is not reliable.
const headStyleEl = document.createElement('style')
headStyleEl.setAttribute('data-report-preview', '')
document.head.appendChild(headStyleEl)

watchEffect(() => {
  const blocks: string[] = []
  const re = /<style[^>]*>([\s\S]*?)<\/style>/gi
  let m: RegExpExecArray | null
  while ((m = re.exec(props.html)) !== null) blocks.push(m[1])
  headStyleEl.textContent = sanitizeCss(blocks.join('\n'))
})

const previewContainer = ref<HTMLElement | null>(null)

function addPageBreakIndicators() {
  if (!previewContainer.value) return
  
  // Remove existing separators
  previewContainer.value.querySelectorAll('.page-separator-visual').forEach(el => el.remove())
  
  // Add visual indicators after each .report-page except the last
  const pages = previewContainer.value.querySelectorAll('.report-page')
  pages.forEach((page, index) => {
    if (index < pages.length - 1) {
      const separator = document.createElement('div')
      separator.className = 'page-separator-visual'
      separator.innerHTML = `<span>— Page ${index + 1} End / Page ${index + 2} Start —</span>`
      page.after(separator)
    }
  })
  
  // Add visual indicators after .page-break elements
  const pageBreaks = previewContainer.value.querySelectorAll('.page-break')
  pageBreaks.forEach((pb) => {
    if (!pb.nextElementSibling?.classList.contains('page-separator-visual')) {
      const separator = document.createElement('div')
      separator.className = 'page-separator-visual'
      separator.innerHTML = `<span>— Page Break —</span>`
      pb.after(separator)
    }
  })
}

async function renderCharts() {
  if (!previewContainer.value) return
  await renderChartsAsSvg(previewContainer.value)
}

watch(() => props.html, async () => {
  await nextTick()
  await renderCharts()
  addPageBreakIndicators()
})

onMounted(() => {
  nextTick(async () => {
    await renderCharts()
    addPageBreakIndicators()
  })
})

onUnmounted(() => {
  headStyleEl.remove()
})
</script>

<template>
  <div
    ref="previewContainer"
    class="report-preview-wrapper"
    :class="[pageSize === 'email' ? 'preview-email' : 'preview-a4', templateType === 'markdown' ? 'preview-markdown' : '']"
    v-html="sanitizedHtml"
  ></div>
</template>

<style scoped>
.report-preview-wrapper {
  background: #e0e0e0;
  min-height: 100%;
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.report-preview-wrapper :deep(.report-preview) {
  padding: 2rem;
}

.report-preview-wrapper :deep(.empty-state) {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.report-preview-wrapper :deep(.empty-state i) {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
  display: block;
}

.report-preview-wrapper :deep(.report-tile) {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}

.report-preview-wrapper :deep(.report-tile.tile-primary) {
  background: linear-gradient(135deg, #2d3e50 0%, #34495e 100%);
  box-shadow: 0 4px 15px rgba(45, 62, 80, 0.3);
}

.report-preview-wrapper :deep(.report-tile.tile-success) {
  background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
  box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
}

.report-preview-wrapper :deep(.report-tile.tile-warning) {
  background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
  box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
}

.report-preview-wrapper :deep(.report-tile.tile-danger) {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
}

.report-preview-wrapper :deep(.report-tile-title) {
  font-size: 0.875rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.report-preview-wrapper :deep(.report-tile-value) {
  font-size: 2rem;
  font-weight: 700;
}

.report-preview-wrapper :deep(.report-table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.report-preview-wrapper :deep(.report-table thead) {
  background: #2d3e50;
  color: white;
}

.report-preview-wrapper :deep(.report-table th) {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
}

.report-preview-wrapper :deep(.report-table td) {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #eee;
}

.report-preview-wrapper :deep(.report-table tbody tr:hover) {
  background: #f8f9fa;
}

.report-preview-wrapper :deep(.chart-container) {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid #eee;
  overflow: hidden;
}

.report-preview-wrapper :deep(.report-bar-chart),
.report-preview-wrapper :deep(.report-pie-chart) {
  position: relative;
  width: 100%;
  max-height: 300px;
}

.report-preview-wrapper :deep(.chart-title) {
  font-size: 1rem;
  font-weight: 600;
  color: #2d3e50;
  margin-bottom: 1rem;
}

.report-preview-wrapper :deep(h1) {
  color: #2d3e50;
  font-weight: 700;
}

.report-preview-wrapper :deep(h2),
.report-preview-wrapper :deep(h3) {
  color: #2d3e50;
}

/* Page break visual indicators */
.report-preview-wrapper :deep(.page-separator-visual) {
  position: relative;
  width: 794px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-preview-wrapper :deep(.page-separator-visual span) {
  background: #ccc;
  padding: 0.2rem 1rem;
  border-radius: 20px;
  font-size: 0.65rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 500;
}

/* A4 page styling: 210mm x 297mm at 96dpi = 794px x 1123px */
.report-preview-wrapper :deep(.report-page) {
  background: white;
  width: 794px;
  min-height: 1123px;
  padding: 38px;
  position: relative;
  border: 1px solid #d0d0d0;
  border-radius: 2px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  box-sizing: border-box;
  overflow: hidden;
}

.report-preview-wrapper :deep(.report-page-header) {
  border-bottom: 2px solid #2d3e50;
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
}

.report-preview-wrapper :deep(.page-number) {
  text-align: center;
  font-size: 0.75rem;
  color: #999;
  padding-top: 1.5rem;
  margin-top: auto;
  border-top: 1px solid #eee;
}

.report-preview-wrapper :deep(.page-break) {
  height: 0;
  margin: 0;
  padding: 0;
  border: none;
}

/* Email layout — 600px wide, no fixed height per "page" */
.preview-email :deep(.report-page) {
  width: 600px;
  min-height: unset;
  padding: 24px 32px;
}

.preview-email :deep(.page-separator-visual) {
  width: 600px;
}

/* Email + markdown: constrain to email width */
.preview-email.preview-markdown :deep(.markdown-body) {
  max-width: 600px;
}

/* Markdown layout — document-style, no fixed page dimensions */
.preview-markdown {
  padding: 2rem;
}

.preview-markdown :deep(.markdown-body) {
  background: white;
  max-width: 860px;
  width: 100%;
  padding: 2.5rem 3rem;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  font-size: 15px;
  line-height: 1.7;
  color: #212529;
}

.preview-markdown :deep(.markdown-body h1),
.preview-markdown :deep(.markdown-body h2),
.preview-markdown :deep(.markdown-body h3),
.preview-markdown :deep(.markdown-body h4),
.preview-markdown :deep(.markdown-body h5),
.preview-markdown :deep(.markdown-body h6) {
  color: #2d3e50;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.preview-markdown :deep(.markdown-body h1) {
  font-size: 2rem;
  font-weight: 700;
  border-bottom: 2px solid #2d3e50;
  padding-bottom: 0.5rem;
}

.preview-markdown :deep(.markdown-body h2) {
  font-size: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 0.25rem;
}

.preview-markdown :deep(.markdown-body table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.preview-markdown :deep(.markdown-body table thead) {
  background: #2d3e50;
  color: white;
}

.preview-markdown :deep(.markdown-body table th) {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
}

.preview-markdown :deep(.markdown-body table td) {
  padding: 0.625rem 1rem;
  border-bottom: 1px solid #eee;
}

.preview-markdown :deep(.markdown-body table tbody tr:nth-child(even)) {
  background: #f8f9fa;
}

.preview-markdown :deep(.markdown-body code) {
  background: #f3f3f3;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.875em;
  color: #c0392b;
}

.preview-markdown :deep(.markdown-body pre) {
  background: #2d2d44;
  color: #f8f8f2;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 1rem;
}

.preview-markdown :deep(.markdown-body pre code) {
  background: none;
  color: inherit;
  padding: 0;
}

.preview-markdown :deep(.markdown-body blockquote) {
  border-left: 4px solid #3498db;
  margin: 0 0 1rem;
  padding: 0.5rem 1rem;
  background: #f0f8ff;
  color: #555;
  border-radius: 0 4px 4px 0;
}

.preview-markdown :deep(.markdown-body blockquote p) {
  margin: 0;
}

.preview-markdown :deep(.markdown-body del) {
  color: #6c757d;
}

.preview-markdown :deep(.markdown-body hr) {
  border: none;
  border-top: 1px solid #dee2e6;
  margin: 1.5rem 0;
}
</style>
