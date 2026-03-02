from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request

from common.factories.cache import app_cache
from common.logger import log as L
from models.template import Template, TemplateCreate, TemplateUpdate
from repositories.templates import TemplatesRepository
from services.data_query import DataQueryService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=List[Template])
async def list_templates(structure_id: Optional[UUID] = Query(None)):
    try:
        repo = TemplatesRepository()
        return await repo.get_all(structure_id=structure_id)
    except RuntimeError:
        L.exception("Failed to list templates")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.get("/{template_id}", response_model=Template)
async def get_template(template_id: UUID):
    try:
        repo = TemplatesRepository()
        template = await repo.get_by_id(template_id)
    except RuntimeError:
        L.exception("Failed to get template")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/", response_model=Template, status_code=201)
async def create_template(body: TemplateCreate):
    try:
        repo = TemplatesRepository()
        return await repo.create(body)
    except RuntimeError:
        L.exception("Failed to create template")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.put("/{template_id}", response_model=Template)
async def update_template(template_id: UUID, body: TemplateUpdate):
    try:
        repo = TemplatesRepository()
        template = await repo.update(template_id, body)
    except RuntimeError:
        L.exception("Failed to update template")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if body.structure_id is not None:
        await app_cache.delete(f"preview:{template_id}:50")
    return template


@router.delete("/{template_id}", status_code=204)
async def delete_template(template_id: UUID):
    try:
        repo = TemplatesRepository()
        deleted = await repo.delete(template_id)
    except RuntimeError:
        L.exception("Failed to delete template")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    await app_cache.delete(f"preview:{template_id}:50")


@router.post("/{template_id}/preview-data", response_model=Dict[str, Any])
async def preview_data(template_id: UUID, request: Request, limit: int = Query(50, ge=1, le=1000)):
    """Query real data from the linked structure's SQL query, limited for preview."""
    try:
        svc = DataQueryService(token=request.headers.get("x-forwarded-access-token"))
        return await svc.execute_for_preview(template_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        L.exception("Failed to execute preview data query")
        raise HTTPException(status_code=502, detail="Failed to query data")


