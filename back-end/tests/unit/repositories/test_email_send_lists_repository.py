"""
Unit tests for EmailSendListsRepository.

LakebaseConnector is fully mocked; no DB connection is made.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.email_send_list import EmailSendList, EmailSendListCreate, EmailSendListUpdate
from repositories.email_send_lists import EmailSendListsRepository

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
PID = uuid.uuid4()
CID = uuid.uuid4()
SLID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _send_list_row(
    *,
    id=None,
    name: str = "Exec List",
    project_id=None,
    smtp_connection_id=None,
    emails=None,
    created_by: str = "admin@example.com",
):
    emails_val = emails if emails is not None else ["alice@example.com"]
    return (
        str(id or SLID),
        name,
        str(project_id or PID),
        str(smtp_connection_id or CID),
        emails_val,  # list (as returned by psycopg)
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
    return result


def _repo() -> tuple[EmailSendListsRepository, MagicMock]:
    mock = MagicMock()
    mock.execute_query = AsyncMock()
    return EmailSendListsRepository(connector=mock), mock


# ---------------------------------------------------------------------------
# get_all_for_project
# ---------------------------------------------------------------------------


class TestGetAllForProject:
    @pytest.mark.asyncio
    async def test_returns_empty_list(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        result = await repo.get_all_for_project(PID)
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_model_list(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_send_list_row(), _send_list_row(name="B")])
        result = await repo.get_all_for_project(PID)
        assert len(result) == 2
        assert isinstance(result[0], EmailSendList)

    @pytest.mark.asyncio
    async def test_filters_by_project_id(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        await repo.get_all_for_project(PID)
        params = mock.execute_query.call_args[0][1]
        assert params["pid"] == str(PID)


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


class TestGetById:
    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        result = await repo.get_by_id(SLID)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_model_when_found(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_send_list_row()])
        result = await repo.get_by_id(SLID)
        assert isinstance(result, EmailSendList)
        assert result.id == SLID

    @pytest.mark.asyncio
    async def test_passes_id_as_param(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        await repo.get_by_id(SLID)
        params = mock.execute_query.call_args[0][1]
        assert params["id"] == str(SLID)


# ---------------------------------------------------------------------------
# get_by_ids
# ---------------------------------------------------------------------------


class TestGetByIds:
    @pytest.mark.asyncio
    async def test_returns_empty_list_for_empty_input(self):
        repo, mock = _repo()
        result = await repo.get_by_ids([])
        assert result == []
        mock.execute_query.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_models_for_multiple_ids(self):
        id1, id2 = uuid.uuid4(), uuid.uuid4()
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([
            _send_list_row(id=id1),
            _send_list_row(id=id2, name="B"),
        ])
        result = await repo.get_by_ids([id1, id2])
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_generates_correct_placeholders(self):
        id1, id2 = uuid.uuid4(), uuid.uuid4()
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        await repo.get_by_ids([id1, id2])
        sql = mock.execute_query.call_args[0][0]
        assert ":id_0" in sql
        assert ":id_1" in sql


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


class TestCreate:
    @pytest.mark.asyncio
    async def test_returns_created_model(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_send_list_row()])
        data = EmailSendListCreate(
            name="Exec List",
            project_id=PID,
            smtp_connection_id=CID,
            emails=["alice@example.com"],
        )
        result = await repo.create(data, "admin@example.com")
        assert isinstance(result, EmailSendList)

    @pytest.mark.asyncio
    async def test_serialises_emails_as_json(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_send_list_row()])
        data = EmailSendListCreate(
            name="X", project_id=PID, smtp_connection_id=CID,
            emails=["alice@example.com", "bob@example.com"],
        )
        await repo.create(data, "admin@example.com")
        params = mock.execute_query.call_args[0][1]
        emails_param = params["emails"]
        parsed = json.loads(emails_param)
        assert "alice@example.com" in parsed


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


class TestUpdate:
    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([])
        result = await repo.update(SLID, EmailSendListUpdate(name="X"))
        assert result is None

    @pytest.mark.asyncio
    async def test_no_op_when_no_fields_set(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_send_list_row()])
        result = await repo.update(SLID, EmailSendListUpdate())
        sql = mock.execute_query.call_args[0][0]
        assert "SELECT" in sql
        assert isinstance(result, EmailSendList)

    @pytest.mark.asyncio
    async def test_partial_update_includes_updated_at(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_send_list_row()])
        await repo.update(SLID, EmailSendListUpdate(name="New Name"))
        sql = mock.execute_query.call_args[0][0]
        assert "updated_at" in sql

    @pytest.mark.asyncio
    async def test_emails_serialised_as_jsonb(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result([_send_list_row()])
        await repo.update(SLID, EmailSendListUpdate(emails=["new@example.com"]))
        sql = mock.execute_query.call_args[0][0]
        assert "jsonb" in sql


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    @pytest.mark.asyncio
    async def test_returns_true_when_deleted(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result(rowcount=1)
        assert await repo.delete(SLID) is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self):
        repo, mock = _repo()
        mock.execute_query.return_value = _make_result(rowcount=0)
        assert await repo.delete(SLID) is False


# ---------------------------------------------------------------------------
# _row_to_model — email parsing
# ---------------------------------------------------------------------------


class TestRowToModel:
    def test_parses_list_emails(self):
        row = _send_list_row(emails=["alice@example.com", "bob@example.com"])
        model = EmailSendListsRepository._row_to_model(row)
        assert model.emails == ["alice@example.com", "bob@example.com"]

    def test_parses_json_string_emails(self):
        row = list(_send_list_row())
        row[4] = json.dumps(["charlie@example.com"])
        model = EmailSendListsRepository._row_to_model(tuple(row))
        assert "charlie@example.com" in model.emails

    def test_handles_none_emails(self):
        row = list(_send_list_row())
        row[4] = None
        model = EmailSendListsRepository._row_to_model(tuple(row))
        assert model.emails == []


# ---------------------------------------------------------------------------
# _require_connector
# ---------------------------------------------------------------------------


class TestRequireConnector:
    @pytest.mark.asyncio
    async def test_raises_when_connector_is_none(self):
        repo = EmailSendListsRepository(connector=None)
        with pytest.raises(RuntimeError, match="Lakebase is not available"):
            await repo.get_all_for_project(PID)
