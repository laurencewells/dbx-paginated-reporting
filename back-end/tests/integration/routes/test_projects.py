"""
Integration tests for the /api/v1/projects routes.

ProjectsRepository is injected via dependency_overrides so no DB or network
calls are required.

Permission model under test:
  - Owner      : project.user_email == caller — full access
  - Shared user: has a project_shares row for caller — read + write, not owner-only ops
  - Global     : project.is_global == True — visible to everyone
  - No access  : user_has_access returns False — 403
  - Locked     : project.is_locked == True — 423 on writes (owner-only ops still allowed)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.authorization import get_projects_repo
from models.project import Project, ProjectShare

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
PID = uuid.uuid4()
SID = uuid.uuid4()  # share id

OWNER_EMAIL = "dev.user@databricks.com"   # matches DEV fallback in authorization.py
OTHER_EMAIL = "other.user@databricks.com"


# ---------------------------------------------------------------------------
# Model builders
# ---------------------------------------------------------------------------


def _project(
    *,
    id: uuid.UUID | None = None,
    name: str = "Test Project",
    user_email: str = OWNER_EMAIL,
    is_locked: bool = False,
    is_global: bool = False,
) -> Project:
    return Project(
        id=id or PID,
        name=name,
        user_email=user_email,
        is_locked=is_locked,
        is_global=is_global,
        created_at=NOW,
        updated_at=NOW,
    )


def _share(
    *,
    id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    shared_with_email: str = OTHER_EMAIL,
    shared_by_email: str = OWNER_EMAIL,
) -> ProjectShare:
    return ProjectShare(
        id=id or SID,
        project_id=project_id or PID,
        shared_with_email=shared_with_email,
        shared_by_email=shared_by_email,
        created_at=NOW,
    )


# ---------------------------------------------------------------------------
# Repository mock builder
# ---------------------------------------------------------------------------


def _mock_repo(
    *,
    get_all_for_user=None,
    get_by_id: Project | None = None,
    create=None,
    update=None,
    delete: bool = True,
    user_has_access: bool = True,
    get_shares=None,
    create_share=None,
    delete_share: bool = True,
) -> MagicMock:
    repo = MagicMock()
    repo.get_all_for_user = AsyncMock(return_value=get_all_for_user or [])
    repo.get_by_id = AsyncMock(return_value=get_by_id)
    repo.create = AsyncMock(return_value=create)
    repo.update = AsyncMock(return_value=update)
    repo.delete = AsyncMock(return_value=delete)
    repo.user_has_access = AsyncMock(return_value=user_has_access)
    repo.get_shares = AsyncMock(return_value=get_shares or [])
    repo.create_share = AsyncMock(return_value=create_share)
    repo.delete_share = AsyncMock(return_value=delete_share)
    return repo


# ---------------------------------------------------------------------------
# GET /projects/
# ---------------------------------------------------------------------------


class TestListProjects:
    @pytest.mark.asyncio
    async def test_returns_200(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all_for_user=[_project()])
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get("/api/v1/projects/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_list_of_projects(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all_for_user=[_project(), _project(name="Second")])
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get("/api/v1/projects/")
        assert len(response.json()) == 2

    @pytest.mark.asyncio
    async def test_empty_returns_empty_list(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all_for_user=[])
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get("/api/v1/projects/")
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_passes_caller_email_to_repo(self, async_client, dependency_overrides):
        repo = _mock_repo(get_all_for_user=[])
        dependency_overrides[get_projects_repo] = lambda: repo
        await async_client.get("/api/v1/projects/")
        repo.get_all_for_user.assert_awaited_once_with(OWNER_EMAIL)

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_all_for_user = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get("/api/v1/projects/")
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_shared_projects_included(self, async_client, dependency_overrides):
        """Repo is responsible for merging owned + shared; route just passes the email."""
        shared_project = _project(user_email=OTHER_EMAIL)
        repo = _mock_repo(get_all_for_user=[shared_project])
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get("/api/v1/projects/")
        assert response.json()[0]["user_email"] == OTHER_EMAIL

    @pytest.mark.asyncio
    async def test_global_projects_included(self, async_client, dependency_overrides):
        global_project = _project(user_email="admin@databricks.com", is_global=True)
        repo = _mock_repo(get_all_for_user=[global_project])
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get("/api/v1/projects/")
        assert response.json()[0]["is_global"] is True


# ---------------------------------------------------------------------------
# GET /projects/{project_id}
# ---------------------------------------------------------------------------


class TestGetProject:
    @pytest.mark.asyncio
    async def test_owner_gets_200(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_shared_user_gets_200(self, async_client, dependency_overrides):
        """A user with a share record can read the project."""
        repo = _mock_repo(
            get_by_id=_project(id=PID, user_email=OTHER_EMAIL),
            user_has_access=True,
        )
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_global_project_visible_to_any_user(self, async_client, dependency_overrides):
        repo = _mock_repo(
            get_by_id=_project(id=PID, user_email=OTHER_EMAIL, is_global=True),
            user_has_access=True,
        )
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_no_access_returns_403(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=False)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_missing_project_returns_404(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None, user_has_access=False)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_uuid_returns_422(self, async_client):
        response = await async_client.get("/api/v1/projects/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.get_by_id = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /projects/
# ---------------------------------------------------------------------------


class TestCreateProject:
    @pytest.mark.asyncio
    async def test_returns_201(self, async_client, dependency_overrides):
        repo = _mock_repo(create=_project())
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.post("/api/v1/projects/", json={"name": "My Project"})
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_returns_created_project(self, async_client, dependency_overrides):
        repo = _mock_repo(create=_project(name="My Project"))
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.post("/api/v1/projects/", json={"name": "My Project"})
        assert response.json()["name"] == "My Project"

    @pytest.mark.asyncio
    async def test_passes_caller_email_to_repo(self, async_client, dependency_overrides):
        repo = _mock_repo(create=_project())
        dependency_overrides[get_projects_repo] = lambda: repo
        await async_client.post("/api/v1/projects/", json={"name": "P"})
        _, kwargs = repo.create.call_args
        assert kwargs.get("user_email") == OWNER_EMAIL or repo.create.call_args[0][1] == OWNER_EMAIL

    @pytest.mark.asyncio
    async def test_returns_422_when_name_missing(self, async_client):
        response = await async_client.post("/api/v1/projects/", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo()
        repo.create = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.post("/api/v1/projects/", json={"name": "P"})
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# PUT /projects/{project_id} — name rename (access + not locked)
# ---------------------------------------------------------------------------


class TestUpdateProjectName:
    @pytest.mark.asyncio
    async def test_owner_can_rename(self, async_client, dependency_overrides):
        updated = _project(id=PID, name="Renamed")
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True, update=updated)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"name": "Renamed"})
        assert response.status_code == 200
        assert response.json()["name"] == "Renamed"

    @pytest.mark.asyncio
    async def test_shared_user_cannot_rename_locked_project(self, async_client, dependency_overrides):
        repo = _mock_repo(
            get_by_id=_project(id=PID, user_email=OTHER_EMAIL, is_locked=True),
            user_has_access=True,
        )
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"name": "Renamed"})
        assert response.status_code == 423

    @pytest.mark.asyncio
    async def test_no_access_returns_403(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=False)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"name": "X"})
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_missing_project_returns_404(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None, user_has_access=False)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{uuid.uuid4()}", json={"name": "X"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True)
        repo.update = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"name": "X"})
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# PUT /projects/{project_id} — lock / global (owner-only)
# ---------------------------------------------------------------------------


class TestUpdateProjectOwnerOnly:
    @pytest.mark.asyncio
    async def test_owner_can_lock(self, async_client, dependency_overrides):
        updated = _project(id=PID, is_locked=True)
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True, update=updated)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"is_locked": True})
        assert response.status_code == 200
        assert response.json()["is_locked"] is True

    @pytest.mark.asyncio
    async def test_owner_can_unlock(self, async_client, dependency_overrides):
        updated = _project(id=PID, is_locked=False)
        repo = _mock_repo(get_by_id=_project(id=PID, is_locked=True), user_has_access=True, update=updated)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"is_locked": False})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_non_owner_cannot_lock(self, async_client, dependency_overrides):
        """A shared user (not the owner) must not be able to lock/unlock."""
        repo = _mock_repo(
            get_by_id=_project(id=PID, user_email=OTHER_EMAIL),
            user_has_access=True,
        )
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"is_locked": True})
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_owner_can_make_global(self, async_client, dependency_overrides):
        updated = _project(id=PID, is_global=True)
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True, update=updated)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"is_global": True})
        assert response.status_code == 200
        assert response.json()["is_global"] is True

    @pytest.mark.asyncio
    async def test_non_owner_cannot_make_global(self, async_client, dependency_overrides):
        repo = _mock_repo(
            get_by_id=_project(id=PID, user_email=OTHER_EMAIL),
            user_has_access=True,
        )
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"is_global": True})
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_owner_can_lock_already_locked_project(self, async_client, dependency_overrides):
        """Owner can still set is_locked even when the project is already locked."""
        updated = _project(id=PID, is_locked=False)
        repo = _mock_repo(get_by_id=_project(id=PID, is_locked=True), user_has_access=True, update=updated)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.put(f"/api/v1/projects/{PID}", json={"is_locked": False})
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# DELETE /projects/{project_id} — owner-only
# ---------------------------------------------------------------------------


class TestDeleteProject:
    @pytest.mark.asyncio
    async def test_owner_can_delete(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), delete=True)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.delete(f"/api/v1/projects/{PID}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_shared_user_cannot_delete(self, async_client, dependency_overrides):
        """A user with access but not the owner must receive 403."""
        repo = _mock_repo(get_by_id=_project(id=PID, user_email=OTHER_EMAIL), user_has_access=True)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.delete(f"/api/v1/projects/{PID}")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_no_access_returns_404_via_missing_project(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.delete(f"/api/v1/projects/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID))
        repo.delete = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.delete(f"/api/v1/projects/{PID}")
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_invalid_uuid_returns_422(self, async_client):
        response = await async_client.delete("/api/v1/projects/not-a-uuid")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /projects/{project_id}/shares
# ---------------------------------------------------------------------------


class TestListShares:
    @pytest.mark.asyncio
    async def test_owner_can_list_shares(self, async_client, dependency_overrides):
        shares = [_share()]
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True, get_shares=shares)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}/shares")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_shared_user_can_list_shares(self, async_client, dependency_overrides):
        """Any user with access can see who else has access."""
        repo = _mock_repo(
            get_by_id=_project(id=PID, user_email=OTHER_EMAIL),
            user_has_access=True,
            get_shares=[_share()],
        )
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}/shares")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_no_access_returns_403(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=False)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}/shares")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_empty_shares_returns_empty_list(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True, get_shares=[])
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}/shares")
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True)
        repo.get_shares = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.get(f"/api/v1/projects/{PID}/shares")
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /projects/{project_id}/shares — owner-only
# ---------------------------------------------------------------------------


class TestCreateShare:
    @pytest.mark.asyncio
    async def test_owner_can_share(self, async_client, dependency_overrides):
        share = _share(shared_with_email=OTHER_EMAIL)
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True, create_share=share)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.post(
            f"/api/v1/projects/{PID}/shares",
            json={"shared_with_email": OTHER_EMAIL},
        )
        assert response.status_code == 201
        assert response.json()["shared_with_email"] == OTHER_EMAIL

    @pytest.mark.asyncio
    async def test_non_owner_cannot_share(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID, user_email=OTHER_EMAIL), user_has_access=True)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.post(
            f"/api/v1/projects/{PID}/shares",
            json={"shared_with_email": "third@example.com"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_cannot_share_with_yourself(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.post(
            f"/api/v1/projects/{PID}/shares",
            json={"shared_with_email": OWNER_EMAIL},
        )
        assert response.status_code == 400
        assert "yourself" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_invalid_email_returns_422(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.post(
            f"/api/v1/projects/{PID}/shares",
            json={"shared_with_email": "not-an-email"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_project_returns_404(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=None, user_has_access=False)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.post(
            f"/api/v1/projects/{uuid.uuid4()}/shares",
            json={"shared_with_email": OTHER_EMAIL},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), user_has_access=True)
        repo.create_share = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.post(
            f"/api/v1/projects/{PID}/shares",
            json={"shared_with_email": OTHER_EMAIL},
        )
        assert response.status_code == 503


# ---------------------------------------------------------------------------
# DELETE /projects/{project_id}/shares/{share_id} — owner-only
# ---------------------------------------------------------------------------


class TestDeleteShare:
    @pytest.mark.asyncio
    async def test_owner_can_remove_share(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), delete_share=True)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.delete(f"/api/v1/projects/{PID}/shares/{SID}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_non_owner_cannot_remove_share(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID, user_email=OTHER_EMAIL), user_has_access=True)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.delete(f"/api/v1/projects/{PID}/shares/{SID}")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_missing_share_returns_404(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID), delete_share=False)
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.delete(f"/api/v1/projects/{PID}/shares/{SID}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_share_uuid_returns_422(self, async_client):
        response = await async_client.delete(f"/api/v1/projects/{PID}/shares/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_repo(get_by_id=_project(id=PID))
        repo.delete_share = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_projects_repo] = lambda: repo
        response = await async_client.delete(f"/api/v1/projects/{PID}/shares/{SID}")
        assert response.status_code == 503
