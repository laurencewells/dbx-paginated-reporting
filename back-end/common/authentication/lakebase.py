"""
Lakebase PostgreSQL authentication for Databricks applications using workspace API.

This module provides authentication to Databricks Lakebase PostgreSQL instances
exclusively through the Databricks workspace API. It follows the same structure as
SQLAuthentication, WorkspaceAuthentication, and AccountAuthentication for consistency.

Key Features:
- OAuth token generation for Lakebase instances via workspace API
- Automatic token refresh every 50 minutes
- Integration with existing SDK authentication
- Environment-based configuration
- Health monitoring capabilities

Based on: https://apps-cookbook.dev/docs/fastapi/getting_started/lakebase_connection
"""

import asyncio
import os
import time
import uuid
from typing import Optional
from common.authentication.workspace import WorkspaceAuthentication
from common.logger import log as L
from common.config import get_lakebase_config


class LakebaseAuthentication:
    """
    Handles authentication to Databricks Lakebase PostgreSQL instances using workspace API.
    
    This class provides OAuth token generation and refresh for Lakebase database connections
    exclusively through the Databricks workspace API.
    
    Environment Variables Required:
        LAKEBASE_INSTANCE_NAME: Name of the Lakebase PostgreSQL instance
        
    Optional Configuration:
        LAKEBASE_DATABASE_NAME: Database name (optional, defaults to instance name)
        LAKEBASE_CATALOG_NAME: Unity Catalog name for the PostgreSQL instance
        DATABRICKS_DATABASE_PORT: Database port (default: 5432)
        
    Attributes:
        instance_name (str): Name of the Lakebase instance
        database_name (str): Name of the database
        catalog_name (str): Unity Catalog name
        port (int): Database port
        workspace_auth (WorkspaceAuthentication): Workspace authentication instance
        client: Authenticated Databricks workspace client (from workspace_auth)
        database_instance: Lakebase instance details
        _current_token (str): Current OAuth token
        _last_token_refresh (float): Timestamp of last token refresh
        _token_refresh_task: Background token refresh task
    """
    
    # DNS suffixes to strip when resolving short instance names from hostnames
    _DNS_SUFFIXES = [".database.azuredatabricks.net", ".database.databricks.net"]

    def __init__(self, bearer: Optional[str] = None) -> None:
        """
        Initialize Lakebase authentication with optional bearer token.
        
        Always uses Databricks workspace API for managed Lakebase instances.
        In deployed Databricks App environments (where PG* env vars are set),
        the SDK get_database_instance call is skipped since connection info
        is already available from the environment.
        
        Args:
            bearer (str, optional): Bearer token for direct authentication.
                                  If not provided, SDK client will be used.
        
        Raises:
            ValueError: If required environment variables are missing
        """
        config = get_lakebase_config()
        
        self.instance_name = config.get("instance_name")
        self.database_name = config.get("database_name")
        self.port = config.get("port", 5432)
        self.bearer = bearer
        
        self._current_token: Optional[str] = None
        self._last_token_refresh: float = 0
        self._token_refresh_task: Optional[asyncio.Task] = None
        
        if not self.instance_name:
            raise ValueError(
                "LAKEBASE_INSTANCE_NAME environment variable is required for workspace API access"
            )
        
        self._resolved_instance_name = self._resolve_instance_name(self.instance_name)
        L.info(
            f"[Lakebase Auth] raw instance_name={self.instance_name!r} "
            f"resolved={self._resolved_instance_name!r} "
            f"database_name={self.database_name!r} port={self.port} "
            f"pg_env_vars={'present' if self._has_pg_env_vars() else 'absent'}"
        )

        self.client = WorkspaceAuthentication(bearer=self.bearer).client
        self._cached_username: Optional[str] = self._resolve_username()
        
        if self._has_pg_env_vars():
            pghost = os.getenv("PGHOST")
            L.info(
                f"[Lakebase Auth] Using PG* env vars — PGHOST={pghost!r} "
                f"PGDATABASE={os.getenv('PGDATABASE')!r} PGUSER={os.getenv('PGUSER')!r}"
            )
            self.database_instance = self._resolve_instance_from_host(pghost)
            if self.database_instance:
                self._resolved_instance_name = self.database_instance.name
                L.info(f"[Lakebase Auth] Resolved logical instance name: {self._resolved_instance_name!r}")
            else:
                L.warning(
                    f"[Lakebase Auth] Could not resolve logical instance name from PGHOST — "
                    f"using DNS-stripped fallback: {self._resolved_instance_name!r}"
                )
        else:
            L.info("[Lakebase Auth] No PG* env vars — fetching instance via SDK")
            self.database_instance = self._get_database_instance()
            L.info(f"[Lakebase Auth] SDK instance retrieved: {self._resolved_instance_name}")
        
    @classmethod
    def _resolve_instance_name(cls, name: str) -> str:
        """Extract the short instance name from a full DNS hostname if necessary."""
        for suffix in cls._DNS_SUFFIXES:
            if name.endswith(suffix):
                return name[: -len(suffix)]
        return name

    @staticmethod
    def _has_pg_env_vars() -> bool:
        """Check if PG* connection env vars are present (deployed Databricks App)."""
        return bool(os.getenv("PGHOST") and os.getenv("PGDATABASE"))

    def _resolve_instance_from_host(self, pghost: str):
        """
        Resolve the database instance object by matching PGHOST against
        known instances.  The platform injects DNS hostnames into
        LAKEBASE_INSTANCE_NAME, but the SDK credential APIs require
        the logical instance name (e.g. 'paginated-reports-db-instance').

        Returns:
            Database instance object if matched, None otherwise
        """
        try:
            L.info(f"[Lakebase Auth] Listing database instances to resolve PGHOST={pghost!r}")
            instances = list(self.client.database.list_database_instances())
            L.info(f"[Lakebase Auth] Found {len(instances)} database instance(s)")
            for inst in instances:
                dns = getattr(inst, "read_write_dns", None)
                L.info(f"[Lakebase Auth]   instance={inst.name!r}  dns={dns!r}")
                if dns and dns == pghost:
                    return inst
            L.warning(f"[Lakebase Auth] No instance matched PGHOST={pghost!r}")
            return None
        except Exception as e:
            L.warning(f"[Lakebase Auth] Failed to list database instances: {e}")
            return None

    def _resolve_username(self) -> Optional[str]:
        """Resolve the database username once at init time to avoid repeated API calls."""
        client_id = os.getenv("DATABRICKS_CLIENT_ID")
        if client_id:
            return client_id
        try:
            return self.client.current_user.me().user_name
        except Exception as e:
            L.warning(f"[Lakebase Auth] Could not resolve username: {e}")
            return None

    def _get_database_instance(self):
        """
        Get the Lakebase database instance details via SDK by name.
        Only used in local/dev environments where PG* env vars are not set.
        
        Returns:
            Database instance object from Databricks SDK

        Raises:
            Exception: If instance is not found or accessible
        """
        try:
            instance = self.client.database.get_database_instance(name=self._resolved_instance_name)
            L.info(f"Retrieved Lakebase instance: {self._resolved_instance_name}")
            return instance
        except Exception as e:
            L.error(f"Failed to get Lakebase instance '{self._resolved_instance_name}': {e}")
            raise
    
    def generate_database_credential(self) -> str:
        """
        Generate OAuth credentials for database connection using workspace API.
        
        Returns:
            str: OAuth token for database authentication
            
        Raises:
            Exception: If credential generation fails
        """
        try:
            instance_name = (
                self.database_instance.name
                if self.database_instance
                else self._resolved_instance_name
            )
            cred = self.client.database.generate_database_credential(
                request_id=str(uuid.uuid4()),
                instance_names=[instance_name],
            )
            token = cred.token
            
            self._current_token = token
            self._last_token_refresh = time.time()
            
            L.info("Generated Lakebase database credential")
            return token
        except Exception as e:
            L.error(f"Failed to generate database credential: {e}")
            raise
    
    def get_current_token(self) -> Optional[str]:
        """
        Get the current OAuth token.
        
        Returns:
            Optional[str]: Current OAuth token if available
        """
        return self._current_token
    
    def get_token_info(self) -> dict:
        """
        Get token information for monitoring.
        
        Returns:
            dict: Token status and timing information
        """
        return {
            "token_exists": self._current_token is not None,
            "last_token_refresh": self._last_token_refresh,
            "token_age_minutes": (time.time() - self._last_token_refresh) / 60 if self._last_token_refresh > 0 else 0,
        }
    
    def get_connection_info(self) -> dict:
        """
        Get connection information for the Lakebase instance.
        
        In deployed environments (PG* vars present), uses environment variables
        directly. In local/dev, falls back to the SDK database_instance object.
        
        Returns:
            dict: Connection details including host, port, database name, etc.
        """
        if self._has_pg_env_vars():
            return {
                "instance_name": self._resolved_instance_name,
                "database_name": os.getenv("PGDATABASE") or self.database_name,
                "host": os.getenv("PGHOST"),
                "port": int(os.getenv("PGPORT", str(self.port))),
                "username": os.getenv("PGUSER") or os.getenv("DATABRICKS_CLIENT_ID"),
            }
        return {
            "instance_name": self._resolved_instance_name,
            "database_name": self.database_name or self.database_instance.name,
            "host": self.database_instance.read_write_dns,
            "port": self.port,
            "username": self._cached_username,
        }
    
    def check_instance_exists(self) -> bool:
        """
        Check if the Lakebase database instance exists and is accessible.
        
        Returns:
            bool: True if instance exists and is accessible, False otherwise
        """
        if self._has_pg_env_vars():
            return True
        try:
            self.client.database.get_database_instance(name=self._resolved_instance_name)
            return True
        except Exception as e:
            if "not found" in str(e).lower() or "resource not found" in str(e).lower():
                L.info(f"Lakebase instance '{self._resolved_instance_name}' not found")
            else:
                L.error(f"Error checking Lakebase instance: {e}")
            return False
    
    async def start_token_refresh(self):
        """
        Start the background token refresh task.
        
        This should be called during application startup to ensure continuous
        token refresh throughout the application lifecycle.
        """
        if self._token_refresh_task is None or self._token_refresh_task.done():
            self._token_refresh_task = asyncio.create_task(self._refresh_token_background())
            L.info("Background token refresh task started")
    
    async def stop_token_refresh(self):
        """
        Stop the background token refresh task.
        
        This should be called during application shutdown to clean up resources.
        """
        if self._token_refresh_task and not self._token_refresh_task.done():
            self._token_refresh_task.cancel()
            try:
                await self._token_refresh_task
            except asyncio.CancelledError:
                pass
            L.info("Background token refresh task stopped")
    
    async def _refresh_token_background(self):
        """
        Background task to refresh OAuth tokens every 50 minutes.
        
        This ensures continuous connectivity by refreshing tokens before they expire.
        OAuth tokens from Databricks typically expire after 1 hour.
        """
        while True:
            try:
                await asyncio.sleep(50 * 60)  # Wait 50 minutes
                L.info("Background token refresh: Generating fresh PostgreSQL OAuth token")
                
                self.generate_database_credential()
                L.info("Background token refresh: Token updated successfully")
                    
            except Exception as e:
                L.error(f"Background token refresh failed: {e}")
    
    @property
    def is_configured(self) -> bool:
        """Check if Lakebase is properly configured for workspace API access."""
        return bool(self.instance_name)

