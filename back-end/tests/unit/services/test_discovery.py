"""
Unit tests for DiscoveryService and its type-parsing helpers.

The pure helpers (_parse_type_to_field, _split_top_level, columns_to_structure_fields)
are tested in isolation.  list_catalogs / list_schemas / list_tables / get_table_columns
are tested with the Databricks SDK client mocked.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.structure import StructureField
from services.discovery import (
    DiscoveryService,
    _parse_struct_fields,
    _parse_type_to_field,
    _split_top_level,
)


# ---------------------------------------------------------------------------
# _split_top_level
# ---------------------------------------------------------------------------


class TestSplitTopLevel:
    def test_simple_comma_split(self):
        assert _split_top_level("a,b,c") == ["a", "b", "c"]

    def test_ignores_comma_inside_angle_brackets(self):
        result = _split_top_level("name:string,tags:array<string,int>")
        assert result == ["name:string", "tags:array<string,int>"]

    def test_deeply_nested_angle_brackets(self):
        result = _split_top_level("a:struct<b:array<c:string>,d:int>,e:string")
        assert result == ["a:struct<b:array<c:string>,d:int>", "e:string"]

    def test_single_element_no_comma(self):
        assert _split_top_level("name:string") == ["name:string"]

    def test_empty_string_returns_empty_list(self):
        # The function iterates characters; an empty string produces no parts.
        assert _split_top_level("") == []


# ---------------------------------------------------------------------------
# _parse_type_to_field — scalar types
# ---------------------------------------------------------------------------


class TestParseTypeToFieldScalars:
    @pytest.mark.parametrize(
        "type_text,expected_type",
        [
            ("STRING", "string"),
            ("VARCHAR", "string"),
            ("INT", "number"),
            ("INTEGER", "number"),
            ("BIGINT", "number"),
            ("FLOAT", "number"),
            ("DOUBLE", "number"),
            ("DECIMAL(10,2)", "number"),
            ("BOOLEAN", "boolean"),
            ("DATE", "date"),
            ("TIMESTAMP", "date"),
            ("TIMESTAMP_NTZ", "date"),
            ("UNKNOWN_TYPE", "string"),  # falls back to "string"
        ],
    )
    def test_scalar_type_mapping(self, type_text: str, expected_type: str):
        field = _parse_type_to_field("col", type_text)
        assert field.type == expected_type

    def test_field_name_is_preserved(self):
        field = _parse_type_to_field("my_column", "STRING")
        assert field.name == "my_column"

    def test_scalar_field_has_no_children(self):
        field = _parse_type_to_field("col", "INT")
        assert field.children is None


# ---------------------------------------------------------------------------
# _parse_type_to_field — complex types
# ---------------------------------------------------------------------------


class TestParseTypeToFieldComplex:
    def test_struct_type_produces_object_type(self):
        field = _parse_type_to_field("addr", "struct<city:string,zip:string>")
        assert field.type == "object"

    def test_struct_type_produces_children(self):
        field = _parse_type_to_field("addr", "struct<city:string,zip:string>")
        assert field.children is not None
        assert len(field.children) == 2
        names = {c.name for c in field.children}
        assert names == {"city", "zip"}

    def test_array_of_scalars_produces_array_without_children(self):
        field = _parse_type_to_field("tags", "array<string>")
        assert field.type == "array"
        assert field.children is None

    def test_array_of_struct_produces_array_with_children(self):
        field = _parse_type_to_field("items", "array<struct<id:int,label:string>>")
        assert field.type == "array"
        assert field.children is not None
        assert {c.name for c in field.children} == {"id", "label"}

    def test_map_type_produces_object_type(self):
        field = _parse_type_to_field("metadata", "map<string,string>")
        assert field.type == "object"
        assert field.children is None

    def test_deeply_nested_struct(self):
        field = _parse_type_to_field(
            "payload",
            "struct<outer:struct<inner:string>>",
        )
        assert field.type == "object"
        assert field.children is not None
        outer_child = field.children[0]
        assert outer_child.name == "outer"
        assert outer_child.type == "object"


# ---------------------------------------------------------------------------
# columns_to_structure_fields
# ---------------------------------------------------------------------------


class TestColumnsToStructureFields:
    def _make_svc(self) -> DiscoveryService:
        """Create a DiscoveryService with a fake WorkspaceConnector."""
        fake_client = MagicMock()
        connector = MagicMock()
        connector.client = fake_client
        with patch("services.discovery.WorkspaceConnector", return_value=connector):
            svc = DiscoveryService(workspace_connector=connector)
        return svc

    def test_returns_list_of_structure_fields(self):
        svc = self._make_svc()
        cols = [{"name": "id", "type_text": "INT", "type_name": "INT"}]
        result = svc.columns_to_structure_fields(cols)
        assert isinstance(result, list)
        assert all(isinstance(f, StructureField) for f in result)

    def test_maps_multiple_columns(self):
        svc = self._make_svc()
        cols = [
            {"name": "id", "type_text": "INT", "type_name": "INT"},
            {"name": "name", "type_text": "STRING", "type_name": "STRING"},
        ]
        result = svc.columns_to_structure_fields(cols)
        assert len(result) == 2
        assert result[0].name == "id"
        assert result[1].name == "name"

    def test_uses_type_text_over_type_name(self):
        """type_text carries nested info; type_name does not."""
        svc = self._make_svc()
        cols = [
            {
                "name": "items",
                "type_text": "array<struct<id:int,label:string>>",
                "type_name": "ARRAY",
            }
        ]
        result = svc.columns_to_structure_fields(cols)
        assert result[0].type == "array"
        assert result[0].children is not None

    def test_empty_column_list_returns_empty_list(self):
        svc = self._make_svc()
        assert svc.columns_to_structure_fields([]) == []


# ---------------------------------------------------------------------------
# DiscoveryService async methods (SDK client mocked)
# ---------------------------------------------------------------------------


def _make_discovery_svc() -> DiscoveryService:
    """Build a DiscoveryService whose Databricks client is a MagicMock."""
    connector = MagicMock()
    connector.client = MagicMock()
    svc = DiscoveryService.__new__(DiscoveryService)
    svc.workspace = connector
    svc.client = connector.client
    return svc


class TestDiscoveryServiceAsyncMethods:
    @pytest.mark.asyncio
    async def test_list_catalogs_returns_list_of_dicts(self):
        svc = _make_discovery_svc()
        cat = MagicMock()
        cat.name = "my_catalog"
        cat.comment = "A catalog"
        cat.owner = "user@example.com"
        svc.client.catalogs.list.return_value = iter([cat])

        result = await svc.list_catalogs()

        assert result == [{"name": "my_catalog", "comment": "A catalog", "owner": "user@example.com"}]

    @pytest.mark.asyncio
    async def test_list_catalogs_empty_returns_empty_list(self):
        svc = _make_discovery_svc()
        svc.client.catalogs.list.return_value = iter([])
        result = await svc.list_catalogs()
        assert result == []

    @pytest.mark.asyncio
    async def test_list_schemas_returns_list_of_dicts(self):
        svc = _make_discovery_svc()
        schema = MagicMock()
        schema.name = "my_schema"
        schema.comment = None
        svc.client.schemas.list.return_value = iter([schema])

        result = await svc.list_schemas("my_catalog")

        assert len(result) == 1
        assert result[0]["name"] == "my_schema"
        assert result[0]["catalog_name"] == "my_catalog"

    @pytest.mark.asyncio
    async def test_list_tables_returns_list_of_dicts(self):
        svc = _make_discovery_svc()
        table = MagicMock()
        table.name = "sales"
        table.full_name = "cat.sch.sales"
        table.table_type = "MANAGED"
        table.comment = None
        svc.client.tables.list.return_value = iter([table])

        result = await svc.list_tables("cat", "sch")

        assert len(result) == 1
        assert result[0]["full_name"] == "cat.sch.sales"

    @pytest.mark.asyncio
    async def test_get_table_columns_returns_column_dicts(self):
        svc = _make_discovery_svc()
        col = MagicMock()
        col.name = "revenue"
        col.type_name = "DOUBLE"
        col.type_text = "double"
        col.comment = None
        col.position = 0
        col.nullable = True

        table_info = MagicMock()
        table_info.columns = [col]
        svc.client.tables.get.return_value = table_info

        result = await svc.get_table_columns("cat", "sch", "sales")

        assert len(result) == 1
        assert result[0]["name"] == "revenue"
        assert result[0]["type_text"] == "double"

    @pytest.mark.asyncio
    async def test_get_table_columns_handles_no_columns(self):
        svc = _make_discovery_svc()
        table_info = MagicMock()
        table_info.columns = None
        svc.client.tables.get.return_value = table_info

        result = await svc.get_table_columns("cat", "sch", "empty_table")
        assert result == []
