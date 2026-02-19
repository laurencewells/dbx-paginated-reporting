"""
Unit tests for ProjectsRepository.

The LakebaseConnector is fully mocked; no DB connection is made.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.project import Project, ProjectCreate, ProjectUpdate, ProjectShare, ProjectShareCreate
from repositories.projects import ProjectsRepository

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
PID = uuid.uuid4()
SID = uuid.uuid4()

OWNER_EMAIL = "owner@example.com"
OTHER_EMAIL = "other@example.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _project_row(
    *,
    id: uuid.UUID | None = None,
    name: str = "Test Project",
    user_email: str = OWNER_EMAIL,
    is_locked: bool = False,
    is_global: bool = False,
):
    return (
        str(id or PID),
        name,
        user_email,
        is_locked,
        is_global,
        NOW,
        NOW,
    )


def _share_row(
    *,
    id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    shared_with_email: str = OTHER_EMAIL,
    shared_by_email: str = OWNER_EMAIL,
):
    return (
        str(id or SID),
        str(project_id or PID),
        shared_with_email,
        shared_by_email,
        NOW,
    )


def _make_result(rows: list | None = None, *, rowcount: int = 1, scalar=None):
    result = MagicMock()
    _rows = rows if rows is not None else []
    result.fetchall.return_value = _rows
    result.fetchone.return_value = _rows[0] if _rows else None
    result.rowcount = rowcount
    result.scalar.return_value = scalar
    return result


def _make_repo(query_result=None) -> tuple[ProjectsRepository, MagicMock]:
    connector = MagicMock()
    connector.execute_query = AsyncMock(return_value=query_result or _make_result())
    repo = ProjectsRepository(connector=connector)
    return repo, connector


# ---------------------------------------------------------------------------
# _require_connector
# ---------------------------------------------------------------------------


class TestRequireConnector:
    def test_raises_runtime_error_when_no_connector(self):
        repo = ProjectsRepository(connector=None)
        with pytest.raises(RuntimeError, match="Lakebase is not available"):
            repo._require_connector()


# ---------------------------------------------------------------------------
# get_all_for_user
# ---------------------------------------------------------------------------


class TestGetAllForUser:
    @pytest.mark.asyncio
    async def test_returns_list_of_projects(self):
        rows = [_project_row(), _project_row(name="Second")]
        repo, _ = _make_repo(_make_result(rows))
        result = await repo.get_all_for_user(OWNER_EMAIL)
        assert len(result) == 2
        assert all(isinstance(p, Project) for p in result)

    @pytest.mark.asyncio
    async def test_empty_returns_empty_list(self):
        repo, _ = _make_repo(_make_result([]))
        result = await repo.get_all_for_user(OWNER_EMAIL)
        assert result == []

    @pytest.mark.asyncio
    async def test_passes_email_as_param(self):
        repo, connector = _make_repo(_make_result([]))
        await repo.get_all_for_user(OWNER_EMAIL)
        params = connector.execute_query.call_args[0][1]
        assert params["email"] == OWNER_EMAIL

    @pytest.mark.asyncio
    async def test_sql_joins_project_shares(self):
        repo, connector = _make_repo(_make_result([]))
        await repo.get_all_for_user(OWNER_EMAIL)
        sql = connector.execute_query.call_args[0][0]
        assert "project_shares" in sql
        assert "is_global" in sql


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


class TestGetById:
    @pytest.mark.asyncio
    async def test_returns_project_when_found(self):
        repo, _ = _make_repo(_make_result([_project_row(id=PID)]))
        result = await repo.get_by_id(PID)
        assert isinstance(result, Project)
        assert str(result.id) == str(PID)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        repo, _ = _make_repo(_make_result([]))
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_passes_id_as_string_param(self):
        repo, connector = _make_repo(_make_result([_project_row()]))
        pid = uuid.uuid4()
        await repo.get_by_id(pid)
        params = connector.execute_query.call_args[0][1]
        assert params["id"] == str(pid)


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


class TestCreate:
    @pytest.mark.asyncio
    async def test_returns_created_project(self):
        repo, _ = _make_repo(_make_result([_project_row()]))
        data = ProjectCreate(name="New Project")
        result = await repo.create(data, OWNER_EMAIL)
        assert isinstance(result, Project)
        assert result.name == "Test Project"

    @pytest.mark.asyncio
    async def test_passes_name_and_email_as_params(self):
        repo, connector = _make_repo(_make_result([_project_row()]))
        data = ProjectCreate(name="New Project")
        await repo.create(data, OWNER_EMAIL)
        params = connector.execute_query.call_args[0][1]
        assert params["name"] == "New Project"
        assert params["email"] == OWNER_EMAIL

    @pytest.mark.asyncio
    async def test_uses_insert_returning(self):
        repo, connector = _make_repo(_make_result([_project_row()]))
        await repo.create(ProjectCreate(name="P"), OWNER_EMAIL)
        sql = connector.execute_query.call_args[0][0]
        assert "INSERT" in sql
        assert "RETURNING" in sql


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_name_returns_updated_project(self):
        row = _project_row(name="Renamed")
        repo, _ = _make_repo(_make_result([row]))
        result = await repo.update(PID, ProjectUpdate(name="Renamed"))
        assert isinstance(result, Project)
        assert result.name == "Renamed"

    @pytest.mark.asyncio
    async def test_update_with_no_fields_falls_back_to_get_by_id(self):
        unique_pid = uuid.uuid4()
        repo, connector = _make_repo(_make_result([_project_row(id=unique_pid)]))
        await repo.update(unique_pid, ProjectUpdate())
        sql = connector.execute_query.call_args[0][0]
        assert "SELECT" in sql

    @pytest.mark.asyncio
    async def test_update_name_builds_set_clause(self):
        repo, connector = _make_repo(_make_result([_project_row(name="X")]))
        await repo.update(PID, ProjectUpdate(name="X"))
        sql = connector.execute_query.call_args[0][0]
        assert "name = :name" in sql

    @pytest.mark.asyncio
    async def test_update_is_locked_builds_set_clause(self):
        repo, connector = _make_repo(_make_result([_project_row(is_locked=True)]))
        await repo.update(PID, ProjectUpdate(is_locked=True))
        sql = connector.execute_query.call_args[0][0]
        assert "is_locked = :is_locked" in sql

    @pytest.mark.asyncio
    async def test_update_is_global_builds_set_clause(self):
        repo, connector = _make_repo(_make_result([_project_row(is_global=True)]))
        await repo.update(PID, ProjectUpdate(is_global=True))
        sql = connector.execute_query.call_args[0][0]
        assert "is_global = :is_global" in sql

    @pytest.mark.asyncio
    async def test_update_always_sets_updated_at(self):
        repo, connector = _make_repo(_make_result([_project_row()]))
        await repo.update(PID, ProjectUpdate(name="Y"))
        sql = connector.execute_query.call_args[0][0]
        assert "updated_at = NOW()" in sql

    @pytest.mark.asyncio
    async def test_update_returns_none_when_not_found(self):
        repo, _ = _make_repo(_make_result([]))
        result = await repo.update(uuid.uuid4(), ProjectUpdate(name="Ghost"))
        assert result is None


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    @pytest.mark.asyncio
    async def test_returns_true_when_row_deleted(self):
        repo, _ = _make_repo(_make_result(rowcount=1))
        assert await repo.delete(PID) is True

    @pytest.mark.asyncio
    async def test_returns_false_when_no_row_deleted(self):
        repo, _ = _make_repo(_make_result(rowcount=0))
        assert await repo.delete(uuid.uuid4()) is False

    @pytest.mark.asyncio
    async def test_passes_id_as_string_param(self):
        repo, connector = _make_repo(_make_result(rowcount=1))
        pid = uuid.uuid4()
        await repo.delete(pid)
        params = connector.execute_query.call_args[0][1]
        assert params["id"] == str(pid)


# ---------------------------------------------------------------------------
# get_shares
# ---------------------------------------------------------------------------


class TestGetShares:
    @pytest.mark.asyncio
    async def test_returns_list_of_shares(self):
        rows = [_share_row(), _share_row(shared_with_email="third@example.com")]
        repo, _ = _make_repo(_make_result(rows))
        result = await repo.get_shares(PID)
        assert len(result) == 2
        assert all(isinstance(s, ProjectShare) for s in result)

    @pytest.mark.asyncio
    async def test_empty_returns_empty_list(self):
        repo, _ = _make_repo(_make_result([]))
        result = await repo.get_shares(PID)
        assert result == []

    @pytest.mark.asyncio
    async def test_passes_project_id_as_string_param(self):
        repo, connector = _make_repo(_make_result([]))
        await repo.get_shares(PID)
        params = connector.execute_query.call_args[0][1]
        assert params["pid"] == str(PID)

    @pytest.mark.asyncio
    async def test_filters_by_project_id(self):
        repo, connector = _make_repo(_make_result([]))
        await repo.get_shares(PID)
        sql = connector.execute_query.call_args[0][0]
        assert "project_id" in sql
        assert ":pid" in sql


# ---------------------------------------------------------------------------
# create_share
# ---------------------------------------------------------------------------


class TestCreateShare:
    @pytest.mark.asyncio
    async def test_returns_created_share(self):
        repo, _ = _make_repo(_make_result([_share_row()]))
        data = ProjectShareCreate(shared_with_email=OTHER_EMAIL)
        result = await repo.create_share(PID, data, OWNER_EMAIL)
        assert isinstance(result, ProjectShare)
        assert result.shared_with_email == OTHER_EMAIL

    @pytest.mark.asyncio
    async def test_passes_correct_params(self):
        repo, connector = _make_repo(_make_result([_share_row()]))
        data = ProjectShareCreate(shared_with_email=OTHER_EMAIL)
        await repo.create_share(PID, data, OWNER_EMAIL)
        params = connector.execute_query.call_args[0][1]
        assert params["pid"] == str(PID)
        assert params["shared_with"] == OTHER_EMAIL
        assert params["shared_by"] == OWNER_EMAIL

    @pytest.mark.asyncio
    async def test_uses_insert_returning(self):
        repo, connector = _make_repo(_make_result([_share_row()]))
        await repo.create_share(PID, ProjectShareCreate(shared_with_email=OTHER_EMAIL), OWNER_EMAIL)
        sql = connector.execute_query.call_args[0][0]
        assert "INSERT" in sql
        assert "RETURNING" in sql


# ---------------------------------------------------------------------------
# delete_share
# ---------------------------------------------------------------------------


class TestDeleteShare:
    @pytest.mark.asyncio
    async def test_returns_true_when_deleted(self):
        repo, _ = _make_repo(_make_result(rowcount=1))
        assert await repo.delete_share(SID) is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self):
        repo, _ = _make_repo(_make_result(rowcount=0))
        assert await repo.delete_share(uuid.uuid4()) is False

    @pytest.mark.asyncio
    async def test_passes_share_id_as_string_param(self):
        repo, connector = _make_repo(_make_result(rowcount=1))
        sid = uuid.uuid4()
        await repo.delete_share(sid)
        params = connector.execute_query.call_args[0][1]
        assert params["id"] == str(sid)


# ---------------------------------------------------------------------------
# user_has_access
# ---------------------------------------------------------------------------


class TestUserHasAccess:
    @pytest.mark.asyncio
    async def test_returns_true_when_db_returns_true(self):
        result_mock = _make_result(rows=[(True,)])
        result_mock.fetchone.return_value = (True,)
        repo, _ = _make_repo(result_mock)
        assert await repo.user_has_access(PID, OWNER_EMAIL) is True

    @pytest.mark.asyncio
    async def test_returns_false_when_db_returns_false(self):
        result_mock = _make_result(rows=[(False,)])
        result_mock.fetchone.return_value = (False,)
        repo, _ = _make_repo(result_mock)
        assert await repo.user_has_access(PID, OTHER_EMAIL) is False

    @pytest.mark.asyncio
    async def test_returns_false_when_no_row(self):
        result_mock = _make_result([])
        repo, _ = _make_repo(result_mock)
        assert await repo.user_has_access(PID, OTHER_EMAIL) is False

    @pytest.mark.asyncio
    async def test_passes_project_id_and_email_as_params(self):
        result_mock = _make_result(rows=[(True,)])
        result_mock.fetchone.return_value = (True,)
        repo, connector = _make_repo(result_mock)
        await repo.user_has_access(PID, OWNER_EMAIL)
        params = connector.execute_query.call_args[0][1]
        assert params["pid"] == str(PID)
        assert params["email"] == OWNER_EMAIL

    @pytest.mark.asyncio
    async def test_sql_checks_owner_shared_and_global(self):
        result_mock = _make_result(rows=[(True,)])
        result_mock.fetchone.return_value = (True,)
        repo, connector = _make_repo(result_mock)
        await repo.user_has_access(PID, OWNER_EMAIL)
        sql = connector.execute_query.call_args[0][0]
        assert "is_global" in sql
        assert "project_shares" in sql
        assert "user_email" in sql


# ---------------------------------------------------------------------------
# _row_to_project
# ---------------------------------------------------------------------------


class TestRowToProject:
    def test_maps_all_fields(self):
        row = _project_row(id=PID, name="P", user_email=OWNER_EMAIL, is_locked=True, is_global=False)
        model = ProjectsRepository._row_to_project(row)
        assert isinstance(model, Project)
        assert str(model.id) == str(PID)
        assert model.name == "P"
        assert model.user_email == OWNER_EMAIL
        assert model.is_locked is True
        assert model.is_global is False
        assert model.created_at == NOW
        assert model.updated_at == NOW

    def test_maps_global_flag(self):
        row = _project_row(is_global=True)
        model = ProjectsRepository._row_to_project(row)
        assert model.is_global is True


# ---------------------------------------------------------------------------
# _row_to_share
# ---------------------------------------------------------------------------


class TestRowToShare:
    def test_maps_all_fields(self):
        row = _share_row(id=SID, project_id=PID, shared_with_email=OTHER_EMAIL, shared_by_email=OWNER_EMAIL)
        model = ProjectsRepository._row_to_share(row)
        assert isinstance(model, ProjectShare)
        assert str(model.id) == str(SID)
        assert str(model.project_id) == str(PID)
        assert model.shared_with_email == OTHER_EMAIL
        assert model.shared_by_email == OWNER_EMAIL
        assert model.created_at == NOW
