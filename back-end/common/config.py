"""
Simple configuration management for the serverless application.
"""

import os
from common.logger import log as L
from typing import Dict, List, Any, Optional


# Image upload limits
MAX_IMAGE_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_IMAGES_PER_PROJECT = 20


def is_development() -> bool:
    """Check if running in development environment."""
    return os.environ.get("ENV") == "DEV"


def get_cors_origins() -> List[str]:
    """Get CORS origins for development."""
    return [
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:5173"
    ]


def get_static_files_directory() -> str:
    """Get static files directory for production."""
    return "./static"


# Lakebase Configuration
def get_lakebase_config() -> Dict[str, Any]:
    """
    Get Lakebase PostgreSQL configuration from environment variables.

    The preferred deployment pattern bypasses the DABs postgres resource entirely
    (to avoid the opaque auto-generated database ID dependency) and instead injects
    connection details as explicit env vars:

        LAKEBASE_ENDPOINT  - full endpoint resource path, e.g.
                             'projects/my-project/branches/main/endpoints/primary'
        PGDATABASE         - database name (e.g. 'databricks_postgres')
        PGUSER             - service-principal client ID used as the DB username
        PGPORT             - port (default 5432)
        PGSSLMODE          - SSL mode (default 'require')

    The host is NOT read from env vars — it is resolved at startup by calling
    w.postgres.get_endpoint(name=LAKEBASE_ENDPOINT) so it is always consistent
    with the live endpoint object.

    Returns:
        dict: Lakebase configuration with default values.
    """
    return {
        # Project / instance name — prefer the explicit var; PGHOST is a legacy fallback
        # for local dev only (it won't be present in production since the postgres app
        # resource is bypassed).
        "instance_name": os.getenv("LAKEBASE_INSTANCE_NAME") or os.getenv("PGHOST"),
        "endpoint": os.getenv("LAKEBASE_ENDPOINT"),
        "database_name": os.getenv("PGDATABASE") or os.getenv("LAKEBASE_DATABASE_NAME"),
        "schema_name": os.getenv("LAKEBASE_SCHEMA", "app"),
        "catalog_name": os.getenv("LAKEBASE_CATALOG_NAME"),
        "application_name": os.getenv("PGAPPNAME") or os.getenv("LAKEBASE_APP_NAME"),
        "port": int(os.getenv("PGPORT") or os.getenv("DATABRICKS_DATABASE_PORT", "5432")),
        "username": os.getenv("PGUSER"),
        "ssl_mode": os.getenv("PGSSLMODE") or "require",
        "pool_settings": {
            "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
            "command_timeout": int(os.getenv("DB_COMMAND_TIMEOUT", "30")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "10")),
            "pool_recycle_interval": int(os.getenv("DB_POOL_RECYCLE_INTERVAL", "3600")),
        }
    }


def is_lakebase_configured() -> bool:
    """
    Check if Lakebase is properly configured for workspace API access.

    The minimum requirement is LAKEBASE_ENDPOINT (preferred) or LAKEBASE_INSTANCE_NAME
    so the authenticator can resolve the endpoint and generate credentials.

    Returns:
        bool: True if the minimum required configuration is present.
    """
    config = get_lakebase_config()

    if config.get("endpoint"):
        L.info("Lakebase configuration detected — using LAKEBASE_ENDPOINT")
        return True
    if config.get("instance_name"):
        L.info("Lakebase configuration detected — using LAKEBASE_INSTANCE_NAME (endpoint will be discovered)")
        return True

    L.warning("Lakebase not configured: set LAKEBASE_ENDPOINT or LAKEBASE_INSTANCE_NAME")
    return False

def get_sql_warehouse_path() -> str:
    """Get SQL warehouse HTTP path from available environment variables."""
    warehouse_id = (
        os.getenv("DATABRICKS_WAREHOUSE_ID")
        or os.getenv("DATABRICKS_SQL_WAREHOUSE_ID")
    )
    if warehouse_id:
        return f"/sql/1.0/warehouses/{warehouse_id}"
    return os.getenv("DATABRICKS_WAREHOUSE_PATH")


def get_lakehouse_catalog() -> Optional[str]:
    """Get the Unity Catalog catalog name from environment variables."""
    return os.getenv("LAKEHOUSE_CATALOG_NAME")


def get_lakehouse_schema() -> Optional[str]:
    """Get the Unity Catalog schema name from environment variables."""
    return os.getenv("LAKEHOUSE_SCHEMA_NAME")


# Model Serving Configuration
def get_model_serving_endpoint() -> str:
    """
    Get the Databricks Model Serving endpoint name.
    
    Returns:
        str: The serving endpoint name, defaults to 'databricks-claude-sonnet-4-6'
    """
    return os.getenv("MODEL_SERVING_ENDPOINT", "databricks-claude-sonnet-4-6")


def is_model_serving_configured() -> bool:
    """
    Check if a Model Serving endpoint is explicitly configured.
    
    Returns:
        bool: True if MODEL_SERVING_ENDPOINT environment variable is set.
    """
    configured = bool(os.getenv("MODEL_SERVING_ENDPOINT"))
    if configured:
        L.info(f"Model Serving endpoint configured: {get_model_serving_endpoint()}")
    else:
        L.warning("MODEL_SERVING_ENDPOINT not set — using default: databricks-claude-sonnet-4-6")
    return configured


def get_environment_info() -> Dict[str, Any]:
    """
    Get comprehensive environment information for debugging.
    
    Returns:
        dict: Environment information including Databricks and Lakebase settings
    """
    return {
        "environment": os.getenv("ENV", "unknown"),
        "is_development": is_development(),
        "databricks": {
            "host": os.getenv("DATABRICKS_HOST"),
            "warehouse_path": os.getenv("DATABRICKS_WAREHOUSE_PATH"),
            "token_configured": bool(os.getenv("DATABRICKS_TOKEN")),
            "client_id_configured": bool(os.getenv("DATABRICKS_CLIENT_ID")),
        },
        "lakebase": get_lakebase_config(),
        "lakebase_configured": is_lakebase_configured(),
        "model_serving": {
            "endpoint": get_model_serving_endpoint(),
            "configured": is_model_serving_configured(),
        },
    }