from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request

from common.config import is_development
from repositories.images import ImagesRepository
from repositories.projects import ProjectsRepository
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


def get_projects_repo() -> ProjectsRepository:
    return ProjectsRepository()


def get_structures_repo() -> StructuresRepository:
    return StructuresRepository()


def get_templates_repo() -> TemplatesRepository:
    return TemplatesRepository()


def get_images_repo() -> ImagesRepository:
    return ImagesRepository()


# Annotated aliases for cleaner route signatures
CurrentUser = Annotated[str, Depends(get_user_email)]
ImagesRepo = Annotated[ImagesRepository, Depends(get_images_repo)]
ProjectsRepo = Annotated[ProjectsRepository, Depends(get_projects_repo)]
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
