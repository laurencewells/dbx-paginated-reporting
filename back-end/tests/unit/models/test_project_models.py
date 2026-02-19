"""
Unit tests for Project domain models.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models.project import Project, ProjectCreate, ProjectUpdate, ProjectShare, ProjectShareCreate

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


class TestProject:
    def _make(self, **kwargs) -> Project:
        defaults = dict(
            id=uuid.uuid4(),
            name="My Project",
            user_email="owner@example.com",
            is_locked=False,
            is_global=False,
            created_at=NOW,
            updated_at=NOW,
        )
        defaults.update(kwargs)
        return Project(**defaults)

    def test_valid_project(self):
        p = self._make()
        assert isinstance(p.id, uuid.UUID)
        assert p.name == "My Project"

    def test_is_locked_defaults_to_false(self):
        p = self._make()
        assert p.is_locked is False

    def test_is_global_defaults_to_false(self):
        p = self._make()
        assert p.is_global is False

    def test_id_is_required(self):
        with pytest.raises(ValidationError):
            Project(name="P", user_email="a@b.com", created_at=NOW, updated_at=NOW)  # type: ignore[call-arg]

    def test_name_is_required(self):
        with pytest.raises(ValidationError):
            Project(id=uuid.uuid4(), user_email="a@b.com", created_at=NOW, updated_at=NOW)  # type: ignore[call-arg]

    def test_user_email_is_required(self):
        with pytest.raises(ValidationError):
            Project(id=uuid.uuid4(), name="P", created_at=NOW, updated_at=NOW)  # type: ignore[call-arg]

    def test_str_strip_whitespace(self):
        p = self._make(name="  padded  ")
        assert p.name == "padded"

    def test_is_locked_true(self):
        p = self._make(is_locked=True)
        assert p.is_locked is True

    def test_is_global_true(self):
        p = self._make(is_global=True)
        assert p.is_global is True


# ---------------------------------------------------------------------------
# ProjectCreate
# ---------------------------------------------------------------------------


class TestProjectCreate:
    def test_valid_create(self):
        pc = ProjectCreate(name="New Project")
        assert pc.name == "New Project"

    def test_name_is_required(self):
        with pytest.raises(ValidationError):
            ProjectCreate()  # type: ignore[call-arg]

    def test_str_strip_whitespace(self):
        pc = ProjectCreate(name="  trimmed  ")
        assert pc.name == "trimmed"


# ---------------------------------------------------------------------------
# ProjectUpdate
# ---------------------------------------------------------------------------


class TestProjectUpdate:
    def test_all_fields_optional(self):
        pu = ProjectUpdate()
        assert pu.name is None
        assert pu.is_locked is None
        assert pu.is_global is None

    def test_can_set_name_only(self):
        pu = ProjectUpdate(name="Renamed")
        assert pu.name == "Renamed"
        assert pu.is_locked is None

    def test_can_set_is_locked_only(self):
        pu = ProjectUpdate(is_locked=True)
        assert pu.is_locked is True
        assert pu.name is None

    def test_can_set_is_global_only(self):
        pu = ProjectUpdate(is_global=True)
        assert pu.is_global is True

    def test_can_set_all_fields(self):
        pu = ProjectUpdate(name="X", is_locked=True, is_global=False)
        assert pu.name == "X"
        assert pu.is_locked is True
        assert pu.is_global is False


# ---------------------------------------------------------------------------
# ProjectShare
# ---------------------------------------------------------------------------


class TestProjectShare:
    def _make(self, **kwargs) -> ProjectShare:
        defaults = dict(
            id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            shared_with_email="other@example.com",
            shared_by_email="owner@example.com",
            created_at=NOW,
        )
        defaults.update(kwargs)
        return ProjectShare(**defaults)

    def test_valid_share(self):
        s = self._make()
        assert isinstance(s.id, uuid.UUID)
        assert isinstance(s.project_id, uuid.UUID)

    def test_id_is_required(self):
        with pytest.raises(ValidationError):
            ProjectShare(
                project_id=uuid.uuid4(),
                shared_with_email="a@b.com",
                shared_by_email="c@d.com",
                created_at=NOW,
            )  # type: ignore[call-arg]

    def test_project_id_is_required(self):
        with pytest.raises(ValidationError):
            ProjectShare(
                id=uuid.uuid4(),
                shared_with_email="a@b.com",
                shared_by_email="c@d.com",
                created_at=NOW,
            )  # type: ignore[call-arg]

    def test_emails_stored_correctly(self):
        s = self._make(shared_with_email="collab@example.com", shared_by_email="boss@example.com")
        assert s.shared_with_email == "collab@example.com"
        assert s.shared_by_email == "boss@example.com"


# ---------------------------------------------------------------------------
# ProjectShareCreate
# ---------------------------------------------------------------------------


class TestProjectShareCreate:
    def test_valid_share_create(self):
        psc = ProjectShareCreate(shared_with_email="collab@example.com")
        assert psc.shared_with_email == "collab@example.com"

    def test_invalid_email_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ProjectShareCreate(shared_with_email="not-an-email")

    def test_email_is_required(self):
        with pytest.raises(ValidationError):
            ProjectShareCreate()  # type: ignore[call-arg]
