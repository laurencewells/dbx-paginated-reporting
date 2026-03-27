// SVG chart generation — geometry constants must match report_renderer.py exactly.

function escapeXml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;')
}

const VW = 560
const VH = 300
const COLORS = ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c', '#e67e22']

export function parseChartData(el: Element): { labels: string[]; values: number[] } {
  const l = (el.getAttribute('data-labels') ?? '').replace(/^\[|\]$/g, '')
  const v = (el.getAttribute('data-values') ?? '').replace(/^\[|\]$/g, '')
  const labels = l.split(',').map(s => s.trim()).filter(Boolean)
  const values = v.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n))
  return { labels, values }
}

export function svgBarChart(labels: string[], values: number[]): string {
  const n = labels.length
  if (n === 0) return ''
  const maxV = Math.max(...values, 0) || 1
  const pT = 30, pB = 50, pL = 50, pR = 20
  const cW = VW - pL - pR, cH = VH - pT - pB
  const gW = cW / n, bW = gW * 0.6
  const many = n > 10, fs = many ? 9 : 11

  const parts: string[] = [
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VW} ${VH}" style="width:100%;max-height:${VH}px;display:block;">`,
    `<line x1="${pL}" y1="${pT}" x2="${pL}" y2="${pT + cH}" stroke="#ccc"/>`,
    `<line x1="${pL}" y1="${pT + cH}" x2="${pL + cW}" y2="${pT + cH}" stroke="#ccc"/>`,
  ]

  for (let i = 0; i < n; i++) {
    const color = COLORS[i % COLORS.length]
    const bH = (values[i] / maxV) * cH
    const x = (pL + i * gW + (gW - bW) / 2).toFixed(1)
    const y = (pT + cH - bH).toFixed(1)
    parts.push(`<rect x="${x}" y="${y}" width="${bW.toFixed(1)}" height="${bH.toFixed(1)}" fill="${color}" rx="2"/>`)
    if (!many) {
      const vs = Number.isInteger(values[i]) ? values[i] : values[i].toFixed(1)
      parts.push(
        `<text x="${(parseFloat(x) + bW / 2).toFixed(1)}" y="${(parseFloat(y) - 4).toFixed(1)}" ` +
        `text-anchor="middle" font-size="${fs}" fill="#555">${vs}</text>`
      )
    }
    const ld = escapeXml(labels[i].length > 10 ? labels[i].slice(0, 10) + '\u2026' : labels[i])
    const cx = (pL + i * gW + gW / 2).toFixed(1)
    parts.push(`<text x="${cx}" y="${pT + cH + 16}" text-anchor="middle" font-size="${fs}" fill="#555">${ld}</text>`)
  }

  parts.push('</svg>')
  return parts.join('')
}

export function svgPieChart(labels: string[], values: number[]): string {
  const n = labels.length
  if (n === 0) return ''
  const total = values.reduce((a, b) => a + b, 0) || 1
  const cx = 200, cy = 150, r = 120
  const lx = 340, ly0 = 60, rh = 24
  const vh = Math.max(VH, 60 + n * rh + 20)

  const parts: string[] = [
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VW} ${vh}" style="width:100%;max-height:${vh}px;display:block;">`,
  ]

  let angle = -Math.PI / 2
  for (let i = 0; i < n; i++) {
    const color = COLORS[i % COLORS.length]
    const sweep = (values[i] / total) * 2 * Math.PI
    const x1 = (cx + r * Math.cos(angle)).toFixed(3)
    const y1 = (cy + r * Math.sin(angle)).toFixed(3)
    angle += sweep
    const x2 = (cx + r * Math.cos(angle)).toFixed(3)
    const y2 = (cy + r * Math.sin(angle)).toFixed(3)
    const large = sweep > Math.PI ? 1 : 0
    parts.push(
      `<path d="M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${large},1 ${x2},${y2} Z" ` +
      `fill="${color}" stroke="#fff" stroke-width="2"/>`
    )
    const ly = ly0 + i * rh
    const ld = escapeXml(labels[i].length > 14 ? labels[i].slice(0, 14) + '\u2026' : labels[i])
    parts.push(`<rect x="${lx}" y="${ly - 10}" width="14" height="14" fill="${color}" rx="2"/>`)
    parts.push(`<text x="${lx + 18}" y="${ly}" font-size="11" fill="#555">${ld}</text>`)
  }

  parts.push('</svg>')
  return parts.join('')
}

export function renderChartsAsSvg(container: Element): void {
  container.querySelectorAll('.report-bar-chart').forEach(el => {
    const { labels, values } = parseChartData(el)
    if (!labels.length) return
    el.innerHTML = svgBarChart(labels, values)
  })
  container.querySelectorAll('.report-pie-chart').forEach(el => {
    const { labels, values } = parseChartData(el)
    if (!labels.length) return
    el.innerHTML = svgPieChart(labels, values)
  })
}
