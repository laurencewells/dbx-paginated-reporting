"""
Unit tests for SchedulesRepository.

The LakebaseConnector is fully mocked; no DB connection is made.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.schedule import ExecutionStatus, Schedule, ScheduleCreate, ScheduleExecution, ScheduleUpdate
from repositories.schedules import SchedulesRepository

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
SCHID = uuid.uuid4()
EXECID = uuid.uuid4()
PID = uuid.uuid4()
SID = uuid.uuid4()
TID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _schedule_row(
    *,
    id=None,
    name: str = "Daily Report",
    project_id=None,
    structure_id=None,
    template_id=None,
    cron_expression: str = "0 9 * * 1",
    is_active: bool = True,
    created_by: str = "user@example.com",
):
    return (
        str(id or SCHID),
        name,
        str(project_id or PID),
        str(structure_id or SID),
        str(template_id or TID),
        cron_expression,
        is_active,
        created_by,
        NOW,
        NOW,
    )


def _execution_row(
    *,
    id=None,
    schedule_id=None,
    status: str = "running",
    started_at=None,
    completed_at=None,
    error_message=None,
):
    return (
        str(id or EXECID),
        str(schedule_id or SCHID),
        status,
        started_at,
        completed_at,
        error_message,
        NOW,
    )


def _make_result(rows=None, *, rowcount: int = 1):
    result = MagicMock()
    _rows = rows if rows is not None else []
    result.fetchall.return_value = _rows
    result.fetchone.return_value = _rows[0] if _rows else None
    result.rowcount = rowcount
    return result


def _make_repo(query_result=None) -> tuple[SchedulesRepository, MagicMock]:
    connector = MagicMock()
    connector.execute_query = AsyncMock(return_value=query_result or _make_result())
    repo = SchedulesRepository(connector=connector)
    return repo, connector


# ---------------------------------------------------------------------------
# _require_connector
# ---------------------------------------------------------------------------


class TestRequireConnector:
    def test_raises_runtime_error_when_no_connector(self):
        repo = SchedulesRepository(connector=None)
        with pytest.raises(RuntimeError, match="Lakebase is not available"):
            repo._require_connector()

    def test_returns_connector_when_present(self):
        connector = MagicMock()
        repo = SchedulesRepository(connector=connector)
        assert repo._require_connector() is connector


# ---------------------------------------------------------------------------
# get_all_for_project
# ---------------------------------------------------------------------------


class TestGetAllForProject:
    @pytest.mark.asyncio
    async def test_returns_list_of_schedules(self):
        rows = [_schedule_row(), _schedule_row(name="Second")]
        repo, _ = _make_repo(_make_result(rows))
        result = await repo.get_all_for_project(PID)
        assert len(result) == 2
        assert all(isinstance(s, Schedule) for s in result)

    @pytest.mark.asyncio
    async def test_returns_empty_list(self):
        repo, _ = _make_repo(_make_result([]))
        result = await repo.get_all_for_project(PID)
        assert result == []

    @pytest.mark.asyncio
    async def test_passes_project_id_param(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        await repo.get_all_for_project(PID)
        params = connector.execute_query.call_args[0][1]
        assert params["pid"] == str(PID)


# ---------------------------------------------------------------------------
# get_all_active
# ---------------------------------------------------------------------------


class TestGetAllActive:
    @pytest.mark.asyncio
    async def test_returns_active_schedules(self):
        rows = [_schedule_row(is_active=True)]
        repo, _ = _make_repo(_make_result(rows))
        result = await repo.get_all_active()
        assert len(result) == 1
        assert result[0].is_active is True

    @pytest.mark.asyncio
    async def test_query_filters_active(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        await repo.get_all_active()
        sql = connector.execute_query.call_args[0][0]
        assert "is_active" in sql


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


class TestGetById:
    @pytest.mark.asyncio
    async def test_returns_schedule_when_found(self):
        repo, _ = _make_repo(_make_result([_schedule_row(id=SCHID)]))
        result = await repo.get_by_id(SCHID)
        assert isinstance(result, Schedule)
        assert str(result.id) == str(SCHID)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        repo, _ = _make_repo(_make_result([]))
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_passes_id_param(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        await repo.get_by_id(SCHID)
        params = connector.execute_query.call_args[0][1]
        assert params["id"] == str(SCHID)


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


class TestCreate:
    @pytest.mark.asyncio
    async def test_returns_schedule(self):
        repo, _ = _make_repo(_make_result([_schedule_row()]))
        data = ScheduleCreate(
            name="New Schedule",
            project_id=PID,
            structure_id=SID,
            template_id=TID,
            cron_expression="0 9 * * 1",
        )
        result = await repo.create(data, "creator@example.com")
        assert isinstance(result, Schedule)

    @pytest.mark.asyncio
    async def test_passes_correct_params(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        data = ScheduleCreate(
            name="New Schedule",
            project_id=PID,
            structure_id=SID,
            template_id=TID,
            cron_expression="0 9 * * 1",
            is_active=False,
        )
        await repo.create(data, "creator@example.com")
        params = connector.execute_query.call_args[0][1]
        assert params["name"] == "New Schedule"
        assert params["project_id"] == str(PID)
        assert params["structure_id"] == str(SID)
        assert params["template_id"] == str(TID)
        assert params["cron_expression"] == "0 9 * * 1"
        assert params["is_active"] is False
        assert params["created_by"] == "creator@example.com"


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


class TestUpdate:
    @pytest.mark.asyncio
    async def test_returns_updated_schedule(self):
        row = _schedule_row(name="Updated Name")
        repo, _ = _make_repo(_make_result([row]))
        data = ScheduleUpdate(name="Updated Name")
        result = await repo.update(SCHID, data)
        assert isinstance(result, Schedule)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        repo, _ = _make_repo(_make_result([]))
        data = ScheduleUpdate(name="Ghost")
        result = await repo.update(uuid.uuid4(), data)
        assert result is None

    @pytest.mark.asyncio
    async def test_empty_update_falls_back_to_get_by_id(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        data = ScheduleUpdate()  # all None
        await repo.update(SCHID, data)
        connector.execute_query.assert_awaited_once()
        sql = connector.execute_query.call_args[0][0]
        assert "SELECT" in sql

    @pytest.mark.asyncio
    async def test_update_name_only_includes_name_set(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        await repo.update(SCHID, ScheduleUpdate(name="New Name"))
        sql = connector.execute_query.call_args[0][0]
        assert "name = :name" in sql
        assert "cron_expression = :cron_expression" not in sql

    @pytest.mark.asyncio
    async def test_update_cron_expression(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        await repo.update(SCHID, ScheduleUpdate(cron_expression="*/5 * * * *"))
        params = connector.execute_query.call_args[0][1]
        assert params["cron_expression"] == "*/5 * * * *"

    @pytest.mark.asyncio
    async def test_update_is_active(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        await repo.update(SCHID, ScheduleUpdate(is_active=False))
        sql = connector.execute_query.call_args[0][0]
        assert "is_active = :is_active" in sql

    @pytest.mark.asyncio
    async def test_expected_updated_at_adds_where_clause(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        await repo.update(SCHID, ScheduleUpdate(name="x", expected_updated_at=NOW))
        sql = connector.execute_query.call_args[0][0]
        assert "updated_at = :expected_updated_at" in sql
        params = connector.execute_query.call_args[0][1]
        assert params["expected_updated_at"] == NOW

    @pytest.mark.asyncio
    async def test_no_expected_updated_at_omits_clause(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        await repo.update(SCHID, ScheduleUpdate(name="x"))
        sql = connector.execute_query.call_args[0][0]
        assert "expected_updated_at" not in sql

    @pytest.mark.asyncio
    async def test_always_sets_updated_at_to_now(self):
        repo, connector = _make_repo(_make_result([_schedule_row()]))
        await repo.update(SCHID, ScheduleUpdate(name="x"))
        sql = connector.execute_query.call_args[0][0]
        assert "updated_at = NOW()" in sql


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    @pytest.mark.asyncio
    async def test_returns_true_when_deleted(self):
        repo, _ = _make_repo(_make_result(rowcount=1))
        result = await repo.delete(SCHID)
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self):
        repo, _ = _make_repo(_make_result(rowcount=0))
        result = await repo.delete(uuid.uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_passes_id_param(self):
        repo, connector = _make_repo(_make_result(rowcount=1))
        await repo.delete(SCHID)
        params = connector.execute_query.call_args[0][1]
        assert params["id"] == str(SCHID)


# ---------------------------------------------------------------------------
# get_executions
# ---------------------------------------------------------------------------


class TestGetExecutions:
    @pytest.mark.asyncio
    async def test_returns_list_of_executions(self):
        rows = [_execution_row(), _execution_row(status="success")]
        repo, _ = _make_repo(_make_result(rows))
        result = await repo.get_executions(SCHID)
        assert len(result) == 2
        assert all(isinstance(e, ScheduleExecution) for e in result)

    @pytest.mark.asyncio
    async def test_returns_empty_list(self):
        repo, _ = _make_repo(_make_result([]))
        result = await repo.get_executions(SCHID)
        assert result == []

    @pytest.mark.asyncio
    async def test_passes_limit_and_offset(self):
        repo, connector = _make_repo(_make_result([]))
        await repo.get_executions(SCHID, limit=10, offset=20)
        params = connector.execute_query.call_args[0][1]
        assert params["lim"] == 10
        assert params["off"] == 20

    @pytest.mark.asyncio
    async def test_default_limit_is_50(self):
        repo, connector = _make_repo(_make_result([]))
        await repo.get_executions(SCHID)
        params = connector.execute_query.call_args[0][1]
        assert params["lim"] == 50


# ---------------------------------------------------------------------------
# create_execution
# ---------------------------------------------------------------------------


class TestCreateExecution:
    @pytest.mark.asyncio
    async def test_returns_schedule_execution(self):
        repo, _ = _make_repo(_make_result([_execution_row()]))
        result = await repo.create_execution(SCHID)
        assert isinstance(result, ScheduleExecution)
        assert result.status == ExecutionStatus.running

    @pytest.mark.asyncio
    async def test_passes_schedule_id(self):
        repo, connector = _make_repo(_make_result([_execution_row()]))
        await repo.create_execution(SCHID)
        params = connector.execute_query.call_args[0][1]
        assert params["sid"] == str(SCHID)


# ---------------------------------------------------------------------------
# update_execution
# ---------------------------------------------------------------------------


class TestUpdateExecution:
    @pytest.mark.asyncio
    async def test_passes_status_and_error_message(self):
        repo, connector = _make_repo(_make_result())
        await repo.update_execution(EXECID, ExecutionStatus.failed, error_message="oops")
        params = connector.execute_query.call_args[0][1]
        assert params["status"] == "failed"
        assert params["error_message"] == "oops"
        assert params["id"] == str(EXECID)

    @pytest.mark.asyncio
    async def test_passes_none_error_message_when_success(self):
        repo, connector = _make_repo(_make_result())
        await repo.update_execution(EXECID, ExecutionStatus.success)
        params = connector.execute_query.call_args[0][1]
        assert params["status"] == "success"
        assert params["error_message"] is None

    @pytest.mark.asyncio
    async def test_sets_completed_at(self):
        repo, connector = _make_repo(_make_result())
        await repo.update_execution(EXECID, ExecutionStatus.success)
        sql = connector.execute_query.call_args[0][0]
        assert "completed_at = NOW()" in sql


# ---------------------------------------------------------------------------
# Row mappers
# ---------------------------------------------------------------------------


class TestRowToSchedule:
    def test_returns_schedule(self):
        row = _schedule_row()
        s = SchedulesRepository._row_to_schedule(row)
        assert isinstance(s, Schedule)
        assert s.name == "Daily Report"
        assert s.cron_expression == "0 9 * * 1"
        assert s.is_active is True
        assert s.created_by == "user@example.com"


class TestRowToExecution:
    def test_returns_execution_with_running_status(self):
        row = _execution_row(status="running")
        e = SchedulesRepository._row_to_execution(row)
        assert isinstance(e, ScheduleExecution)
        assert e.status == ExecutionStatus.running

    def test_returns_execution_with_optional_fields_none(self):
        row = _execution_row()
        e = SchedulesRepository._row_to_execution(row)
        assert e.started_at is None
        assert e.completed_at is None
        assert e.error_message is None

    def test_returns_execution_with_error_message(self):
        row = _execution_row(status="failed", error_message="timeout")
        e = SchedulesRepository._row_to_execution(row)
        assert e.status == ExecutionStatus.failed
        assert e.error_message == "timeout"
