"""
Unit tests for services/report_renderer.py.

All external dependencies (repos, DataQueryService, chevron) are mocked.
Fixtures live in back-end/tests/fixtures/ — fully synthetic, no customer data.
"""
from __future__ import annotations

import base64
import struct
import uuid
import zlib
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.fixtures.synthetic_data import (
    KPI_ROWS,
    KPI_TEMPLATE,
    LOGO_UUID,
    SUPPLIER_ROWS,
    SUPPLIER_TEMPLATE,
    kpi_context_with_first,
)

from models.structure import Structure, StructureTable
from models.template import Template

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)


def _make_1x1_png() -> bytes:
    """Build a minimal valid 1×1 white-pixel PNG without PIL."""
    def _chunk(name: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)

    return (
        b'\x89PNG\r\n\x1a\n'
        + _chunk(b'IHDR', struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + _chunk(b'IDAT', zlib.compress(b'\x00\xff\xff\xff'))
        + _chunk(b'IEND', b'')
    )


TID = uuid.uuid4()
SID = uuid.uuid4()
PID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _template(*, sql_via_structure: bool = True) -> Template:
    return Template(
        id=TID,
        name="Report",
        structure_id=SID,
        html_content="<p>{{#rows}}{{name}}{{/rows}}</p>",
        created_at=NOW,
        updated_at=NOW,
    )


def _structure(*, sql_query: str | None = "SELECT name FROM t") -> Structure:
    return Structure(
        id=SID,
        name="My Structure",
        project_id=PID,
        fields=[],
        tables=[StructureTable(full_name="cat.sch.tbl", alias="tbl")],
        relationships=[],
        selected_columns=[],
        sql_query=sql_query,
        created_at=NOW,
        updated_at=NOW,
    )


def _mock_templates_repo(template=None):
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=template)
    return repo


def _mock_structures_repo(structure=None):
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=structure)
    return repo


def _mock_data_query_svc(result=None):
    svc = MagicMock()
    svc.execute_for_preview = AsyncMock(return_value=result or {"data": {"rows": []}})
    return svc


# ---------------------------------------------------------------------------
# render_report
# ---------------------------------------------------------------------------


class TestRenderReport:
    @pytest.mark.asyncio
    async def test_raises_value_error_when_template_not_found(self):
        with (
            patch("services.report_renderer.TemplatesRepository", return_value=_mock_templates_repo(None)),
            patch("services.report_renderer.StructuresRepository", return_value=_mock_structures_repo()),
        ):
            from services.report_renderer import render_report
            with pytest.raises(ValueError, match="Template"):
                await render_report(TID)

    @pytest.mark.asyncio
    async def test_raises_value_error_when_structure_not_found(self):
        with (
            patch("services.report_renderer.TemplatesRepository", return_value=_mock_templates_repo(_template())),
            patch("services.report_renderer.StructuresRepository", return_value=_mock_structures_repo(None)),
        ):
            from services.report_renderer import render_report
            with pytest.raises(ValueError, match="Structure"):
                await render_report(TID)

    @pytest.mark.asyncio
    async def test_returns_rendered_html_on_success(self):
        tmpl = _template()
        struct = _structure()
        query_result = {"data": {"rows": [{"name": "Alice"}]}}

        mock_svc = _mock_data_query_svc(query_result)

        with (
            patch("services.report_renderer.TemplatesRepository", return_value=_mock_templates_repo(tmpl)),
            patch("services.report_renderer.StructuresRepository", return_value=_mock_structures_repo(struct)),
            patch("services.report_renderer.DataQueryService", return_value=mock_svc),
            patch("services.report_renderer.SQLConnector"),
        ):
            from services.report_renderer import render_report
            result, returned_template = await render_report(TID)

        assert "Alice" in result
        assert isinstance(result, str)
        assert returned_template.id == TID

    @pytest.mark.asyncio
    async def test_renders_empty_context_when_no_sql_query(self):
        tmpl = Template(
            id=TID,
            name="Report",
            structure_id=SID,
            html_content="<p>{{#rows}}row{{/rows}}</p>",
            created_at=NOW,
            updated_at=NOW,
        )
        struct = _structure(sql_query=None)

        with (
            patch("services.report_renderer.TemplatesRepository", return_value=_mock_templates_repo(tmpl)),
            patch("services.report_renderer.StructuresRepository", return_value=_mock_structures_repo(struct)),
        ):
            from services.report_renderer import render_report
            result, _ = await render_report(TID)

        assert isinstance(result, str)
        assert "row" not in result  # empty rows — mustache block renders nothing

    @pytest.mark.asyncio
    async def test_raises_runtime_error_when_query_fails(self):
        tmpl = _template()
        struct = _structure()

        mock_svc = MagicMock()
        mock_svc.execute_for_preview = AsyncMock(side_effect=ConnectionError("Databricks down"))

        with (
            patch("services.report_renderer.TemplatesRepository", return_value=_mock_templates_repo(tmpl)),
            patch("services.report_renderer.StructuresRepository", return_value=_mock_structures_repo(struct)),
            patch("services.report_renderer.DataQueryService", return_value=mock_svc),
            patch("services.report_renderer.SQLConnector"),
        ):
            from services.report_renderer import render_report
            with pytest.raises(RuntimeError, match="Failed to execute query"):
                await render_report(TID)

    @pytest.mark.asyncio
    async def test_raises_runtime_error_when_render_fails(self):
        tmpl = _template()
        struct = _structure()
        mock_svc = _mock_data_query_svc({"data": {"rows": []}})

        with (
            patch("services.report_renderer.TemplatesRepository", return_value=_mock_templates_repo(tmpl)),
            patch("services.report_renderer.StructuresRepository", return_value=_mock_structures_repo(struct)),
            patch("services.report_renderer.DataQueryService", return_value=mock_svc),
            patch("services.report_renderer.SQLConnector"),
            patch("services.report_renderer.chevron.render", side_effect=Exception("bad template")),
        ):
            from services.report_renderer import render_report
            with pytest.raises(RuntimeError, match="Failed to render template"):
                await render_report(TID)

    @pytest.mark.asyncio
    async def test_data_query_called_with_template_id_and_full_limit(self):
        tmpl = _template()
        struct = _structure()
        mock_svc = _mock_data_query_svc({"data": {"rows": []}})

        with (
            patch("services.report_renderer.TemplatesRepository", return_value=_mock_templates_repo(tmpl)),
            patch("services.report_renderer.StructuresRepository", return_value=_mock_structures_repo(struct)),
            patch("services.report_renderer.DataQueryService", return_value=mock_svc),
            patch("services.report_renderer.SQLConnector"),
        ):
            from services.report_renderer import render_report
            await render_report(TID)

        mock_svc.execute_for_preview.assert_awaited_once_with(TID, limit=10000)

    @pytest.mark.asyncio
    async def test_uses_data_key_from_query_result(self):
        tmpl = Template(
            id=TID,
            name="Report",
            structure_id=SID,
            html_content="{{#rows}}{{val}}{{/rows}}",
            created_at=NOW,
            updated_at=NOW,
        )
        struct = _structure()
        query_result = {"data": {"rows": [{"val": "X"}]}}
        mock_svc = _mock_data_query_svc(query_result)

        with (
            patch("services.report_renderer.TemplatesRepository", return_value=_mock_templates_repo(tmpl)),
            patch("services.report_renderer.StructuresRepository", return_value=_mock_structures_repo(struct)),
            patch("services.report_renderer.DataQueryService", return_value=mock_svc),
            patch("services.report_renderer.SQLConnector"),
        ):
            from services.report_renderer import render_report
            result, _ = await render_report(TID)

        assert "X" in result


# ---------------------------------------------------------------------------
# render_charts_as_svg
# ---------------------------------------------------------------------------


class TestRenderChartsAsSvg:
    def test_bar_chart_div_replaced_with_svg(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-bar-chart" data-labels="[Jan,Feb]" data-values="[100,200]"></div>'
        result = render_charts_as_svg(html)
        assert '<svg' in result
        assert 'report-bar-chart' in result
        assert '<rect' in result

    def test_pie_chart_div_replaced_with_svg(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-pie-chart" data-labels="[A,B,C]" data-values="[30,50,20]"></div>'
        result = render_charts_as_svg(html)
        assert '<svg' in result
        assert 'report-pie-chart' in result
        assert '<path' in result

    def test_missing_data_attributes_returns_div_unchanged(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-bar-chart"></div>'
        assert render_charts_as_svg(html) == html

    def test_non_numeric_values_returns_div_unchanged(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-bar-chart" data-labels="[A,B]" data-values="[x,y]"></div>'
        assert render_charts_as_svg(html) == html

    def test_all_zero_values_does_not_raise(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-bar-chart" data-labels="[A,B]" data-values="[0,0]"></div>'
        result = render_charts_as_svg(html)
        assert '<svg' in result

    def test_non_chart_html_is_unchanged(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="some-other-class"><p>Hello</p></div>'
        assert render_charts_as_svg(html) == html

    def test_pie_chart_legend_entries_present(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-pie-chart" data-labels="[Alpha,Beta]" data-values="[60,40]"></div>'
        result = render_charts_as_svg(html)
        assert 'Alpha' in result
        assert 'Beta' in result

    def test_bracket_stripped_from_data_attributes(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-bar-chart" data-labels="[X,Y,Z]" data-values="[10,20,30]"></div>'
        result = render_charts_as_svg(html)
        assert 'X' in result
        assert '<rect' in result

    def test_data_title_applied_to_bar_chart(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-bar-chart" data-labels="A,B" data-values="10,20" data-title="My Chart"></div>'
        result = render_charts_as_svg(html)
        assert '<svg' in result
        assert 'My Chart' in result

    def test_data_title_applied_to_pie_chart(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-pie-chart" data-labels="A,B" data-values="40,60" data-title="Pie Title"></div>'
        result = render_charts_as_svg(html)
        assert '<svg' in result
        assert 'Pie Title' in result

    def test_color_scheme_does_not_raise(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-bar-chart" data-labels="A,B" data-values="10,20" data-color-scheme="blues"></div>'
        result = render_charts_as_svg(html)
        assert '<svg' in result

    def test_sort_ascending_does_not_raise(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-bar-chart" data-labels="C,A,B" data-values="3,1,2" data-sort="ascending"></div>'
        result = render_charts_as_svg(html)
        assert '<svg' in result

    def test_inner_radius_produces_donut(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-pie-chart" data-labels="A,B" data-values="50,50" data-inner-radius="50"></div>'
        result = render_charts_as_svg(html)
        assert '<svg' in result

    def test_markdown_template_charts_render(self):
        from services.report_renderer import render_charts_as_svg

        html = (
            '<div class="markdown-body">'
            '<div class="report-bar-chart" data-labels="Jan,Feb" data-values="100,200"></div>'
            '</div>'
        )
        result = render_charts_as_svg(html)
        assert '<svg' in result
        assert '<rect' in result


# ---------------------------------------------------------------------------
# render_charts_for_pdf
# ---------------------------------------------------------------------------


class TestRenderChartsForPdf:
    def test_bar_chart_replaced_with_png_img_tag(self):
        from services.report_renderer import render_charts_for_pdf

        html = '<div class="report-bar-chart" data-labels="[Jan,Feb]" data-values="[100,200]"></div>'
        result = render_charts_for_pdf(html)
        assert '<img ' in result
        assert 'data:image/png;base64,' in result

    def test_pie_chart_replaced_with_png_img_tag(self):
        from services.report_renderer import render_charts_for_pdf

        html = '<div class="report-pie-chart" data-labels="[A,B]" data-values="[60,40]"></div>'
        result = render_charts_for_pdf(html)
        assert '<img ' in result
        assert 'data:image/png;base64,' in result

    def test_missing_data_returns_div_unchanged(self):
        from services.report_renderer import render_charts_for_pdf

        html = '<div class="report-bar-chart"></div>'
        assert render_charts_for_pdf(html) == html

    def test_non_numeric_values_returns_div_unchanged(self):
        from services.report_renderer import render_charts_for_pdf

        html = '<div class="report-bar-chart" data-labels="[A,B]" data-values="[x,y]"></div>'
        assert render_charts_for_pdf(html) == html

    def test_vega_exception_returns_div_unchanged(self):
        from services.report_renderer import render_charts_for_pdf
        import services.report_renderer as rr

        html = '<div class="report-bar-chart" data-labels="A,B" data-values="10,20"></div>'
        with patch.object(rr, "vlc") as mock_vlc:
            mock_vlc.vegalite_to_png.side_effect = RuntimeError("vega error")
            result = render_charts_for_pdf(html)
        assert result == html

    def test_non_chart_html_unchanged(self):
        from services.report_renderer import render_charts_for_pdf

        html = '<div class="some-other-class"><p>Hello</p></div>'
        assert render_charts_for_pdf(html) == html


# ---------------------------------------------------------------------------
# build_pdf_html_document
# ---------------------------------------------------------------------------


class TestBuildPdfHtmlDocument:
    def test_returns_complete_html_document(self):
        from services.report_renderer import build_pdf_html_document

        result = build_pdf_html_document("<p>Body</p>", "My Report")
        assert result.startswith("<!DOCTYPE html>")
        assert "<p>Body</p>" in result

    def test_title_embedded(self):
        from services.report_renderer import build_pdf_html_document

        result = build_pdf_html_document("", "KPI Dashboard")
        assert "<title>KPI Dashboard</title>" in result

    def test_no_bootstrap_cdn_link(self):
        from services.report_renderer import build_pdf_html_document

        result = build_pdf_html_document("", "T")
        assert "cdn.jsdelivr.net" not in result

    def test_uses_a4_page_size(self):
        from services.report_renderer import build_pdf_html_document

        result = build_pdf_html_document("", "T")
        assert "A4" in result

    def test_markdown_styles_included_when_flag_set(self):
        from services.report_renderer import build_pdf_html_document

        result = build_pdf_html_document("", "T", is_markdown=True)
        assert "markdown-body" in result

    def test_no_markdown_styles_by_default(self):
        from services.report_renderer import build_pdf_html_document

        result = build_pdf_html_document("", "T", is_markdown=False)
        assert "markdown-body" not in result

    def test_short_circuit_on_full_html_doc(self):
        """If body is already a full HTML doc, it should be returned as-is."""
        from services.report_renderer import build_pdf_html_document

        full = '<!DOCTYPE html><html><head><title>X</title></head><body>BODY</body></html>'
        result = build_pdf_html_document(full, "ignored")
        assert result == full

    def test_short_circuit_warns_unconditionally(self, caplog):
        """Short-circuit drops _PDF_STYLES; must warn on every full-doc body."""
        import logging
        from services.report_renderer import build_pdf_html_document

        full = '<!DOCTYPE html><html><body>x</body></html>'
        with caplog.at_level(logging.WARNING):
            build_pdf_html_document(full, "T", is_markdown=False)
        assert any("full HTML document" in r.message for r in caplog.records)

    def test_short_circuit_warns_when_markdown_flag_set(self, caplog):
        """Same warning fires when is_markdown=True — both styling sources are dropped."""
        import logging
        from services.report_renderer import build_pdf_html_document

        full = '<!DOCTYPE html><html><body>x</body></html>'
        with caplog.at_level(logging.WARNING):
            build_pdf_html_document(full, "T", is_markdown=True)
        assert any("full HTML document" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# html_to_pdf_bytes
# ---------------------------------------------------------------------------


class TestHtmlToPdfBytes:
    def test_simple_html_produces_valid_pdf(self):
        from services.report_renderer import html_to_pdf_bytes, build_pdf_html_document

        html = build_pdf_html_document("<h1>Test</h1><p>Hello world</p>", "Test")
        pdf = html_to_pdf_bytes(html)
        assert pdf.startswith(b'%PDF')
        assert len(pdf) > 0

    def test_image_data_uri_increases_pdf_size(self):
        """xhtml2pdf must embed the image — PDF with a data: URI should be larger than without."""
        from services.report_renderer import html_to_pdf_bytes, build_pdf_html_document

        png_b64 = base64.b64encode(_make_1x1_png()).decode()

        html_no_img = build_pdf_html_document("<p>No image</p>", "Test")
        html_with_img = build_pdf_html_document(
            f'<p>With image</p><img src="data:image/png;base64,{png_b64}" width="100" height="100" />',
            "Test",
        )

        pdf_no_img = html_to_pdf_bytes(html_no_img)
        pdf_with_img = html_to_pdf_bytes(html_with_img)

        assert pdf_with_img.startswith(b'%PDF')
        assert len(pdf_with_img) > len(pdf_no_img), (
            "PDF with an embedded image should be larger than without one — "
            "if this fails, xhtml2pdf is silently dropping data: URI images"
        )

    def test_returns_pdf_when_pisa_reports_nonfatal_errors(self, caplog):
        """pisa.err is a warning count, not a fatal flag — must not raise when buffer is valid."""
        import io
        import logging
        from services.report_renderer import html_to_pdf_bytes

        fake_result = MagicMock()
        fake_result.err = 5  # parser logged 5 non-fatal issues

        def fake_pisa_document(src, dest, encoding, link_callback=None):
            dest.write(b'%PDF-1.4\n%fake pdf content\n')
            return fake_result

        with patch("xhtml2pdf.pisa.pisaDocument", side_effect=fake_pisa_document):
            with caplog.at_level(logging.WARNING):
                pdf = html_to_pdf_bytes("<html></html>")
        assert pdf.startswith(b'%PDF')
        assert any("5" in r.message and "non-fatal" in r.message.lower() for r in caplog.records)

    def test_raises_when_buffer_is_empty(self):
        """If xhtml2pdf produces no PDF bytes at all, that is a real failure."""
        from services.report_renderer import html_to_pdf_bytes

        fake_result = MagicMock()
        fake_result.err = 1

        def fake_pisa_document(src, dest, encoding, link_callback=None):
            return fake_result  # writes nothing

        with patch("xhtml2pdf.pisa.pisaDocument", side_effect=fake_pisa_document):
            with pytest.raises(RuntimeError, match="invalid"):
                html_to_pdf_bytes("<html></html>")


# ---------------------------------------------------------------------------
# Full PDF pipeline — supplier template
# ---------------------------------------------------------------------------


class TestPdfPipelineSupplierTemplate:
    def test_chart_divs_replaced_with_png_imgs_after_mustache(self):
        import chevron
        from services.report_renderer import render_charts_for_pdf

        rendered = chevron.render(SUPPLIER_TEMPLATE, {"rows": SUPPLIER_ROWS})
        result = render_charts_for_pdf(rendered)

        assert 'report-bar-chart' not in result
        assert 'data:image/png;base64,' in result

    def test_supplier_names_present_in_rendered_body(self):
        import chevron
        from services.report_renderer import render_charts_for_pdf

        rendered = chevron.render(SUPPLIER_TEMPLATE, {"rows": SUPPLIER_ROWS})
        rendered = render_charts_for_pdf(rendered)

        assert "ACME Corp" in rendered
        assert "Global Trade Ltd" in rendered

    @pytest.mark.asyncio
    async def test_full_pipeline_produces_valid_pdf(self):
        import chevron
        from services.report_renderer import (
            html_to_pdf_bytes,
            build_pdf_html_document,
            inline_images,
            render_charts_for_pdf,
        )

        rendered = chevron.render(SUPPLIER_TEMPLATE, {"rows": SUPPLIER_ROWS})
        rendered = render_charts_for_pdf(rendered)
        rendered = await inline_images(rendered)
        html = build_pdf_html_document(rendered, "Supplier Summary Report")
        pdf = html_to_pdf_bytes(html)

        assert pdf.startswith(b'%PDF')
        assert len(pdf) > 5_000

    @pytest.mark.asyncio
    async def test_nested_customer_and_product_rows_render(self):
        import chevron
        from services.report_renderer import render_charts_for_pdf

        rendered = chevron.render(SUPPLIER_TEMPLATE, {"rows": SUPPLIER_ROWS})
        rendered = render_charts_for_pdf(rendered)

        assert "Widget Co" in rendered
        assert "Widget A" in rendered

    @pytest.mark.asyncio
    async def test_empty_nested_arrays_render_fallback_message(self):
        import chevron

        rendered = chevron.render(SUPPLIER_TEMPLATE, {"rows": SUPPLIER_ROWS})

        # Global Trade Ltd has empty top_5_customers and top_3_products
        assert "No customer data available" in rendered
        assert "No product data available" in rendered


# ---------------------------------------------------------------------------
# Full PDF pipeline — synthetic KPI template
# ---------------------------------------------------------------------------


class TestPdfPipelineKpiTemplate:
    @pytest.mark.asyncio
    async def test_full_pipeline_produces_valid_pdf(self):
        import chevron
        from services.report_renderer import (
            html_to_pdf_bytes,
            build_pdf_html_document,
            inline_images,
            render_charts_for_pdf,
            process_layout_magic,
        )

        png_b64 = base64.b64encode(_make_1x1_png()).decode()
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=("image/png", png_b64))

        rendered = chevron.render(KPI_TEMPLATE, kpi_context_with_first())
        rendered = process_layout_magic(rendered)
        rendered = render_charts_for_pdf(rendered)
        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            rendered = await inline_images(rendered)
        html = build_pdf_html_document(rendered, "KPI Report")
        pdf = html_to_pdf_bytes(html)

        assert pdf.startswith(b'%PDF')
        assert len(pdf) > 1_000

    @pytest.mark.asyncio
    async def test_logo_image_inlined_as_data_uri(self):
        import chevron
        from services.report_renderer import inline_images, render_charts_for_pdf

        png_b64 = base64.b64encode(_make_1x1_png()).decode()
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=("image/png", png_b64))

        rendered = chevron.render(KPI_TEMPLATE, {"rows": KPI_ROWS})
        rendered = render_charts_for_pdf(rendered)
        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            result = await inline_images(rendered)

        assert f"img:{LOGO_UUID}" not in result
        assert "data:image/png;base64," in result

    @pytest.mark.asyncio
    async def test_logo_image_survives_to_pdf(self):
        """PDF with resolved image must be larger — fails if xhtml2pdf drops data: URIs."""
        import chevron
        from services.report_renderer import (
            html_to_pdf_bytes,
            build_pdf_html_document,
            inline_images,
            render_charts_for_pdf,
        )

        png_b64 = base64.b64encode(_make_1x1_png()).decode()
        mock_found = MagicMock()
        mock_found.get_data = AsyncMock(return_value=("image/png", png_b64))
        mock_not_found = MagicMock()
        mock_not_found.get_data = AsyncMock(return_value=None)

        base_rendered = render_charts_for_pdf(chevron.render(KPI_TEMPLATE, {"rows": KPI_ROWS}))

        with patch("repositories.images.ImagesRepository", return_value=mock_not_found):
            body_no_img = await inline_images(base_rendered)
        pdf_no_img = html_to_pdf_bytes(build_pdf_html_document(body_no_img, "KPI Report"))

        with patch("repositories.images.ImagesRepository", return_value=mock_found):
            body_with_img = await inline_images(base_rendered)
        pdf_with_img = html_to_pdf_bytes(build_pdf_html_document(body_with_img, "KPI Report"))

        assert pdf_with_img.startswith(b'%PDF')
        assert len(pdf_with_img) > len(pdf_no_img), (
            "PDF with logo should be larger than without — "
            "xhtml2pdf may be silently dropping data: URI images"
        )

    @pytest.mark.asyncio
    async def test_first_scalar_rendered_from_row_data(self):
        """{{#_first}}{{report_date}}{{/_first}} resolves against DataQueryService._first."""
        import chevron
        from services.report_renderer import inline_images, render_charts_for_pdf

        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=None)

        rendered = chevron.render(KPI_TEMPLATE, kpi_context_with_first())
        rendered = render_charts_for_pdf(rendered)
        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            rendered = await inline_images(rendered)

        assert "2026-04-30" in rendered  # report_date from KPI_ROWS[0]

    @pytest.mark.asyncio
    async def test_first_subtitle_absent_when_field_missing(self):
        """If report_date is missing from _first, the {{#_first}}{{report_date}}{{/_first}} block renders empty."""
        import chevron
        from services.report_renderer import inline_images, render_charts_for_pdf

        ctx = kpi_context_with_first()
        ctx["_first"].pop("report_date", None)
        for row in ctx["rows"]:
            row.pop("report_date", None)

        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=None)

        rendered = chevron.render(KPI_TEMPLATE, ctx)
        rendered = render_charts_for_pdf(rendered)
        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            rendered = await inline_images(rendered)

        assert "2026-04-30" not in rendered

    def test_section_headers_render_without_metric_row(self):
        """{{^metric_name}} renders only when metric_name is falsy — section header rows."""
        import chevron

        rendered = chevron.render(KPI_TEMPLATE, {"rows": KPI_ROWS})

        assert "REVENUE" in rendered          # section header (metric_name="")
        assert "Net Revenue" in rendered      # data row (metric_name="Net Revenue")

    def test_kpi_values_present_in_rendered_body(self):
        import chevron

        rendered = chevron.render(KPI_TEMPLATE, {"rows": KPI_ROWS})

        assert "$720K" in rendered            # current_value
        assert "+5.9%" in rendered            # vs_prior_pct on Net Revenue row
        assert "Gross Margin" in rendered     # 2nd data row


# ---------------------------------------------------------------------------
# process_layout_magic — _inject_global_header_footer
# ---------------------------------------------------------------------------


class TestInjectGlobalHeaderFooter:
    def test_header_cloned_into_report_page(self):
        from services.report_renderer import process_layout_magic

        html = (
            '<div class="report-global-header">HDR</div>'
            '<div class="report-page"><p>Content</p></div>'
        )
        result = process_layout_magic(html)
        assert result.count("HDR") == 1
        assert "<p>Content</p>" in result
        assert result.index("HDR") > result.index('<div class="report-page">')

    def test_footer_cloned_into_report_page(self):
        from services.report_renderer import process_layout_magic

        html = (
            '<div class="report-global-footer">FTR</div>'
            '<div class="report-page"><p>Body</p></div>'
        )
        result = process_layout_magic(html)
        assert result.count("FTR") == 1
        assert "FTR" in result

    def test_header_and_footer_both_cloned(self):
        from services.report_renderer import process_layout_magic

        html = (
            '<div class="report-global-header">HDR</div>'
            '<div class="report-global-footer">FTR</div>'
            '<div class="report-page">PAGE</div>'
        )
        result = process_layout_magic(html)
        assert "HDR" in result
        assert "FTR" in result

    def test_header_footer_cloned_into_every_page(self):
        from services.report_renderer import process_layout_magic

        html = (
            '<div class="report-global-header">HDR</div>'
            '<div class="report-page">A</div>'
            '<div class="report-page">B</div>'
        )
        result = process_layout_magic(html)
        assert result.count("HDR") == 2

    def test_no_op_when_no_header_or_footer(self):
        from services.report_renderer import process_layout_magic

        html = '<div class="report-page"><p>Content</p></div>'
        assert process_layout_magic(html) == html

    def test_original_header_position_removed(self):
        from services.report_renderer import process_layout_magic

        html = (
            '<div class="report-global-header">HDR</div>'
            '<div class="report-page">PAGE</div>'
        )
        result = process_layout_magic(html)
        page_start = result.index('<div class="report-page">')
        hdr_pos = result.index("HDR")
        assert hdr_pos > page_start


# ---------------------------------------------------------------------------
# process_layout_magic — _apply_break_after
# ---------------------------------------------------------------------------


class TestApplyBreakAfter:
    def test_break_inserted_after_n_top_level_children(self):
        from services.report_renderer import process_layout_magic

        html = (
            '<div data-break-after="2">'
            "<div>A</div><div>B</div><div>C</div><div>D</div>"
            "</div>"
        )
        result = process_layout_magic(html)
        assert result.count('class="page-break"') == 1

    def test_no_trailing_break_on_last_group(self):
        from services.report_renderer import process_layout_magic

        html = (
            '<div data-break-after="2">'
            "<div>1</div><div>2</div><div>3</div><div>4</div>"
            "</div>"
        )
        result = process_layout_magic(html)
        assert result.count('class="page-break"') == 1

    def test_three_full_groups_produces_two_breaks(self):
        from services.report_renderer import process_layout_magic

        html = (
            '<div data-break-after="2">'
            "<div>1</div><div>2</div>"
            "<div>3</div><div>4</div>"
            "<div>5</div><div>6</div>"
            "</div>"
        )
        result = process_layout_magic(html)
        assert result.count('class="page-break"') == 2

    def test_data_break_after_attr_removed_from_wrapper(self):
        from services.report_renderer import process_layout_magic

        html = '<div data-break-after="1"><div>X</div></div>'
        result = process_layout_magic(html)
        assert "data-break-after" not in result

    def test_preserves_other_attrs_on_wrapper(self):
        from services.report_renderer import process_layout_magic

        html = '<div class="my-list" data-break-after="3"><div>A</div></div>'
        result = process_layout_magic(html)
        assert 'class="my-list"' in result

    def test_n_zero_skipped(self):
        from services.report_renderer import process_layout_magic

        html = '<div data-break-after="0"><div>A</div></div>'
        result = process_layout_magic(html)
        assert "data-break-after" in result


# ---------------------------------------------------------------------------
# build_html_document
# ---------------------------------------------------------------------------


class TestBuildHtmlDocument:
    def test_returns_valid_html_wrapper(self):
        from services.report_renderer import build_html_document

        result = build_html_document("<p>Body</p>", "My Report")
        assert result.startswith("<!DOCTYPE html>")
        assert "<p>Body</p>" in result

    def test_title_embedded_in_head(self):
        from services.report_renderer import build_html_document

        result = build_html_document("", "Revenue Dashboard")
        assert "<title>Revenue Dashboard</title>" in result

    def test_includes_bootstrap(self):
        from services.report_renderer import build_html_document

        result = build_html_document("", "T")
        assert "bootstrap" in result.lower()

    def test_no_markdown_styles_by_default(self):
        from services.report_renderer import build_html_document

        result = build_html_document("", "T", is_markdown=False)
        assert "markdown-body" not in result

    def test_markdown_styles_included_when_flag_set(self):
        from services.report_renderer import build_html_document

        result = build_html_document("", "T", is_markdown=True)
        assert "markdown-body" in result


# ---------------------------------------------------------------------------
# render_report — markdown template path
# ---------------------------------------------------------------------------


class TestRenderReportMarkdown:
    @pytest.mark.asyncio
    async def test_markdown_template_wrapped_in_markdown_body(self):
        tmpl = Template(
            id=TID,
            name="MD Report",
            structure_id=SID,
            html_content="# Hello {{#rows}}{{name}}{{/rows}}",
            template_type="markdown",
            created_at=NOW,
            updated_at=NOW,
        )
        struct = _structure()
        mock_svc = _mock_data_query_svc({"data": {"rows": [{"name": "World"}]}})

        with (
            patch("services.report_renderer.TemplatesRepository", return_value=_mock_templates_repo(tmpl)),
            patch("services.report_renderer.StructuresRepository", return_value=_mock_structures_repo(struct)),
            patch("services.report_renderer.DataQueryService", return_value=mock_svc),
            patch("services.report_renderer.SQLConnector"),
        ):
            from services.report_renderer import render_report
            result, returned_template = await render_report(TID)

        assert "markdown-body" in result
        assert "World" in result


# ---------------------------------------------------------------------------
# build_email_html_document
# ---------------------------------------------------------------------------


class TestBuildEmailHtmlDocument:
    def test_returns_valid_html_wrapper(self):
        from services.report_renderer import build_email_html_document

        result = build_email_html_document("<p>Body</p>", "My Report")
        assert result.startswith("<!DOCTYPE html>") or "<html" in result
        assert "Body" in result

    def test_title_embedded(self):
        from services.report_renderer import build_email_html_document

        result = build_email_html_document("", "Email Report")
        assert "Email Report" in result

    def test_bootstrap_utilities_are_inlined(self):
        from services.report_renderer import build_email_html_document

        body = '<span class="text-muted">hint</span>'
        result = build_email_html_document(body, "T")
        assert "style=" in result
        assert "6c757d" in result

    def test_no_bootstrap_cdn_link(self):
        from services.report_renderer import build_email_html_document

        result = build_email_html_document("", "T")
        assert "cdn.jsdelivr.net" not in result

    def test_markdown_styles_included_when_flag_set(self):
        from services.report_renderer import build_email_html_document

        result = build_email_html_document('<div class="markdown-body"><p>hi</p></div>', "T", is_markdown=True)
        assert "1.7" in result  # line-height from _MARKDOWN_STYLES

    def test_no_markdown_styles_by_default(self):
        from services.report_renderer import build_email_html_document

        result = build_email_html_document("", "T", is_markdown=False)
        assert "markdown-body" not in result

    def test_css_inline_failure_falls_back_to_unannotated_html(self):
        import css_inline
        from services.report_renderer import build_email_html_document

        with patch.object(css_inline, "CSSInliner", side_effect=RuntimeError("inliner broke")):
            result = build_email_html_document("<p>ok</p>", "T")
        assert "ok" in result


# ---------------------------------------------------------------------------
# _bootstrap_css singleton
# ---------------------------------------------------------------------------


class TestBootstrapCssSingleton:
    def test_returns_non_empty_string(self):
        import services.report_renderer as rr

        css = rr._bootstrap_css()
        assert isinstance(css, str)
        assert len(css) > 10_000

    def test_cached_on_second_call(self):
        import services.report_renderer as rr

        rr._bootstrap_css_cache = None
        first = rr._bootstrap_css()
        second = rr._bootstrap_css()
        assert first is second

    def test_cache_populated_after_call(self):
        import services.report_renderer as rr

        rr._bootstrap_css_cache = None
        rr._bootstrap_css()
        assert rr._bootstrap_css_cache is not None

    def test_raises_when_vendor_file_missing(self, tmp_path, monkeypatch):
        import services.report_renderer as rr

        rr._bootstrap_css_cache = None
        monkeypatch.setattr(rr, "__file__", str(tmp_path / "report_renderer.py"))
        with pytest.raises(FileNotFoundError):
            rr._bootstrap_css()
        rr._bootstrap_css_cache = None


# ---------------------------------------------------------------------------
# render_charts_as_svg — additional edge cases
# ---------------------------------------------------------------------------


class TestRenderChartsAsSvgEdgeCases:
    def test_empty_labels_after_strip_returns_div_unchanged(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-bar-chart" data-labels="  ,  " data-values="10,20"></div>'
        result = render_charts_as_svg(html)
        assert result == html

    def test_vega_exception_returns_div_unchanged(self):
        from services.report_renderer import render_charts_as_svg
        import services.report_renderer as rr

        html = '<div class="report-bar-chart" data-labels="A,B" data-values="10,20"></div>'
        with patch.object(rr, "vlc") as mock_vlc:
            mock_vlc.vegalite_to_svg.side_effect = RuntimeError("vega error")
            result = render_charts_as_svg(html)
        assert result == html


# ---------------------------------------------------------------------------
# inline_images
# ---------------------------------------------------------------------------


class TestInlineImages:
    @pytest.mark.asyncio
    async def test_no_op_when_no_img_uuids(self):
        from services.report_renderer import inline_images

        html = "<p>No images here</p>"
        result = await inline_images(html)
        assert result == html

    @pytest.mark.asyncio
    async def test_replaces_img_uuid_with_data_uri(self):
        from services.report_renderer import inline_images

        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        html = f'<img src="img:{uid}" alt="logo" />'
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=("image/png", "abc123=="))

        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            result = await inline_images(html)

        assert "data:image/png;base64,abc123==" in result
        assert f"img:{uid}" not in result

    @pytest.mark.asyncio
    async def test_leaves_src_unchanged_when_image_not_found(self):
        from services.report_renderer import inline_images

        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        html = f'<img src="img:{uid}" alt="logo" />'
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=None)

        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            result = await inline_images(html)

        assert f"img:{uid}" in result

    @pytest.mark.asyncio
    async def test_deduplicated_uuids_fetched_once(self):
        from services.report_renderer import inline_images

        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        html = f'<img src="img:{uid}" /><img src="img:{uid}" />'
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=("image/png", "data=="))

        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            await inline_images(html)

        mock_repo.get_data.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_pdf_mode_svg_rasterised_to_png(self):
        """In PDF mode, SVG payloads are rasterised before the data URI is built."""
        from services.report_renderer import inline_images
        import services.report_renderer as rr

        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        html = f'<img src="img:{uid}" />'
        svg_b64 = base64.b64encode(b"<svg/>").decode()
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=("image/svg+xml", svg_b64))

        with (
            patch("repositories.images.ImagesRepository", return_value=mock_repo),
            patch.object(rr, "vlc") as mock_vlc,
        ):
            mock_vlc.svg_to_png.return_value = _make_1x1_png()
            result = await inline_images(html, pdf_mode=True)

        assert "data:image/png;base64," in result
        assert "svg+xml" not in result

    @pytest.mark.asyncio
    async def test_pdf_mode_drops_image_when_svg_rasterise_fails(self):
        """Failed SVG→PNG must drop the image — never emit data:image/png with SVG bytes."""
        from services.report_renderer import inline_images
        import services.report_renderer as rr

        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        html = f'<img src="img:{uid}" />'
        svg_b64 = base64.b64encode(b"<svg/>").decode()
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=("image/svg+xml", svg_b64))

        with (
            patch("repositories.images.ImagesRepository", return_value=mock_repo),
            patch.object(rr, "vlc") as mock_vlc,
        ):
            mock_vlc.svg_to_png.side_effect = RuntimeError("vega failure")
            result = await inline_images(html, pdf_mode=True)

        # Source must be untouched — no broken data URI, no PNG mime over SVG bytes
        assert f"img:{uid}" in result
        assert "data:image/png" not in result

    @pytest.mark.asyncio
    async def test_non_pdf_mode_svg_left_unrasterised(self):
        """Without pdf_mode, SVG is kept as-is — browsers and email handle svg+xml fine."""
        from services.report_renderer import inline_images

        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        html = f'<img src="img:{uid}" />'
        svg_b64 = base64.b64encode(b"<svg/>").decode()
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=("image/svg+xml", svg_b64))

        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            result = await inline_images(html, pdf_mode=False)

        assert "data:image/svg+xml;base64," in result


# ---------------------------------------------------------------------------
# _pdf_link_callback
# ---------------------------------------------------------------------------


class TestPdfLinkCallback:
    def test_data_uri_allowed(self):
        from services.report_renderer import _pdf_link_callback

        uri = "data:image/png;base64,abc=="
        assert _pdf_link_callback(uri, None) == uri

    def test_http_uri_blocked(self):
        from services.report_renderer import _pdf_link_callback

        assert _pdf_link_callback("http://internal.example/secret.css", None) == ""

    def test_https_uri_blocked(self):
        from services.report_renderer import _pdf_link_callback

        assert _pdf_link_callback("https://cdn.example.com/x.css", None) == ""

    def test_file_uri_blocked(self):
        from services.report_renderer import _pdf_link_callback

        assert _pdf_link_callback("file:///etc/passwd", None) == ""


# ---------------------------------------------------------------------------
# collect_images_for_email
# ---------------------------------------------------------------------------


class TestCollectImagesForEmail:
    @pytest.mark.asyncio
    async def test_no_op_when_no_img_uuids(self):
        from services.report_renderer import collect_images_for_email

        html = "<p>No images here</p>"
        result_html, images = await collect_images_for_email(html)
        assert result_html == html
        assert images == {}

    @pytest.mark.asyncio
    async def test_rewrites_src_to_cid_reference(self):
        from services.report_renderer import CID_DOMAIN, collect_images_for_email

        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        html = f'<img src="img:{uid}" alt="logo" />'
        raw = b"\x89PNG"
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=("image/png", base64.b64encode(raw).decode()))

        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            result_html, images = await collect_images_for_email(html)

        assert f'src="cid:{uid}@{CID_DOMAIN}"' in result_html
        assert f"img:{uid}" not in result_html
        assert uid in images
        assert images[uid] == ("image/png", raw)

    @pytest.mark.asyncio
    async def test_leaves_src_unchanged_when_image_not_found(self):
        from services.report_renderer import collect_images_for_email

        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        html = f'<img src="img:{uid}" alt="logo" />'
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=None)

        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            result_html, images = await collect_images_for_email(html)

        assert f"img:{uid}" in result_html
        assert images == {}

    @pytest.mark.asyncio
    async def test_deduplicated_uuids_fetched_once(self):
        from services.report_renderer import collect_images_for_email

        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        html = f'<img src="img:{uid}" /><img src="img:{uid}" />'
        mock_repo = MagicMock()
        mock_repo.get_data = AsyncMock(return_value=("image/png", base64.b64encode(b"x").decode()))

        with patch("repositories.images.ImagesRepository", return_value=mock_repo):
            await collect_images_for_email(html)

        mock_repo.get_data.assert_awaited_once()
