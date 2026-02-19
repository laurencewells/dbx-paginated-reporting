<script setup lang="ts">
import { ref, computed, watch, watchEffect, onMounted, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import DOMPurify from 'dompurify'

Chart.register(...registerables)

const props = defineProps<{
  html: string
}>()

// Strip <style> blocks from the HTML before sanitising; they are injected
// into <head> directly via a managed DOM element (see watchEffect below).
const sanitizedHtml = computed(() => {
  const stripped = props.html.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
  return DOMPurify.sanitize(stripped, {
    ADD_ATTR: ['data-labels', 'data-values'],
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
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const chartInstances = ref<any[]>([])

function destroyCharts() {
  chartInstances.value.forEach((chart) => {
    chart.destroy()
  })
  chartInstances.value = []
}

function parseChartData(element: HTMLElement): { labels: string[]; values: number[] } {
  const labelsStr = (element.getAttribute('data-labels') || '').replace(/^\[|]$/g, '')
  const valuesStr = (element.getAttribute('data-values') || '').replace(/^\[|]$/g, '')

  const labels = labelsStr.split(',').map((l) => l.trim()).filter(Boolean)
  const values = valuesStr.split(',').map((v) => v.trim()).filter(Boolean).map(Number)

  return { labels, values }
}

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

function renderCharts() {
  if (!previewContainer.value) return
  
  destroyCharts()
  
  // Render Bar Charts
  const barCharts = previewContainer.value.querySelectorAll('.report-bar-chart')
  barCharts.forEach((element) => {
    const { labels, values } = parseChartData(element as HTMLElement)
    if (labels.length === 0) return
    
    const canvas = document.createElement('canvas')
    canvas.style.maxHeight = '300px'
    element.innerHTML = ''
    element.appendChild(canvas)
    
    const chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Value',
          data: values,
          backgroundColor: [
            'rgba(52, 152, 219, 0.8)',
            'rgba(46, 204, 113, 0.8)',
            'rgba(155, 89, 182, 0.8)',
            'rgba(241, 196, 15, 0.8)',
            'rgba(231, 76, 60, 0.8)',
          ],
          borderColor: [
            'rgba(52, 152, 219, 1)',
            'rgba(46, 204, 113, 1)',
            'rgba(155, 89, 182, 1)',
            'rgba(241, 196, 15, 1)',
            'rgba(231, 76, 60, 1)',
          ],
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    })
    
    chartInstances.value.push(chart)
  })
  
  // Render Pie Charts
  const pieCharts = previewContainer.value.querySelectorAll('.report-pie-chart')
  pieCharts.forEach((element) => {
    const { labels, values } = parseChartData(element as HTMLElement)
    if (labels.length === 0) return
    
    const canvas = document.createElement('canvas')
    canvas.style.maxHeight = '300px'
    element.innerHTML = ''
    element.appendChild(canvas)
    
    const chart = new Chart(canvas, {
      type: 'pie',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: [
            'rgba(52, 152, 219, 0.8)',
            'rgba(46, 204, 113, 0.8)',
            'rgba(155, 89, 182, 0.8)',
            'rgba(241, 196, 15, 0.8)',
            'rgba(231, 76, 60, 0.8)',
            'rgba(26, 188, 156, 0.8)',
            'rgba(230, 126, 34, 0.8)',
          ],
          borderColor: '#fff',
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
          },
        },
      },
    })
    
    chartInstances.value.push(chart)
  })
}

watch(() => props.html, async () => {
  await nextTick()
  renderCharts()
  addPageBreakIndicators()
})

onMounted(() => {
  nextTick(() => {
    renderCharts()
    addPageBreakIndicators()
  })
})

onUnmounted(() => {
  destroyCharts()
  headStyleEl.remove()
})
</script>

<template>
  <div ref="previewContainer" class="report-preview-wrapper" v-html="sanitizedHtml"></div>
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
</style>
