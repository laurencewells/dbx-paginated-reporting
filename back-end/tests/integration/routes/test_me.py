"""
Integration tests for the /api/v1/me endpoint.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest


class TestGetMe:
    @pytest.mark.asyncio
    async def test_me_returns_200(self, async_client):
        with patch("routes.v1.me.is_development", return_value=True):
            response = await async_client.get("/api/v1/me")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_me_returns_dev_defaults_in_dev_mode(self, async_client):
        """In dev mode without headers, the endpoint should return dev fallback values."""
        with patch("routes.v1.me.is_development", return_value=True):
            response = await async_client.get("/api/v1/me")
        data = response.json()
        assert data["email"] == "dev.user@databricks.com"
        assert data["username"] == "Development User"

    @pytest.mark.asyncio
    async def test_me_uses_forwarded_headers_when_present(self, async_client):
        with patch("routes.v1.me.is_development", return_value=False):
            response = await async_client.get(
                "/api/v1/me",
                headers={
                    "X-Forwarded-Email": "alice@example.com",
                    "X-Forwarded-Preferred-Username": "Alice Smith",
                    "X-Real-Ip": "10.0.0.1",
                },
            )
        data = response.json()
        assert data["email"] == "alice@example.com"
        assert data["username"] == "Alice Smith"
        assert data["ip"] == "10.0.0.1"

    @pytest.mark.asyncio
    async def test_me_response_schema_has_required_keys(self, async_client):
        with patch("routes.v1.me.is_development", return_value=True):
            response = await async_client.get("/api/v1/me")
        data = response.json()
        assert "email" in data
        assert "username" in data
        assert "ip" in data
