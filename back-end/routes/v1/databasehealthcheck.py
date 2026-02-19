from fastapi import APIRouter
from common.connectors.lakebase import get_lakebase_connector
from common.config import is_lakebase_configured, is_development
from common.logger import log as L
from models import DatabaseHealth

router = APIRouter()


@router.get("/databasehealthcheck", operation_id="databaseHealthCheck")
async def database_health_check() -> DatabaseHealth:
    """
    Comprehensive database health check endpoint.

    Checks configuration, instance existence, connection health,
    and returns pool / token diagnostics.
    """
    try:
        lakebase_configured = is_lakebase_configured()
        connector = get_lakebase_connector()

        instance_exists = (
            connector.check_database_exists()
            if lakebase_configured and connector
            else False
        )
        connection_healthy = (
            await connector.health_check()
            if instance_exists and connector
            else False
        )

        health_status = {
            "lakebase_configured": lakebase_configured,
            "database_instance_exists": instance_exists,
            "connection_healthy": connection_healthy,
            "status": "healthy" if (lakebase_configured and instance_exists and connection_healthy) else "unhealthy",
            "connection_info": connector.get_connection_info() if is_development() and lakebase_configured and connector else None,
            "error": None,
        }

        return DatabaseHealth(**health_status)

    except Exception:
        L.exception("Database health check failed")
        return DatabaseHealth(
            lakebase_configured=False,
            database_instance_exists=False,
            connection_healthy=False,
            status="unhealthy",
            connection_info=None,
            error="Health check failed" if is_development() else None,
        )
