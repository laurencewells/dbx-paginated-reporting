from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException

from common.authorization import CurrentUser, ProjectsRepo
from common.factories.cache import app_cache
from common.logger import log as L
from models.project import Project, ProjectCreate, ProjectShare, ProjectShareCreate, ProjectUpdate
from repositories.projects import ProjectsRepository

router = APIRouter(prefix="/projects", tags=["projects"])


async def _get_project_or_404(repo: ProjectsRepository, project_id: UUID) -> Project:
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _require_access(repo: ProjectsRepository, project_id: UUID, user_email: str) -> Project:
    project = await _get_project_or_404(repo, project_id)
    has_access = await repo.user_has_access(project_id, user_email)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    return project


async def _require_owner(repo: ProjectsRepository, project_id: UUID, user_email: str) -> Project:
    project = await _get_project_or_404(repo, project_id)
    if project.user_email != user_email:
        raise HTTPException(status_code=403, detail="Only the project owner can perform this action")
    return project


async def _require_unlocked(repo: ProjectsRepository, project_id: UUID, user_email: str) -> Project:
    project = await _require_access(repo, project_id, user_email)
    if project.is_locked:
        raise HTTPException(status_code=423, detail="Project is locked")
    return project


# -- project CRUD -------------------------------------------------------------

@router.get("/", response_model=List[Project])
async def list_projects(email: CurrentUser, repo: ProjectsRepo):
    try:
        return await repo.get_all_for_user(email)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to list projects")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: UUID, email: CurrentUser, repo: ProjectsRepo):
    try:
        return await _require_access(repo, project_id, email)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to get project")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.post("/", response_model=Project, status_code=201)
async def create_project(body: ProjectCreate, email: CurrentUser, repo: ProjectsRepo):
    try:
        return await repo.create(body, email)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to create project")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: UUID, body: ProjectUpdate, email: CurrentUser, repo: ProjectsRepo):
    try:
        # Only owner can lock/unlock or toggle global
        if body.is_locked is not None or body.is_global is not None:
            await _require_owner(repo, project_id, email)
        else:
            await _require_unlocked(repo, project_id, email)
        project = await repo.update(project_id, body)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await app_cache.delete(f"project:{project_id}")
        return project
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to update project")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: UUID, email: CurrentUser, repo: ProjectsRepo):
    try:
        await _require_owner(repo, project_id, email)
        deleted = await repo.delete(project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        await app_cache.delete(f"project:{project_id}")
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to delete project")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


# -- shares -------------------------------------------------------------------

@router.get("/{project_id}/shares", response_model=List[ProjectShare])
async def list_shares(project_id: UUID, email: CurrentUser, repo: ProjectsRepo):
    try:
        await _require_access(repo, project_id, email)
        return await repo.get_shares(project_id)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to list shares")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.post("/{project_id}/shares", response_model=ProjectShare, status_code=201)
async def create_share(project_id: UUID, body: ProjectShareCreate, email: CurrentUser, repo: ProjectsRepo):
    try:
        await _require_owner(repo, project_id, email)
        if body.shared_with_email == email:
            raise HTTPException(status_code=400, detail="Cannot share a project with yourself")
        return await repo.create_share(project_id, body, email)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to create share")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.delete("/{project_id}/shares/{share_id}", status_code=204)
async def delete_share(project_id: UUID, share_id: UUID, email: CurrentUser, repo: ProjectsRepo):
    try:
        await _require_owner(repo, project_id, email)
        deleted = await repo.delete_share(share_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Share not found")
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to delete share")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
