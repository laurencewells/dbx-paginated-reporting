"""
Lakebase factory for database initialization and migrations.

This module handles Lakebase PostgreSQL bootstrapping including:
- Authentication initialization with retry / exponential backoff
- Connector initialization and token refresh
- Table creation and seeding via migrations

The factory creates and owns both the LakebaseAuthentication and
LakebaseConnector instances, then publishes the connector as a
runtime singleton via set_lakebase_connector().
"""

import asyncio

from common.logger import log as L
from common.config import is_lakebase_configured, get_lakebase_config
from common.authentication.lakebase import LakebaseAuthentication
from common.connectors.lakebase import (
    LakebaseConnector,
    set_lakebase_connector,
)
from migrations import (
    CREATE_APP_SCHEMA,
    CREATE_PROJECTS_TABLE,
    CREATE_PROJECTS_INDEXES,
    CREATE_PROJECT_SHARES_TABLE,
    CREATE_PROJECT_SHARES_INDEXES,
    CREATE_STRUCTURES_TABLE,
    CREATE_STRUCTURES_INDEXES,
    CREATE_TEMPLATES_TABLE,
    CREATE_TEMPLATES_INDEXES,
    CREATE_CONVERSATION_MESSAGES_TABLE,
    CREATE_CONVERSATION_MESSAGES_INDEXES,
    CREATE_IMAGES_TABLE,
    CREATE_IMAGES_INDEXES,
    SEED_PROJECTS,
    SEED_STRUCTURES,
    SEED_TEMPLATES,
)

_MAX_RETRIES = 4
_INITIAL_BACKOFF_SECONDS = 2


class LakebaseFactory:
    """
    Factory for initializing Lakebase PostgreSQL and running migrations.

    Owns the auth and connector lifecycle. After initialization the
    connector is published via set_lakebase_connector() so repositories
    can retrieve it with get_lakebase_connector().
    """

    def __init__(self):
        self.auth: LakebaseAuthentication | None = None
        self.connector: LakebaseConnector | None = None
        self._schema: str = get_lakebase_config().get("schema_name", "app")

    async def _initialize_auth(self) -> bool:
        """
        Create a LakebaseAuthentication instance with exponential backoff.

        Returns True on success, False after all retries exhausted.
        """
        L.info(f"[Lakebase] Initializing authentication (max {_MAX_RETRIES} attempts)...")
        backoff = _INITIAL_BACKOFF_SECONDS
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                L.info(f"[Lakebase] Auth init attempt {attempt}/{_MAX_RETRIES}")
                self.auth = LakebaseAuthentication()
                L.info(f"[Lakebase] Auth initialized successfully on attempt {attempt}")
                return True
            except Exception as e:
                if attempt < _MAX_RETRIES:
                    L.warning(
                        f"[Lakebase] Auth init attempt {attempt}/{_MAX_RETRIES} failed: {e} "
                        f"— retrying in {backoff}s"
                    )
                    await asyncio.sleep(backoff)
                    backoff *= 2
                else:
                    L.error(
                        f"[Lakebase] Auth init attempt {attempt}/{_MAX_RETRIES} failed: {e} "
                        f"— no retries remaining"
                    )

        L.error("[Lakebase] Authentication initialization failed after all retries")
        return False

    async def initialize(self) -> None:
        """
        Initialize auth, connector, token refresh, and run migrations.
        No-ops gracefully if Lakebase is not configured or the instance doesn't exist.
        """
        L.info("[Lakebase] === Starting Lakebase initialization ===")

        L.info("[Lakebase] Step 1/4: Checking configuration...")
        if not is_lakebase_configured():
            L.info("[Lakebase] Not configured — skipping database initialization")
            return
        L.info("[Lakebase] Configuration detected")

        L.info("[Lakebase] Step 2/4: Initializing authentication...")
        if not await self._initialize_auth():
            L.warning("[Lakebase] Authentication unavailable — database endpoints disabled")
            return

        try:
            L.info("[Lakebase] Step 3/4: Creating connector and starting token refresh...")
            self.connector = LakebaseConnector(auth=self.auth)
            set_lakebase_connector(self.connector)
            await self.auth.start_token_refresh()
            L.info("[Lakebase] Connector initialized with token refresh")

            L.info("[Lakebase] Step 4/4: Running database migrations...")
            await self._ensure_schema()
            await self._ensure_projects_table()
            await self._ensure_project_shares_table()
            await self._ensure_structures_table()
            await self._ensure_templates_table()
            await self._ensure_conversation_messages_table()
            await self._ensure_images_table()
            L.info("[Lakebase] === Lakebase initialization complete ===")
        except Exception as e:
            L.error(f"[Lakebase] Failed to initialize connector: {e}")
            L.warning("[Lakebase] Application will continue without Lakebase connectivity")

    async def shutdown(self) -> None:
        """Stop the Lakebase token refresh."""
        try:
            if self.auth:
                await self.auth.stop_token_refresh()
                L.info("Lakebase token refresh stopped")
        except Exception as e:
            L.error(f"Error stopping token refresh: {e}")

    # -- migration helpers -----------------------------------------------

    async def _run_migration(self, table_name: str, create_sql: str,
                              index_sql: str | None = None,
                              seed_sql: str | None = None) -> None:
        """Generic helper to create a table, optional indexes, and optional seed data."""
        try:
            check_result = await self.connector.execute_query(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = :schema AND table_name = :table_name",
                {"schema": self._schema, "table_name": table_name},
            )
            table_count = check_result.scalar()

            if table_count and table_count > 0:
                L.info(f"{table_name} table already exists — skipping migration")
                return

            L.info(f"{table_name} table not found — running migration")

            result = await self.connector.execute_query(create_sql)
            L.info(f"CREATE TABLE {table_name} result: rowcount={result.rowcount}")

            if index_sql:
                for statement in index_sql.split(";"):
                    cleaned = statement.strip()
                    if not cleaned:
                        continue
                    result = await self.connector.execute_query(cleaned)
                    L.info(f"CREATE INDEX result: rowcount={result.rowcount}")

            if seed_sql:
                result = await self.connector.execute_query(seed_sql)
                L.info(f"SEED {table_name} result: rowcount={result.rowcount}")

            L.info(f"{table_name} table created successfully")
        except Exception as e:
            L.error(f"Error ensuring {table_name} table: {e}")
            L.warning(f"Application will continue — {table_name} may not be available")

    async def _ensure_schema(self) -> None:
        """Create the application schema if it doesn't already exist."""
        try:
            sql = CREATE_APP_SCHEMA.format(schema=self._schema)
            await self.connector.execute_query(sql)
            L.info(f"Schema '{self._schema}' ensured")
        except Exception as e:
            L.error(f"Error creating schema '{self._schema}': {e}")
            raise

    async def _ensure_projects_table(self) -> None:
        await self._run_migration(
            "projects",
            CREATE_PROJECTS_TABLE,
            index_sql=CREATE_PROJECTS_INDEXES,
            seed_sql=SEED_PROJECTS,
        )

    async def _ensure_project_shares_table(self) -> None:
        await self._run_migration(
            "project_shares",
            CREATE_PROJECT_SHARES_TABLE,
            index_sql=CREATE_PROJECT_SHARES_INDEXES,
        )

    async def _ensure_structures_table(self) -> None:
        await self._run_migration(
            "structures",
            CREATE_STRUCTURES_TABLE,
            index_sql=CREATE_STRUCTURES_INDEXES,
            seed_sql=SEED_STRUCTURES,
        )

    async def _ensure_templates_table(self) -> None:
        await self._run_migration(
            "templates",
            CREATE_TEMPLATES_TABLE,
            index_sql=CREATE_TEMPLATES_INDEXES,
            seed_sql=SEED_TEMPLATES,
        )

    async def _ensure_conversation_messages_table(self) -> None:
        await self._run_migration(
            "conversation_messages",
            CREATE_CONVERSATION_MESSAGES_TABLE,
            index_sql=CREATE_CONVERSATION_MESSAGES_INDEXES,
        )

    async def _ensure_images_table(self) -> None:
        await self._run_migration(
            "images",
            CREATE_IMAGES_TABLE,
            index_sql=CREATE_IMAGES_INDEXES,
        )
