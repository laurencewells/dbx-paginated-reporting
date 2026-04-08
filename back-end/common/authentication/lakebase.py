"""
Lakebase PostgreSQL authentication for Databricks applications using workspace API.

Deployment model
----------------
The DABs postgres app resource is bypassed entirely because the database resource path
contains an opaque auto-generated ID (db-8uv1-...) that cannot be predicted at bundle
authoring time, creating a chicken-and-egg dependency.

Instead, connection details are passed as explicit env vars in databricks.yml / app.yaml:

    LAKEBASE_ENDPOINT   full endpoint resource path, e.g.
                        'projects/my-project/branches/main/endpoints/primary'
    PGDATABASE          database name (e.g. 'databricks_postgres')
    PGUSER              service-principal client ID, used as the DB username
    PGPORT              port (default 5432)
    PGSSLMODE           SSL mode (default 'require')

The hostname is NOT hard-coded or read from PGHOST. It is resolved at startup by
calling w.postgres.get_endpoint(name=LAKEBASE_ENDPOINT), which returns the live
endpoint object including its DNS hostname. This approach is consistent with the
Autoscaling Postgres SDK APIs described in the Databricks documentation.

Role creation / grants
----------------------
Because the postgres app resource is bypassed, DABs cannot automatically create
a Postgres role for the app's service principal. An initialisation notebook (run
once as the project owner, before the app first connects) must create the role and
grant the required permissions.

Ref: https://databricks-sdk-py.readthedocs.io/en/latest/workspace/postgres/postgres.html
     https://docs.databricks.com/aws/en/oltp/projects/authentication
"""

import asyncio
import os
import time
from typing import Optional
from common.authentication.workspace import WorkspaceAuthentication
from common.logger import log as L
from common.config import get_lakebase_config


class LakebaseAuthentication:
    """
    Handles authentication to Databricks Lakebase PostgreSQL instances.

    Resolves the postgres endpoint and generates short-lived OAuth tokens using
    the Databricks workspace SDK. Tokens are refreshed automatically before
    expiry using the expire_time returned by generate_database_credential.

    Required env vars:
        LAKEBASE_ENDPOINT   Full endpoint resource path.
        PGDATABASE          Database name.
        PGUSER              Service-principal client ID (DB username).

    Optional env vars:
        LAKEBASE_INSTANCE_NAME  Project name — only needed when LAKEBASE_ENDPOINT
                                is not set (triggers SDK endpoint discovery).
        LAKEBASE_BRANCH         Branch name for discovery fallback (default: 'main').
        PGPORT                  Port (default 5432).
        PGSSLMODE               SSL mode (default 'require').
    """

    def __init__(self, bearer: Optional[str] = None) -> None:
        config = get_lakebase_config()

        self.database_name: Optional[str] = config.get("database_name")
        self.port: int = config.get("port", 5432)
        self.bearer = bearer

        self._current_token: Optional[str] = None
        self._last_token_refresh: float = 0
        self._token_expire_time: Optional[float] = None
        self._token_refresh_task: Optional[asyncio.Task] = None

        self.client = WorkspaceAuthentication(bearer=self.bearer).client
        self._cached_username: Optional[str] = self._resolve_username()

        # Resolve and cache the endpoint resource path.
        # This is the canonical input for both generate_database_credential and
        # get_endpoint (for DNS resolution).
        self._endpoint: str = self._resolve_endpoint(config)

        # Resolve and cache the hostname by calling get_endpoint.
        # We do this once at startup so that every new connection gets the
        # correct host without an extra round-trip.
        self._host: Optional[str] = self._resolve_host()

        L.info(
            f"[Lakebase Auth] endpoint={self._endpoint!r} "
            f"host={self._host!r} "
            f"database={self.database_name!r} "
            f"username={self._cached_username!r}"
        )

    # ------------------------------------------------------------------
    # Endpoint resolution
    # ------------------------------------------------------------------

    def _resolve_endpoint(self, config: dict) -> str:
        """
        Return the full endpoint resource path for credential generation.

        Resolution order:
        1. LAKEBASE_ENDPOINT env var — explicit, recommended for production.
        2. SDK discovery — list_endpoints for the configured project/branch.
        3. Convention fallback — projects/{project}/branches/{branch}/endpoints/primary.
        """
        explicit = config.get("endpoint") or os.getenv("LAKEBASE_ENDPOINT")
        if explicit:
            L.info(f"[Lakebase Auth] Using LAKEBASE_ENDPOINT: {explicit!r}")
            return explicit

        # Derive project name for SDK discovery / convention fallback
        project_name = config.get("instance_name") or os.getenv("LAKEBASE_INSTANCE_NAME")
        if not project_name:
            raise ValueError(
                "Set LAKEBASE_ENDPOINT (preferred) or LAKEBASE_INSTANCE_NAME "
                "so the authenticator can resolve the Lakebase endpoint."
            )

        # Strip DNS suffix if someone passed PGHOST as LAKEBASE_INSTANCE_NAME
        for suffix in (".database.azuredatabricks.net", ".database.databricks.net"):
            if project_name.endswith(suffix):
                project_name = project_name[: -len(suffix)]
                break

        branch_id = os.getenv("LAKEBASE_BRANCH", "main")
        branch_resource = f"projects/{project_name}/branches/{branch_id}"

        # SDK discovery
        try:
            endpoints = list(self.client.postgres.list_endpoints(parent=branch_resource))
            if endpoints:
                endpoint = endpoints[0].name
                L.info(f"[Lakebase Auth] Discovered endpoint via SDK: {endpoint!r}")
                return endpoint
            L.warning(f"[Lakebase Auth] No endpoints found for {branch_resource!r}; using convention")
        except Exception as exc:
            L.warning(f"[Lakebase Auth] list_endpoints failed for {branch_resource!r}: {exc}; using convention")

        # Convention fallback
        endpoint = f"{branch_resource}/endpoints/primary"
        L.info(f"[Lakebase Auth] Using convention endpoint: {endpoint!r}")
        return endpoint

    # ------------------------------------------------------------------
    # Host resolution
    # ------------------------------------------------------------------

    def _resolve_host(self) -> Optional[str]:
        """
        Resolve the DNS hostname for the endpoint by calling get_endpoint.

        The host lives at endpoint.status.hosts.host (EndpointStatus → EndpointHosts).
        Falls back to PGHOST env var if the SDK call fails or the status is not yet
        populated (endpoint still initialising).
        """
        try:
            endpoint_obj = self.client.postgres.get_endpoint(name=self._endpoint)
            status = endpoint_obj.status
            if status and status.hosts and status.hosts.host:
                host = status.hosts.host
                L.info(f"[Lakebase Auth] Resolved host from endpoint.status.hosts.host: {host!r}")
                return host
            L.warning(
                f"[Lakebase Auth] get_endpoint returned no host "
                f"(status={status!r}); endpoint may still be initialising"
            )
        except Exception as exc:
            L.warning(f"[Lakebase Auth] get_endpoint({self._endpoint!r}) failed: {exc}")

        # Fallback — PGHOST may be present in local dev or if still using the
        # postgres app resource
        pghost = os.getenv("PGHOST")
        if pghost:
            L.info(f"[Lakebase Auth] Falling back to PGHOST={pghost!r}")
            return pghost

        L.error("[Lakebase Auth] Could not resolve hostname — connections will fail")
        return None

    # ------------------------------------------------------------------
    # Username
    # ------------------------------------------------------------------

    def _resolve_username(self) -> Optional[str]:
        """Resolve the DB username once at init time."""
        # PGUSER is the service-principal client ID injected by the platform / app.yaml
        username = os.getenv("PGUSER") or os.getenv("DATABRICKS_CLIENT_ID")
        if username:
            return username
        try:
            return self.client.current_user.me().user_name
        except Exception as exc:
            L.warning(f"[Lakebase Auth] Could not resolve username: {exc}")
            return None

    # ------------------------------------------------------------------
    # Credential generation
    # ------------------------------------------------------------------

    def generate_database_credential(self) -> str:
        """
        Generate an OAuth token for the Lakebase endpoint.

        Stores expire_time from the response so the background refresh task
        can wake up precisely rather than sleeping a fixed interval.

        Returns:
            str: OAuth token to use as the database password.

        Raises:
            Exception: If the SDK call fails.
        """
        try:
            cred = self.client.postgres.generate_database_credential(
                endpoint=self._endpoint
            )
            self._current_token = cred.token
            self._last_token_refresh = time.time()

            if cred.expire_time is not None:
                # expire_time is a protobuf Timestamp — use ToSeconds() for a Unix timestamp
                self._token_expire_time = cred.expire_time.ToSeconds()
                remaining = (self._token_expire_time - time.time()) / 60
                L.info(f"[Lakebase Auth] Token generated; expires in {remaining:.1f} min")
            else:
                self._token_expire_time = None
                L.info("[Lakebase Auth] Token generated (no expire_time in response)")

            return self._current_token
        except Exception as exc:
            L.error(f"[Lakebase Auth] generate_database_credential failed: {exc}")
            raise

    def get_current_token(self) -> Optional[str]:
        """Return the cached OAuth token, or None if not yet generated."""
        return self._current_token

    def get_token_info(self) -> dict:
        """Return token status and timing info for health / monitoring endpoints."""
        now = time.time()
        expires_in = (
            (self._token_expire_time - now) / 60
            if self._token_expire_time is not None else None
        )
        return {
            "token_exists": self._current_token is not None,
            "last_token_refresh": self._last_token_refresh,
            "token_age_minutes": (now - self._last_token_refresh) / 60 if self._last_token_refresh else 0,
            "token_expire_time": self._token_expire_time,
            "token_expires_in_minutes": expires_in,
        }

    # ------------------------------------------------------------------
    # Connection info
    # ------------------------------------------------------------------

    def get_connection_info(self) -> dict:
        """
        Return connection parameters for the SQLAlchemy engine.

        The host is the value resolved at startup from get_endpoint; all other
        values come from env vars set in databricks.yml / app.yaml.
        """
        return {
            "host": self._host,
            "port": int(os.getenv("PGPORT", str(self.port))),
            "database_name": os.getenv("PGDATABASE") or self.database_name,
            "username": os.getenv("PGUSER") or self._cached_username,
        }

    def check_instance_exists(self) -> bool:
        """Return True if the endpoint is reachable via the SDK."""
        try:
            self.client.postgres.get_endpoint(name=self._endpoint)
            return True
        except Exception as exc:
            L.error(f"[Lakebase Auth] Could not reach endpoint {self._endpoint!r}: {exc}")
            return False

    # ------------------------------------------------------------------
    # Background token refresh
    # ------------------------------------------------------------------

    async def start_token_refresh(self):
        """Start the background refresh task (call during app startup)."""
        if self._token_refresh_task is None or self._token_refresh_task.done():
            self._token_refresh_task = asyncio.create_task(self._refresh_token_background())
            L.info("[Lakebase Auth] Background token refresh task started")

    async def stop_token_refresh(self):
        """Stop the background refresh task (call during app shutdown)."""
        if self._token_refresh_task and not self._token_refresh_task.done():
            self._token_refresh_task.cancel()
            try:
                await self._token_refresh_task
            except asyncio.CancelledError:
                pass
            L.info("[Lakebase Auth] Background token refresh task stopped")

    async def _refresh_token_background(self):
        """
        Refresh the OAuth token before it expires.

        When expire_time is available the task sleeps until 2 minutes before
        expiry (minimum 60 s). When expire_time is absent it falls back to a
        50-minute fixed interval (safe within the 1-hour token lifetime).
        On error the task backs off for 60 seconds before retrying.
        """
        while True:
            try:
                now = time.time()
                if self._token_expire_time is not None and self._token_expire_time > now:
                    sleep_secs = max(60.0, self._token_expire_time - now - 120)
                else:
                    sleep_secs = 50 * 60

                L.info(f"[Lakebase Auth] Next token refresh in {sleep_secs:.0f}s")
                await asyncio.sleep(sleep_secs)

                L.info("[Lakebase Auth] Refreshing OAuth token")
                self.generate_database_credential()
                L.info("[Lakebase Auth] Token refreshed successfully")

            except asyncio.CancelledError:
                raise
            except Exception as exc:
                L.error(f"[Lakebase Auth] Background token refresh failed: {exc}")
                await asyncio.sleep(60)

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    @property
    def is_configured(self) -> bool:
        """Return True if the endpoint is configured."""
        return bool(self._endpoint)
