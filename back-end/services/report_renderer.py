"""
Server-side report renderer for scheduled executions.

Executes the structure's SQL query against the Databricks SQL warehouse,
builds the Mustache context, and renders the template HTML using chevron.
No user bearer token is available in scheduled context — the app's service
principal credentials (from environment) are used by SQLConnector by default.
"""

import math
import re
from uuid import UUID

import chevron
import markdown2

from common.connectors.sql import SQLConnector
from common.logger import log as L
from models.template import Template
from repositories.structures import StructuresRepository
from repositories.templates import TemplatesRepository
from services.data_query import DataQueryService

# Mirrors REPORT_STYLES in PreviewExportModal.vue — keep in sync.
_REPORT_STYLES = """
  @page { size: A4; margin: 8mm 10mm; }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; box-sizing: border-box; }
  body { margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; color: #212529; font-size: 14px; overflow-x: hidden; }
  .report-page { page-break-after: always; break-after: page; padding: 16px 20px; position: relative; max-width: 100%; overflow: hidden; }
  .report-page:last-child { page-break-after: auto; break-after: auto; }
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
  /* Bootstrap grid overrides — applied unconditionally so WeasyPrint (no viewport) and
     downloaded HTML files render columns correctly without relying on @media breakpoints. */
  .row { display: flex !important; flex-wrap: wrap !important; margin-right: -0.75rem; margin-left: -0.75rem; }
  [class*="col-"] { flex-shrink: 0; padding-right: 0.75rem; padding-left: 0.75rem; box-sizing: border-box; }
  .col-1,  .col-sm-1,  .col-md-1,  .col-lg-1,  .col-xl-1  { width: 8.3333%   !important; }
  .col-2,  .col-sm-2,  .col-md-2,  .col-lg-2,  .col-xl-2  { width: 16.6667%  !important; }
  .col-3,  .col-sm-3,  .col-md-3,  .col-lg-3,  .col-xl-3  { width: 25%       !important; }
  .col-4,  .col-sm-4,  .col-md-4,  .col-lg-4,  .col-xl-4  { width: 33.3333%  !important; }
  .col-5,  .col-sm-5,  .col-md-5,  .col-lg-5,  .col-xl-5  { width: 41.6667%  !important; }
  .col-6,  .col-sm-6,  .col-md-6,  .col-lg-6,  .col-xl-6  { width: 50%       !important; }
  .col-7,  .col-sm-7,  .col-md-7,  .col-lg-7,  .col-xl-7  { width: 58.3333%  !important; }
  .col-8,  .col-sm-8,  .col-md-8,  .col-lg-8,  .col-xl-8  { width: 66.6667%  !important; }
  .col-9,  .col-sm-9,  .col-md-9,  .col-lg-9,  .col-xl-9  { width: 75%       !important; }
  .col-10, .col-sm-10, .col-md-10, .col-lg-10, .col-xl-10 { width: 83.3333%  !important; }
  .col-11, .col-sm-11, .col-md-11, .col-lg-11, .col-xl-11 { width: 91.6667%  !important; }
  .col-12, .col-sm-12, .col-md-12, .col-lg-12, .col-xl-12 { width: 100%      !important; }
  .col { flex: 1 0 0% !important; }
  .d-flex { display: flex !important; }
  .gap-1 { gap: 0.25rem !important; }
  .gap-2 { gap: 0.5rem  !important; }
  .gap-3 { gap: 1rem    !important; }
  .gap-4 { gap: 1.5rem  !important; }
  .g-1 > *, .gx-1 > * { padding-right: 0.25rem !important; padding-left: 0.25rem !important; }
  .g-2 > *, .gx-2 > * { padding-right: 0.5rem  !important; padding-left: 0.5rem  !important; }
  .g-3 > *, .gx-3 > * { padding-right: 0.75rem !important; padding-left: 0.75rem !important; }
  .g-4 > *, .gx-4 > * { padding-right: 1rem    !important; padding-left: 1rem    !important; }
  /* Pagination magic — page break commands */
  .page-break { height: 0; margin: 0; padding: 0; border: none; display: block; page-break-after: always; break-after: page; }
  .page-break-before { height: 0; margin: 0; padding: 0; border: none; display: block; page-break-before: always; break-before: page; }
  .no-break { break-inside: avoid; page-break-inside: avoid; }
  /* Pagination magic — multi-column layouts */
  .report-columns-2 { column-count: 2; column-gap: 2rem; }
  .report-columns-3 { column-count: 3; column-gap: 1.5rem; }
  .report-columns-4 { column-count: 4; column-gap: 1rem; }
  /* Report grid — media-query-free CSS Grid for reliable PDF/email output.
     Prefer these over Bootstrap col-* in templates. Keep in sync with REPORT_STYLES
     in front-end/src/components/PreviewExportModal.vue. */
  .report-grid-2   { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
  .report-grid-3   { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
  .report-grid-4   { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
  .report-grid-1-2 { display: grid; grid-template-columns: 1fr 2fr; gap: 1rem; }
  .report-grid-2-1 { display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; }
  .report-grid-1-3 { display: grid; grid-template-columns: 1fr 3fr; gap: 1rem; }
  .report-grid-3-1 { display: grid; grid-template-columns: 3fr 1fr; gap: 1rem; }
  /* Pagination magic — global header/footer (injected into every .report-page by the renderer) */
  .report-global-header { border-bottom: 2px solid #2d3e50; padding-bottom: 1rem; margin-bottom: 1.5rem; }
  .report-global-footer { border-top: 1px solid #dee2e6; padding-top: 0.75rem; margin-top: 1.5rem; font-size: 0.8rem; color: #6c757d; }
"""

# Inline SVG chart renderer — mirrors chartSvg.ts in the frontend.
# Geometry constants must match _svg_bar_chart / _svg_pie_chart below exactly.
# Only included in HTML output; omitted for PDF (charts are pre-rendered as SVG).
_CHART_SCRIPT = """
<script>
(function(){
  var VW=560,VH=300;
  var COLORS=['#3498db','#2ecc71','#9b59b6','#f1c40f','#e74c3c','#1abc9c','#e67e22'];
  function parse(el){
    var l=(el.getAttribute('data-labels')||'').replace(/^\\[|\\]$/g,'');
    var v=(el.getAttribute('data-values')||'').replace(/^\\[|\\]$/g,'');
    return{labels:l.split(',').map(function(s){return s.trim()}).filter(Boolean),values:v.split(',').map(function(s){return parseFloat(s.trim())}).filter(function(n){return !isNaN(n)})};
  }
  function bar(labels,values){
    var n=labels.length,maxV=Math.max.apply(null,values.concat([0]))||1;
    var pT=30,pB=50,pL=50,pR=20,cW=VW-pL-pR,cH=VH-pT-pB,gW=cW/n,bW=gW*0.6,many=n>10,fs=many?9:11;
    var s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+VW+' '+VH+'" style="width:100%;max-height:'+VH+'px;display:block;">';
    s+='<line x1="'+pL+'" y1="'+pT+'" x2="'+pL+'" y2="'+(pT+cH)+'" stroke="#ccc"/>';
    s+='<line x1="'+pL+'" y1="'+(pT+cH)+'" x2="'+(pL+cW)+'" y2="'+(pT+cH)+'" stroke="#ccc"/>';
    for(var i=0;i<n;i++){
      var c=COLORS[i%COLORS.length],bH=(values[i]/maxV)*cH,x=(pL+i*gW+(gW-bW)/2).toFixed(1),y=(pT+cH-bH).toFixed(1);
      s+='<rect x="'+x+'" y="'+y+'" width="'+bW.toFixed(1)+'" height="'+bH.toFixed(1)+'" fill="'+c+'" rx="2"/>';
      if(!many){var vs=Number.isInteger(values[i])?values[i]:values[i].toFixed(1);s+='<text x="'+(parseFloat(x)+bW/2).toFixed(1)+'" y="'+(parseFloat(y)-4).toFixed(1)+'" text-anchor="middle" font-size="'+fs+'" fill="#555">'+vs+'</text>';}
      var ld=labels[i].length>10?labels[i].slice(0,10)+'\u2026':labels[i],cx=(pL+i*gW+gW/2).toFixed(1);
      s+='<text x="'+cx+'" y="'+(pT+cH+16)+'" text-anchor="middle" font-size="'+fs+'" fill="#555">'+ld+'</text>';
    }
    return s+'</svg>';
  }
  function pie(labels,values){
    var n=labels.length,total=values.reduce(function(a,b){return a+b},0)||1;
    var cx=200,cy=150,r=120,lx=340,ly0=60,rh=24,vh=Math.max(VH,60+n*rh+20);
    var s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 '+vh+'" style="width:100%;max-height:'+vh+'px;display:block;">';
    var a=-Math.PI/2;
    for(var i=0;i<n;i++){
      var c=COLORS[i%COLORS.length],sw=(values[i]/total)*2*Math.PI;
      var x1=(cx+r*Math.cos(a)).toFixed(3),y1=(cy+r*Math.sin(a)).toFixed(3);
      a+=sw;
      var x2=(cx+r*Math.cos(a)).toFixed(3),y2=(cy+r*Math.sin(a)).toFixed(3);
      var lg=sw>Math.PI?1:0;
      s+='<path d="M'+cx+','+cy+' L'+x1+','+y1+' A'+r+','+r+' 0 '+lg+',1 '+x2+','+y2+' Z" fill="'+c+'" stroke="#fff" stroke-width="2"/>';
      var ly=ly0+i*rh,ld=labels[i].length>14?labels[i].slice(0,14)+'\u2026':labels[i];
      s+='<rect x="'+lx+'" y="'+(ly-10)+'" width="14" height="14" fill="'+c+'" rx="2"/>';
      s+='<text x="'+(lx+18)+'" y="'+ly+'" font-size="11" fill="#555">'+ld+'</text>';
    }
    return s+'</svg>';
  }
  function renderAll(sel,fn){document.querySelectorAll(sel).forEach(function(el){var d=parse(el);if(!d.labels.length)return;el.innerHTML=fn(d.labels,d.values);});}
  document.addEventListener('DOMContentLoaded',function(){renderAll('.report-bar-chart',bar);renderAll('.report-pie-chart',pie);});
})();
</script>
"""

# ---- SVG geometry constants (must match _CHART_SCRIPT and chartSvg.ts exactly) ----
_SVG_COLORS = ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c', '#e67e22']
_SVG_VW = 560
_SVG_VH = 300


def _svg_bar_chart(labels: list[str], values: list[float]) -> str:
    """Return an inline SVG bar chart string."""
    n = len(labels)
    if n == 0:
        return ''
    max_val = max(values) if max(values) > 0 else 1
    p_top, p_bot, p_left, p_right = 30, 50, 50, 20
    chart_w = _SVG_VW - p_left - p_right
    chart_h = _SVG_VH - p_top - p_bot
    group_w = chart_w / n
    bar_w = group_w * 0.6
    many = n > 10
    fs = 9 if many else 11

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_SVG_VW} {_SVG_VH}"'
        f' style="width:100%;max-height:{_SVG_VH}px;display:block;">',
        f'<line x1="{p_left}" y1="{p_top}" x2="{p_left}" y2="{p_top + chart_h}" stroke="#ccc"/>',
        f'<line x1="{p_left}" y1="{p_top + chart_h}" x2="{p_left + chart_w}" y2="{p_top + chart_h}" stroke="#ccc"/>',
    ]
    for i, (label, value) in enumerate(zip(labels, values)):
        color = _SVG_COLORS[i % len(_SVG_COLORS)]
        bar_h = (value / max_val) * chart_h
        x = p_left + i * group_w + (group_w - bar_w) / 2
        y = p_top + chart_h - bar_h
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}" rx="2"/>'
        )
        if not many:
            val_str = str(int(value)) if value == int(value) else f'{value:.1f}'
            parts.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{y - 4:.1f}" text-anchor="middle"'
                f' font-size="{fs}" fill="#555">{val_str}</text>'
            )
        label_disp = label[:10] + '\u2026' if len(label) > 10 else label
        cx = p_left + i * group_w + group_w / 2
        parts.append(
            f'<text x="{cx:.1f}" y="{p_top + chart_h + 16}" text-anchor="middle"'
            f' font-size="{fs}" fill="#555">{label_disp}</text>'
        )
    parts.append('</svg>')
    return ''.join(parts)


def _svg_pie_chart(labels: list[str], values: list[float]) -> str:
    """Return an inline SVG pie chart with legend."""
    n = len(labels)
    if n == 0:
        return ''
    total = sum(values) or 1
    cx, cy, r = 200, 150, 120
    lx, ly0, row_h = 340, 60, 24
    vh = max(_SVG_VH, 60 + n * row_h + 20)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_SVG_VW} {vh}"'
        f' style="width:100%;max-height:{vh}px;display:block;">',
    ]
    angle = -math.pi / 2
    for i, (label, value) in enumerate(zip(labels, values)):
        color = _SVG_COLORS[i % len(_SVG_COLORS)]
        sweep = (value / total) * 2 * math.pi
        x1 = cx + r * math.cos(angle)
        y1 = cy + r * math.sin(angle)
        angle += sweep
        x2 = cx + r * math.cos(angle)
        y2 = cy + r * math.sin(angle)
        large = 1 if sweep > math.pi else 0
        parts.append(
            f'<path d="M{cx},{cy} L{x1:.3f},{y1:.3f} A{r},{r} 0 {large},1 {x2:.3f},{y2:.3f} Z"'
            f' fill="{color}" stroke="#fff" stroke-width="2"/>'
        )
        ly = ly0 + i * row_h
        label_disp = label[:14] + '\u2026' if len(label) > 14 else label
        parts.append(f'<rect x="{lx}" y="{ly - 10}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{lx + 18}" y="{ly}" font-size="11" fill="#555">{label_disp}</text>')
    parts.append('</svg>')
    return ''.join(parts)


_MARKDOWN_STYLES = """
  .markdown-body { max-width: 860px; margin: 0 auto; padding: 2rem; font-size: 15px; line-height: 1.7; color: #212529; }
  .markdown-body h1, .markdown-body h2, .markdown-body h3,
  .markdown-body h4, .markdown-body h5, .markdown-body h6 { color: #2d3e50; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; }
  .markdown-body h1 { font-size: 2rem; font-weight: 700; border-bottom: 2px solid #2d3e50; padding-bottom: 0.5rem; }
  .markdown-body h2 { font-size: 1.5rem; border-bottom: 1px solid #dee2e6; padding-bottom: 0.25rem; }
  .markdown-body h3 { font-size: 1.25rem; }
  .markdown-body p { margin-bottom: 1rem; }
  .markdown-body table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
  .markdown-body table thead { background: #2d3e50; color: white; }
  .markdown-body table th { padding: 0.75rem 1rem; text-align: left; font-weight: 600; font-size: 0.875rem; }
  .markdown-body table td { padding: 0.625rem 1rem; border-bottom: 1px solid #eee; }
  .markdown-body table tbody tr:nth-child(even) { background: #f8f9fa; }
  .markdown-body code { background: #f3f3f3; padding: 0.15rem 0.4rem; border-radius: 3px; font-family: 'Fira Code', 'Consolas', monospace; font-size: 0.875em; color: #c0392b; }
  .markdown-body pre { background: #2d2d44; color: #f8f8f2; padding: 1rem; border-radius: 6px; overflow-x: auto; margin-bottom: 1rem; }
  .markdown-body pre code { background: none; color: inherit; padding: 0; }
  .markdown-body blockquote { border-left: 4px solid #3498db; margin: 0 0 1rem; padding: 0.5rem 1rem; background: #f0f8ff; color: #555; border-radius: 0 4px 4px 0; }
  .markdown-body blockquote p { margin: 0; }
  .markdown-body ul, .markdown-body ol { padding-left: 1.75rem; margin-bottom: 1rem; }
  .markdown-body li { margin-bottom: 0.3rem; }
  .markdown-body hr { border: none; border-top: 1px solid #dee2e6; margin: 1.5rem 0; }
  .markdown-body del { color: #6c757d; }
  .markdown-body input[type="checkbox"] { margin-right: 0.4rem; }
  .markdown-body a { color: #3498db; text-decoration: none; }
  .markdown-body a:hover { text-decoration: underline; }
"""

_MARKDOWN_EXTRAS = [
    "tables",
    "fenced-code-blocks",
    "footnotes",
    "strike",
    "task_list",
    "header-ids",
]


def _render_markdown(content: str) -> str:
    """Convert Markdown content to an HTML fragment wrapped in .markdown-body."""
    html = markdown2.markdown(content, extras=_MARKDOWN_EXTRAS)
    return f'<div class="markdown-body">{html}</div>'


_CHART_DIV_RE = re.compile(
    r'<div\b([^>]*)\bclass="([^"]*\breport-(bar|pie)-chart\b[^"]*)"([^>]*)>(.*?)</div>',
    re.DOTALL,
)
_DATA_LABELS_RE = re.compile(r'\bdata-labels="([^"]*)"')
_DATA_VALUES_RE = re.compile(r'\bdata-values="([^"]*)"')


def render_charts_as_svg(html: str) -> str:
    """Replace .report-bar-chart and .report-pie-chart divs with inline SVG markup."""
    def _replace(m: re.Match) -> str:
        before, cls, chart_type, after = m.group(1), m.group(2), m.group(3), m.group(4)
        all_attrs = before + f' class="{cls}"' + after
        lm = _DATA_LABELS_RE.search(all_attrs)
        vm = _DATA_VALUES_RE.search(all_attrs)
        if not lm or not vm:
            return m.group(0)
        raw_labels = lm.group(1).strip().lstrip('[').rstrip(']')
        raw_values = vm.group(1).strip().lstrip('[').rstrip(']')
        labels = [s.strip() for s in raw_labels.split(',') if s.strip()]
        if not labels:
            return m.group(0)
        try:
            values = [float(v.strip()) for v in raw_values.split(',') if v.strip()]
        except ValueError:
            return m.group(0)
        svg = _svg_bar_chart(labels, values) if chart_type == 'bar' else _svg_pie_chart(labels, values)
        return f'<div{before} class="{cls}"{after}>{svg}</div>'

    return _CHART_DIV_RE.sub(_replace, html)


_IMAGE_SRC_RE = re.compile(
    r'(src=["\'])(/api/v1/images/([0-9a-f-]{36})/data)(["\'])',
    re.IGNORECASE,
)


async def inline_images(html: str) -> str:
    """
    Replace /api/v1/images/{uuid}/data src attributes with base64 data URIs
    fetched directly from the database.

    Safe to call for both HTML downloads and WeasyPrint — images that cannot
    be resolved are left as-is rather than raising.
    """
    from repositories.images import ImagesRepository

    uuids = {m.group(3) for m in _IMAGE_SRC_RE.finditer(html)}
    if not uuids:
        return html

    repo = ImagesRepository()
    data_map: dict[str, str] = {}
    for uid in uuids:
        try:
            result = await repo.get_data(UUID(uid))
            if result:
                mime_type, data_b64 = result
                data_map[uid] = f"data:{mime_type};base64,{data_b64}"
        except Exception:
            L.warning(f"[ReportRenderer] Could not inline image {uid}")

    def _replace(m: re.Match) -> str:
        uid = m.group(3)
        return f'{m.group(1)}{data_map[uid]}{m.group(4)}' if uid in data_map else m.group(0)

    return _IMAGE_SRC_RE.sub(_replace, html)


def build_html_document(body: str, title: str, include_charts: bool = True, is_markdown: bool = False) -> str:
    """
    Wrap a rendered report body in a complete HTML document with Bootstrap
    and report styles — equivalent to buildDocument() in PreviewExportModal.vue.

    Pass include_charts=False for WeasyPrint (no JS engine).
    Pass is_markdown=True for markdown templates to include markdown typography styles.
    """
    chart_script = _CHART_SCRIPT if (include_charts and not is_markdown) else ""
    extra_styles = _MARKDOWN_STYLES if is_markdown else ""
    return (
        f'<!DOCTYPE html><html><head>\n'
        f'<meta charset="utf-8">\n'
        f'<title>{title}</title>\n'
        f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">\n'
        f'<style>{_REPORT_STYLES}{extra_styles}</style>\n'
        f'</head><body>{body}{chart_script}</body></html>'
    )


async def render_report(template_id: UUID) -> tuple[str, Template]:
    """
    Render a report template server-side using the app's service principal.

    Returns a (rendered_body, template) tuple — the body is a raw HTML
    fragment suitable for email or wrapping with build_html_document().
    Raises ValueError if the template or structure cannot be found.
    Raises RuntimeError on query or rendering failure.
    """
    templates_repo = TemplatesRepository()
    structures_repo = StructuresRepository()

    template = await templates_repo.get_by_id(template_id)
    if not template:
        raise ValueError(f"Template {template_id} not found")

    structure = await structures_repo.get_by_id(template.structure_id)
    if not structure:
        raise ValueError(f"Structure {template.structure_id} not found")

    if not structure.sql_query:
        L.warning(f"[ReportRenderer] Template {template_id} has no SQL query — rendering empty")
        context: dict = {"rows": []}
    else:
        try:
            svc = DataQueryService(sql_connector=SQLConnector())
            result = await svc.execute_for_preview(template_id, limit=10000)
            context = result.get("data", {"rows": []})
        except Exception as e:
            raise RuntimeError(f"Failed to execute query for template {template_id}: {e}") from e

    try:
        rendered = chevron.render(template.html_content, context)
    except Exception as e:
        raise RuntimeError(f"Failed to render template {template_id}: {e}") from e

    if template.template_type == "markdown":
        rendered = _render_markdown(rendered)

    return rendered, template


async def render_report_pdf(template_id: UUID) -> tuple[bytes, Template]:
    """
    Render a report template to PDF bytes using WeasyPrint.

    Wraps the rendered body in a full HTML document (Bootstrap + styles)
    before passing to WeasyPrint so that all styles are applied.
    Returns a (pdf_bytes, template) tuple.
    """
    import weasyprint  # lazy — requires system libs (pango/cairo); not needed at import time

    body, template = await render_report(template_id)
    body = await inline_images(body)
    is_markdown = template.template_type == "markdown"
    if not is_markdown:
        body = render_charts_as_svg(body)
    full_html = build_html_document(body, template.name, include_charts=False, is_markdown=is_markdown)
    try:
        pdf_bytes = weasyprint.HTML(string=full_html).write_pdf()
    except Exception as e:
        raise RuntimeError(f"Failed to convert template {template_id} to PDF: {e}") from e

    return pdf_bytes, template
