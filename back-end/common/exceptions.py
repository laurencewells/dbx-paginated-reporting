from contextlib import asynccontextmanager

from fastapi import HTTPException

from common.logger import log as L


@asynccontextmanager
async def db_op(action: str):
    """Translate RuntimeError from repository calls into HTTP 503."""
    try:
        yield
    except RuntimeError:
        L.exception(f"Failed to {action}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
