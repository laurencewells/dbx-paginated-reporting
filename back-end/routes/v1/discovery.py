from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi import Request
from services.discovery import DiscoveryService
from models.structure import StructureField
from common.logger import log as L

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get("/catalogs", response_model=List[Dict[str, Any]])
async def list_catalogs(request: Request):
    try:
        svc = DiscoveryService(token=request.headers.get("x-forwarded-access-token"))
        return await svc.list_catalogs()
    except Exception as e:
        L.error(f"list_catalogs failed: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Failed to list catalogs")


@router.get("/catalogs/{catalog}/schemas", response_model=List[Dict[str, Any]])
async def list_schemas(catalog: str, request: Request): 
    try:
        svc = DiscoveryService(token=request.headers.get("x-forwarded-access-token"))
        return await svc.list_schemas(catalog)
    except Exception as e:
        L.error(f"list_schemas failed: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Failed to list schemas")


@router.get(
    "/catalogs/{catalog}/schemas/{schema}/tables",
    response_model=List[Dict[str, Any]],
)
async def list_tables(catalog: str, schema: str, request: Request):
    try:
        svc = DiscoveryService(token=request.headers.get("x-forwarded-access-token"))
        return await svc.list_tables(catalog, schema)
    except Exception as e:
        L.error(f"list_tables failed: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Failed to list tables")


@router.get(
    "/catalogs/{catalog}/schemas/{schema}/tables/{table}/columns",
    response_model=List[Dict[str, Any]],
)
async def get_table_columns(catalog: str, schema: str, table: str, request: Request):
    try:
        svc = DiscoveryService(token=request.headers.get("x-forwarded-access-token"))
        return await svc.get_table_columns(catalog, schema, table)
    except Exception as e:
        L.error(f"get_table_columns failed: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Failed to get table columns")


@router.get(
    "/catalogs/{catalog}/schemas/{schema}/tables/{table}/as-fields",
    response_model=List[StructureField],
)
async def get_table_as_fields(catalog: str, schema: str, table: str, request: Request):
    """Return UC table columns mapped to structure field types."""
    try:
        svc = DiscoveryService(token=request.headers.get("x-forwarded-access-token"))
        columns = await svc.get_table_columns(catalog, schema, table)
        return svc.columns_to_structure_fields(columns)
    except Exception as e:
        L.error(f"get_table_as_fields failed: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Failed to get table fields")
