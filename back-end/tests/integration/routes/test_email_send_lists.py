"""
Integration tests for the /api/v1/send-lists routes.

EmailSendListsRepository and ProjectsRepository are injected via
dependency_overrides so no real DB calls are made.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.authorization import get_projects_repo
from models.email_send_list import EmailSendList
from models.project import Project

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
PID = uuid.uuid4()
CID = uuid.uuid4()
SLID = uuid.uuid4()

_USER = "user@example.com"
_USER_HEADERS = {"X-Forwarded-Email": _USER}

_BASE = "/api/v1/send-lists"


def _send_list(*, id=None, name="Exec List") -> EmailSendList:
    return EmailSendList(
        id=id or SLID,
        name=name,
        project_id=PID,
        smtp_connection_id=CID,
        emails=["alice@example.com"],
        created_by=_USER,
        created_at=NOW,
        updated_at=NOW,
    )


def _mock_send_list_repo(**kwargs) -> MagicMock:
    repo = MagicMock()
    repo.get_all_for_project = AsyncMock(return_value=kwargs.get("get_all_for_project", []))
    repo.get_by_id = AsyncMock(return_value=kwargs.get("get_by_id", None))
    repo.create = AsyncMock(return_value=kwargs.get("create", None))
    repo.update = AsyncMock(return_value=kwargs.get("update", None))
    repo.delete = AsyncMock(return_value=kwargs.get("delete", True))
    return repo


def _mock_projects_repo(*, has_access: bool = True, is_locked: bool = False) -> MagicMock:
    repo = MagicMock()
    repo.user_has_access = AsyncMock(return_value=has_access)
    repo.get_access_and_lock_status = AsyncMock(return_value=(has_access, is_locked))
    return repo


# ---------------------------------------------------------------------------
# GET /send-lists/?project_id=...
# ---------------------------------------------------------------------------


class TestListSendLists:
    @pytest.mark.asyncio
    async def test_returns_200_with_empty_list(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo()
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.get(
            f"{_BASE}/", params={"project_id": str(PID)}, headers=_USER_HEADERS
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_returns_list_of_send_lists(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(
            get_all_for_project=[_send_list(), _send_list(id=uuid.uuid4(), name="B")]
        )
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.get(
            f"{_BASE}/", params={"project_id": str(PID)}, headers=_USER_HEADERS
        )
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.asyncio
    async def test_returns_403_when_no_project_access(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo()
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo(has_access=False)
        response = await async_client.get(
            f"{_BASE}/", params={"project_id": str(PID)}, headers=_USER_HEADERS
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_401_when_no_auth_header(self, async_client):
        with patch("common.authorization.is_development", return_value=False):
            response = await async_client.get(f"{_BASE}/", params={"project_id": str(PID)})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_503_when_lakebase_unavailable(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        repo = MagicMock()
        repo.get_all_for_project = AsyncMock(side_effect=RuntimeError("Lakebase down"))
        dependency_overrides[_get_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.get(
            f"{_BASE}/", params={"project_id": str(PID)}, headers=_USER_HEADERS
        )
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# GET /send-lists/{id}
# ---------------------------------------------------------------------------


class TestGetSendList:
    @pytest.mark.asyncio
    async def test_returns_200_when_found(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(get_by_id=_send_list())
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.get(f"{_BASE}/{SLID}", headers=_USER_HEADERS)
        assert response.status_code == 200
        assert response.json()["name"] == "Exec List"

    @pytest.mark.asyncio
    async def test_returns_404_when_not_found(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(get_by_id=None)
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.get(f"{_BASE}/{SLID}", headers=_USER_HEADERS)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_403_when_no_project_access(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(get_by_id=_send_list())
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo(has_access=False)
        response = await async_client.get(f"{_BASE}/{SLID}", headers=_USER_HEADERS)
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /send-lists/
# ---------------------------------------------------------------------------


class TestCreateSendList:
    _body = {
        "name": "Exec List",
        "project_id": str(PID),
        "smtp_connection_id": str(CID),
        "emails": ["alice@example.com"],
    }

    @pytest.mark.asyncio
    async def test_returns_201_when_created(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(create=_send_list())
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.post(f"{_BASE}/", json=self._body, headers=_USER_HEADERS)
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_returns_403_when_no_project_access(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo()
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo(has_access=False)
        response = await async_client.post(f"{_BASE}/", json=self._body, headers=_USER_HEADERS)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_423_when_project_locked(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo()
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo(is_locked=True)
        response = await async_client.post(f"{_BASE}/", json=self._body, headers=_USER_HEADERS)
        assert response.status_code == 423

    @pytest.mark.asyncio
    async def test_503_when_lakebase_unavailable(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        repo = MagicMock()
        repo.create = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[_get_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.post(f"{_BASE}/", json=self._body, headers=_USER_HEADERS)
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# PUT /send-lists/{id}
# ---------------------------------------------------------------------------


class TestUpdateSendList:
    _body = {"name": "Updated List"}

    @pytest.mark.asyncio
    async def test_returns_200_when_updated(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        updated = _send_list(name="Updated List")
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(get_by_id=_send_list(), update=updated)
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.put(f"{_BASE}/{SLID}", json=self._body, headers=_USER_HEADERS)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated List"

    @pytest.mark.asyncio
    async def test_returns_404_when_not_found(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(get_by_id=_send_list(), update=None)
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.put(f"{_BASE}/{SLID}", json=self._body, headers=_USER_HEADERS)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_423_when_project_locked(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(get_by_id=_send_list())
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo(is_locked=True)
        response = await async_client.put(f"{_BASE}/{SLID}", json=self._body, headers=_USER_HEADERS)
        assert response.status_code == 423


# ---------------------------------------------------------------------------
# DELETE /send-lists/{id}
# ---------------------------------------------------------------------------


class TestDeleteSendList:
    @pytest.mark.asyncio
    async def test_returns_204_when_deleted(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(get_by_id=_send_list(), delete=True)
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.delete(f"{_BASE}/{SLID}", headers=_USER_HEADERS)
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_returns_404_when_delete_returns_false(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(get_by_id=_send_list(), delete=False)
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        response = await async_client.delete(f"{_BASE}/{SLID}", headers=_USER_HEADERS)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_403_when_no_project_access(self, async_client, dependency_overrides):
        from routes.v1.email_send_lists import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_send_list_repo(get_by_id=_send_list())
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo(has_access=False)
        response = await async_client.delete(f"{_BASE}/{SLID}", headers=_USER_HEADERS)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_401_when_no_auth_header(self, async_client):
        with patch("common.authorization.is_development", return_value=False):
            response = await async_client.delete(f"{_BASE}/{SLID}")
        assert response.status_code == 401
