from fastapi import APIRouter, Request, HTTPException
from models import Me
from common.config import is_development
from common.logger import log as L


router = APIRouter()


@router.get("/me", operation_id="getMe")
async def get_me(request: Request) -> Me:
    """
    Return details for the currently authenticated user.

    This endpoint uses the Databricks Workspace client to retrieve the
    identity associated with the provided Authorization header and extracts
    user information from various request headers.
    """
    try:
        headers = request.headers

        email = headers.get("X-Forwarded-Email")
        username = headers.get("X-Forwarded-Preferred-Username")
        ip = headers.get("X-Real-Ip")

        if is_development() and (not email and not username):
            email = "dev.user@databricks.com"
            username = "Development User"
            ip = ip or "127.0.0.1"

        return Me(email=email, username=username, ip=ip)
    except Exception:
        L.exception("Unable to determine current user")
        raise HTTPException(status_code=401, detail="Unable to determine current user")


