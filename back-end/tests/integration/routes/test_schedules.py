"""
Integration tests for the /api/v1/schedules routes.

SchedulesRepository and ProjectsRepository are injected via dependency_overrides.
APScheduler and authorization checks are patched per test.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.authorization import get_projects_repo, get_schedules_repo
from models.schedule import ExecutionStatus, Schedule, ScheduleExecution

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
PID = uuid.uuid4()
SID = uuid.uuid4()
TID = uuid.uuid4()
SCHID = uuid.uuid4()
EXECID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _schedule(
    *,
    id: uuid.UUID | None = None,
    name: str = "Daily Report",
    is_active: bool = True,
    cron_expression: str = "0 9 * * 1",
) -> Schedule:
    return Schedule(
        id=id or SCHID,
        name=name,
        project_id=PID,
        structure_id=SID,
        template_id=TID,
        cron_expression=cron_expression,
        is_active=is_active,
        created_by="user@example.com",
        created_at=NOW,
        updated_at=NOW,
    )


def _execution(*, status: ExecutionStatus = ExecutionStatus.success) -> ScheduleExecution:
    return ScheduleExecution(
        id=EXECID,
        schedule_id=SCHID,
        status=status,
        started_at=NOW,
        completed_at=NOW,
        created_at=NOW,
    )


def _mock_repo(
    *,
    get_all_for_project=None,
    get_by_id=None,
    create=None,
    update=None,
    delete=None,
    get_executions=None,
    create_execution=None,
):
    repo = MagicMock()
    repo.get_all_for_project = AsyncMock(return_value=get_all_for_project or [])
    repo.get_by_id = AsyncMock(return_value=get_by_id)
    repo.create = AsyncMock(return_value=create)
    repo.update = AsyncMock(return_value=update)
    repo.delete = AsyncMock(return_value=delete if delete is not None else True)
    repo.get_executions = AsyncMock(return_value=get_executions or [])
    repo.create_execution = AsyncMock(return_value=create_execution)
    return repo


def _mock_projects_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    return repo


class _NO_AUTH:
    """Patches all authorization checks used by the schedules routes."""
    def __enter__(self):
        self._p1 = patch("routes.v1.schedules.check_project_access", return_value=None, new_callable=AsyncMock)
        self._p2 = patch("routes.v1.schedules.check_project_access_and_not_locked", return_value=None, new_callable=AsyncMock)
        self._p3 = patch("routes.v1.schedules.check_schedule_project_access", return_value=None, new_callable=AsyncMock)
        self._p1.__enter__()
        self._p2.__enter__()
        self._p3.__enter__()
        return self

    def __exit__(self, *args):
        self._p3.__exit__(*args)
        self._p2.__exit__(*args)
        self._p1.__exit__(*args)


def _mock_scheduler():
    scheduler = MagicMock()
    scheduler.remove_job = MagicMock()
    scheduler.add_job = MagicMock()
    return scheduler


# ---------------------------------------------------------------------------
# Unit tests for _parse_cron
# ---------------------------------------------------------------------------


class TestParseCron:
    def test_valid_5_field_expression(self):
        from routes.v1.schedules import _parse_cron
        result = _parse_cron("0 9 * * 1")
        assert result == {
            "minute": "0",
            "hour": "9",
            "day": "*",
            "month": "*",
            "day_of_week": "1",
        }

    def test_raises_for_too_few_fields(self):
        from routes.v1.schedules import _parse_cron
        import pytest
        with pytest.raises(ValueError, match="5 fields"):
            _parse_cron("0 9 * *")

    def test_raises_for_too_many_fields(self):
        from routes.v1.schedules import _parse_cron
        import pytest
        with pytest.raises(ValueError, match="5 fields"):
            _parse_cron("0 9 * * 1 extra")

    def test_strips_leading_trailing_whitespace(self):
        from routes.v1.schedules import _parse_cron
        result = _parse_cron("  */5 * * * *  ")
        assert result["minute"] == "*/5"

    def test_step_expression(self):
        from routes.v1.schedules import _parse_cron
        result = _parse_cron("*/15 * * * *")
        assert result["minute"] == "*/15"

    def test_range_expression(self):
        from routes.v1.schedules import _parse_cron
        result = _parse_cron("0 8-18 * * 1-5")
        assert result["hour"] == "8-18"
        assert result["day_of_week"] == "1-5"


# ---------------------------------------------------------------------------
# Unit tests for _register_job / _remove_job
# ---------------------------------------------------------------------------


class TestRegisterJob:
    def test_registers_cron_job_for_active_schedule(self):
        from routes.v1.schedules import _register_job
        scheduler = _mock_scheduler()
        with patch("routes.v1.schedules._scheduler", scheduler):
            _register_job(_schedule(is_active=True))
        scheduler.add_job.assert_called_once()
        call_kwargs = scheduler.add_job.call_args
        assert call_kwargs[1]["id"] == str(SCHID)

    def test_does_not_add_job_for_inactive_schedule(self):
        from routes.v1.schedules import _register_job
        scheduler = _mock_scheduler()
        with patch("routes.v1.schedules._scheduler", scheduler):
            _register_job(_schedule(is_active=False))
        scheduler.add_job.assert_not_called()

    def test_removes_existing_job_before_registering(self):
        from routes.v1.schedules import _register_job
        scheduler = _mock_scheduler()
        with patch("routes.v1.schedules._scheduler", scheduler):
            _register_job(_schedule(is_active=True))
        scheduler.remove_job.assert_called_once_with(str(SCHID))

    def test_handles_job_lookup_error_on_remove(self):
        from apscheduler.jobstores.base import JobLookupError
        from routes.v1.schedules import _register_job
        scheduler = _mock_scheduler()
        scheduler.remove_job.side_effect = JobLookupError(str(SCHID))
        with patch("routes.v1.schedules._scheduler", scheduler):
            _register_job(_schedule(is_active=True))  # should not raise
        scheduler.add_job.assert_called_once()


class TestRemoveJob:
    def test_removes_job_by_schedule_id(self):
        from routes.v1.schedules import _remove_job
        scheduler = _mock_scheduler()
        with patch("routes.v1.schedules._scheduler", scheduler):
            _remove_job(SCHID)
        scheduler.remove_job.assert_called_once_with(str(SCHID))

    def test_handles_job_lookup_error_silently(self):
        from apscheduler.jobstores.base import JobLookupError
        from routes.v1.schedules import _remove_job
        scheduler = _mock_scheduler()
        scheduler.remove_job.side_effect = JobLookupError(str(SCHID))
        with patch("routes.v1.schedules._scheduler", scheduler):
            _remove_job(SCHID)  # should not raise


# ---------------------------------------------------------------------------
# GET /schedules/
# ---------------------------------------------------------------------------


class TestListSchedules:
    @pytest.mark.asyncio
    async def test_returns_200(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all_for_project=[_schedule()])
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/?project_id={PID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_list_of_schedules(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all_for_project=[_schedule(), _schedule(name="Weekly")])
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/?project_id={PID}")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all_for_project=[])
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/?project_id={PID}")
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_requires_project_id_query_param(self, async_client):
        response = await async_client.get("/api/v1/schedules/")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_all_for_project = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/?project_id={PID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# GET /schedules/{id}
# ---------------------------------------------------------------------------


class TestGetSchedule:
    @pytest.mark.asyncio
    async def test_returns_200_when_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_schedule(id=SCHID))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/{SCHID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_correct_name(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_schedule(id=SCHID, name="Monthly"))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/{SCHID}")
        assert response.json()["name"] == "Monthly"

    @pytest.mark.asyncio
    async def test_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None)
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_422_for_invalid_uuid(self, async_client):
        response = await async_client.get("/api/v1/schedules/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_by_id = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/{SCHID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /schedules/
# ---------------------------------------------------------------------------


class TestCreateSchedule:
    def _valid_body(self) -> dict:
        return {
            "name": "New Schedule",
            "project_id": str(PID),
            "structure_id": str(SID),
            "template_id": str(TID),
            "cron_expression": "0 9 * * 1",
        }

    @pytest.mark.asyncio
    async def test_returns_201(self, async_client, dependency_overrides):
        repo = _mock_repo(create=_schedule())
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        scheduler = _mock_scheduler()
        with _NO_AUTH(), patch("routes.v1.schedules._scheduler", scheduler):
            response = await async_client.post("/api/v1/schedules/", json=self._valid_body())
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_registers_job_after_create(self, async_client, dependency_overrides):
        repo = _mock_repo(create=_schedule(is_active=True))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        scheduler = _mock_scheduler()
        with _NO_AUTH(), patch("routes.v1.schedules._scheduler", scheduler):
            await async_client.post("/api/v1/schedules/", json=self._valid_body())
        scheduler.add_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_422_for_invalid_cron(self, async_client, dependency_overrides):
        body = self._valid_body()
        body["cron_expression"] = "bad cron"
        dependency_overrides[get_schedules_repo] = lambda: _mock_repo()
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.post("/api/v1/schedules/", json=body)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_422_when_name_missing(self, async_client):
        body = self._valid_body()
        del body["name"]
        response = await async_client.post("/api/v1/schedules/", json=body)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.create = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.post("/api/v1/schedules/", json=self._valid_body())
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# PUT /schedules/{id}
# ---------------------------------------------------------------------------


class TestUpdateSchedule:
    @pytest.mark.asyncio
    async def test_returns_200(self, async_client, dependency_overrides):
        updated = _schedule(id=SCHID, name="Updated")
        repo = _mock_repo(get_by_id=updated, update=updated)
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        scheduler = _mock_scheduler()
        with _NO_AUTH(), patch("routes.v1.schedules._scheduler", scheduler):
            response = await async_client.put(f"/api/v1/schedules/{SCHID}", json={"name": "Updated"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_re_registers_job_after_update(self, async_client, dependency_overrides):
        updated = _schedule(id=SCHID, is_active=True)
        repo = _mock_repo(get_by_id=updated, update=updated)
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        scheduler = _mock_scheduler()
        with _NO_AUTH(), patch("routes.v1.schedules._scheduler", scheduler):
            await async_client.put(f"/api/v1/schedules/{SCHID}", json={"is_active": True})
        scheduler.add_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_422_for_invalid_cron(self, async_client, dependency_overrides):
        dependency_overrides[get_schedules_repo] = lambda: _mock_repo()
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.put(
                f"/api/v1/schedules/{SCHID}",
                json={"cron_expression": "bad cron"},
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None, update=None)
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.put(
                f"/api/v1/schedules/{uuid.uuid4()}",
                json={"name": "Ghost"},
            )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_409_on_conflict(self, async_client, dependency_overrides):
        existing = _schedule(id=SCHID)
        repo = _mock_repo(get_by_id=existing, update=None)
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.put(
                f"/api/v1/schedules/{SCHID}",
                json={"name": "Stale", "expected_updated_at": NOW.isoformat()},
            )
        assert response.status_code == 409
        assert "modified by another user" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.update = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.put(
                f"/api/v1/schedules/{SCHID}",
                json={"name": "Broken"},
            )
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# DELETE /schedules/{id}
# ---------------------------------------------------------------------------


class TestDeleteSchedule:
    @pytest.mark.asyncio
    async def test_returns_204(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_schedule(id=SCHID), delete=True)
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        scheduler = _mock_scheduler()
        with _NO_AUTH(), patch("routes.v1.schedules._scheduler", scheduler):
            response = await async_client.delete(f"/api/v1/schedules/{SCHID}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_removes_job_after_delete(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_schedule(id=SCHID), delete=True)
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        scheduler = _mock_scheduler()
        with _NO_AUTH(), patch("routes.v1.schedules._scheduler", scheduler):
            await async_client.delete(f"/api/v1/schedules/{SCHID}")
        scheduler.remove_job.assert_called_once_with(str(SCHID))

    @pytest.mark.asyncio
    async def test_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None, delete=False)
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.delete(f"/api/v1/schedules/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.delete = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.delete(f"/api/v1/schedules/{SCHID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# GET /schedules/{id}/executions
# ---------------------------------------------------------------------------


class TestListExecutions:
    @pytest.mark.asyncio
    async def test_returns_200(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_schedule(id=SCHID), get_executions=[_execution()])
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/{SCHID}/executions")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_list_of_executions(self, async_client, dependency_overrides):
        repo = _mock_repo(
            get_by_id=_schedule(id=SCHID),
            get_executions=[_execution(), _execution(status=ExecutionStatus.failed)],
        )
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/{SCHID}/executions")
        assert len(response.json()) == 2

    @pytest.mark.asyncio
    async def test_passes_limit_and_offset(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_schedule(id=SCHID), get_executions=[])
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            await async_client.get(f"/api/v1/schedules/{SCHID}/executions?limit=10&offset=5")
        repo.get_executions.assert_awaited_once_with(SCHID, limit=10, offset=5)

    @pytest.mark.asyncio
    async def test_returns_422_when_limit_exceeds_max(self, async_client, dependency_overrides):
        dependency_overrides[get_schedules_repo] = lambda: _mock_repo()
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(
                f"/api/v1/schedules/{SCHID}/executions?limit=201"
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_422_when_offset_negative(self, async_client, dependency_overrides):
        dependency_overrides[get_schedules_repo] = lambda: _mock_repo()
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(
                f"/api/v1/schedules/{SCHID}/executions?offset=-1"
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_executions = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/{SCHID}/executions")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /schedules/{id}/trigger
# ---------------------------------------------------------------------------


class TestTriggerSchedule:
    @pytest.mark.asyncio
    async def test_returns_202(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_schedule(id=SCHID))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        scheduler = _mock_scheduler()
        with _NO_AUTH(), patch("routes.v1.schedules._scheduler", scheduler):
            response = await async_client.post(f"/api/v1/schedules/{SCHID}/trigger")
        assert response.status_code == 202

    @pytest.mark.asyncio
    async def test_returns_detail_message(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_schedule(id=SCHID))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        scheduler = _mock_scheduler()
        with _NO_AUTH(), patch("routes.v1.schedules._scheduler", scheduler):
            response = await async_client.post(f"/api/v1/schedules/{SCHID}/trigger")
        assert "triggered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_adds_immediate_job(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_schedule(id=SCHID))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        scheduler = _mock_scheduler()
        with _NO_AUTH(), patch("routes.v1.schedules._scheduler", scheduler):
            await async_client.post(f"/api/v1/schedules/{SCHID}/trigger")
        scheduler.add_job.assert_called_once()
        _, kwargs = scheduler.add_job.call_args
        assert kwargs["id"].startswith("manual_")

    @pytest.mark.asyncio
    async def test_returns_404_when_schedule_not_found(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None)
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.post(f"/api/v1/schedules/{uuid.uuid4()}/trigger")
        assert response.status_code == 404

# ---------------------------------------------------------------------------
# _register_job with invalid cron
# ---------------------------------------------------------------------------


class TestRegisterJobInvalidCron:
    def test_invalid_cron_logs_error_and_does_not_add_job(self):
        from routes.v1.schedules import _register_job
        scheduler = _mock_scheduler()
        bad_schedule = _schedule(is_active=True, cron_expression="not valid at all")
        with patch("routes.v1.schedules._scheduler", scheduler):
            _register_job(bad_schedule)  # should not raise
        scheduler.add_job.assert_not_called()


# ---------------------------------------------------------------------------
# _send_to_one_list
# ---------------------------------------------------------------------------


def _smtp_conn():
    from models.smtp_connection import SmtpConnection
    import uuid
    return SmtpConnection(
        id=uuid.uuid4(),
        name="Test SMTP",
        provider="smtp",
        from_email="noreply@example.com",
        smtp_host="smtp.example.com",
        smtp_port=587,
        username="user",
        secret_scope="scope",
        secret_key="key",
        created_by="admin@example.com",
        created_at=NOW,
        updated_at=NOW,
    )


def _send_list(*, emails=None):
    from models.email_send_list import EmailSendList
    import uuid
    return EmailSendList(
        id=uuid.uuid4(),
        name="Weekly List",
        project_id=PID,
        smtp_connection_id=uuid.uuid4(),
        emails=emails if emails is not None else ["alice@example.com", "bob@example.com"],
        created_by="user@example.com",
        created_at=NOW,
        updated_at=NOW,
    )


class TestSendToOneList:
    @pytest.mark.asyncio
    async def test_sends_html_email_and_returns_success(self):
        from routes.v1.schedules import _send_to_one_list
        provider = MagicMock()
        provider.send_html = AsyncMock()
        with patch("routes.v1.schedules.get_provider", return_value=provider):
            msg, has_error = await _send_to_one_list(_schedule(), _send_list(), _smtp_conn(), "<p>body</p>", None)
        assert has_error is False
        assert "Emails sent" in msg
        provider.send_html.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sends_pdf_attachment_when_pdf_bytes_provided(self):
        from routes.v1.schedules import _send_to_one_list
        provider = MagicMock()
        provider.send_attachment = AsyncMock()
        with patch("routes.v1.schedules.get_provider", return_value=provider):
            msg, has_error = await _send_to_one_list(
                _schedule(), _send_list(), _smtp_conn(), "<p>body</p>", b"%PDF"
            )
        assert has_error is False
        provider.send_attachment.assert_awaited_once()
        assert "Emails sent" in msg

    @pytest.mark.asyncio
    async def test_returns_error_on_send_failure(self):
        from routes.v1.schedules import _send_to_one_list
        provider = MagicMock()
        provider.send_html = AsyncMock(side_effect=Exception("SMTP timeout"))
        with patch("routes.v1.schedules.get_provider", return_value=provider):
            msg, has_error = await _send_to_one_list(_schedule(), _send_list(), _smtp_conn(), "<p>x</p>", None)
        assert has_error is True
        assert "Email failed" in msg


# ---------------------------------------------------------------------------
# _send_to_lists
# ---------------------------------------------------------------------------


class TestSendToLists:
    @pytest.mark.asyncio
    async def test_returns_empty_string_when_no_send_list_ids(self):
        from routes.v1.schedules import _send_to_lists
        schedule = _schedule()  # has no send_list_ids
        send_lists_repo = MagicMock()
        smtp_repo = MagicMock()
        msg, has_failures = await _send_to_lists(schedule, "<p>x</p>", send_lists_repo, smtp_repo)
        assert msg == ""
        assert has_failures is False

    @pytest.mark.asyncio
    async def test_skips_send_list_with_no_emails(self):
        from routes.v1.schedules import _send_to_lists
        sl = _send_list(emails=[])
        schedule = _schedule()
        schedule.send_list_ids = [sl.id]
        send_lists_repo = MagicMock()
        send_lists_repo.get_by_ids = AsyncMock(return_value=[sl])
        smtp_repo = MagicMock()
        _, has_failures = await _send_to_lists(schedule, "<p>x</p>", send_lists_repo, smtp_repo)
        assert has_failures is False

    @pytest.mark.asyncio
    async def test_records_failure_when_smtp_conn_not_found(self):
        from routes.v1.schedules import _send_to_lists
        sl = _send_list()
        schedule = _schedule()
        schedule.send_list_ids = [sl.id]
        send_lists_repo = MagicMock()
        send_lists_repo.get_by_ids = AsyncMock(return_value=[sl])
        smtp_repo = MagicMock()
        smtp_repo.get_by_id = AsyncMock(return_value=None)
        msg, has_failures = await _send_to_lists(schedule, "<p>x</p>", send_lists_repo, smtp_repo)
        assert has_failures is True
        assert "connection not found" in msg

    @pytest.mark.asyncio
    async def test_sends_to_found_smtp_connection(self):
        from routes.v1.schedules import _send_to_lists
        sl = _send_list()
        schedule = _schedule()
        schedule.send_list_ids = [sl.id]
        send_lists_repo = MagicMock()
        send_lists_repo.get_by_ids = AsyncMock(return_value=[sl])
        smtp_repo = MagicMock()
        smtp_repo.get_by_id = AsyncMock(return_value=_smtp_conn())
        provider = MagicMock()
        provider.send_html = AsyncMock()
        with patch("routes.v1.schedules.get_provider", return_value=provider):
            msg, has_failures = await _send_to_lists(schedule, "<p>body</p>", send_lists_repo, smtp_repo)
        assert has_failures is False
        provider.send_html.assert_awaited_once()


# ---------------------------------------------------------------------------
# _execute_report
# ---------------------------------------------------------------------------


class TestExecuteReport:
    @pytest.mark.asyncio
    async def test_email_page_size_sends_html(self):
        from routes.v1.schedules import _execute_report
        from models.template import Template
        email_tmpl = Template(
            id=TID, name="Rpt", structure_id=SID, html_content="",
            page_size="email", template_type="html",
            created_at=NOW, updated_at=NOW,
        )
        repo = MagicMock()
        repo.update_execution = AsyncMock()
        send_lists_repo = MagicMock()
        smtp_repo = MagicMock()

        with (
            patch("routes.v1.schedules.render_report", new=AsyncMock(return_value=("<p>x</p>", email_tmpl))),
            patch("routes.v1.schedules.render_charts_as_svg", return_value="<p>x</p>"),
            patch("routes.v1.schedules.build_html_document", return_value="<html/>"),
            patch("routes.v1.schedules._send_to_lists", new=AsyncMock(return_value=("", False))),
        ):
            await _execute_report(EXECID, _schedule(), repo, send_lists_repo, smtp_repo)

        repo.update_execution.assert_awaited_once()
        args = repo.update_execution.call_args
        assert args[0][1].value == "success"

    @pytest.mark.asyncio
    async def test_pdf_page_size_sends_attachment(self):
        from routes.v1.schedules import _execute_report
        from models.template import Template
        pdf_tmpl = Template(
            id=TID, name="Rpt", structure_id=SID, html_content="",
            page_size="A4", template_type="html",
            created_at=NOW, updated_at=NOW,
        )
        repo = MagicMock()
        repo.update_execution = AsyncMock()

        with (
            patch("routes.v1.schedules.render_report", new=AsyncMock(return_value=("<p>x</p>", pdf_tmpl))),
            patch("routes.v1.schedules.render_report_pdf", new=AsyncMock(return_value=(b"%PDF", pdf_tmpl))),
            patch("routes.v1.schedules._send_to_lists", new=AsyncMock(return_value=("", False))),
        ):
            await _execute_report(EXECID, _schedule(), repo, MagicMock(), MagicMock())

        repo.update_execution.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_marks_execution_failed_when_emails_fail(self):
        from routes.v1.schedules import _execute_report
        from models.template import Template
        email_tmpl = Template(
            id=TID, name="Rpt", structure_id=SID, html_content="",
            page_size="email", template_type="html",
            created_at=NOW, updated_at=NOW,
        )
        repo = MagicMock()
        repo.update_execution = AsyncMock()

        with (
            patch("routes.v1.schedules.render_report", new=AsyncMock(return_value=("", email_tmpl))),
            patch("routes.v1.schedules.render_charts_as_svg", return_value=""),
            patch("routes.v1.schedules.build_html_document", return_value=""),
            patch("routes.v1.schedules._send_to_lists", new=AsyncMock(return_value=("SMTP error", True))),
        ):
            await _execute_report(EXECID, _schedule(), repo, MagicMock(), MagicMock())

        args = repo.update_execution.call_args
        assert args[0][1].value == "failed"


# ---------------------------------------------------------------------------
# _run_scheduled_report
# ---------------------------------------------------------------------------


class TestRunScheduledReport:
    @pytest.mark.asyncio
    async def test_skips_when_schedule_not_found(self):
        from routes.v1.schedules import _run_scheduled_report
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=None)
        mock_repo.create_execution = AsyncMock()
        with patch("routes.v1.schedules.SchedulesRepository", return_value=mock_repo):
            await _run_scheduled_report(SCHID)
        mock_repo.create_execution.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_skips_when_schedule_inactive(self):
        from routes.v1.schedules import _run_scheduled_report
        inactive = _schedule(is_active=False)
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=inactive)
        mock_repo.create_execution = AsyncMock()
        with patch("routes.v1.schedules.SchedulesRepository", return_value=mock_repo):
            await _run_scheduled_report(SCHID)
        mock_repo.create_execution.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_marks_execution_failed_on_timeout(self):
        from routes.v1.schedules import _run_scheduled_report
        import asyncio
        active = _schedule(is_active=True)
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=active)
        mock_repo.create_execution = AsyncMock(return_value=_execution())
        mock_repo.update_execution = AsyncMock()

        with (
            patch("routes.v1.schedules.SchedulesRepository", return_value=mock_repo),
            patch("routes.v1.schedules.EmailSendListsRepository"),
            patch("routes.v1.schedules.SmtpConnectionsRepository"),
            patch("routes.v1.schedules._execute_report", new=AsyncMock(side_effect=asyncio.TimeoutError())),
        ):
            await _run_scheduled_report(SCHID)

        mock_repo.update_execution.assert_awaited_once()
        status_arg = mock_repo.update_execution.call_args[0][1]
        assert status_arg.value == "failed"

    @pytest.mark.asyncio
    async def test_marks_execution_failed_on_exception(self):
        from routes.v1.schedules import _run_scheduled_report
        active = _schedule(is_active=True)
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=active)
        mock_repo.create_execution = AsyncMock(return_value=_execution())
        mock_repo.update_execution = AsyncMock()

        with (
            patch("routes.v1.schedules.SchedulesRepository", return_value=mock_repo),
            patch("routes.v1.schedules.EmailSendListsRepository"),
            patch("routes.v1.schedules.SmtpConnectionsRepository"),
            patch("routes.v1.schedules._execute_report", new=AsyncMock(side_effect=ValueError("boom"))),
        ):
            await _run_scheduled_report(SCHID)

        mock_repo.update_execution.assert_awaited_once()
        status_arg = mock_repo.update_execution.call_args[0][1]
        assert status_arg.value == "failed"

    @pytest.mark.asyncio
    async def test_creates_execution_on_success(self):
        from routes.v1.schedules import _run_scheduled_report
        active = _schedule(is_active=True)
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=active)
        mock_repo.create_execution = AsyncMock(return_value=_execution())
        mock_repo.update_execution = AsyncMock()

        with (
            patch("routes.v1.schedules.SchedulesRepository", return_value=mock_repo),
            patch("routes.v1.schedules.EmailSendListsRepository"),
            patch("routes.v1.schedules.SmtpConnectionsRepository"),
            patch("routes.v1.schedules._execute_report", new=AsyncMock(return_value=None)),
        ):
            await _run_scheduled_report(SCHID)

        mock_repo.create_execution.assert_awaited_once_with(SCHID)


# ---------------------------------------------------------------------------
# GET /schedules/executions
# ---------------------------------------------------------------------------


class TestListAllExecutions:
    @pytest.mark.asyncio
    async def test_returns_200_with_executions(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_all_executions_for_project = AsyncMock(return_value=[_execution()])
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/executions?project_id={PID}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_all_executions_for_project = AsyncMock(return_value=[])
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/executions?project_id={PID}")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_requires_project_id_param(self, async_client):
        response = await async_client.get("/api/v1/schedules/executions")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_all_executions_for_project = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_schedules_repo] = lambda: repo
        dependency_overrides[get_projects_repo] = lambda: _mock_projects_repo()
        with _NO_AUTH():
            response = await async_client.get(f"/api/v1/schedules/executions?project_id={PID}")
        assert response.status_code == 503
