"""
Unit tests for DataQueryService.

The SQL connector and both repositories are mocked so no real
Databricks or database connections are made.

NOTE: execute_for_preview is decorated with @app_cache.cached.  The
autouse ``bypass_cache`` fixture patches ``app_cache.get`` to always
return None (cache miss) and replaces ``set_fire_and_forget`` with a
no-op, so every test runs the real service logic without inter-test
cache bleed.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pandas as pd
import pytest

from common.factories.cache import app_cache
from models.structure import Structure, StructureField, StructureTable
from models.template import Template
from services.data_query import DataQueryService

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
STRUCT_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def bypass_cache(monkeypatch):
    """Disable caching for execute_for_preview so each test runs its real logic."""
    monkeypatch.setattr(app_cache, "get", AsyncMock(return_value=None))
    monkeypatch.setattr(app_cache, "set_fire_and_forget", lambda *a, **kw: None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_structure(sql_query: str | None = "SELECT col FROM cat.sch.tbl") -> Structure:
    return Structure(
        id=STRUCT_ID,
        name="Test",
        project_id=uuid.uuid4(),
        fields=[StructureField(name="col", type="string")],
        tables=[StructureTable(full_name="cat.sch.tbl", alias="tbl")],
        selected_columns=["col"],
        sql_query=sql_query,
        created_at=NOW,
        updated_at=NOW,
    )


def _make_template(
    structure_id: uuid.UUID | None = None,
    id: uuid.UUID | None = None,
) -> Template:
    return Template(
        id=id or uuid.uuid4(),
        name="My Template",
        structure_id=structure_id or STRUCT_ID,
        html_content="<p>{{rows}}</p>",
        created_at=NOW,
        updated_at=NOW,
    )


def _make_svc(
    *,
    template: Template | None = None,
    structure: Structure | None = None,
    df: pd.DataFrame | None = None,
) -> DataQueryService:
    """
    Build a DataQueryService with all external dependencies mocked.

    By default the service finds a template, then its linked structure,
    and the SQL connector returns a two-row DataFrame.
    """
    tmpl = template or _make_template()
    struct = structure or _make_structure()
    df_result = df if df is not None else pd.DataFrame({"col": ["a", "b"]})

    sql_connector = MagicMock()
    sql_connector.run_sql_statement_async = AsyncMock(return_value=df_result)

    templates_repo = MagicMock()
    templates_repo.get_by_id = AsyncMock(return_value=tmpl)

    structures_repo = MagicMock()
    structures_repo.get_by_id = AsyncMock(return_value=struct)

    svc = DataQueryService.__new__(DataQueryService)
    svc.sql_connector = sql_connector
    svc.templates_repo = templates_repo
    svc.structures_repo = structures_repo
    return svc


# ---------------------------------------------------------------------------
# execute_for_preview
# ---------------------------------------------------------------------------


class TestExecuteForPreview:
    @pytest.mark.asyncio
    async def test_returns_dict_with_data_query_row_count(self):
        tmpl_id = uuid.uuid4()
        tmpl = _make_template(id=tmpl_id)
        svc = _make_svc(template=tmpl)
        result = await svc.execute_for_preview(tmpl_id, limit=50)
        assert "data" in result
        assert "query" in result
        assert "row_count" in result

    @pytest.mark.asyncio
    async def test_row_count_matches_dataframe_rows(self):
        tmpl_id = uuid.uuid4()
        tmpl = _make_template(id=tmpl_id)
        df = pd.DataFrame({"col": ["x", "y", "z"]})
        svc = _make_svc(template=tmpl, df=df)
        result = await svc.execute_for_preview(tmpl_id, limit=50)
        assert result["row_count"] == 3

    @pytest.mark.asyncio
    async def test_data_contains_rows_key(self):
        tmpl_id = uuid.uuid4()
        tmpl = _make_template(id=tmpl_id)
        svc = _make_svc(template=tmpl)
        result = await svc.execute_for_preview(tmpl_id, limit=50)
        assert "rows" in result["data"]

    @pytest.mark.asyncio
    async def test_raises_value_error_when_template_not_found(self):
        tmpl_id = uuid.uuid4()
        svc = _make_svc()
        svc.templates_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(ValueError, match="Template not found"):
            await svc.execute_for_preview(tmpl_id, limit=50)

    @pytest.mark.asyncio
    async def test_raises_value_error_when_structure_not_found(self):
        tmpl_id = uuid.uuid4()
        tmpl = _make_template(id=tmpl_id)
        svc = _make_svc(template=tmpl)
        svc.structures_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(ValueError, match="Linked structure not found"):
            await svc.execute_for_preview(tmpl_id, limit=50)

    @pytest.mark.asyncio
    async def test_returns_empty_result_when_no_sql_query(self):
        tmpl_id = uuid.uuid4()
        tmpl = _make_template(id=tmpl_id)
        struct = _make_structure(sql_query=None)
        svc = _make_svc(template=tmpl, structure=struct)
        result = await svc.execute_for_preview(tmpl_id, limit=50)
        assert result == {"data": {}, "query": None, "row_count": 0}

    @pytest.mark.asyncio
    async def test_sql_includes_limit(self):
        tmpl_id = uuid.uuid4()
        tmpl = _make_template(id=tmpl_id)
        svc = _make_svc(template=tmpl)
        await svc.execute_for_preview(tmpl_id, limit=25)
        call_args = svc.sql_connector.run_sql_statement_async.call_args[0][0]
        assert "LIMIT 25" in call_args

    @pytest.mark.asyncio
    async def test_returns_empty_rows_when_dataframe_is_empty(self):
        tmpl_id = uuid.uuid4()
        tmpl = _make_template(id=tmpl_id)
        svc = _make_svc(template=tmpl, df=pd.DataFrame())
        result = await svc.execute_for_preview(tmpl_id, limit=50)
        assert result["row_count"] == 0

    @pytest.mark.asyncio
    async def test_query_field_contains_original_sql(self):
        tmpl_id = uuid.uuid4()
        tmpl = _make_template(id=tmpl_id)
        struct = _make_structure(sql_query="SELECT revenue FROM cat.sch.sales")
        svc = _make_svc(template=tmpl, structure=struct)
        result = await svc.execute_for_preview(tmpl_id, limit=10)
        assert result["query"] == "SELECT revenue FROM cat.sch.sales"


# ---------------------------------------------------------------------------
# _map_results_to_data
# ---------------------------------------------------------------------------


class TestMapResultsToData:
    def _svc(self) -> DataQueryService:
        return _make_svc()

    def test_rows_have_index_and_total_injected(self):
        svc = self._svc()
        struct = _make_structure()
        cols = ["col"]
        rows = [{"col": "a"}, {"col": "b"}, {"col": "c"}]
        result = svc._map_results_to_data(cols, rows, struct)
        enriched = result["rows"]
        assert enriched[0]["_index"] == 1
        assert enriched[0]["_total"] == 3
        assert enriched[2]["_index"] == 3

    def test_empty_rows_returns_empty_list(self):
        svc = self._svc()
        result = svc._map_results_to_data([], [], _make_structure())
        assert result == {"rows": []}


# ---------------------------------------------------------------------------
# _run_query — numpy type conversion
# ---------------------------------------------------------------------------


class TestRunQuery:
    """_run_query is a direct method — it does not go through the cache."""

    @pytest.mark.asyncio
    async def test_numpy_integer_converted_to_python_int(self):
        df = pd.DataFrame({"count": np.array([1, 2], dtype=np.int64)})
        svc = _make_svc()
        svc.sql_connector.run_sql_statement_async = AsyncMock(return_value=df)
        rows, _ = await svc._run_query("SELECT count FROM t")
        assert isinstance(rows[0]["count"], int)

    @pytest.mark.asyncio
    async def test_numpy_float_converted_to_python_float(self):
        df = pd.DataFrame({"revenue": np.array([1.5, 2.5], dtype=np.float64)})
        svc = _make_svc()
        svc.sql_connector.run_sql_statement_async = AsyncMock(return_value=df)
        rows, _ = await svc._run_query("SELECT revenue FROM t")
        assert isinstance(rows[0]["revenue"], float)

    @pytest.mark.asyncio
    async def test_numpy_bool_converted_to_python_bool(self):
        df = pd.DataFrame({"active": np.array([True, False], dtype=np.bool_)})
        svc = _make_svc()
        svc.sql_connector.run_sql_statement_async = AsyncMock(return_value=df)
        rows, _ = await svc._run_query("SELECT active FROM t")
        assert isinstance(rows[0]["active"], bool)

    @pytest.mark.asyncio
    async def test_none_dataframe_returns_empty(self):
        svc = _make_svc()
        svc.sql_connector.run_sql_statement_async = AsyncMock(return_value=None)
        rows, cols = await svc._run_query("SELECT 1")
        assert rows == []
        assert cols == []
