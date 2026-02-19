"""
Unit tests for common/authorization.py.

All repository calls are mocked — no DB or network calls are made.
Repos are passed directly as arguments (no patching of constructors needed).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from common.authorization import (
    check_project_access,
    check_project_access_and_not_locked,
    check_project_not_locked,
    check_structure_project_access,
    check_structure_project_not_locked,
    check_structure_read_access,
    check_template_project_access,
    check_template_project_not_locked,
    check_template_read_access,
    get_user_email,
)
from models.project import Project
from models.structure import Structure, StructureTable
from models.template import Template

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
PID = uuid.uuid4()
SID = uuid.uuid4()
TID = uuid.uuid4()

OWNER_EMAIL = "owner@example.com"
OTHER_EMAIL = "other@example.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _project(*, is_locked: bool = False, is_global: bool = False) -> Project:
    return Project(
        id=PID,
        name="Test",
        user_email=OWNER_EMAIL,
        is_locked=is_locked,
        is_global=is_global,
        created_at=NOW,
        updated_at=NOW,
    )


def _structure() -> Structure:
    return Structure(
        id=SID,
        name="Test",
        project_id=PID,
        fields=[],
        tables=[StructureTable(full_name="cat.sch.tbl", alias="tbl")],
        relationships=[],
        selected_columns=[],
        sql_query=None,
        created_at=NOW,
        updated_at=NOW,
    )


def _template() -> Template:
    return Template(
        id=TID,
        name="Test",
        structure_id=SID,
        html_content="<p>{{name}}</p>",
        created_at=NOW,
        updated_at=NOW,
    )


def _mock_request(*, email: str | None = None) -> MagicMock:
    request = MagicMock()
    request.headers = {"X-Forwarded-Email": email} if email else {}
    return request


def _proj_repo(**kwargs) -> MagicMock:
    repo = MagicMock()
    for attr, val in kwargs.items():
        setattr(repo, attr, AsyncMock(return_value=val))
    return repo


def _struct_repo(**kwargs) -> MagicMock:
    repo = MagicMock()
    for attr, val in kwargs.items():
        setattr(repo, attr, AsyncMock(return_value=val))
    return repo


def _tmpl_repo(**kwargs) -> MagicMock:
    repo = MagicMock()
    for attr, val in kwargs.items():
        setattr(repo, attr, AsyncMock(return_value=val))
    return repo


# ---------------------------------------------------------------------------
# get_user_email
# ---------------------------------------------------------------------------


class TestGetUserEmail:
    def test_returns_email_from_header(self):
        request = _mock_request(email="user@example.com")
        assert get_user_email(request) == "user@example.com"

    def test_falls_back_to_dev_email_when_no_header_in_dev_mode(self):
        request = _mock_request()
        email = get_user_email(request)
        # ENV=DEV is set in conftest, so fallback is active
        assert email == "dev.user@databricks.com"

    def test_raises_401_when_no_header_and_not_dev(self):
        request = _mock_request()
        with patch("common.authorization.is_development", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                get_user_email(request)
        assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# check_project_not_locked
# ---------------------------------------------------------------------------


class TestCheckProjectNotLocked:
    @pytest.mark.asyncio
    async def test_does_not_raise_when_project_unlocked(self):
        repo = _proj_repo(get_by_id=_project(is_locked=False))
        await check_project_not_locked(PID, repo)  # no exception

    @pytest.mark.asyncio
    async def test_raises_423_when_project_locked(self):
        repo = _proj_repo(get_by_id=_project(is_locked=True))
        with pytest.raises(HTTPException) as exc_info:
            await check_project_not_locked(PID, repo)
        assert exc_info.value.status_code == 423

    @pytest.mark.asyncio
    async def test_does_not_raise_when_project_missing(self):
        repo = _proj_repo(get_by_id=None)
        await check_project_not_locked(uuid.uuid4(), repo)  # no exception


# ---------------------------------------------------------------------------
# check_project_access
# ---------------------------------------------------------------------------


class TestCheckProjectAccess:
    @pytest.mark.asyncio
    async def test_does_not_raise_when_user_has_access(self):
        repo = _proj_repo(user_has_access=True)
        await check_project_access(PID, OWNER_EMAIL, repo)  # no exception

    @pytest.mark.asyncio
    async def test_raises_403_when_user_has_no_access(self):
        repo = _proj_repo(user_has_access=False)
        with pytest.raises(HTTPException) as exc_info:
            await check_project_access(PID, OTHER_EMAIL, repo)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_passes_correct_args_to_repo(self):
        repo = _proj_repo(user_has_access=True)
        await check_project_access(PID, OWNER_EMAIL, repo)
        repo.user_has_access.assert_awaited_once_with(PID, OWNER_EMAIL)


# ---------------------------------------------------------------------------
# check_project_access_and_not_locked
# ---------------------------------------------------------------------------


class TestCheckProjectAccessAndNotLocked:
    @pytest.mark.asyncio
    async def test_does_not_raise_when_access_and_unlocked(self):
        repo = _proj_repo(get_access_and_lock_status=(True, False))
        await check_project_access_and_not_locked(PID, OWNER_EMAIL, repo)  # no exception

    @pytest.mark.asyncio
    async def test_raises_403_when_no_access(self):
        repo = _proj_repo(get_access_and_lock_status=(False, False))
        with pytest.raises(HTTPException) as exc_info:
            await check_project_access_and_not_locked(PID, OTHER_EMAIL, repo)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_raises_423_when_locked(self):
        repo = _proj_repo(get_access_and_lock_status=(True, True))
        with pytest.raises(HTTPException) as exc_info:
            await check_project_access_and_not_locked(PID, OWNER_EMAIL, repo)
        assert exc_info.value.status_code == 423

    @pytest.mark.asyncio
    async def test_raises_403_before_423_when_no_access_and_locked(self):
        repo = _proj_repo(get_access_and_lock_status=(False, True))
        with pytest.raises(HTTPException) as exc_info:
            await check_project_access_and_not_locked(PID, OTHER_EMAIL, repo)
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# check_structure_read_access
# ---------------------------------------------------------------------------


class TestCheckStructureReadAccess:
    @pytest.mark.asyncio
    async def test_checks_project_access_for_existing_structure(self):
        struct_repo = _struct_repo(get_by_id=_structure())
        proj_repo = _proj_repo(user_has_access=True)
        await check_structure_read_access(SID, OWNER_EMAIL, struct_repo, proj_repo)
        proj_repo.user_has_access.assert_awaited_once_with(PID, OWNER_EMAIL)

    @pytest.mark.asyncio
    async def test_raises_403_when_no_project_access(self):
        struct_repo = _struct_repo(get_by_id=_structure())
        proj_repo = _proj_repo(user_has_access=False)
        with pytest.raises(HTTPException) as exc_info:
            await check_structure_read_access(SID, OTHER_EMAIL, struct_repo, proj_repo)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_does_not_raise_when_structure_missing(self):
        struct_repo = _struct_repo(get_by_id=None)
        proj_repo = _proj_repo()
        await check_structure_read_access(uuid.uuid4(), OWNER_EMAIL, struct_repo, proj_repo)  # no exception


# ---------------------------------------------------------------------------
# check_structure_project_not_locked
# ---------------------------------------------------------------------------


class TestCheckStructureProjectNotLocked:
    @pytest.mark.asyncio
    async def test_raises_423_when_project_locked(self):
        struct_repo = _struct_repo(get_by_id=_structure())
        proj_repo = _proj_repo(get_by_id=_project(is_locked=True))
        with pytest.raises(HTTPException) as exc_info:
            await check_structure_project_not_locked(SID, struct_repo, proj_repo)
        assert exc_info.value.status_code == 423

    @pytest.mark.asyncio
    async def test_does_not_raise_when_structure_missing(self):
        struct_repo = _struct_repo(get_by_id=None)
        proj_repo = _proj_repo()
        await check_structure_project_not_locked(uuid.uuid4(), struct_repo, proj_repo)  # no exception


# ---------------------------------------------------------------------------
# check_structure_project_access
# ---------------------------------------------------------------------------


class TestCheckStructureProjectAccess:
    @pytest.mark.asyncio
    async def test_raises_403_when_no_project_access(self):
        struct_repo = _struct_repo(get_by_id=_structure())
        proj_repo = _proj_repo(get_access_and_lock_status=(False, False))
        with pytest.raises(HTTPException) as exc_info:
            await check_structure_project_access(SID, OTHER_EMAIL, struct_repo, proj_repo)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_raises_423_when_project_locked(self):
        struct_repo = _struct_repo(get_by_id=_structure())
        proj_repo = _proj_repo(get_access_and_lock_status=(True, True))
        with pytest.raises(HTTPException) as exc_info:
            await check_structure_project_access(SID, OWNER_EMAIL, struct_repo, proj_repo)
        assert exc_info.value.status_code == 423

    @pytest.mark.asyncio
    async def test_does_not_raise_when_structure_missing(self):
        struct_repo = _struct_repo(get_by_id=None)
        proj_repo = _proj_repo()
        await check_structure_project_access(uuid.uuid4(), OWNER_EMAIL, struct_repo, proj_repo)


# ---------------------------------------------------------------------------
# check_template_read_access
# ---------------------------------------------------------------------------


class TestCheckTemplateReadAccess:
    @pytest.mark.asyncio
    async def test_raises_403_when_no_project_access(self):
        tmpl_repo = _tmpl_repo(get_by_id=_template())
        struct_repo = _struct_repo(get_by_id=_structure())
        proj_repo = _proj_repo(user_has_access=False)
        with pytest.raises(HTTPException) as exc_info:
            await check_template_read_access(TID, OTHER_EMAIL, tmpl_repo, struct_repo, proj_repo)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_does_not_raise_when_template_missing(self):
        tmpl_repo = _tmpl_repo(get_by_id=None)
        struct_repo = _struct_repo()
        proj_repo = _proj_repo()
        await check_template_read_access(uuid.uuid4(), OWNER_EMAIL, tmpl_repo, struct_repo, proj_repo)


# ---------------------------------------------------------------------------
# check_template_project_not_locked
# ---------------------------------------------------------------------------


class TestCheckTemplateProjectNotLocked:
    @pytest.mark.asyncio
    async def test_raises_423_when_project_locked(self):
        tmpl_repo = _tmpl_repo(get_by_id=_template())
        struct_repo = _struct_repo(get_by_id=_structure())
        proj_repo = _proj_repo(get_by_id=_project(is_locked=True))
        with pytest.raises(HTTPException) as exc_info:
            await check_template_project_not_locked(TID, tmpl_repo, struct_repo, proj_repo)
        assert exc_info.value.status_code == 423

    @pytest.mark.asyncio
    async def test_does_not_raise_when_template_missing(self):
        tmpl_repo = _tmpl_repo(get_by_id=None)
        struct_repo = _struct_repo()
        proj_repo = _proj_repo()
        await check_template_project_not_locked(uuid.uuid4(), tmpl_repo, struct_repo, proj_repo)


# ---------------------------------------------------------------------------
# check_template_project_access
# ---------------------------------------------------------------------------


class TestCheckTemplateProjectAccess:
    @pytest.mark.asyncio
    async def test_raises_403_when_no_project_access(self):
        tmpl_repo = _tmpl_repo(get_by_id=_template())
        struct_repo = _struct_repo(get_by_id=_structure())
        proj_repo = _proj_repo(get_access_and_lock_status=(False, False))
        with pytest.raises(HTTPException) as exc_info:
            await check_template_project_access(TID, OTHER_EMAIL, tmpl_repo, struct_repo, proj_repo)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_raises_423_when_project_locked(self):
        tmpl_repo = _tmpl_repo(get_by_id=_template())
        struct_repo = _struct_repo(get_by_id=_structure())
        proj_repo = _proj_repo(get_access_and_lock_status=(True, True))
        with pytest.raises(HTTPException) as exc_info:
            await check_template_project_access(TID, OWNER_EMAIL, tmpl_repo, struct_repo, proj_repo)
        assert exc_info.value.status_code == 423

    @pytest.mark.asyncio
    async def test_does_not_raise_when_template_missing(self):
        tmpl_repo = _tmpl_repo(get_by_id=None)
        struct_repo = _struct_repo()
        proj_repo = _proj_repo()
        await check_template_project_access(uuid.uuid4(), OWNER_EMAIL, tmpl_repo, struct_repo, proj_repo)
