"""
Integration tests for the /api/v1/templates routes.

TemplatesRepository is injected via dependency_overrides; DataQueryService is patched.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.authorization import get_templates_repo
from models.template import Template

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
TID = uuid.uuid4()
SID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _template(
    *,
    id: uuid.UUID | None = None,
    name: str = "Test Template",
    structure_id: uuid.UUID | None = None,
    html_content: str = "<p>{{rows}}</p>",
) -> Template:
    return Template(
        id=id or TID,
        name=name,
        structure_id=structure_id or SID,
        html_content=html_content,
        created_at=NOW,
        updated_at=NOW,
    )


class _NO_LOCK:
    """Context manager that mocks all authorization checks used by template routes."""
    def __enter__(self):
        self._p1 = patch("routes.v1.templates.check_structure_project_access", return_value=None, new_callable=AsyncMock)
        self._p2 = patch("routes.v1.templates.check_template_project_access", return_value=None, new_callable=AsyncMock)
        self._p3 = patch("routes.v1.templates.check_structure_read_access", return_value=None, new_callable=AsyncMock)
        self._p4 = patch("routes.v1.templates.check_template_read_access", return_value=None, new_callable=AsyncMock)
        self._p1.__enter__()
        self._p2.__enter__()
        self._p3.__enter__()
        self._p4.__enter__()
        return self
    def __exit__(self, *args):
        self._p4.__exit__(*args)
        self._p3.__exit__(*args)
        self._p2.__exit__(*args)
        self._p1.__exit__(*args)


def _mock_repo(
    *,
    get_all=None,
    get_by_id=None,
    create=None,
    update=None,
    delete=None,
):
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=get_all or [])
    repo.get_by_id = AsyncMock(return_value=get_by_id)
    repo.create = AsyncMock(return_value=create)
    repo.update = AsyncMock(return_value=update)
    repo.delete = AsyncMock(return_value=delete if delete is not None else True)
    return repo



# ---------------------------------------------------------------------------
# GET /templates/
# ---------------------------------------------------------------------------


class TestListTemplates:
    @pytest.mark.asyncio
    async def test_list_templates_returns_200(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all=[_template()])
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.get(f"/api/v1/templates/?structure_id={SID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_templates_returns_list(self, async_client, dependency_overrides):
        templates = [_template(), _template(name="Second")]
        repo = _mock_repo(get_all=templates)
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.get(f"/api/v1/templates/?structure_id={SID}")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_templates_filters_by_structure_id(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all=[_template()])
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            await async_client.get(f"/api/v1/templates/?structure_id={SID}")
        repo.get_all.assert_awaited_once_with(structure_id=SID, project_id=None)

    @pytest.mark.asyncio
    async def test_list_templates_empty_returns_empty_list(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all=[])
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.get(f"/api/v1/templates/?structure_id={SID}")
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_templates_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_all = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.get(f"/api/v1/templates/?structure_id={SID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# GET /templates/{id}
# ---------------------------------------------------------------------------


class TestGetTemplate:
    @pytest.mark.asyncio
    async def test_get_template_returns_200_when_found(self, async_client, dependency_overrides):
        tmpl = _template(id=TID)
        repo = _mock_repo(get_by_id=tmpl)
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.get(f"/api/v1/templates/{TID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_template_returns_correct_name(self, async_client, dependency_overrides):
        tmpl = _template(id=TID, name="Annual Report")
        repo = _mock_repo(get_by_id=tmpl)
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.get(f"/api/v1/templates/{TID}")
        assert response.json()["name"] == "Annual Report"

    @pytest.mark.asyncio
    async def test_get_template_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None)
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.get(f"/api/v1/templates/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_template_returns_422_for_invalid_uuid(self, async_client):
        response = await async_client.get("/api/v1/templates/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_template_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_by_id = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.get(f"/api/v1/templates/{TID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /templates/
# ---------------------------------------------------------------------------


class TestCreateTemplate:
    @pytest.mark.asyncio
    async def test_create_template_returns_201(self, async_client, dependency_overrides):
        tmpl = _template()
        repo = _mock_repo(create=tmpl)
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.post(
                "/api/v1/templates/",
                json={"name": "New Template", "structure_id": str(SID)},
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_template_returns_422_when_name_missing(self, async_client):
        response = await async_client.post(
            "/api/v1/templates/",
            json={"structure_id": str(SID)},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_template_returns_422_when_structure_id_missing(self, async_client):
        response = await async_client.post(
            "/api/v1/templates/",
            json={"name": "New"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_template_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.create = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.post(
                "/api/v1/templates/",
                json={"name": "New", "structure_id": str(SID)},
            )
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# PUT /templates/{id}
# ---------------------------------------------------------------------------


class TestUpdateTemplate:
    @pytest.mark.asyncio
    async def test_update_template_returns_200(self, async_client, dependency_overrides):
        tmpl = _template(id=TID, name="Updated")
        repo = _mock_repo(get_by_id=tmpl, update=tmpl)
        dependency_overrides[get_templates_repo] = lambda: repo
        with (
            patch("routes.v1.templates.app_cache") as mock_cache,
            _NO_LOCK(),
        ):
            mock_cache.delete = AsyncMock()
            response = await async_client.put(
                f"/api/v1/templates/{TID}",
                json={"name": "Updated"},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_template_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None, update=None)
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.put(
                f"/api/v1/templates/{uuid.uuid4()}",
                json={"name": "Ghost"},
            )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_template_invalidates_cache_when_structure_id_changes(self, async_client, dependency_overrides):
        tmpl = _template(id=TID)
        repo = _mock_repo(get_by_id=tmpl, update=tmpl)
        dependency_overrides[get_templates_repo] = lambda: repo
        with (
            patch("routes.v1.templates.app_cache") as mock_cache,
            _NO_LOCK(),
        ):
            mock_cache.delete = AsyncMock()
            await async_client.put(
                f"/api/v1/templates/{TID}",
                json={"structure_id": str(uuid.uuid4())},
            )
            mock_cache.delete.assert_awaited_once_with(f"preview:{TID}:50")

    @pytest.mark.asyncio
    async def test_update_template_does_not_invalidate_cache_when_structure_id_unchanged(
        self, async_client, dependency_overrides
    ):
        """Updating only html_content should NOT trigger a cache invalidation."""
        tmpl = _template(id=TID)
        repo = _mock_repo(get_by_id=tmpl, update=tmpl)
        dependency_overrides[get_templates_repo] = lambda: repo
        with (
            patch("routes.v1.templates.app_cache") as mock_cache,
            _NO_LOCK(),
        ):
            mock_cache.delete = AsyncMock()
            await async_client.put(
                f"/api/v1/templates/{TID}",
                json={"html_content": "<b>new</b>"},
            )
            mock_cache.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_template_returns_409_on_conflict(self, async_client, dependency_overrides):
        tmpl = _template(id=TID)
        repo = _mock_repo(get_by_id=tmpl, update=None)
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.put(
                f"/api/v1/templates/{TID}",
                json={
                    "html_content": "<p>stale</p>",
                    "expected_updated_at": NOW.isoformat(),
                },
            )
        assert response.status_code == 409
        assert "modified by another user" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_template_returns_404_without_expected_updated_at(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None, update=None)
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.put(
                f"/api/v1/templates/{uuid.uuid4()}",
                json={"name": "Ghost"},
            )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_template_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        tmpl = _template(id=TID)
        repo = _mock_repo(get_by_id=tmpl)
        repo.update = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.put(
                f"/api/v1/templates/{TID}",
                json={"name": "Broken"},
            )
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# DELETE /templates/{id}
# ---------------------------------------------------------------------------


class TestDeleteTemplate:
    @pytest.mark.asyncio
    async def test_delete_template_returns_204(self, async_client, dependency_overrides):
        tmpl = _template(id=TID)
        repo = _mock_repo(get_by_id=tmpl, delete=True)
        dependency_overrides[get_templates_repo] = lambda: repo
        with (
            patch("routes.v1.templates.app_cache") as mock_cache,
            _NO_LOCK(),
        ):
            mock_cache.delete = AsyncMock()
            response = await async_client.delete(f"/api/v1/templates/{TID}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_template_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None, delete=False)
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.delete(f"/api/v1/templates/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_template_invalidates_cache(self, async_client, dependency_overrides):
        tmpl = _template(id=TID)
        repo = _mock_repo(get_by_id=tmpl, delete=True)
        dependency_overrides[get_templates_repo] = lambda: repo
        with (
            patch("routes.v1.templates.app_cache") as mock_cache,
            _NO_LOCK(),
        ):
            mock_cache.delete = AsyncMock()
            await async_client.delete(f"/api/v1/templates/{TID}")
            mock_cache.delete.assert_awaited_once_with(f"preview:{TID}:50")

    @pytest.mark.asyncio
    async def test_delete_template_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        tmpl = _template(id=TID)
        repo = _mock_repo(get_by_id=tmpl)
        repo.delete = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_templates_repo] = lambda: repo
        with _NO_LOCK():
            response = await async_client.delete(f"/api/v1/templates/{TID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /templates/{id}/preview-data
# ---------------------------------------------------------------------------


class TestPreviewData:
    @pytest.mark.asyncio
    async def test_preview_data_returns_200_on_success(self, async_client):
        mock_svc = MagicMock()
        mock_svc.execute_for_preview = AsyncMock(
            return_value={"data": {"rows": [{"col": "a"}]}, "query": "SELECT col FROM t", "row_count": 1}
        )
        with patch("routes.v1.templates.DataQueryService", return_value=mock_svc), _NO_LOCK():
            response = await async_client.post(f"/api/v1/templates/{TID}/preview-data")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_preview_data_returns_correct_body(self, async_client):
        payload = {"data": {"rows": [{"x": 1}]}, "query": "SELECT x FROM t", "row_count": 1}
        mock_svc = MagicMock()
        mock_svc.execute_for_preview = AsyncMock(return_value=payload)
        with patch("routes.v1.templates.DataQueryService", return_value=mock_svc), _NO_LOCK():
            response = await async_client.post(f"/api/v1/templates/{TID}/preview-data")
        assert response.json()["row_count"] == 1

    @pytest.mark.asyncio
    async def test_preview_data_returns_404_on_value_error(self, async_client):
        mock_svc = MagicMock()
        mock_svc.execute_for_preview = AsyncMock(side_effect=ValueError("Template not found"))
        with patch("routes.v1.templates.DataQueryService", return_value=mock_svc), _NO_LOCK():
            response = await async_client.post(f"/api/v1/templates/{TID}/preview-data")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_preview_data_returns_502_on_unexpected_exception(self, async_client):
        mock_svc = MagicMock()
        mock_svc.execute_for_preview = AsyncMock(side_effect=ConnectionError("Databricks down"))
        with patch("routes.v1.templates.DataQueryService", return_value=mock_svc), _NO_LOCK():
            response = await async_client.post(f"/api/v1/templates/{TID}/preview-data")
        assert response.status_code == 502

    @pytest.mark.asyncio
    async def test_preview_data_passes_limit_query_param(self, async_client):
        mock_svc = MagicMock()
        mock_svc.execute_for_preview = AsyncMock(return_value={"data": {}, "query": None, "row_count": 0})
        with patch("routes.v1.templates.DataQueryService", return_value=mock_svc), _NO_LOCK():
            await async_client.post(f"/api/v1/templates/{TID}/preview-data?limit=10")
        mock_svc.execute_for_preview.assert_awaited_once_with(TID, limit=10)

    @pytest.mark.asyncio
    async def test_preview_data_returns_422_when_limit_below_minimum(self, async_client):
        with _NO_LOCK():
            response = await async_client.post(f"/api/v1/templates/{TID}/preview-data?limit=0")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_preview_data_returns_422_when_limit_above_maximum(self, async_client):
        with _NO_LOCK():
            response = await async_client.post(f"/api/v1/templates/{TID}/preview-data?limit=1001")
        assert response.status_code == 422
