"""
Unit tests for TemplatesRepository.

The LakebaseConnector is fully mocked; no DB connection is made.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.template import Template, TemplateCreate, TemplateUpdate
from repositories.templates import TemplatesRepository

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
TID = uuid.uuid4()
SID = uuid.uuid4()
PID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row(
    *,
    id: str | None = None,
    name: str = "My Template",
    structure_id: str | None = None,
    html_content: str = "<p>hello</p>",
):
    return (
        str(id or TID),
        name,
        str(structure_id or SID),
        html_content,
        NOW,
        NOW,
    )


def _make_result(rows: list | None = None, *, rowcount: int = 1):
    result = MagicMock()
    _rows = rows if rows is not None else []
    result.fetchall.return_value = _rows
    result.fetchone.return_value = _rows[0] if _rows else None
    result.rowcount = rowcount
    return result


def _make_repo(query_result=None) -> tuple[TemplatesRepository, MagicMock]:
    connector = MagicMock()
    connector.execute_query = AsyncMock(return_value=query_result or _make_result())
    repo = TemplatesRepository(connector=connector)
    return repo, connector


# ---------------------------------------------------------------------------
# _require_connector
# ---------------------------------------------------------------------------


class TestRequireConnector:
    def test_raises_runtime_error_when_no_connector(self):
        repo = TemplatesRepository(connector=None)
        with pytest.raises(RuntimeError, match="Lakebase is not available"):
            repo._require_connector()


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------


class TestGetAll:
    @pytest.mark.asyncio
    async def test_get_all_returns_list_of_templates(self):
        rows = [_row(), _row(name="Second Template")]
        repo, connector = _make_repo(_make_result(rows))
        result = await repo.get_all(project_id=PID)
        assert len(result) == 2
        assert all(isinstance(t, Template) for t in result)

    @pytest.mark.asyncio
    async def test_get_all_empty_returns_empty_list(self):
        repo, connector = _make_repo(_make_result([]))
        result = await repo.get_all(project_id=PID)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_with_structure_id_filter_passes_param(self):
        repo, connector = _make_repo(_make_result([_row()]))
        await repo.get_all(structure_id=SID)
        params = connector.execute_query.call_args[0][1]
        assert params["sid"] == str(SID)

    @pytest.mark.asyncio
    async def test_get_all_with_project_id_filter_passes_param(self):
        repo, connector = _make_repo(_make_result([_row()]))
        await repo.get_all(project_id=PID)
        params = connector.execute_query.call_args[0][1]
        assert params["pid"] == str(PID)

    @pytest.mark.asyncio
    async def test_get_all_with_project_id_joins_structures(self):
        repo, connector = _make_repo(_make_result([_row()]))
        await repo.get_all(project_id=PID)
        sql = connector.execute_query.call_args[0][0]
        assert "JOIN structures" in sql
        assert "project_id" in sql


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


class TestGetById:
    @pytest.mark.asyncio
    async def test_get_by_id_returns_template_when_found(self):
        row = _row(id=TID)
        repo, connector = _make_repo(_make_result([row]))
        result = await repo.get_by_id(TID)
        assert isinstance(result, Template)
        assert str(result.id) == str(TID)

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(self):
        repo, connector = _make_repo(_make_result([]))
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_returns_template(self):
        repo, connector = _make_repo(_make_result([_row()]))
        data = TemplateCreate(name="New", structure_id=SID, html_content="<b>hi</b>")
        result = await repo.create(data)
        assert isinstance(result, Template)

    @pytest.mark.asyncio
    async def test_create_passes_correct_params(self):
        repo, connector = _make_repo(_make_result([_row()]))
        data = TemplateCreate(name="New", structure_id=SID, html_content="<b>hi</b>")
        await repo.create(data)
        params = connector.execute_query.call_args[0][1]
        assert params["name"] == "New"
        assert params["structure_id"] == str(SID)
        assert params["html_content"] == "<b>hi</b>"


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_returns_updated_template(self):
        row = _row(name="Updated Name")
        repo, connector = _make_repo(_make_result([row]))
        data = TemplateUpdate(name="Updated Name")
        result = await repo.update(TID, data)
        assert isinstance(result, Template)

    @pytest.mark.asyncio
    async def test_update_returns_none_when_not_found(self):
        repo, connector = _make_repo(_make_result([]))
        data = TemplateUpdate(name="Ghost")
        result = await repo.update(uuid.uuid4(), data)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_with_no_fields_falls_back_to_get_by_id(self):
        repo, connector = _make_repo(_make_result([_row()]))
        data = TemplateUpdate()  # all None
        await repo.update(TID, data)
        connector.execute_query.assert_awaited_once()
        sql = connector.execute_query.call_args[0][0]
        assert "SELECT" in sql

    @pytest.mark.asyncio
    async def test_update_html_content_only(self):
        row = _row(html_content="<h1>new</h1>")
        repo, connector = _make_repo(_make_result([row]))
        data = TemplateUpdate(html_content="<h1>new</h1>")
        await repo.update(TID, data)
        params = connector.execute_query.call_args[0][1]
        assert params["html_content"] == "<h1>new</h1>"

    @pytest.mark.asyncio
    async def test_update_with_expected_updated_at_adds_where_clause(self):
        row = _row(html_content="<h1>new</h1>")
        repo, connector = _make_repo(_make_result([row]))
        data = TemplateUpdate(html_content="<h1>new</h1>", expected_updated_at=NOW)
        await repo.update(TID, data)
        sql = connector.execute_query.call_args[0][0]
        assert "updated_at = :expected_updated_at" in sql
        params = connector.execute_query.call_args[0][1]
        assert params["expected_updated_at"] == NOW

    @pytest.mark.asyncio
    async def test_update_without_expected_updated_at_omits_clause(self):
        row = _row(html_content="<h1>new</h1>")
        repo, connector = _make_repo(_make_result([row]))
        data = TemplateUpdate(html_content="<h1>new</h1>")
        await repo.update(TID, data)
        sql = connector.execute_query.call_args[0][0]
        assert "expected_updated_at" not in sql

    @pytest.mark.asyncio
    async def test_update_returns_none_on_stale_expected_updated_at(self):
        repo, connector = _make_repo(_make_result([]))
        data = TemplateUpdate(html_content="<h1>new</h1>", expected_updated_at=NOW)
        result = await repo.update(TID, data)
        assert result is None


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_returns_true_when_row_deleted(self):
        repo, connector = _make_repo(_make_result(rowcount=1))
        deleted = await repo.delete(TID)
        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_no_row_deleted(self):
        repo, connector = _make_repo(_make_result(rowcount=0))
        deleted = await repo.delete(uuid.uuid4())
        assert deleted is False


# ---------------------------------------------------------------------------
# _row_to_model
# ---------------------------------------------------------------------------


class TestRowToModel:
    def test_row_to_model_returns_template(self):
        row = _row()
        model = TemplatesRepository._row_to_model(row)
        assert isinstance(model, Template)
        assert str(model.id) == str(TID)
        assert model.name == "My Template"
        assert model.html_content == "<p>hello</p>"
