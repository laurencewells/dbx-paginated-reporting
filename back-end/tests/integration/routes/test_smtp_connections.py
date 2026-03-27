"""
Integration tests for the /api/v1/smtp-connections routes.

SmtpConnectionsRepository is injected via dependency_overrides.
Databricks Workspace secret calls are patched per test.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.smtp_connection import SmtpConnection

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
CID = uuid.uuid4()

_ADMIN_EMAIL = "admin@example.com"
_ADMIN_HEADERS = {"X-Forwarded-Email": _ADMIN_EMAIL}
_USER_HEADERS = {"X-Forwarded-Email": "user@example.com"}

_BASE = "/api/v1/smtp-connections"


def _conn(*, id=None, name="My SMTP") -> SmtpConnection:
    return SmtpConnection(
        id=id or CID,
        name=name,
        provider="gsuite",
        from_email="sender@example.com",
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        username="sender@example.com",
        secret_scope="paginated-reports-smtp",
        secret_key=f"smtp_{id or CID}",
        created_by=_ADMIN_EMAIL,
        created_at=NOW,
        updated_at=NOW,
    )


def _mock_repo(**kwargs) -> MagicMock:
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=kwargs.get("get_all", []))
    repo.get_by_id = AsyncMock(return_value=kwargs.get("get_by_id", None))
    repo.create = AsyncMock(return_value=kwargs.get("create", None))
    repo.update = AsyncMock(return_value=kwargs.get("update", None))
    repo.delete = AsyncMock(return_value=kwargs.get("delete", True))
    repo.has_active_send_lists = AsyncMock(return_value=kwargs.get("has_active_send_lists", False))
    return repo


@pytest.fixture
def admin_env(monkeypatch):
    monkeypatch.setenv("ADMIN_EMAILS", _ADMIN_EMAIL)


# ---------------------------------------------------------------------------
# GET /smtp-connections/
# ---------------------------------------------------------------------------


class TestListSmtpConnections:
    @pytest.mark.asyncio
    async def test_returns_200_with_empty_list(self, async_client, dependency_overrides):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo()
        response = await async_client.get(f"{_BASE}/")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_returns_list_of_connections(self, async_client, dependency_overrides):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_all=[_conn(), _conn(id=uuid.uuid4(), name="B")])
        response = await async_client.get(f"{_BASE}/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.asyncio
    async def test_503_when_lakebase_unavailable(self, async_client, dependency_overrides):
        from routes.v1.smtp_connections import _get_repo
        repo = MagicMock()
        repo.get_all = AsyncMock(side_effect=RuntimeError("Lakebase down"))
        dependency_overrides[_get_repo] = lambda: repo
        response = await async_client.get(f"{_BASE}/")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# GET /smtp-connections/{id}
# ---------------------------------------------------------------------------


class TestGetSmtpConnection:
    @pytest.mark.asyncio
    async def test_returns_200_when_found(self, async_client, dependency_overrides):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=_conn())
        response = await async_client.get(f"{_BASE}/{CID}")
        assert response.status_code == 200
        assert response.json()["name"] == "My SMTP"

    @pytest.mark.asyncio
    async def test_returns_404_when_not_found(self, async_client, dependency_overrides):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=None)
        response = await async_client.get(f"{_BASE}/{CID}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_503_when_lakebase_unavailable(self, async_client, dependency_overrides):
        from routes.v1.smtp_connections import _get_repo
        repo = MagicMock()
        repo.get_by_id = AsyncMock(side_effect=RuntimeError("down"))
        dependency_overrides[_get_repo] = lambda: repo
        response = await async_client.get(f"{_BASE}/{CID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /smtp-connections/
# ---------------------------------------------------------------------------


class TestCreateSmtpConnection:
    _body = {
        "name": "My SMTP",
        "provider": "gsuite",
        "from_email": "sender@example.com",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "sender@example.com",
        "password": "secret",
    }

    @pytest.mark.asyncio
    async def test_returns_201_for_admin(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(create=_conn())
        with patch("routes.v1.smtp_connections._write_secret"):
            response = await async_client.post(f"{_BASE}/", json=self._body, headers=_ADMIN_HEADERS)
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_returns_403_for_non_admin(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(create=_conn())
        with patch("routes.v1.smtp_connections._write_secret"):
            response = await async_client.post(f"{_BASE}/", json=self._body, headers=_USER_HEADERS)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_503_when_secret_write_fails(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo()
        with patch("routes.v1.smtp_connections._write_secret", side_effect=Exception("Secret store down")):
            response = await async_client.post(f"{_BASE}/", json=self._body, headers=_ADMIN_HEADERS)
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_rollback_secret_if_db_create_fails(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        repo = MagicMock()
        repo.create = AsyncMock(side_effect=RuntimeError("DB failure"))
        dependency_overrides[_get_repo] = lambda: repo
        with (
            patch("routes.v1.smtp_connections._write_secret"),
            patch("routes.v1.smtp_connections._delete_secret") as mock_delete,
        ):
            response = await async_client.post(f"{_BASE}/", json=self._body, headers=_ADMIN_HEADERS)
        assert response.status_code == 503
        mock_delete.assert_called_once()


# ---------------------------------------------------------------------------
# PUT /smtp-connections/{id}
# ---------------------------------------------------------------------------


class TestUpdateSmtpConnection:
    _body = {"name": "Updated SMTP"}

    @pytest.mark.asyncio
    async def test_returns_200_when_updated(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        existing = _conn()
        updated = _conn(name="Updated SMTP")
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=existing, update=updated)
        with patch("routes.v1.smtp_connections._write_secret"):
            response = await async_client.put(f"{_BASE}/{CID}", json=self._body, headers=_ADMIN_HEADERS)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated SMTP"

    @pytest.mark.asyncio
    async def test_returns_404_when_not_found(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=None)
        response = await async_client.put(f"{_BASE}/{CID}", json=self._body, headers=_ADMIN_HEADERS)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_403_for_non_admin(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=_conn())
        response = await async_client.put(f"{_BASE}/{CID}", json=self._body, headers=_USER_HEADERS)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_updates_secret_when_password_provided(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        existing = _conn()
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=existing, update=existing)
        with patch("routes.v1.smtp_connections._write_secret") as mock_write:
            await async_client.put(
                f"{_BASE}/{CID}",
                json={"password": "new-secret"},
                headers=_ADMIN_HEADERS,
            )
        mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_update_secret_when_no_password(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        existing = _conn()
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=existing, update=existing)
        with patch("routes.v1.smtp_connections._write_secret") as mock_write:
            await async_client.put(
                f"{_BASE}/{CID}",
                json={"name": "No Password Update"},
                headers=_ADMIN_HEADERS,
            )
        mock_write.assert_not_called()


# ---------------------------------------------------------------------------
# DELETE /smtp-connections/{id}
# ---------------------------------------------------------------------------


class TestDeleteSmtpConnection:
    @pytest.mark.asyncio
    async def test_returns_204_when_deleted(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=_conn(), delete=True)
        with patch("routes.v1.smtp_connections._delete_secret"):
            response = await async_client.delete(f"{_BASE}/{CID}", headers=_ADMIN_HEADERS)
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_returns_404_when_not_found(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=None)
        response = await async_client.delete(f"{_BASE}/{CID}", headers=_ADMIN_HEADERS)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_409_when_send_lists_exist(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=_conn(), has_active_send_lists=True)
        response = await async_client.delete(f"{_BASE}/{CID}", headers=_ADMIN_HEADERS)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_returns_403_for_non_admin(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=_conn())
        response = await async_client.delete(f"{_BASE}/{CID}", headers=_USER_HEADERS)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_deletes_secret_after_db_delete(self, async_client, dependency_overrides, admin_env):
        from routes.v1.smtp_connections import _get_repo
        dependency_overrides[_get_repo] = lambda: _mock_repo(get_by_id=_conn(), delete=True)
        with patch("routes.v1.smtp_connections._delete_secret") as mock_del:
            await async_client.delete(f"{_BASE}/{CID}", headers=_ADMIN_HEADERS)
        mock_del.assert_called_once()
