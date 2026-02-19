from typing import Any, Literal, Optional
from pydantic import BaseModel
from pydantic import ConfigDict


class DatabaseHealth(BaseModel):
    """Pydantic model representing the database health check response."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "lakebase_configured": True,
                    "database_instance_exists": True,
                    "connection_healthy": True,
                    "status": "healthy",
                    "token_status": "valid",
                }
            ]
        },
    )

    lakebase_configured: bool
    database_instance_exists: bool
    connection_healthy: bool
    status: Literal["healthy", "unhealthy"]
    connection_info: Optional[dict[str, Any]]
    error: Optional[str]
  
