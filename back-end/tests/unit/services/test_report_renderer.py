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
            result = await render_report(TID)

        assert "Alice" in result
        assert isinstance(result, str)

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
            result = await render_report(TID)

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
            result = await render_report(TID)

        assert "X" in result
