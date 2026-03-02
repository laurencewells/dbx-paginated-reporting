"""
Lakebase PostgreSQL connector for database operations.

This module provides a connector for interacting with Databricks Lakebase
PostgreSQL instances. It handles connection pooling, automatic token refresh,
and async query execution using SQLAlchemy.

The connector is created by LakebaseFactory during the application lifespan
and stored as a runtime singleton via set_lakebase_connector(). Repositories
and other consumers retrieve it via get_lakebase_connector().

Based on: https://apps-cookbook.dev/docs/fastapi/getting_started/lakebase_connection
"""

from typing import AsyncGenerator, Optional, Any, Dict
from contextlib import asynccontextmanager

from sqlalchemy import URL, event, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pandas import DataFrame
from common.config import get_lakebase_config
from common.logger import log as L
from common.authentication.lakebase import LakebaseAuthentication


class LakebaseConnector:
    """
    Connector for Databricks Lakebase PostgreSQL instances.

    Owns the SQLAlchemy engine, session factory, and auth reference.
    Created once by LakebaseFactory and shared via the module-level
    runtime singleton.
    """

    def __init__(self, auth: LakebaseAuthentication) -> None:
        self.auth = auth
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._init_engine()

    def _init_engine(self):
        """Initialize the SQLAlchemy async engine with connection pooling."""
        try:
            self.auth.generate_database_credential()
            L.info("Generated initial OAuth credentials for Lakebase")

            conn_info = self.auth.get_connection_info()

            url = URL.create(
                drivername="postgresql+asyncpg",
                username=conn_info["username"],
                password="",
                host=conn_info["host"],
                port=conn_info["port"],
                database=conn_info["database_name"],
            )

            lakebase_config = get_lakebase_config()
            pool_settings = lakebase_config.get("pool_settings", {})

            self.engine = create_async_engine(
                url,
                pool_pre_ping=False,
                echo=False,
                pool_size=pool_settings.get("pool_size", 5),
                max_overflow=pool_settings.get("max_overflow", 10),
                pool_timeout=pool_settings.get("pool_timeout", 10),
                pool_recycle=pool_settings.get("pool_recycle_interval", 3600),
                connect_args={
                    "command_timeout": pool_settings.get("command_timeout", 30),
                    "server_settings": {
                        "application_name": lakebase_config.get("application_name") or "databricks_app",
                        "search_path": lakebase_config.get("schema_name", "app"),
                    },
                    "ssl": lakebase_config.get("ssl_mode", "require"),
                },
            )

            auth_ref = self.auth

            @event.listens_for(self.engine.sync_engine, "do_connect")
            def provide_token(dialect, conn_rec, cargs, cparams):
                current_token = auth_ref.get_current_token()
                if current_token:
                    cparams["password"] = current_token
                else:
                    L.error("No current token available for database connection")
                    raise RuntimeError("No OAuth token available")

            self.session_factory = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            L.info(f"Lakebase engine initialized for {conn_info['database_name']}")

        except Exception as e:
            L.error(f"Error initializing Lakebase engine: {e}")
            raise RuntimeError(f"Failed to initialize Lakebase engine: {e}") from e

    # -- query methods --------------------------------------------------

    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        async with self.get_session() as session:
            try:
                result = await session.execute(text(query), params or {})
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                L.error(f"Query execution failed: {e}")
                raise

    async def execute_query_to_dataframe(self, query: str, params: Optional[Dict[str, Any]] = None) -> DataFrame:
        result = await self.execute_query(query, params)
        if result.returns_rows:
            rows = result.fetchall()
            columns = result.keys()
            return DataFrame(rows, columns=columns)
        return DataFrame()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self.session_factory is None:
            raise RuntimeError("Session factory not initialized")

        async with self.session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                L.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()

    # -- health / diagnostics -------------------------------------------

    async def health_check(self) -> bool:
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
                L.info("Lakebase connection health check passed")
                return True
        except Exception as e:
            L.error(f"Lakebase health check failed: {e}")
            return False

    def check_database_exists(self) -> bool:
        try:
            return self.auth.check_instance_exists()
        except Exception as e:
            L.error(f"Error checking database existence: {e}")
            return False

    def get_connection_info(self) -> Dict[str, Any]:
        base_info = self.auth.get_connection_info()
        token_info = self.auth.get_token_info()
        base_info.update(token_info)
        base_info.update({
            "engine_initialized": self.engine is not None,
            "session_factory_initialized": self.session_factory is not None,
        })
        return base_info


# ---------------------------------------------------------------------------
# Runtime singleton -- set by LakebaseFactory, read by repositories / services
# ---------------------------------------------------------------------------

_connector: Optional[LakebaseConnector] = None


def get_lakebase_connector() -> Optional[LakebaseConnector]:
    """Return the shared LakebaseConnector instance (None before initialization)."""
    return _connector


def set_lakebase_connector(connector: LakebaseConnector) -> None:
    """Store the shared LakebaseConnector instance (called by LakebaseFactory)."""
    global _connector
    _connector = connector
