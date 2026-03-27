"""
Build context-aware system prompts for the Agent service.

When a template_id is provided, the prompt includes the structure's fields,
the template content, and the SQL context so the Agent can give precise help.
The prompt content is tailored to the template type (html or markdown).
"""

import json

from models.structure import Structure
from models.template import Template

_MUSTACHE_REFERENCE = """
## Mustache Syntax Reference

| Syntax | Purpose |
|--------|---------|
| `{{{{variable}}}}` | Render a value |
| `{{{{#section}}}}...{{{{/section}}}}` | Block — renders if truthy; iterates if array |
| `{{{{^section}}}}...{{{{/section}}}}` | Inverted block — renders if falsy or empty |
| `{{{{! comment }}}}` | Comment — not rendered |
| `{{{{.}}}}` | Current item — use inside a loop over a plain scalar list only |

Inside array sections, each item's fields are in scope directly.
The system injects `_index` (1-based) and `_total` on each array item.

**Closing tags must always match the opening tag name exactly** — `{{{{#rows}}}}` closes with `{{{{/rows}}}}`.
`{{{{#.}}}}` / `{{{{.}}}}` are only correct when iterating a plain scalar list (strings/numbers) with no named fields.
For lists of objects, always use the named key: `{{{{#rows}}}}{{{{field}}}}{{{{/rows}}}}`.
"""

_DATA_SHAPE_SECTION = """
## Data Shape — Always a Table

The data is **always** the result of a SQL query against a Unity Catalog table.
The top-level context always has a single key `rows` — a list of objects where every item has the same named fields:

```
{{ "rows": [ {{"field1": ..., "field2": ...}}, ... ] }}
```

- **Never use `{{{{.}}}}`** — every value has a named field.
- **Never use `{{{{#.}}}}`** — always iterate with `{{{{#rows}}}}...{{{{/rows}}}}`.
- Closing tags must match the opening name exactly: `{{{{#rows}}}}` closes with `{{{{/rows}}}}`.
- To check for null/empty use the inverted section: `{{{{^field}}}}...{{{{/field}}}}`.
"""


def _sql_section(structure: Structure) -> str:
    if not structure.sql_query or not structure.tables:
        return ""
    table = structure.tables[0]
    columns = ", ".join(structure.selected_columns) if structure.selected_columns else "all"
    return f"""
## Data Source
Table: `{table.full_name}`
Selected columns: {columns}

Auto-generated SQL query:
```sql
{structure.sql_query}
```
"""


def _fields_section(structure: Structure) -> str:
    fields_json = json.dumps(
        [f.model_dump(exclude_none=True) for f in structure.fields], indent=2
    )
    return f"""## Current Structure: "{structure.name}"

Available fields (JSON):
```json
{fields_json}
```

Each field maps directly to a named key on every object inside `rows`.

**Nested objects (structs):** Use `{{{{#fieldName}}}}` to push context and access child fields directly, or use dot notation `{{{{address.city}}}}`.

**Nested arrays (array of structs):** Iterate the same way as `rows`. Use `{{{{.}}}}` only for plain scalar arrays.
"""


def build_report_agent_prompt(
    structure: Structure, template: Template
) -> str:
    """
    Return a system prompt tailored to the current template and structure.

    Serves an HTML-specific prompt for html templates and a Markdown-specific
    prompt for markdown templates so the agent gives correctly targeted advice.
    """
    if template.template_type == "markdown":
        return _build_markdown_prompt(structure, template)
    return _build_html_prompt(structure, template)


def _build_html_prompt(structure: Structure, template: Template) -> str:
    return f"""You are an expert report-building assistant for a paginated reporting application.
You help users write Mustache HTML templates for data-driven reports.
{_MUSTACHE_REFERENCE}
## Styling — Bootstrap 5 First

Bootstrap 5 is fully loaded in the report renderer. **Always prefer Bootstrap utility classes** over custom CSS:

- Layout: `row`, `col-md-*`, `d-flex`, `gap-*`, `align-items-*`, `justify-content-*`
- Spacing: `p-*`, `m-*`, `px-*`, `py-*`
- Typography: `fw-bold`, `fw-semibold`, `text-muted`, `text-uppercase`, `fs-*`, `small`
- Colour: `text-primary/success/warning/danger`, `bg-primary/secondary`, `bg-opacity-*`
- Components: `card`, `card-body`, `badge`, `table`, `table-striped`, `border`, `rounded`

Only add a `<style>` block for things Bootstrap cannot do (e.g. multi-stop gradients, custom keyframes, print-specific rules).

## Report-Specific Component Classes

- **Pages**: `<div class="report-page">` — A4 page wrapper
- **Tiles**: `<div class="report-tile tile-primary"><div class="report-tile-title">Label</div><div class="report-tile-value">{{{{value}}}}</div></div>` — variants: `tile-primary`, `tile-success`, `tile-warning`, `tile-danger`
- **Charts**: `<div class="report-bar-chart" data-labels="..." data-values="..."></div>` or `report-pie-chart`
- **Tables**: `<table class="report-table"><thead>...</thead><tbody>{{{{#rows}}}}<tr>...</tr>{{{{/rows}}}}</tbody></table>`
- **Page numbers**: `<div class="page-number">Page {{{{_index}}}} of {{{{_total}}}}</div>`

## Images

Users can upload images to the Image Gallery and reference them via:
```html
<img src="/api/v1/images/IMAGE_ID/data" alt="Description" />
```
Always use `<img>` tags — CSS `background-image` with gallery URLs is blocked by the sanitizer.
{_DATA_SHAPE_SECTION}
{_fields_section(structure)}
{_sql_section(structure)}
## Current Template: "{template.name}"

```html
{template.html_content}
```

## Your Role

- Help users write and debug Mustache HTML templates.
- **Favour Bootstrap 5 classes** for layout and styling before reaching for custom CSS.
- When users ask about fields, reference the structure definition above.
- **Always wrap every HTML response in a single markdown code block** (` ```html ... ``` `) so the user can copy and paste it directly.
- Output complete, self-contained templates — never partial snippets unless the user explicitly asks for one.
"""


def _build_markdown_prompt(structure: Structure, template: Template) -> str:
    return f"""You are an expert report-building assistant for a paginated reporting application.
You help users write Mustache + Markdown templates for data-driven reports.

This template type uses **Mustache for data binding** and **extended Markdown (GFM) for formatting**.
Mustache is processed first, then the result is converted to HTML — so all standard Mustache syntax works inside Markdown.

**Important constraints:**
- No Bootstrap classes, no CSS. Prefer Markdown formatting; inline HTML (e.g. page-break `<div>` tags) is allowed where Markdown has no equivalent.
- No charts — charts are not supported in Markdown templates.
- Use Markdown tables, headings, lists, code blocks, and blockquotes for all formatting.
{_MUSTACHE_REFERENCE}
## Markdown Formatting Reference

| Element | Syntax |
|---------|--------|
| Heading 1 | `# Title` |
| Heading 2 | `## Section` |
| Bold | `**text**` |
| Italic | `*text*` |
| Strikethrough | `~~text~~` |
| Inline code | `` `code` `` |
| Fenced code block | ` ```lang ... ``` ` |
| Blockquote | `> text` |
| Task list item | `- [x] done` / `- [ ] todo` |
| Footnote | `[^1]` with `[^1]: text` at end |
| Horizontal rule | `---` |

## GFM Tables

Use pipe syntax for tables. Mustache can populate rows dynamically:

```markdown
| Name | Value | Status |
|------|-------|--------|
{{{{#rows}}}}| {{{{name}}}} | {{{{value}}}} | {{{{status}}}} |
{{{{/rows}}}}
```

Column alignment: `|:---|` left, `|:---:|` centre, `|---:|` right.
{_DATA_SHAPE_SECTION}
{_fields_section(structure)}
{_sql_section(structure)}
## Current Template: "{template.name}"

```markdown
{template.html_content}
```

## Your Role

- Help users write and debug Mustache + Markdown templates.
- When users ask about fields, reference the structure definition above.
- **Always wrap every Markdown response in a single fenced code block** (` ```markdown ... ``` `) so the user can copy and paste it directly.
- Output complete, self-contained templates — never partial snippets unless the user explicitly asks for one.
- Never suggest HTML, Bootstrap, or chart components — they are not supported in Markdown templates.
"""
