"""
Simple configuration management for the serverless application.
"""

import os
from common.logger import log as L
from typing import Dict, List, Any, Optional


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
    
    Uses Databricks workspace API for managed Lakebase instances:
    - LAKEBASE_* variables for Databricks-specific configuration
    
    Returns:
        dict: Lakebase configuration with default values
    """
    return {
                
        "instance_name": os.getenv("PGHOST") or os.getenv("LAKEBASE_INSTANCE_NAME"),
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
    
    Returns:
        bool: True if required Databricks Lakebase configuration variables are set.
    """
    config = get_lakebase_config()
    
    # Check if we have Databricks Lakebase configuration
    has_databricks_vars = bool(config.get("instance_name"))
    
    if has_databricks_vars:
        L.info("Databricks Lakebase configuration detected - workspace API mode")
        return True
    else:
        L.warning("Databricks Lakebase configuration (LAKEBASE_INSTANCE_NAME) not found")
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