"""
Unit tests for QueryBuilderService.

QueryBuilderService.build_query is pure logic — no I/O.
QueryBuilderService.infer_fields delegates to DiscoveryService which is mocked.

Security surface:  build_query performs simple string interpolation of
table.full_name and selected_columns without any sanitisation. Tests here
document the current (unsafe) behaviour and will need to be updated once
input validators are added to StructureTable / StructureCreate.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from models.structure import StructureField, StructureTable
from services.query_builder import QueryBuilderService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _table(full_name: str = "cat.sch.tbl", alias: str = "tbl") -> StructureTable:
    return StructureTable(full_name=full_name, alias=alias)


def _make_service(columns: list | None = None) -> tuple[QueryBuilderService, MagicMock]:
    """Return a QueryBuilderService with a mocked DiscoveryService."""
    mock_discovery = MagicMock()
    mock_discovery.get_table_columns = AsyncMock(
        return_value=columns
        or [
            {"name": "col1", "type_text": "string", "type_name": "STRING"},
            {"name": "col2", "type_text": "int", "type_name": "INT"},
        ]
    )
    mock_discovery.columns_to_structure_fields = MagicMock(
        return_value=[
            StructureField(name="col1", type="string"),
            StructureField(name="col2", type="number"),
        ]
    )

    svc = QueryBuilderService.__new__(QueryBuilderService)
    svc.discovery = mock_discovery
    return svc, mock_discovery


# ---------------------------------------------------------------------------
# build_query — happy paths
# ---------------------------------------------------------------------------


class TestBuildQuery:
    def test_build_query_single_column_returns_correct_sql(self):
        svc, _ = _make_service()
        sql = svc.build_query(_table("cat.sch.sales"), ["revenue"])
        assert sql == "SELECT revenue FROM cat.sch.sales"

    def test_build_query_multiple_columns_joins_with_comma(self):
        svc, _ = _make_service()
        sql = svc.build_query(_table("cat.sch.tbl"), ["col1", "col2", "col3"])
        assert sql == "SELECT col1, col2, col3 FROM cat.sch.tbl"

    def test_build_query_uses_table_full_name_verbatim(self):
        svc, _ = _make_service()
        table = _table(full_name="my_catalog.my_schema.my_table")
        sql = svc.build_query(table, ["id"])
        assert "my_catalog.my_schema.my_table" in sql

    def test_build_query_returns_string(self):
        svc, _ = _make_service()
        result = svc.build_query(_table(), ["col1"])
        assert isinstance(result, str)

    # -- error path ----------------------------------------------------------

    def test_build_query_raises_value_error_when_no_columns_selected(self):
        svc, _ = _make_service()
        with pytest.raises(ValueError, match="At least one column must be selected"):
            svc.build_query(_table(), [])

    # -- SQL injection surface (documenting current behaviour) ---------------

    def test_build_query_does_not_sanitise_malicious_table_name(self):
        """
        SECURITY NOTE: build_query currently interpolates full_name directly
        into the SQL string without sanitisation.  A malicious full_name can
        inject arbitrary SQL.  This test documents the current unsafe
        behaviour; once validators are added to StructureTable this test
        should be replaced by one asserting a ValidationError is raised.
        """
        svc, _ = _make_service()
        malicious_full_name = "cat.sch.tbl; DROP TABLE structures; --"
        table = StructureTable(full_name=malicious_full_name, alias="evil")
        sql = svc.build_query(table, ["col1"])
        # Current behaviour: injection passes through unchanged
        assert "DROP TABLE" in sql

    def test_build_query_does_not_sanitise_malicious_column_name(self):
        """
        SECURITY NOTE: selected_columns values are interpolated verbatim.
        A malicious column name can produce invalid or injected SQL.
        Documents current unsafe behaviour pending input validation.
        """
        svc, _ = _make_service()
        malicious_col = "1; DROP TABLE structures; --"
        sql = svc.build_query(_table(), [malicious_col])
        assert "DROP TABLE" in sql


# ---------------------------------------------------------------------------
# infer_fields
# ---------------------------------------------------------------------------


class TestInferFields:
    @pytest.mark.asyncio
    async def test_infer_fields_returns_structure_fields(self):
        svc, _ = _make_service()
        result = await svc.infer_fields(_table("cat.sch.tbl"), ["col1"])
        assert isinstance(result, list)
        assert all(isinstance(f, StructureField) for f in result)

    @pytest.mark.asyncio
    async def test_infer_fields_calls_discovery_with_correct_parts(self):
        svc, mock_discovery = _make_service()
        await svc.infer_fields(_table("mycat.mysch.mytbl"), ["col1"])
        mock_discovery.get_table_columns.assert_awaited_once_with(
            "mycat", "mysch", "mytbl"
        )

    @pytest.mark.asyncio
    async def test_infer_fields_raises_value_error_for_invalid_table_name(self):
        svc, _ = _make_service()
        bad_table = StructureTable(full_name="only_two.parts", alias="t")
        with pytest.raises(ValueError, match="Invalid table name"):
            await svc.infer_fields(bad_table, ["col1"])

    @pytest.mark.asyncio
    async def test_infer_fields_filters_to_selected_columns_only(self):
        """Only columns whose name is in selected_columns should be returned."""
        columns = [
            {"name": "id", "type_text": "int", "type_name": "INT"},
            {"name": "name", "type_text": "string", "type_name": "STRING"},
            {"name": "secret", "type_text": "string", "type_name": "STRING"},
        ]
        svc, mock_discovery = _make_service(columns)
        # Override columns_to_structure_fields to inspect what's passed
        passed_cols: list = []

        def capture(cols):
            passed_cols.extend(cols)
            return [StructureField(name=c["name"], type="string") for c in cols]

        mock_discovery.columns_to_structure_fields.side_effect = capture

        await svc.infer_fields(_table("c.s.t"), ["id", "name"])

        assert all(c["name"] != "secret" for c in passed_cols)
        assert {c["name"] for c in passed_cols} == {"id", "name"}

    @pytest.mark.asyncio
    async def test_infer_fields_preserves_user_column_order(self):
        """Fields must follow the order the user specified, not DB column order."""
        columns = [
            {"name": "alpha", "type_text": "string", "type_name": "STRING"},
            {"name": "beta", "type_text": "string", "type_name": "STRING"},
            {"name": "gamma", "type_text": "string", "type_name": "STRING"},
        ]
        svc, mock_discovery = _make_service(columns)

        passed_cols: list = []

        def capture(cols):
            passed_cols.extend(cols)
            return [StructureField(name=c["name"], type="string") for c in cols]

        mock_discovery.columns_to_structure_fields.side_effect = capture

        # Request columns in reverse DB order
        await svc.infer_fields(_table("c.s.t"), ["gamma", "beta", "alpha"])

        assert [c["name"] for c in passed_cols] == ["gamma", "beta", "alpha"]
