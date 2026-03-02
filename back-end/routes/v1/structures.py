from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from common.logger import log as L
from models.structure import Structure, StructureCreate, StructureUpdate
from repositories.structures import StructuresRepository
from services.query_builder import QueryBuilderService

router = APIRouter(prefix="/structures", tags=["structures"])


@router.get("/", response_model=List[Structure])
async def list_structures():
    try:
        repo = StructuresRepository()
        return await repo.get_all()
    except RuntimeError:
        L.exception("Failed to list structures")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.get("/{structure_id}", response_model=Structure)
async def get_structure(structure_id: UUID):
    try:
        repo = StructuresRepository()
        structure = await repo.get_by_id(structure_id)
    except RuntimeError:
        L.exception("Failed to get structure")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not structure:
        raise HTTPException(status_code=404, detail="Structure not found")
    return structure


@router.post("/", response_model=Structure, status_code=201)
async def create_structure(body: StructureCreate):
    try:
        repo = StructuresRepository()
        return await repo.create(body)
    except RuntimeError:
        L.exception("Failed to create structure")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.put("/{structure_id}", response_model=Structure)
async def update_structure(structure_id: UUID, body: StructureUpdate):
    try:
        repo = StructuresRepository()
        structure = await repo.update(structure_id, body)
    except RuntimeError:
        L.exception("Failed to update structure")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not structure:
        raise HTTPException(status_code=404, detail="Structure not found")
    return structure


@router.delete("/{structure_id}", status_code=204)
async def delete_structure(structure_id: UUID):
    try:
        repo = StructuresRepository()
        deleted = await repo.delete(structure_id)
    except RuntimeError:
        L.exception("Failed to delete structure")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not deleted:
        raise HTTPException(status_code=404, detail="Structure not found")


@router.post("/{structure_id}/build", response_model=Structure)
async def build_structure(structure_id: UUID, request: Request):
    """
    Generate the SQL query from the structure's single table + selected columns,
    infer fields from UC column metadata (including nested ARRAY/STRUCT types),
    and persist the results.
    """
    repo = StructuresRepository()
    structure = await repo.get_by_id(structure_id)
    if not structure:
        raise HTTPException(status_code=404, detail="Structure not found")

    if not structure.tables or len(structure.tables) != 1:
        raise HTTPException(
            status_code=400,
            detail="Structure must have exactly one table before building",
        )

    if not structure.selected_columns:
        raise HTTPException(
            status_code=400,
            detail="Structure must have at least one selected column before building",
        )

    try:
        table = structure.tables[0]
        builder = QueryBuilderService(token=request.headers.get("x-forwarded-access-token"))
        sql_query = builder.build_query(table, structure.selected_columns)
        fields = await builder.infer_fields(table, structure.selected_columns)
        updated = await repo.update_built(structure_id, sql_query, fields)
        if not updated:
            raise HTTPException(status_code=404, detail="Structure not found after build")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        L.exception("Structure build failed")
        raise HTTPException(status_code=502, detail="Build failed")
