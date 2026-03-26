from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from common.authorization import (
    CurrentUser,
    ProjectsRepo,
    check_project_access,
    check_project_access_and_not_locked,
)
from common.logger import log as L
from models.email_send_list import EmailSendList, EmailSendListCreate, EmailSendListUpdate
from repositories.email_send_lists import EmailSendListsRepository
from repositories.projects import ProjectsRepository

router = APIRouter(prefix="/send-lists", tags=["send-lists"])


def _get_repo() -> EmailSendListsRepository:
    return EmailSendListsRepository()


SendListsRepo = Annotated[EmailSendListsRepository, Depends(_get_repo)]


async def _check_send_list_project_access(
    send_list_id: UUID,
    user_email: str,
    send_lists_repo: EmailSendListsRepository,
    projects_repo: ProjectsRepository,
) -> None:
    send_list = await send_lists_repo.get_by_id(send_list_id)
    if send_list:
        await check_project_access_and_not_locked(send_list.project_id, user_email, projects_repo)


@router.get("/", response_model=List[EmailSendList])
async def list_send_lists(
    email: CurrentUser,
    repo: SendListsRepo,
    projects_repo: ProjectsRepo,
    project_id: UUID = Query(...),
):
    await check_project_access(project_id, email, projects_repo)
    try:
        return await repo.get_all_for_project(project_id)
    except RuntimeError:
        L.exception("Failed to list send lists")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.get("/{send_list_id}", response_model=EmailSendList)
async def get_send_list(
    send_list_id: UUID,
    email: CurrentUser,
    repo: SendListsRepo,
    projects_repo: ProjectsRepo,
):
    await _check_send_list_project_access(send_list_id, email, repo, projects_repo)
    try:
        send_list = await repo.get_by_id(send_list_id)
    except RuntimeError:
        L.exception("Failed to get send list")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not send_list:
        raise HTTPException(status_code=404, detail="Send list not found")
    return send_list


@router.post("/", response_model=EmailSendList, status_code=201)
async def create_send_list(
    body: EmailSendListCreate,
    email: CurrentUser,
    repo: SendListsRepo,
    projects_repo: ProjectsRepo,
):
    await check_project_access_and_not_locked(body.project_id, email, projects_repo)
    try:
        return await repo.create(body, email)
    except RuntimeError:
        L.exception("Failed to create send list")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.put("/{send_list_id}", response_model=EmailSendList)
async def update_send_list(
    send_list_id: UUID,
    body: EmailSendListUpdate,
    email: CurrentUser,
    repo: SendListsRepo,
    projects_repo: ProjectsRepo,
):
    await _check_send_list_project_access(send_list_id, email, repo, projects_repo)
    try:
        send_list = await repo.update(send_list_id, body)
    except RuntimeError:
        L.exception("Failed to update send list")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not send_list:
        raise HTTPException(status_code=404, detail="Send list not found")
    return send_list


@router.delete("/{send_list_id}", status_code=204)
async def delete_send_list(
    send_list_id: UUID,
    email: CurrentUser,
    repo: SendListsRepo,
    projects_repo: ProjectsRepo,
):
    await _check_send_list_project_access(send_list_id, email, repo, projects_repo)
    try:
        deleted = await repo.delete(send_list_id)
    except RuntimeError:
        L.exception("Failed to delete send list")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not deleted:
        raise HTTPException(status_code=404, detail="Send list not found")
