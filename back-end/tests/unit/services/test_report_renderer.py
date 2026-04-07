"""
Unit tests for services/report_renderer.py.

All external dependencies (repos, DataQueryService, chevron) are mocked.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.structure import Structure, StructureTable
from models.template import Template

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
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
            await render_report(TID)  # noqa: F841 — testing side-effects

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
        assert '<rect' in result  # bars

    def test_pie_chart_div_replaced_with_svg(self):
        from services.report_renderer import render_charts_as_svg

        html = '<div class="report-pie-chart" data-labels="[A,B,C]" data-values="[30,50,20]"></div>'
        result = render_charts_as_svg(html)
        assert '<svg' in result
        assert 'report-pie-chart' in result
        assert '<path' in result  # pie slices

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

        # Labels with surrounding brackets must still render
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

        # Charts inside markdown-rendered HTML (inline HTML passthrough) must render identically
        html = (
            '<div class="markdown-body">'
            '<div class="report-bar-chart" data-labels="Jan,Feb" data-values="100,200"></div>'
            '</div>'
        )
        result = render_charts_as_svg(html)
        assert '<svg' in result
        assert '<rect' in result


# ---------------------------------------------------------------------------
# render_report_pdf
# ---------------------------------------------------------------------------



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
        # header appears inside the page div
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
        # HDR should not appear before the report-page open tag
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
        assert result.count('class="page-break"') == 1  # after 2nd child; no trailing break

    def test_no_trailing_break_on_last_group(self):
        from services.report_renderer import process_layout_magic

        # 4 items, break-after=2 → break after item 2 only (item 4 is the last)
        html = (
            '<div data-break-after="2">'
            "<div>1</div><div>2</div><div>3</div><div>4</div>"
            "</div>"
        )
        result = process_layout_magic(html)
        # Trailing break removed — only 1 break between groups
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
        # 3 full groups of 2 → breaks after group 1 and group 2 (last group has no trailing break)
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
        # n=0 is skipped; the div is left unchanged
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
        # css-inline adds style="" attributes so the bare tag won't match; check text content
        assert "Body" in result

    def test_title_embedded(self):
        from services.report_renderer import build_email_html_document

        result = build_email_html_document("", "Email Report")
        assert "Email Report" in result

    def test_bootstrap_utilities_are_inlined(self):
        from services.report_renderer import build_email_html_document

        # text-muted maps to color:#6c757d in Bootstrap — inlining should produce a style attr
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

        # css-inline inlines rules onto matching elements; pass a .markdown-body div
        # so the line-height rule from _MARKDOWN_STYLES gets applied
        result = build_email_html_document('<div class="markdown-body"><p>hi</p></div>', "T", is_markdown=True)
        assert "1.7" in result  # line-height: 1.7 from _MARKDOWN_STYLES

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
        assert len(css) > 10_000  # Bootstrap minified is ~230 KB

    def test_cached_on_second_call(self):
        import services.report_renderer as rr

        rr._bootstrap_css_cache = None  # reset
        first = rr._bootstrap_css()
        second = rr._bootstrap_css()
        assert first is second  # same object — cached

    def test_cache_populated_after_call(self):
        import services.report_renderer as rr

        rr._bootstrap_css_cache = None
        rr._bootstrap_css()
        assert rr._bootstrap_css_cache is not None

    def test_raises_when_vendor_file_missing(self, tmp_path, monkeypatch):
        import services.report_renderer as rr

        rr._bootstrap_css_cache = None
        # Point the module file to a tmp dir that has no vendor/ subdir
        monkeypatch.setattr(rr, "__file__", str(tmp_path / "report_renderer.py"))
        with pytest.raises(FileNotFoundError):
            rr._bootstrap_css()
        rr._bootstrap_css_cache = None  # clean up so other tests aren't affected


# ---------------------------------------------------------------------------
# render_charts_as_svg — additional edge cases
# ---------------------------------------------------------------------------


class TestRenderChartsAsSvgEdgeCases:
    def test_empty_labels_after_strip_returns_div_unchanged(self):
        from services.report_renderer import render_charts_as_svg

        # All label entries are blank after stripping
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
