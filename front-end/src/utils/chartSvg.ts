// Vega-Lite chart rendering — generates inline SVG from .report-bar-chart and
// .report-pie-chart divs using data-labels / data-values attributes.
// vega + vega-lite are lazy-loaded so they only hit the bundle when charts are present.

import type { TopLevelSpec } from 'vega-lite'
import type { ColorScheme } from 'vega'

interface ChartOpts {
  title?: string
  colorScheme?: string
  width?: number
  height?: number
  xTitle?: string
  yTitle?: string
  sort?: string
  innerRadius?: number
}

export function parseChartData(el: Element): { labels: string[]; values: number[]; opts: ChartOpts } {
  const l = (el.getAttribute('data-labels') ?? '').replace(/^\[|\]$/g, '')
  const v = (el.getAttribute('data-values') ?? '').replace(/^\[|\]$/g, '')
  const rawLabels = l.split(',').map(s => s.trim())
  const rawValues = v.split(',').map(s => parseFloat(s.trim()))
  const pairs = rawLabels
    .map((label, i) => ({ label, value: rawValues[i] }))
    .filter(p => p.label && !isNaN(p.value))

  const opts: ChartOpts = {}
  const title = el.getAttribute('data-title')
  const colorScheme = el.getAttribute('data-color-scheme')
  const width = el.getAttribute('data-width')
  const height = el.getAttribute('data-height')
  const xTitle = el.getAttribute('data-x-title')
  const yTitle = el.getAttribute('data-y-title')
  const sort = el.getAttribute('data-sort')
  const innerRadius = el.getAttribute('data-inner-radius')

  if (title) opts.title = title
  if (colorScheme) opts.colorScheme = colorScheme
  if (width) opts.width = parseInt(width, 10)
  if (height) opts.height = parseInt(height, 10)
  if (xTitle) opts.xTitle = xTitle
  if (yTitle) opts.yTitle = yTitle
  if (sort) opts.sort = sort
  if (innerRadius) opts.innerRadius = parseInt(innerRadius, 10)

  return { labels: pairs.map(p => p.label), values: pairs.map(p => p.value), opts }
}

function buildBarSpec(labels: string[], values: number[], opts: ChartOpts): TopLevelSpec {
  return {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    width: opts.width ?? 500,
    height: opts.height ?? 250,
    title: opts.title ?? '',
    mark: { type: 'bar', cornerRadiusTopLeft: 2, cornerRadiusTopRight: 2 },
    data: { values: labels.map((label, i) => ({ label, value: values[i] })) },
    encoding: {
      x: {
        field: 'label',
        type: 'nominal',
        sort: (opts.sort as 'ascending' | 'descending' | null) ?? null,
        axis: { labelAngle: -30, title: opts.xTitle ?? null },
      },
      y: {
        field: 'value',
        type: 'quantitative',
        axis: { title: opts.yTitle ?? null },
      },
      color: {
        field: 'label',
        type: 'nominal',
        scale: { scheme: (opts.colorScheme ?? 'tableau10') as ColorScheme },
        legend: null,
      },
    },
  }
}

function buildPieSpec(labels: string[], values: number[], opts: ChartOpts): TopLevelSpec {
  return {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    width: opts.width ?? 300,
    height: opts.height ?? 300,
    title: opts.title ?? '',
    mark: { type: 'arc', innerRadius: opts.innerRadius ?? 0 },
    data: { values: labels.map((label, i) => ({ label, value: values[i] })) },
    encoding: {
      theta: { field: 'value', type: 'quantitative' },
      color: {
        field: 'label',
        type: 'nominal',
        scale: { scheme: (opts.colorScheme ?? 'tableau10') as ColorScheme },
      },
    },
  }
}

async function svgFromSpec(spec: TopLevelSpec): Promise<string> {
  const [vegaMod, vlMod] = await Promise.all([import('vega'), import('vega-lite')])
  const compiled = vlMod.compile(spec).spec
  const view = new vegaMod.View(vegaMod.parse(compiled), { renderer: 'none' })
  return view.toSVG()
}

export async function renderChartsAsSvg(container: Element): Promise<void> {
  const barEls = Array.from(container.querySelectorAll('.report-bar-chart'))
  const pieEls = Array.from(container.querySelectorAll('.report-pie-chart'))
  if (!barEls.length && !pieEls.length) return

  await Promise.all([
    ...barEls.map(async el => {
      const { labels, values, opts } = parseChartData(el)
      if (!labels.length) return
      try {
        el.innerHTML = await svgFromSpec(buildBarSpec(labels, values, opts))
      } catch (e) {
        console.warn('[chartSvg] bar chart render failed', e)
      }
    }),
    ...pieEls.map(async el => {
      const { labels, values, opts } = parseChartData(el)
      if (!labels.length) return
      try {
        el.innerHTML = await svgFromSpec(buildPieSpec(labels, values, opts))
      } catch (e) {
        console.warn('[chartSvg] pie chart render failed', e)
      }
    }),
  ])
}
