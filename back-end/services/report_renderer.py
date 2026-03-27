"""
Server-side report renderer for scheduled executions.

Executes the structure's SQL query against the Databricks SQL warehouse,
builds the Mustache context, and renders the template HTML using chevron.
No user bearer token is available in scheduled context — the app's service
principal credentials (from environment) are used by SQLConnector by default.
"""

import re
from uuid import UUID

import altair as alt
import chevron
import markdown2
import vl_convert as vlc

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
  /* Pagination magic — global header/footer (injected into every .report-page by the renderer) */
  .report-global-header { border-bottom: 2px solid #2d3e50; padding-bottom: 1rem; margin-bottom: 1.5rem; }
  .report-global-footer { border-top: 1px solid #dee2e6; padding-top: 0.75rem; margin-top: 1.5rem; font-size: 0.8rem; color: #6c757d; }
"""

# ---------------------------------------------------------------------------
# Pagination layout magic — post-processing for header/footer and break-after
# ---------------------------------------------------------------------------

_DIV_OPEN_RE = re.compile(r'<div\b')
_DIV_CLOSE_RE = re.compile(r'</div>')
# Matches a .report-page opening tag — report-page as a standalone class (not a prefix like report-page-header)
_REPORT_PAGE_OPEN_RE = re.compile(
    r'<div\b[^>]*\bclass="(?:[^"]*\s|)report-page(?:\s[^"]*)?"[^>]*>'
)
_BREAK_AFTER_OPEN_RE = re.compile(r'<div\b([^>]*)\bdata-break-after="(\d+)"([^>]*)>')
_VOID_TAGS = frozenset(
    'area base br col embed hr img input link meta param source track wbr'.split()
)
_CHILD_TAG_RE = re.compile(r'<(/?)(\w+)([^>]*)>', re.DOTALL)


def _find_div_close(html: str, content_start: int) -> tuple[int | None, int | None]:
    """
    Find the </div> that closes a <div> whose content starts at content_start.
    Returns (inner_end, outer_end) — positions before/after the closing tag.
    Returns (None, None) on malformed HTML.
    """
    depth = 1
    pos = content_start
    while depth > 0:
        open_m = _DIV_OPEN_RE.search(html, pos)
        close_m = _DIV_CLOSE_RE.search(html, pos)
        if not close_m:
            return None, None
        if open_m and open_m.start() < close_m.start():
            depth += 1
            pos = open_m.end()
        else:
            depth -= 1
            if depth == 0:
                return close_m.start(), close_m.end()
            pos = close_m.end()
    return None, None


def _extract_class_div(html: str, cls: str) -> tuple[str | None, str]:
    """
    Find the first <div> whose class attribute contains `cls` as a standalone class,
    extract its inner HTML, and return (inner_html, html_without_that_div).
    Returns (None, html) if not found.
    """
    m = re.search(
        rf'<div\b[^>]*\bclass="(?:[^"]*\s|){re.escape(cls)}(?:\s[^"]*)?"[^>]*>',
        html,
    )
    if not m:
        return None, html
    inner_end, outer_end = _find_div_close(html, m.end())
    if inner_end is None:
        return None, html
    inner = html[m.end():inner_end]
    cleaned = html[:m.start()] + html[outer_end:]
    return inner, cleaned


def _inject_breaks_in_content(content: str, n: int) -> str:
    """
    Scan top-level child elements in `content` and insert a .page-break div
    after every n-th element. The final partial group never gets a trailing break.
    """
    BREAK = '<div class="page-break"></div>'
    parts: list[tuple[str, bool]] = []  # (text, is_break_marker)
    pos = 0
    depth = 0
    count = 0

    for m in _CHILD_TAG_RE.finditer(content):
        parts.append((content[pos:m.start()], False))
        is_close = bool(m.group(1))
        tag = m.group(2).lower()
        self_closing = m.group(3).rstrip().endswith('/') or tag in _VOID_TAGS
        parts.append((m.group(0), False))
        pos = m.end()

        if is_close:
            if depth > 0:
                depth -= 1
            if depth == 0:
                count += 1
                if count % n == 0:
                    parts.append((BREAK, True))
        elif not self_closing:
            depth += 1

    parts.append((content[pos:], False))

    # Drop trailing break marker if nothing meaningful follows it
    last_break = next((i for i in reversed(range(len(parts))) if parts[i][1]), -1)
    if last_break != -1:
        after_text = ''.join(t for t, _ in parts[last_break + 1:]).strip()
        if not after_text:
            parts = parts[:last_break] + parts[last_break + 1:]

    return ''.join(t for t, _ in parts)


def _inject_global_header_footer(html: str) -> str:
    """
    Find .report-global-header and .report-global-footer divs, remove them from
    their original positions, and inject copies at the top/bottom of every .report-page.
    """
    header_inner, html = _extract_class_div(html, 'report-global-header')
    footer_inner, html = _extract_class_div(html, 'report-global-footer')
    if not header_inner and not footer_inner:
        return html

    header_html = f'<div class="report-global-header">{header_inner}</div>' if header_inner else ''
    footer_html = f'<div class="report-global-footer">{footer_inner}</div>' if footer_inner else ''

    out: list[str] = []
    pos = 0
    for m in _REPORT_PAGE_OPEN_RE.finditer(html):
        inner_end, outer_end = _find_div_close(html, m.end())
        if inner_end is None:
            out.append(html[pos:m.end()])
            pos = m.end()
            continue
        out.append(html[pos:m.start()])
        out.append(m.group(0))
        out.append(header_html)
        out.append(html[m.end():inner_end])
        out.append(footer_html)
        out.append('</div>')
        pos = outer_end

    out.append(html[pos:])
    return ''.join(out)


def _apply_break_after(html: str) -> str:
    """
    Find <div data-break-after="N"> elements and inject .page-break divs
    after every N top-level child elements within each one.
    """
    out: list[str] = []
    pos = 0
    for m in _BREAK_AFTER_OPEN_RE.finditer(html):
        n = int(m.group(2))
        if n <= 0:
            continue
        content_start = m.end()
        inner_end, outer_end = _find_div_close(html, content_start)
        if inner_end is None:
            continue
        inner = html[content_start:inner_end]
        other_attrs = (m.group(1) + m.group(3)).strip()
        open_tag = f'<div {other_attrs}>' if other_attrs else '<div>'
        out.append(html[pos:m.start()])
        out.append(open_tag)
        out.append(_inject_breaks_in_content(inner, n))
        out.append('</div>')
        pos = outer_end

    out.append(html[pos:])
    return ''.join(out)


def process_layout_magic(html: str) -> str:
    """
    Post-process rendered Mustache HTML to apply pagination magic commands:
    - Clone .report-global-header / .report-global-footer into every .report-page
    - Inject .page-break divs at data-break-after="N" intervals
    """
    html = _inject_global_header_footer(html)
    html = _apply_break_after(html)
    return html


def _parse_chart_opts(all_attrs: str) -> dict:
    """Extract optional Vega-Lite data attributes from a chart div's attribute string."""
    opts: dict = {}
    for key in ('title', 'color-scheme', 'width', 'height', 'x-title', 'y-title', 'sort', 'inner-radius'):
        m = re.search(rf'\bdata-{re.escape(key)}=["\']([^"\']*)["\']', all_attrs)
        if m:
            opts[key] = m.group(1).strip()
    return opts


def _build_bar_spec(labels: list[str], values: list[float], opts: dict) -> dict:
    data = [{'label': l, 'value': v} for l, v in zip(labels, values)]
    sort = opts.get('sort') or None
    chart = (
        alt.Chart(alt.Data(values=data))
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X('label:N', sort=sort, axis=alt.Axis(labelAngle=-30, title=opts.get('x-title') or None)),
            y=alt.Y('value:Q', axis=alt.Axis(title=opts.get('y-title') or None)),
            color=alt.Color('label:N', scale=alt.Scale(scheme=opts.get('color-scheme') or 'tableau10'), legend=None),
        )
        .properties(
            width=int(opts['width']) if opts.get('width') else 500,
            height=int(opts['height']) if opts.get('height') else 250,
            title=opts.get('title') or '',
        )
    )
    return chart.to_dict()


def _build_pie_spec(labels: list[str], values: list[float], opts: dict) -> dict:
    data = [{'label': l, 'value': v} for l, v in zip(labels, values)]
    inner_radius = int(opts['inner-radius']) if opts.get('inner-radius') else 0
    chart = (
        alt.Chart(alt.Data(values=data))
        .mark_arc(innerRadius=inner_radius)
        .encode(
            theta=alt.Theta('value:Q'),
            color=alt.Color('label:N', scale=alt.Scale(scheme=opts.get('color-scheme') or 'tableau10')),
        )
        .properties(
            width=int(opts['width']) if opts.get('width') else 300,
            height=int(opts['height']) if opts.get('height') else 300,
            title=opts.get('title') or '',
        )
    )
    return chart.to_dict()


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
    """Replace .report-bar-chart and .report-pie-chart divs with inline Vega-Lite SVG."""
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
        opts = _parse_chart_opts(all_attrs)
        try:
            spec = _build_bar_spec(labels, values, opts) if chart_type == 'bar' else _build_pie_spec(labels, values, opts)
            svg = vlc.vegalite_to_svg(spec)
        except Exception as exc:
            L.warning(f"[ReportRenderer] Chart render failed ({chart_type}): {exc}")
            return m.group(0)
        return f'<div{before} class="{cls}"{after}>{svg}</div>'

    return _CHART_DIV_RE.sub(_replace, html)


_IMAGE_SRC_RE = re.compile(
    r'(src=["\'])(img:([0-9a-f-]{36}))(["\'])',
    re.IGNORECASE,
)


async def inline_images(html: str) -> str:
    """
    Replace img:UUID src attributes with base64 data URIs fetched directly
    from the database.

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


def build_html_document(body: str, title: str, is_markdown: bool = False) -> str:
    """
    Wrap a rendered report body in a complete HTML document with Bootstrap
    and report styles — equivalent to buildDocument() in PreviewExportModal.vue.

    Pass is_markdown=True for markdown templates to include markdown typography styles.
    Charts are pre-rendered as inline SVG before this is called — no JS required.
    """
    extra_styles = _MARKDOWN_STYLES if is_markdown else ""
    return (
        f'<!DOCTYPE html><html><head>\n'
        f'<meta charset="utf-8">\n'
        f'<title>{title}</title>\n'
        f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">\n'
        f'<style>{_REPORT_STYLES}{extra_styles}</style>\n'
        f'</head><body>{body}</body></html>'
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

    rendered = process_layout_magic(rendered)

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
    body = render_charts_as_svg(body)
    is_markdown = template.template_type == "markdown"
    full_html = build_html_document(body, template.name, is_markdown=is_markdown)
    try:
        pdf_bytes = weasyprint.HTML(string=full_html).write_pdf()
    except Exception as e:
        raise RuntimeError(f"Failed to convert template {template_id} to PDF: {e}") from e

    return pdf_bytes, template
