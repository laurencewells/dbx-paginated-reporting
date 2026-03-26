"""
Unit tests for models/schedule.py.

Validates field types, defaults, required fields, and model construction.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models.schedule import (
    ExecutionStatus,
    Schedule,
    ScheduleCreate,
    ScheduleExecution,
    ScheduleUpdate,
)

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
PID = uuid.uuid4()
SID = uuid.uuid4()
TID = uuid.uuid4()
SCHID = uuid.uuid4()
EXECID = uuid.uuid4()


# ---------------------------------------------------------------------------
# ExecutionStatus
# ---------------------------------------------------------------------------


class TestExecutionStatus:
    def test_all_values_defined(self):
        assert set(ExecutionStatus) == {
            ExecutionStatus.pending,
            ExecutionStatus.running,
            ExecutionStatus.success,
            ExecutionStatus.failed,
        }

    def test_values_are_strings(self):
        assert ExecutionStatus.success == "success"
        assert ExecutionStatus.failed == "failed"
        assert ExecutionStatus.running == "running"
        assert ExecutionStatus.pending == "pending"

    def test_is_str_subclass(self):
        assert isinstance(ExecutionStatus.success, str)


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------


class TestSchedule:
    def _make(self, **kwargs) -> Schedule:
        defaults = dict(
            id=SCHID,
            name="Daily Report",
            project_id=PID,
            structure_id=SID,
            template_id=TID,
            cron_expression="0 9 * * 1",
            is_active=True,
            created_by="user@example.com",
            created_at=NOW,
            updated_at=NOW,
        )
        defaults.update(kwargs)
        return Schedule(**defaults)

    def test_valid_construction(self):
        s = self._make()
        assert s.name == "Daily Report"
        assert s.cron_expression == "0 9 * * 1"
        assert s.is_active is True
        assert s.created_by == "user@example.com"

    def test_id_is_uuid(self):
        s = self._make()
        assert isinstance(s.id, uuid.UUID)

    def test_project_id_is_uuid(self):
        s = self._make()
        assert isinstance(s.project_id, uuid.UUID)

    def test_name_is_required(self):
        with pytest.raises(ValidationError):
            Schedule(
                id=SCHID,
                project_id=PID,
                structure_id=SID,
                template_id=TID,
                cron_expression="* * * * *",
                is_active=True,
                created_by="u@x.com",
                created_at=NOW,
                updated_at=NOW,
            )

    def test_is_active_false(self):
        s = self._make(is_active=False)
        assert s.is_active is False


# ---------------------------------------------------------------------------
# ScheduleCreate
# ---------------------------------------------------------------------------


class TestScheduleCreate:
    def _make(self, **kwargs) -> ScheduleCreate:
        defaults = dict(
            name="Weekly Report",
            project_id=PID,
            structure_id=SID,
            template_id=TID,
            cron_expression="0 8 * * 1",
        )
        defaults.update(kwargs)
        return ScheduleCreate(**defaults)

    def test_valid_construction(self):
        sc = self._make()
        assert sc.name == "Weekly Report"
        assert sc.cron_expression == "0 8 * * 1"

    def test_is_active_defaults_to_true(self):
        sc = self._make()
        assert sc.is_active is True

    def test_is_active_can_be_false(self):
        sc = self._make(is_active=False)
        assert sc.is_active is False

    def test_name_is_stripped(self):
        sc = self._make(name="  Weekly Report  ")
        assert sc.name == "Weekly Report"

    def test_cron_expression_is_stripped(self):
        sc = self._make(cron_expression="  0 8 * * 1  ")
        assert sc.cron_expression == "0 8 * * 1"

    def test_name_is_required(self):
        with pytest.raises(ValidationError):
            ScheduleCreate(
                project_id=PID,
                structure_id=SID,
                template_id=TID,
                cron_expression="* * * * *",
            )

    def test_project_id_is_required(self):
        with pytest.raises(ValidationError):
            ScheduleCreate(
                name="x",
                structure_id=SID,
                template_id=TID,
                cron_expression="* * * * *",
            )

    def test_cron_expression_is_required(self):
        with pytest.raises(ValidationError):
            ScheduleCreate(
                name="x",
                project_id=PID,
                structure_id=SID,
                template_id=TID,
            )


# ---------------------------------------------------------------------------
# ScheduleUpdate
# ---------------------------------------------------------------------------


class TestScheduleUpdate:
    def test_all_fields_optional(self):
        su = ScheduleUpdate()
        assert su.name is None
        assert su.cron_expression is None
        assert su.is_active is None
        assert su.expected_updated_at is None

    def test_partial_update_name_only(self):
        su = ScheduleUpdate(name="New Name")
        assert su.name == "New Name"
        assert su.cron_expression is None

    def test_partial_update_cron_only(self):
        su = ScheduleUpdate(cron_expression="*/5 * * * *")
        assert su.cron_expression == "*/5 * * * *"

    def test_partial_update_is_active_only(self):
        su = ScheduleUpdate(is_active=False)
        assert su.is_active is False

    def test_name_is_stripped(self):
        su = ScheduleUpdate(name="  Trimmed  ")
        assert su.name == "Trimmed"

    def test_expected_updated_at_accepted(self):
        su = ScheduleUpdate(expected_updated_at=NOW)
        assert su.expected_updated_at == NOW


# ---------------------------------------------------------------------------
# ScheduleExecution
# ---------------------------------------------------------------------------


class TestScheduleExecution:
    def _make(self, **kwargs) -> ScheduleExecution:
        defaults = dict(
            id=EXECID,
            schedule_id=SCHID,
            status=ExecutionStatus.running,
            created_at=NOW,
        )
        defaults.update(kwargs)
        return ScheduleExecution(**defaults)

    def test_valid_construction(self):
        e = self._make()
        assert e.status == ExecutionStatus.running
        assert e.started_at is None
        assert e.completed_at is None
        assert e.error_message is None

    def test_optional_fields_accepted(self):
        e = self._make(
            status=ExecutionStatus.success,
            started_at=NOW,
            completed_at=NOW,
            error_message=None,
        )
        assert e.status == ExecutionStatus.success
        assert e.started_at == NOW
        assert e.completed_at == NOW

    def test_failed_status_with_error_message(self):
        e = self._make(status=ExecutionStatus.failed, error_message="timeout")
        assert e.status == ExecutionStatus.failed
        assert e.error_message == "timeout"

    def test_id_is_uuid(self):
        e = self._make()
        assert isinstance(e.id, uuid.UUID)

    def test_schedule_id_is_uuid(self):
        e = self._make()
        assert isinstance(e.schedule_id, uuid.UUID)

    def test_invalid_status_raises(self):
        with pytest.raises(ValidationError):
            self._make(status="unknown_status")
