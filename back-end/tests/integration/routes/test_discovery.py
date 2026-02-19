"""
Integration tests for the /api/v1/discovery routes.

DiscoveryService is mocked at the route level.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.structure import StructureField


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_discovery_svc(
    *,
    catalogs=None,
    schemas=None,
    tables=None,
    columns=None,
    fields=None,
):
    svc = MagicMock()
    svc.list_catalogs = AsyncMock(
        return_value=catalogs or [{"name": "cat1", "comment": None, "owner": None}]
    )
    svc.list_schemas = AsyncMock(
        return_value=schemas or [{"name": "sch1", "catalog_name": "cat1", "comment": None}]
    )
    svc.list_tables = AsyncMock(
        return_value=tables
        or [{"name": "tbl1", "full_name": "cat1.sch1.tbl1", "table_type": "MANAGED", "comment": None}]
    )
    svc.get_table_columns = AsyncMock(
        return_value=columns
        or [{"name": "col1", "type_text": "string", "type_name": "STRING", "comment": None, "position": 0, "nullable": True}]
    )
    svc.columns_to_structure_fields = MagicMock(
        return_value=fields or [StructureField(name="col1", type="string")]
    )
    return svc


# ---------------------------------------------------------------------------
# GET /discovery/catalogs
# ---------------------------------------------------------------------------


class TestListCatalogs:
    @pytest.mark.asyncio
    async def test_list_catalogs_returns_200(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get("/api/v1/discovery/catalogs")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_catalogs_returns_list(self, async_client):
        svc = _mock_discovery_svc(catalogs=[{"name": "main", "comment": None, "owner": "admin"}])
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get("/api/v1/discovery/catalogs")
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["name"] == "main"

    @pytest.mark.asyncio
    async def test_list_catalogs_returns_502_on_exception(self, async_client):
        svc = _mock_discovery_svc()
        svc.list_catalogs = AsyncMock(side_effect=Exception("SDK error"))
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get("/api/v1/discovery/catalogs")
        assert response.status_code == 502

    @pytest.mark.asyncio
    async def test_list_catalogs_passes_forwarded_token(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc) as mock_cls:
            await async_client.get(
                "/api/v1/discovery/catalogs",
                headers={"x-forwarded-access-token": "my-token"},
            )
            mock_cls.assert_called_once_with(token="my-token")


# ---------------------------------------------------------------------------
# GET /discovery/catalogs/{catalog}/schemas
# ---------------------------------------------------------------------------


class TestListSchemas:
    @pytest.mark.asyncio
    async def test_list_schemas_returns_200(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get("/api/v1/discovery/catalogs/cat1/schemas")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_schemas_calls_service_with_catalog(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            await async_client.get("/api/v1/discovery/catalogs/my_catalog/schemas")
        svc.list_schemas.assert_awaited_once_with("my_catalog")

    @pytest.mark.asyncio
    async def test_list_schemas_returns_502_on_exception(self, async_client):
        svc = _mock_discovery_svc()
        svc.list_schemas = AsyncMock(side_effect=Exception("SDK error"))
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get("/api/v1/discovery/catalogs/cat/schemas")
        assert response.status_code == 502


# ---------------------------------------------------------------------------
# GET /discovery/catalogs/{catalog}/schemas/{schema}/tables
# ---------------------------------------------------------------------------


class TestListTables:
    @pytest.mark.asyncio
    async def test_list_tables_returns_200(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get("/api/v1/discovery/catalogs/cat1/schemas/sch1/tables")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_tables_calls_service_with_catalog_and_schema(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            await async_client.get("/api/v1/discovery/catalogs/my_cat/schemas/my_sch/tables")
        svc.list_tables.assert_awaited_once_with("my_cat", "my_sch")

    @pytest.mark.asyncio
    async def test_list_tables_returns_502_on_exception(self, async_client):
        svc = _mock_discovery_svc()
        svc.list_tables = AsyncMock(side_effect=Exception("SDK error"))
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get("/api/v1/discovery/catalogs/c/schemas/s/tables")
        assert response.status_code == 502


# ---------------------------------------------------------------------------
# GET /discovery/catalogs/{catalog}/schemas/{schema}/tables/{table}/columns
# ---------------------------------------------------------------------------


class TestGetTableColumns:
    @pytest.mark.asyncio
    async def test_get_table_columns_returns_200(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get(
                "/api/v1/discovery/catalogs/c/schemas/s/tables/t/columns"
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_table_columns_calls_service_with_correct_args(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            await async_client.get(
                "/api/v1/discovery/catalogs/cat/schemas/sch/tables/tbl/columns"
            )
        svc.get_table_columns.assert_awaited_once_with("cat", "sch", "tbl")

    @pytest.mark.asyncio
    async def test_get_table_columns_returns_502_on_exception(self, async_client):
        svc = _mock_discovery_svc()
        svc.get_table_columns = AsyncMock(side_effect=Exception("SDK error"))
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get(
                "/api/v1/discovery/catalogs/c/schemas/s/tables/t/columns"
            )
        assert response.status_code == 502


# ---------------------------------------------------------------------------
# GET /discovery/catalogs/{catalog}/schemas/{schema}/tables/{table}/as-fields
# ---------------------------------------------------------------------------


class TestGetTableAsFields:
    @pytest.mark.asyncio
    async def test_get_table_as_fields_returns_200(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get(
                "/api/v1/discovery/catalogs/c/schemas/s/tables/t/as-fields"
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_table_as_fields_returns_structure_fields(self, async_client):
        fields = [
            StructureField(name="id", type="number"),
            StructureField(name="name", type="string"),
        ]
        svc = _mock_discovery_svc(fields=fields)
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get(
                "/api/v1/discovery/catalogs/c/schemas/s/tables/t/as-fields"
            )
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["name"] == "id"
        assert data[1]["type"] == "string"

    @pytest.mark.asyncio
    async def test_get_table_as_fields_returns_502_on_exception(self, async_client):
        svc = _mock_discovery_svc()
        svc.get_table_columns = AsyncMock(side_effect=Exception("SDK error"))
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            response = await async_client.get(
                "/api/v1/discovery/catalogs/c/schemas/s/tables/t/as-fields"
            )
        assert response.status_code == 502

    @pytest.mark.asyncio
    async def test_get_table_as_fields_calls_columns_to_structure_fields(self, async_client):
        svc = _mock_discovery_svc()
        with patch("routes.v1.discovery.DiscoveryService", return_value=svc):
            await async_client.get(
                "/api/v1/discovery/catalogs/c/schemas/s/tables/t/as-fields"
            )
        svc.columns_to_structure_fields.assert_called_once()
