"""
Integration tests for the healthcheck and database-healthcheck routes.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestHealthcheck:
    @pytest.mark.asyncio
    async def test_healthcheck_returns_200(self, async_client):
        response = await async_client.get("/api/v1/healthcheck")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_healthcheck_returns_ok_status(self, async_client):
        response = await async_client.get("/api/v1/healthcheck")
        data = response.json()
        assert data["status"] == "OK"

    @pytest.mark.asyncio
    async def test_healthcheck_returns_timestamp(self, async_client):
        response = await async_client.get("/api/v1/healthcheck")
        data = response.json()
        assert "timestamp" in data
        assert data["timestamp"]  # non-empty


class TestDatabaseHealthcheck:
    @pytest.mark.asyncio
    async def test_database_healthcheck_returns_200_when_unconfigured(self, async_client):
        """When Lakebase is not configured, the endpoint still returns 200 with unhealthy status."""
        with (
            patch("routes.v1.databasehealthcheck.is_lakebase_configured", return_value=False),
            patch("routes.v1.databasehealthcheck.get_lakebase_connector", return_value=None),
            patch("routes.v1.databasehealthcheck.is_development", return_value=False),
        ):
            response = await async_client.get("/api/v1/databasehealthcheck")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_database_healthcheck_reports_unhealthy_when_not_configured(self, async_client):
        with (
            patch("routes.v1.databasehealthcheck.is_lakebase_configured", return_value=False),
            patch("routes.v1.databasehealthcheck.get_lakebase_connector", return_value=None),
            patch("routes.v1.databasehealthcheck.is_development", return_value=False),
        ):
            response = await async_client.get("/api/v1/databasehealthcheck")
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["lakebase_configured"] is False

    @pytest.mark.asyncio
    async def test_database_healthcheck_reports_healthy_when_all_checks_pass(self, async_client):
        mock_connector = MagicMock()
        mock_connector.check_database_exists.return_value = True
        mock_connector.health_check = AsyncMock(return_value=True)
        mock_connector.get_connection_info.return_value = {}

        with (
            patch("routes.v1.databasehealthcheck.is_lakebase_configured", return_value=True),
            patch("routes.v1.databasehealthcheck.get_lakebase_connector", return_value=mock_connector),
            patch("routes.v1.databasehealthcheck.is_development", return_value=False),
        ):
            response = await async_client.get("/api/v1/databasehealthcheck")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["lakebase_configured"] is True
        assert data["database_instance_exists"] is True
        assert data["connection_healthy"] is True

    @pytest.mark.asyncio
    async def test_database_healthcheck_returns_200_even_on_exception(self, async_client):
        with (
            patch("routes.v1.databasehealthcheck.is_lakebase_configured", side_effect=Exception("boom")),
            patch("routes.v1.databasehealthcheck.is_development", return_value=False),
        ):
            response = await async_client.get("/api/v1/databasehealthcheck")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
