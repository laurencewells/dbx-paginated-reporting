import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request

from common.config import is_development
from repositories.images import ImagesRepository
from repositories.projects import ProjectsRepository
from repositories.schedules import SchedulesRepository
from repositories.structures import StructuresRepository
from repositories.templates import TemplatesRepository


# ---------------------------------------------------------------------------
# Dependency providers — injectable via Depends() and overridable in tests
# ---------------------------------------------------------------------------

def get_user_email(request: Request) -> str:
    """Extract the authenticated user's email from the request headers."""
    email = request.headers.get("X-Forwarded-Email")
    if not email and is_development():
        email = "dev.user@databricks.com"
    if not email:
        raise HTTPException(status_code=401, detail="Unable to determine current user")
    return email


def is_admin(user_email: str) -> bool:
    """Return True if the user is listed in the ADMIN_EMAILS environment variable."""
    admin_emails = os.getenv("ADMIN_EMAILS", "")
    return user_email in [e.strip() for e in admin_emails.split(",") if e.strip()]


async def require_admin(email: Annotated[str, Depends(get_user_email)]) -> str:
    """FastAPI dependency — raises 403 if the current user is not an admin."""
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")
    return email


def get_projects_repo() -> ProjectsRepository:
    return ProjectsRepository()


def get_structures_repo() -> StructuresRepository:
    return StructuresRepository()


def get_templates_repo() -> TemplatesRepository:
    return TemplatesRepository()


def get_images_repo() -> ImagesRepository:
    return ImagesRepository()


def get_schedules_repo() -> SchedulesRepository:
    return SchedulesRepository()


# Annotated aliases for cleaner route signatures
CurrentUser = Annotated[str, Depends(get_user_email)]
AdminUser = Annotated[str, Depends(require_admin)]
ImagesRepo = Annotated[ImagesRepository, Depends(get_images_repo)]
ProjectsRepo = Annotated[ProjectsRepository, Depends(get_projects_repo)]
SchedulesRepo = Annotated[SchedulesRepository, Depends(get_schedules_repo)]
StructuresRepo = Annotated[StructuresRepository, Depends(get_structures_repo)]
TemplatesRepo = Annotated[TemplatesRepository, Depends(get_templates_repo)]


# ---------------------------------------------------------------------------
# Authorization helpers — accept repo instances so they are testable
# ---------------------------------------------------------------------------

async def check_project_not_locked(project_id: UUID, repo: ProjectsRepository) -> None:
    """Raise 423 if the given project exists and is locked."""
    project = await repo.get_by_id(project_id)
    if project and project.is_locked:
        raise HTTPException(status_code=423, detail="Project is locked")


async def check_project_access(
    project_id: UUID, user_email: str, repo: ProjectsRepository
) -> None:
    """Raise 403 if the user has no access to the project."""
    has_access = await repo.user_has_access(project_id, user_email)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")


async def check_project_access_and_not_locked(
    project_id: UUID, user_email: str, repo: ProjectsRepository
) -> None:
    """Raise 403/423 if the user has no access or the project is locked."""
    has_access, is_locked = await repo.get_access_and_lock_status(project_id, user_email)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    if is_locked:
        raise HTTPException(status_code=423, detail="Project is locked")


async def check_structure_read_access(
    structure_id: UUID,
    user_email: str,
    structures_repo: StructuresRepository,
    projects_repo: ProjectsRepository,
) -> None:
    """Look up a structure's project and raise 403 if no access (read-only, no lock check)."""
    structure = await structures_repo.get_by_id(structure_id)
    if structure:
        await check_project_access(structure.project_id, user_email, projects_repo)


async def check_structure_project_not_locked(
    structure_id: UUID,
    structures_repo: StructuresRepository,
    projects_repo: ProjectsRepository,
) -> None:
    """Look up a structure's project and raise 423 if locked."""
    structure = await structures_repo.get_by_id(structure_id)
    if structure:
        await check_project_not_locked(structure.project_id, projects_repo)


async def check_structure_project_access(
    structure_id: UUID,
    user_email: str,
    structures_repo: StructuresRepository,
    projects_repo: ProjectsRepository,
) -> None:
    """Look up a structure's project and raise 403/423 if no access or locked."""
    structure = await structures_repo.get_by_id(structure_id)
    if not structure:
        return
    has_access, is_locked = await projects_repo.get_access_and_lock_status(
        structure.project_id, user_email
    )
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    if is_locked:
        raise HTTPException(status_code=423, detail="Project is locked")


async def check_template_read_access(
    template_id: UUID,
    user_email: str,
    templates_repo: TemplatesRepository,
    structures_repo: StructuresRepository,
    projects_repo: ProjectsRepository,
) -> None:
    """Look up a template's structure's project and raise 403 if no access (read-only)."""
    template = await templates_repo.get_by_id(template_id)
    if template:
        await check_structure_read_access(
            template.structure_id, user_email, structures_repo, projects_repo
        )


async def check_template_project_not_locked(
    template_id: UUID,
    templates_repo: TemplatesRepository,
    structures_repo: StructuresRepository,
    projects_repo: ProjectsRepository,
) -> None:
    """Look up a template's structure's project and raise 423 if locked."""
    template = await templates_repo.get_by_id(template_id)
    if template:
        await check_structure_project_not_locked(
            template.structure_id, structures_repo, projects_repo
        )


async def check_template_project_access(
    template_id: UUID,
    user_email: str,
    templates_repo: TemplatesRepository,
    structures_repo: StructuresRepository,
    projects_repo: ProjectsRepository,
) -> None:
    """Look up a template's structure's project and raise 403/423 if no access or locked."""
    template = await templates_repo.get_by_id(template_id)
    if template:
        await check_structure_project_access(
            template.structure_id, user_email, structures_repo, projects_repo
        )


async def check_schedule_project_access(
    schedule_id: UUID,
    user_email: str,
    schedules_repo: SchedulesRepository,
    projects_repo: ProjectsRepository,
) -> None:
    """Look up a schedule's project and raise 403/423 if no access or locked."""
    schedule = await schedules_repo.get_by_id(schedule_id)
    if schedule:
        await check_project_access_and_not_locked(schedule.project_id, user_email, projects_repo)
