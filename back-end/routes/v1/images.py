import base64
from typing import List
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from common.authorization import (
    CurrentUser,
    ImagesRepo,
    ProjectsRepo,
    check_project_access,
    check_project_not_locked,
)
from common.logger import log as L
from models.image import Image, ImageCreate, ImageUpdate

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_IMAGES_PER_PROJECT = 20
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
}


router = APIRouter(prefix="/images", tags=["images"])


@router.get("/", response_model=List[Image])
async def list_images(
    email: CurrentUser,
    repo: ImagesRepo,
    projects_repo: ProjectsRepo,
    project_id: UUID = Query(...),
):
    try:
        await check_project_access(project_id, email, projects_repo)
        return await repo.get_all(project_id)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to list images")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.get("/{image_id}", response_model=Image)
async def get_image(
    image_id: UUID,
    email: CurrentUser,
    repo: ImagesRepo,
    projects_repo: ProjectsRepo,
):
    try:
        image = await repo.get_by_id(image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        await check_project_access(image.project_id, email, projects_repo)
        return image
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to get image")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.get("/{image_id}/data")
async def get_image_data(
    image_id: UUID,
    email: CurrentUser,
    repo: ImagesRepo,
    projects_repo: ProjectsRepo,
):
    """Serve the raw image binary with correct Content-Type for use in templates."""
    try:
        image_meta = await repo.get_by_id(image_id)
        if not image_meta:
            raise HTTPException(status_code=404, detail="Image not found")
        await check_project_access(image_meta.project_id, email, projects_repo)
        data = await repo.get_data(image_id)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to get image data")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not data:
        raise HTTPException(status_code=404, detail="Image not found")

    mime_type, data_base64 = data
    image_bytes = base64.b64decode(data_base64)
    return Response(
        content=image_bytes,
        media_type=mime_type,
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Security-Policy": "default-src 'none'",
        },
    )


@router.post("/", response_model=Image, status_code=201)
async def upload_image(
    email: CurrentUser,
    repo: ImagesRepo,
    projects_repo: ProjectsRepo,
    project_id: UUID = Query(...),
    file: UploadFile = File(...),
):
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. "
            f"Allowed types: {', '.join(sorted(ALLOWED_MIME_TYPES))}",
        )

    # Read and validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({len(contents)} bytes) exceeds the {MAX_FILE_SIZE // (1024 * 1024)}MB limit.",
        )

    try:
        await check_project_access(project_id, email, projects_repo)
        await check_project_not_locked(project_id, projects_repo)

        # Check image count limit
        count = await repo.count(project_id)
        if count >= MAX_IMAGES_PER_PROJECT:
            raise HTTPException(
                status_code=400,
                detail=f"Project already has {count} images. Maximum is {MAX_IMAGES_PER_PROJECT}.",
            )

        data_base64 = base64.b64encode(contents).decode("ascii")

        image_data = ImageCreate(
            project_id=project_id,
            filename=file.filename or "untitled",
            mime_type=file.content_type,
            size_bytes=len(contents),
            data_base64=data_base64,
        )
        return await repo.create(image_data)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to upload image")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.put("/{image_id}", response_model=Image)
async def update_image(
    image_id: UUID,
    body: ImageUpdate,
    email: CurrentUser,
    repo: ImagesRepo,
    projects_repo: ProjectsRepo,
):
    try:
        existing = await repo.get_by_id(image_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Image not found")
        await check_project_access(existing.project_id, email, projects_repo)
        await check_project_not_locked(existing.project_id, projects_repo)
        image = await repo.update(image_id, body)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to update image")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.delete("/{image_id}", status_code=204)
async def delete_image(
    image_id: UUID,
    email: CurrentUser,
    repo: ImagesRepo,
    projects_repo: ProjectsRepo,
):
    try:
        existing = await repo.get_by_id(image_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Image not found")
        await check_project_access(existing.project_id, email, projects_repo)
        await check_project_not_locked(existing.project_id, projects_repo)
        deleted = await repo.delete(image_id)
    except HTTPException:
        raise
    except RuntimeError:
        L.exception("Failed to delete image")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not deleted:
        raise HTTPException(status_code=404, detail="Image not found")
