"""
Shared pytest fixtures for the Databricks Paginated Reporting test suite.

All fixtures mock external dependencies (Lakebase, Databricks Workspace,
SQL Warehouse) so no real network calls are made.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# ---------------------------------------------------------------------------
# Ensure environment is clearly non-production before any import of app code
# ---------------------------------------------------------------------------
os.environ.setdefault("ENV", "DEV")
# Prevent LakebaseFactory from doing real auth on startup
os.environ.setdefault("LAKEBASE_INSTANCE_NAME", "")
os.environ.setdefault("DATABRICKS_HOST", "https://test.databricks.com")
os.environ.setdefault("DATABRICKS_TOKEN", "fake-token-for-tests")
os.environ.setdefault("DATABRICKS_WAREHOUSE_ID", "fake-warehouse-id")


# ---------------------------------------------------------------------------
# Sentinel datetimes used across fixtures
# ---------------------------------------------------------------------------
NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Sample domain-object builders
# ---------------------------------------------------------------------------

def make_template_row(
    *,
    id: str | None = None,
    name: str = "Test Template",
    structure_id: str | None = None,
    html_content: str = "<p>{{rows}}</p>",
    created_at=None,
    updated_at=None,
):
    """Return a tuple that mimics a DB row for the templates table."""
    return (
        id or str(uuid.uuid4()),
        name,
        structure_id or str(uuid.uuid4()),
        html_content,
        created_at or NOW,
        updated_at or NOW,
    )


# ---------------------------------------------------------------------------
# Mock result objects for SQLAlchemy execute_query return values
# ---------------------------------------------------------------------------

def make_query_result(rows=None, *, rowcount: int = 1):
    """Build a mock that mimics a SQLAlchemy CursorResult."""
    result = MagicMock()
    if rows is None:
        rows = []
    result.fetchall.return_value = rows
    result.fetchone.return_value = rows[0] if rows else None
    result.rowcount = rowcount
    return result


# ---------------------------------------------------------------------------
# Lakebase connector mock
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_lakebase_connector():
    """Return a MagicMock that stands in for a LakebaseConnector instance."""
    connector = MagicMock()
    connector.execute_query = AsyncMock()
    connector.health_check = AsyncMock(return_value=True)
    connector.check_database_exists = MagicMock(return_value=True)
    connector.get_connection_info = MagicMock(return_value={"host": "test-host", "port": 5432})
    return connector


# ---------------------------------------------------------------------------
# FastAPI app fixture (patches Lakebase so lifespan doesn't crash)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    """
    FastAPI application instance (session-scoped; imported once).

    Infrastructure is mocked at the test-session level so the module
    import itself does not trigger real Databricks connections.
    """
    from app import app as _app  # noqa: PLC0415

    return _app


@pytest_asyncio.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTPX client wired to the FastAPI app.

    The LakebaseFactory.initialize() is patched to a no-op so the app
    starts without real Databricks credentials.
    """
    with (
        patch("common.factories.lakebase.LakebaseFactory.initialize", new_callable=AsyncMock),
        patch("common.factories.scheduler.SchedulerFactory.scheduler", new_callable=MagicMock),
        patch("apscheduler.schedulers.asyncio.AsyncIOScheduler.start"),
        patch("apscheduler.schedulers.asyncio.AsyncIOScheduler.shutdown"),
        patch("apscheduler.schedulers.asyncio.AsyncIOScheduler.running", new=False),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client


@pytest.fixture
def dependency_overrides(app):
    """
    Yield the app's dependency_overrides dict for the duration of one test.

    Usage::

        def test_something(async_client, dependency_overrides):
            dependency_overrides[get_structures_repo] = lambda: mock_repo
            ...

    All overrides are cleared automatically when the test finishes.
    """
    yield app.dependency_overrides
    app.dependency_overrides.clear()
