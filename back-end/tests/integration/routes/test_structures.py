"""
Integration tests for the /api/v1/structures routes.

StructuresRepository is injected via dependency_overrides so no DB
connection is required.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.authorization import get_structures_repo
from models.structure import Structure, StructureField, StructureTable

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
SID = uuid.uuid4()
PID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _structure(
    *,
    id: uuid.UUID | None = None,
    name: str = "Test Structure",
    project_id: uuid.UUID | None = None,
    sql_query: str | None = "SELECT col FROM cat.sch.tbl",
    tables=None,
    selected_columns=None,
) -> Structure:
    return Structure(
        id=id or SID,
        name=name,
        project_id=project_id or PID,
        fields=[StructureField(name="col", type="string")],
        tables=tables if tables is not None else [StructureTable(full_name="cat.sch.tbl", alias="tbl")],
        relationships=[],
        selected_columns=selected_columns if selected_columns is not None else ["col"],
        sql_query=sql_query,
        created_at=NOW,
        updated_at=NOW,
    )


def _NO_LOCK():
    return patch("routes.v1.structures.check_structure_project_access", return_value=None, new_callable=AsyncMock)


def _ALLOW_ACCESS():
    return patch("routes.v1.structures.check_project_access", return_value=None, new_callable=AsyncMock)


def _ALLOW_ACCESS_AND_NOT_LOCKED():
    return patch("routes.v1.structures.check_project_access_and_not_locked", return_value=None, new_callable=AsyncMock)


def _ALLOW_READ():
    return patch("routes.v1.structures.check_structure_read_access", return_value=None, new_callable=AsyncMock)


def _mock_repo(
    *,
    get_by_project_id=None,
    get_by_id=None,
    create=None,
    update=None,
    update_built=None,
    delete=None,
):
    repo = MagicMock()
    repo.get_by_project_id = AsyncMock(return_value=get_by_project_id or [])
    repo.get_by_id = AsyncMock(return_value=get_by_id)
    repo.create = AsyncMock(return_value=create)
    repo.update = AsyncMock(return_value=update)
    repo.update_built = AsyncMock(return_value=update_built)
    repo.delete = AsyncMock(return_value=delete if delete is not None else True)
    return repo


# ---------------------------------------------------------------------------
# GET /structures/
# ---------------------------------------------------------------------------


class TestListStructures:
    @pytest.mark.asyncio
    async def test_list_structures_returns_200(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_project_id=[_structure()])
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_ACCESS():
            response = await async_client.get(f"/api/v1/structures/?project_id={PID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_structures_returns_list(self, async_client, dependency_overrides):
        structures = [_structure(), _structure(name="Second")]
        repo = _mock_repo(get_by_project_id=structures)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_ACCESS():
            response = await async_client.get(f"/api/v1/structures/?project_id={PID}")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_structures_empty_returns_empty_list(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_project_id=[])
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_ACCESS():
            response = await async_client.get(f"/api/v1/structures/?project_id={PID}")
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_structures_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_by_project_id = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_ACCESS():
            response = await async_client.get(f"/api/v1/structures/?project_id={PID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# GET /structures/{id}
# ---------------------------------------------------------------------------


class TestGetStructure:
    @pytest.mark.asyncio
    async def test_get_structure_returns_200_when_found(self, async_client, dependency_overrides):
        struct = _structure(id=SID)
        repo = _mock_repo(get_by_id=struct)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_READ():
            response = await async_client.get(f"/api/v1/structures/{SID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_structure_returns_correct_name(self, async_client, dependency_overrides):
        struct = _structure(id=SID, name="Revenue Report")
        repo = _mock_repo(get_by_id=struct)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_READ():
            response = await async_client.get(f"/api/v1/structures/{SID}")
        assert response.json()["name"] == "Revenue Report"

    @pytest.mark.asyncio
    async def test_get_structure_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_READ():
            response = await async_client.get(f"/api/v1/structures/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_structure_returns_422_for_invalid_uuid(self, async_client):
        response = await async_client.get("/api/v1/structures/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_structure_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_by_id = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_READ():
            response = await async_client.get(f"/api/v1/structures/{SID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /structures/
# ---------------------------------------------------------------------------


class TestCreateStructure:
    @pytest.mark.asyncio
    async def test_create_structure_returns_201(self, async_client, dependency_overrides):
        struct = _structure()
        repo = _mock_repo(create=struct)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_ACCESS_AND_NOT_LOCKED():
            response = await async_client.post(
                "/api/v1/structures/",
                json={"name": "New Structure", "project_id": str(PID)},
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_structure_returns_created_structure(self, async_client, dependency_overrides):
        struct = _structure(name="Created")
        repo = _mock_repo(create=struct)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_ACCESS_AND_NOT_LOCKED():
            response = await async_client.post(
                "/api/v1/structures/",
                json={"name": "Created", "project_id": str(PID)},
            )
        assert response.json()["name"] == "Created"

    @pytest.mark.asyncio
    async def test_create_structure_returns_422_when_name_missing(self, async_client):
        response = await async_client.post("/api/v1/structures/", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_structure_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.create = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_structures_repo] = lambda: repo
        with _ALLOW_ACCESS_AND_NOT_LOCKED():
            response = await async_client.post(
                "/api/v1/structures/",
                json={"name": "New", "project_id": str(PID)},
            )
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# PUT /structures/{id}
# ---------------------------------------------------------------------------


class TestUpdateStructure:
    @pytest.mark.asyncio
    async def test_update_structure_returns_200(self, async_client, dependency_overrides):
        struct = _structure(id=SID, name="Updated")
        repo = _mock_repo(update=struct)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.put(
                f"/api/v1/structures/{SID}",
                json={"name": "Updated"},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_structure_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(update=None)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.put(
                f"/api/v1/structures/{uuid.uuid4()}",
                json={"name": "Ghost"},
            )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_structure_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.update = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_structures_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.put(
                f"/api/v1/structures/{SID}",
                json={"name": "Broken"},
            )
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# DELETE /structures/{id}
# ---------------------------------------------------------------------------


class TestDeleteStructure:
    @pytest.mark.asyncio
    async def test_delete_structure_returns_204_when_deleted(self, async_client, dependency_overrides):
        repo = _mock_repo(delete=True)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.delete(f"/api/v1/structures/{SID}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_structure_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(delete=False)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.delete(f"/api/v1/structures/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_structure_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.delete = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_structures_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.delete(f"/api/v1/structures/{SID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /structures/{id}/build
# ---------------------------------------------------------------------------


class TestBuildStructure:
    @pytest.mark.asyncio
    async def test_build_returns_200_on_success(self, async_client, dependency_overrides):
        struct = _structure(id=SID)
        built = _structure(id=SID, sql_query="SELECT col FROM cat.sch.tbl")
        repo = _mock_repo(get_by_id=struct, update_built=built)
        dependency_overrides[get_structures_repo] = lambda: repo

        mock_builder = MagicMock()
        mock_builder.build_query = MagicMock(return_value="SELECT col FROM cat.sch.tbl")
        mock_builder.infer_fields = AsyncMock(return_value=[StructureField(name="col", type="string")])

        with (
            patch("routes.v1.structures.QueryBuilderService", return_value=mock_builder),
            _NO_LOCK(),
        ):
            response = await async_client.post(f"/api/v1/structures/{SID}/build")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_build_returns_404_when_structure_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.post(f"/api/v1/structures/{uuid.uuid4()}/build")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_build_returns_400_when_no_tables(self, async_client, dependency_overrides):
        struct = _structure(id=SID, tables=[])
        repo = _mock_repo(get_by_id=struct)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.post(f"/api/v1/structures/{SID}/build")
        assert response.status_code == 400
        assert "exactly one table" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_build_returns_400_when_no_selected_columns(self, async_client, dependency_overrides):
        struct = _structure(id=SID, selected_columns=[])
        repo = _mock_repo(get_by_id=struct)
        dependency_overrides[get_structures_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.post(f"/api/v1/structures/{SID}/build")
        assert response.status_code == 400
        assert "selected column" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_build_returns_400_on_value_error_from_builder(self, async_client, dependency_overrides):
        struct = _structure(id=SID)
        repo = _mock_repo(get_by_id=struct)
        dependency_overrides[get_structures_repo] = lambda: repo

        mock_builder = MagicMock()
        mock_builder.build_query = MagicMock(side_effect=ValueError("bad table name"))

        with (
            patch("routes.v1.structures.QueryBuilderService", return_value=mock_builder),
            _NO_LOCK(),
        ):
            response = await async_client.post(f"/api/v1/structures/{SID}/build")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_build_returns_502_on_unexpected_exception(self, async_client, dependency_overrides):
        struct = _structure(id=SID)
        repo = _mock_repo(get_by_id=struct)
        dependency_overrides[get_structures_repo] = lambda: repo

        mock_builder = MagicMock()
        mock_builder.build_query = MagicMock(side_effect=ConnectionError("databricks down"))

        with (
            patch("routes.v1.structures.QueryBuilderService", return_value=mock_builder),
            _NO_LOCK(),
        ):
            response = await async_client.post(f"/api/v1/structures/{SID}/build")
        assert response.status_code == 502
