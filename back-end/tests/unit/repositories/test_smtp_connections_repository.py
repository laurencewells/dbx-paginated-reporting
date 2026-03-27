"""
Unit tests for SmtpConnectionsRepository.

LakebaseConnector is fully mocked; no DB connection is made.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.smtp_connection import SmtpConnection, SmtpConnectionCreate, SmtpConnectionUpdate
from repositories.smtp_connections import SmtpConnectionsRepository

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
CID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _conn_row(
    *,
    id=None,
    name: str = "My SMTP",
    provider: str = "gsuite",
    from_email: str = "sender@example.com",
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    username: str = "sender@example.com",
    secret_scope: str = "paginated-reports-smtp",
    secret_key: str = "smtp_abc",
    created_by: str = "admin@example.com",
):
    return (
        str(id or CID),
        name,
        provider,
        from_email,
        smtp_host,
        smtp_port,
        username,
        secret_scope,
        secret_key,
        created_by,
        NOW,
        NOW,
    )


def _make_result(rows=None, *, rowcount: int = 1):
    result = MagicMock()
    _rows = rows if rows is not None else []
    result.fetchall.return_value = _rows
    result.fetchone.return_value = _rows[0] if _rows else None
    result.rowcount = rowcount
    result.scalar.return_value = len(_rows) if _rows is not None else 0
    return result


def _repo(connector=None) -> tuple[SmtpConnectionsRepository, MagicMock]:
    mock = MagicMock()
    mock.execute_query = AsyncMock()
    repo = SmtpConnectionsRepository(connector=mock)
    return repo, mock


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------


class TestGetAll:
    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_rows(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        result = await repo.get_all()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_model_list(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_conn_row(), _conn_row(name="B")])
        result = await repo.get_all()
        assert len(result) == 2
        assert isinstance(result[0], SmtpConnection)

    @pytest.mark.asyncio
    async def test_query_orders_by_name(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        await repo.get_all()
        sql = mock.execute_query.call_args[0][0]
        assert "ORDER BY name" in sql


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


class TestGetById:
    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        result = await repo.get_by_id(CID)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_model_when_found(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_conn_row()])
        result = await repo.get_by_id(CID)
        assert isinstance(result, SmtpConnection)
        assert result.id == CID

    @pytest.mark.asyncio
    async def test_passes_id_as_param(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        await repo.get_by_id(CID)
        params = mock.execute_query.call_args[0][1]
        assert params["id"] == str(CID)


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


class TestCreate:
    @pytest.mark.asyncio
    async def test_returns_created_model(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_conn_row()])
        data = SmtpConnectionCreate(
            name="My SMTP",
            provider="gsuite",
            from_email="sender@example.com",
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="sender@example.com",
            password="secret",
        )
        result = await repo.create(
            data, "admin@example.com",
            secret_scope="paginated-reports-smtp",
            secret_key="smtp_abc",
        )
        assert isinstance(result, SmtpConnection)
        assert result.name == "My SMTP"

    @pytest.mark.asyncio
    async def test_uses_provided_connection_id(self):
        repo, mock = _repo()
        fixed_id = uuid.uuid4()
        mock.execute_query.return_value = _make_result([_conn_row(id=fixed_id)])
        data = SmtpConnectionCreate(
            name="X", provider="gsuite", from_email="a@b.com",
            smtp_host="smtp.example.com", username="u", password="p",
        )
        await repo.create(data, "user@example.com", secret_scope="s", secret_key="k", connection_id=fixed_id)
        params = mock.execute_query.call_args[0][1]
        assert params["id"] == str(fixed_id)


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


class TestUpdate:
    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        result = await repo.update(CID, SmtpConnectionUpdate(name="X"))
        assert result is None

    @pytest.mark.asyncio
    async def test_no_op_when_no_fields_set(self):
        """With no fields, it should call get_by_id instead of running an UPDATE."""
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_conn_row()])
        result = await repo.update(CID, SmtpConnectionUpdate())
        # get_by_id was called (SELECT, not UPDATE)
        sql = mock.execute_query.call_args[0][0]
        assert "SELECT" in sql
        assert isinstance(result, SmtpConnection)

    @pytest.mark.asyncio
    async def test_includes_updated_at_in_set_clause(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_conn_row()])
        await repo.update(CID, SmtpConnectionUpdate(name="New Name"))
        sql = mock.execute_query.call_args[0][0]
        assert "updated_at" in sql

    @pytest.mark.asyncio
    async def test_partial_update_only_sets_provided_fields(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_conn_row()])
        await repo.update(CID, SmtpConnectionUpdate(smtp_port=465))
        params = mock.execute_query.call_args[0][1]
        assert "smtp_port" in params
        assert "name" not in params


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    @pytest.mark.asyncio
    async def test_returns_true_when_deleted(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result(rowcount=1)
        result = await repo.delete(CID)
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result(rowcount=0)
        result = await repo.delete(CID)
        assert result is False


# ---------------------------------------------------------------------------
# has_active_send_lists
# ---------------------------------------------------------------------------


class TestHasActiveSendLists:
    @pytest.mark.asyncio
    async def test_returns_true_when_count_positive(self):
        repo, mock = _repo()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 3
        mock.execute_query.return_value = result_mock
        assert await repo.has_active_send_lists(CID) is True

    @pytest.mark.asyncio
    async def test_returns_false_when_count_zero(self):
        repo, mock = _repo()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 0
        mock.execute_query.return_value = result_mock
        assert await repo.has_active_send_lists(CID) is False

    @pytest.mark.asyncio
    async def test_returns_false_when_count_is_none(self):
        repo, mock = _repo()
        result_mock = MagicMock()
        result_mock.scalar.return_value = None
        mock.execute_query.return_value = result_mock
        assert await repo.has_active_send_lists(CID) is False


# ---------------------------------------------------------------------------
# _require_connector
# ---------------------------------------------------------------------------


class TestRequireConnector:
    @pytest.mark.asyncio
    async def test_raises_when_connector_is_none(self):
        repo = SmtpConnectionsRepository(connector=None)
        with pytest.raises(RuntimeError, match="Lakebase is not available"):
            await repo.get_all()
