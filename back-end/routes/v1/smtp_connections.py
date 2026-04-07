import os
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from common.authorization import AdminUser, CurrentUser
from common.exceptions import db_op
from common.logger import log as L
from models.smtp_connection import SmtpConnection, SmtpConnectionCreate, SmtpConnectionPublic, SmtpConnectionUpdate
from repositories.smtp_connections import SmtpConnectionsRepository

router = APIRouter(prefix="/smtp-connections", tags=["smtp-connections"])

_PROVIDER_DEFAULTS = {
    "gsuite": {"smtp_host": "smtp.gmail.com", "smtp_port": 587},
    # smtp: user supplies host/port/username — no defaults applied
    # sendgrid: uses the API SDK — no SMTP host/port needed
}


def _get_repo() -> SmtpConnectionsRepository:
    return SmtpConnectionsRepository()


SmtpRepo = Annotated[SmtpConnectionsRepository, Depends(_get_repo)]


def _get_workspace_client():
    from common.authentication.workspace import WorkspaceAuthentication
    return WorkspaceAuthentication().client


def _secret_scope() -> str:
    return os.getenv("SMTP_SECRET_SCOPE", "paginated-reports-smtp")


def _write_secret(scope: str, key: str, value: str) -> None:
    client = _get_workspace_client()
    client.secrets.put_secret(scope=scope, key=key, string_value=value)


def _delete_secret(scope: str, key: str) -> None:
    client = _get_workspace_client()
    client.secrets.delete_secret(scope=scope, key=key)


@router.get("/", response_model=List[SmtpConnectionPublic])
async def list_smtp_connections(repo: SmtpRepo, email: CurrentUser):
    """List all SMTP connections (readable by any authenticated user)."""
    async with db_op("list SMTP connections"):
        return await repo.get_all()


@router.get("/{connection_id}", response_model=SmtpConnectionPublic)
async def get_smtp_connection(connection_id: UUID, repo: SmtpRepo, email: CurrentUser):
    async with db_op("get SMTP connection"):
        conn = await repo.get_by_id(connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="SMTP connection not found")
    return conn


@router.post("/", response_model=SmtpConnectionPublic, status_code=201)
async def create_smtp_connection(
    body: SmtpConnectionCreate,
    email: AdminUser,
    repo: SmtpRepo,
):
    import uuid as _uuid

    # Apply provider defaults
    if body.provider in _PROVIDER_DEFAULTS:
        defaults = _PROVIDER_DEFAULTS[body.provider]
        body.smtp_host = body.smtp_host or defaults["smtp_host"]
        if body.smtp_port == 587:
            body.smtp_port = defaults["smtp_port"]

    scope = _secret_scope()
    connection_id = _uuid.uuid4()
    secret_key = f"smtp_{connection_id}"

    # Write secret first — if this fails, nothing is created
    try:
        _write_secret(scope, secret_key, body.password)
    except Exception as e:
        L.error(f"[SMTP] Failed to write secret: {e}")
        raise HTTPException(status_code=503, detail="Failed to store credentials in secret store")

    try:
        conn = await repo.create(
            body, email,
            connection_id=connection_id,
            secret_scope=scope,
            secret_key=secret_key,
        )
    except RuntimeError:
        # Roll back the secret — log explicitly if the cleanup itself fails
        try:
            _delete_secret(scope, secret_key)
        except Exception as del_err:
            L.error(
                f"[SMTP] Secret rollback failed for {scope}/{secret_key}: {del_err}. "
                "Manual cleanup of the orphaned secret is required."
            )
        L.exception("Failed to create SMTP connection")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    return conn


@router.put("/{connection_id}", response_model=SmtpConnectionPublic)
async def update_smtp_connection(
    connection_id: UUID,
    body: SmtpConnectionUpdate,
    email: AdminUser,
    repo: SmtpRepo,
):
    existing = await repo.get_by_id(connection_id)
    if not existing:
        raise HTTPException(status_code=404, detail="SMTP connection not found")

    # Update the secret if a new password was provided
    if body.password:
        try:
            _write_secret(existing.secret_scope, existing.secret_key, body.password)
        except Exception as e:
            L.error(f"[SMTP] Failed to update secret for connection {connection_id}: {e}")
            raise HTTPException(status_code=503, detail="Failed to update credentials in secret store")

    async with db_op("update SMTP connection"):
        conn = await repo.update(connection_id, body)

    if not conn:
        raise HTTPException(status_code=404, detail="SMTP connection not found")
    return conn


@router.delete("/{connection_id}", status_code=204)
async def delete_smtp_connection(
    connection_id: UUID,
    email: AdminUser,
    repo: SmtpRepo,
):
    existing = await repo.get_by_id(connection_id)
    if not existing:
        raise HTTPException(status_code=404, detail="SMTP connection not found")

    if await repo.has_active_send_lists(connection_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete: this connection is used by one or more send lists",
        )

    async with db_op("delete SMTP connection"):
        deleted = await repo.delete(connection_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="SMTP connection not found")

    try:
        _delete_secret(existing.secret_scope, existing.secret_key)
    except Exception as e:
        L.error(f"[SMTP] Failed to delete secret {existing.secret_scope}/{existing.secret_key}: {e}. Manual cleanup required.")
