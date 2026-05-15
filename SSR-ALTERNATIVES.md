# Server-side PDF rendering — alternatives evaluation

**Date:** 2026-05-15
**Status:** Research notes. No code change. Captures the trade-offs for a future decision to switch off `xhtml2pdf`.

## Why this doc exists

The app's A4 PDF path uses `xhtml2pdf` + `reportlab`. xhtml2pdf is CSS-2.1-only: no flexbox, no grid, no gradients, no `box-shadow`. That ceiling is real and will eventually be hit by a template. This doc records what the realistic replacements are, with verdicts under the project's hard constraint.

## Hard constraint

**Databricks Apps serverless: no OS packages.** The deploy environment has no `apt-get`, no `sudo`, and no way to install native system libraries (`libpango`, `libcairo`, `libharfbuzz`, Chromium shared libs, etc.) outside of what the base runtime image already ships with.

A library is therefore only viable if **all** of these hold:
- It is pure Python, OR it ships native code inside a manylinux wheel that is fully self-contained (does not dynamically link to a system library that isn't already in the base image).
- All of its transitive dependencies satisfy the same rule.

This is the same reason WeasyPrint was removed earlier in the project: it depends on Pango / Cairo / HarfBuzz, none of which are pip-installable wheels.

This rules out more libraries than it might appear, including some that "feel" pure-Python at first glance. The `xhtml2pdf 0.2.16+` chain pulls `svglib >= 1.6 → rlpycairo → pycairo`, and `pycairo`'s wheel dynamically links to system `libcairo` — which is why this project pins `svglib==1.5.1`.

## Candidate evaluation

### WeasyPrint — blocked

- Requires Pango, Cairo, HarfBuzz, GDK-PixBuf at runtime.
- None of these are PyPI wheels. The Linux distribution path is `apt-get install`.
- **Verdict:** out, unless the Databricks Apps runtime image starts bundling those system libs (unlikely; they're not Python tooling).

### Playwright / pyppeteer — almost certainly blocked

- Renders HTML in headless Chromium → PDF. Highest possible fidelity (full modern CSS, JS, web fonts).
- `pip install playwright` works, but `playwright install chromium` downloads a Chromium binary that dynamically links to a long list of system libs (`libnss3`, `libxcomposite1`, `libxrandr2`, `libasound2`, fonts, etc.). On a stock Databricks Apps base image these are not present.
- A 30-minute spike to confirm in a real Databricks App is worthwhile only when there is a concrete need; assume it's blocked otherwise.
- **Verdict:** out for now. Re-evaluate only if the base image documentation states the required Chromium shared libs are present.

### PyMuPDF `fitz.Story` — viable

- PyMuPDF ships a self-contained manylinux wheel. No system Cairo/Pango.
- `fitz.Story` renders an HTML/CSS subset to PDF with richer CSS support than xhtml2pdf (multi-column flow, better fonts, better tables).
- Fast — runs at native speed via MuPDF's C core.
- **Caveat:** AGPL-3.0 license (or commercial). Internal use inside a Databricks App is compatible with AGPL provided the source remains accessible to users of the app, but it's a flag worth raising with whoever maintains the project's licensing posture before adopting.
- **Verdict:** first-choice replacement if a switch is triggered, subject to license acceptance.

### Typst (`typst-py`) — viable, but expensive

- `typst-py` ships a Rust-based wheel on PyPI. Apache 2.0 license.
- Produces excellent PDFs — Typst is designed for typesetting and the output quality is the best in the candidate list.
- **Caveat:** Typst uses its own template language, not HTML. Migration would require either a Mustache-HTML → Typst translation layer (non-trivial; many HTML constructs have no Typst analogue) or a parallel template type alongside HTML and Markdown (more work in the editor, AI assistant, preview pipeline, and docs).
- **Verdict:** viable but not a drop-in. Worth it only if the template authoring experience is going to change anyway.

### fpdf2 — viable, but programmatic

- Pure Python. Apache 2.0.
- `FPDF.write_html()` exists but supports only a tiny HTML subset (no CSS, no layout primitives, no images via `src=data:`).
- Practically, fpdf2 is a "build a PDF page by page" library — you compose with `cell()`, `multi_cell()`, etc.
- **Verdict:** rules out the HTML-first templating model. Out of scope for this app unless the template layer is also rewritten.

### borb — viable, but programmatic

- Pure Python. AGPL-3.0 or commercial.
- Same shape as fpdf2: rich programmatic API, no real HTML-in path.
- **Verdict:** same conclusion as fpdf2.

### pdfme — viable, but programmatic

- Pure Python. MIT.
- JSON-template-based: you describe the document as a JSON structure of "paragraphs", "tables", "images", etc.
- **Verdict:** would require swapping the entire template authoring model. Not a renderer-only swap.

## Recommendation

**Stay on `xhtml2pdf`.** The 2026-05-15 upgrade (xhtml2pdf 0.2.11 → 0.2.17, reportlab 3.6.13 → 4.5.0) closes a four-year version gap and resolves the Python 3.13 build problem. The CSS-2.1 ceiling is a known limitation that templates can be written around.

## When to revisit

Switch off xhtml2pdf only if one of these triggers fires:
1. A real customer template requires CSS that xhtml2pdf cannot render (modern table layout, web fonts, flex/grid, complex backgrounds).
2. xhtml2pdf stops receiving releases for >18 months and a security or compatibility issue lands without an upstream fix.
3. The browser preview and the server-side PDF diverge in ways that cannot be hidden behind the existing PDF style restrictions, and the divergence is user-reported.

## If a switch is triggered

- **First choice:** PyMuPDF `fitz.Story`, subject to AGPL acceptance review.
- **Second choice:** Typst, accepting the cost of either a translation layer or a parallel template type.
- **Not a choice:** anything that adds a system-library dep. The constraint that started this doc still holds.
