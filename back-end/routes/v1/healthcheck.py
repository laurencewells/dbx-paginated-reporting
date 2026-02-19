from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()

@router.get("/healthcheck", operation_id="healthcheck")
async def healthcheck() -> dict[str, str]:
    """Return the API status."""
    return {"status": "OK", "timestamp": datetime.now(timezone.utc).isoformat()}