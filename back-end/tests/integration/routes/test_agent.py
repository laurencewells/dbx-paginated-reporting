"""
Integration tests for the /api/v1/agent routes.

POST /agent/chat  — non-streaming REST endpoint
WebSocket /agent/ws — streaming endpoint

AgentService and auth helpers are mocked; no real Model Serving calls are made.
"""
from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.testclient import TestClient

from models.agent import ChatResult

TEMPLATE_ID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _chat_result(content: str = "Hello!") -> ChatResult:
    return ChatResult(content=content, usage={"input_tokens": 5, "output_tokens": 10})


def _mock_service(*, content: str = "Hello!", stream_chunks=None):
    """Return a mock AgentService."""
    svc = MagicMock()
    svc.get_response = AsyncMock(return_value=_chat_result(content))

    async def _stream(messages, **kwargs):
        chunks = stream_chunks or [
            ("delta", "Hello", None),
            ("done", None, {"input_tokens": 5, "output_tokens": 10}),
        ]
        for chunk in chunks:
            yield chunk

    svc.stream_response = _stream
    return svc


def _allow_template_access():
    return patch("routes.v1.agent.check_template_read_access", return_value=None, new_callable=AsyncMock)


def _deny_template_access():
    from fastapi import HTTPException
    return patch(
        "routes.v1.agent.check_template_read_access",
        side_effect=HTTPException(status_code=403, detail="Access denied"),
        new_callable=AsyncMock,
    )


def _patch_build_service(svc):
    return patch("routes.v1.agent._build_service", return_value=svc, new_callable=AsyncMock)


# ---------------------------------------------------------------------------
# Sync test client fixture (needed for WebSocket support)
# ---------------------------------------------------------------------------


@pytest.fixture()
def sync_client():
    with (
        patch("common.factories.lakebase.LakebaseFactory.initialize", new_callable=AsyncMock),
        patch("common.factories.scheduler.SchedulerFactory.scheduler", new_callable=MagicMock),
        patch("apscheduler.schedulers.asyncio.AsyncIOScheduler.start"),
        patch("apscheduler.schedulers.asyncio.AsyncIOScheduler.shutdown"),
        patch("apscheduler.schedulers.asyncio.AsyncIOScheduler.running", new=False),
    ):
        from app import app
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


# ---------------------------------------------------------------------------
# POST /agent/chat
# ---------------------------------------------------------------------------


class TestAgentChat:
    @pytest.mark.asyncio
    async def test_returns_200_with_response(self, async_client):
        svc = _mock_service(content="Hello!")
        with _patch_build_service(svc):
            response = await async_client.post(
                "/api/v1/agent/chat",
                json={"messages": [{"role": "user", "content": "Hi"}]},
            )
        assert response.status_code == 200
        assert response.json()["content"] == "Hello!"
        assert response.json()["success"] is True

    @pytest.mark.asyncio
    async def test_returns_model_endpoint_in_response(self, async_client):
        svc = _mock_service()
        with _patch_build_service(svc), patch("routes.v1.agent.get_model_serving_endpoint", return_value="my-endpoint"):
            response = await async_client.post(
                "/api/v1/agent/chat",
                json={"messages": [{"role": "user", "content": "Hi"}]},
            )
        assert response.json()["model"] == "my-endpoint"

    @pytest.mark.asyncio
    async def test_returns_400_when_messages_empty(self, async_client):
        response = await async_client.post(
            "/api/v1/agent/chat",
            json={"messages": []},
        )
        assert response.status_code == 400
        assert "messages" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_returns_422_when_messages_missing(self, async_client):
        response = await async_client.post("/api/v1/agent/chat", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_502_on_service_error(self, async_client):
        svc = MagicMock()
        svc.get_response = AsyncMock(side_effect=Exception("Model Serving down"))
        with _patch_build_service(svc):
            response = await async_client.post(
                "/api/v1/agent/chat",
                json={"messages": [{"role": "user", "content": "Hi"}]},
            )
        assert response.status_code == 502

    @pytest.mark.asyncio
    async def test_with_template_id_checks_access(self, async_client):
        svc = _mock_service()
        with _patch_build_service(svc), _allow_template_access() as mock_check:
            await async_client.post(
                f"/api/v1/agent/chat?template_id={TEMPLATE_ID}",
                json={"messages": [{"role": "user", "content": "Hi"}]},
            )
        mock_check.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_with_template_id_returns_403_on_no_access(self, async_client):
        with _deny_template_access():
            response = await async_client.post(
                f"/api/v1/agent/chat?template_id={TEMPLATE_ID}",
                json={"messages": [{"role": "user", "content": "Hi"}]},
            )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_without_template_id_skips_access_check(self, async_client):
        svc = _mock_service()
        with _patch_build_service(svc), _allow_template_access() as mock_check:
            await async_client.post(
                "/api/v1/agent/chat",
                json={"messages": [{"role": "user", "content": "Hi"}]},
            )
        mock_check.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_usage_included_in_response(self, async_client):
        svc = _mock_service()
        with _patch_build_service(svc):
            response = await async_client.post(
                "/api/v1/agent/chat",
                json={"messages": [{"role": "user", "content": "Hi"}]},
            )
        assert "usage" in response.json()


# ---------------------------------------------------------------------------
# WebSocket /agent/ws
# ---------------------------------------------------------------------------


class TestAgentWebSocket:
    def test_connect_receives_connected_message(self, sync_client):
        svc = _mock_service()
        with _patch_build_service(svc):
            with sync_client.websocket_connect("/api/v1/agent/ws") as ws:
                msg = json.loads(ws.receive_text())
        assert msg["type"] == "connected"
        assert "model" in msg

    def test_streaming_message_receives_delta_and_done(self, sync_client):
        svc = _mock_service(stream_chunks=[
            ("delta", "Hello", None),
            ("delta", " world", None),
            ("done", None, {"input_tokens": 5, "output_tokens": 10}),
        ])
        with _patch_build_service(svc):
            with sync_client.websocket_connect("/api/v1/agent/ws") as ws:
                ws.receive_text()  # connected
                ws.send_text(json.dumps({"type": "message", "content": "Hi", "stream": True}))
                messages = []
                for _ in range(3):  # 2 deltas + 1 done
                    messages.append(json.loads(ws.receive_text()))

        types = [m["type"] for m in messages]
        assert "delta" in types
        assert "done" in types

    def test_non_streaming_message_receives_response(self, sync_client):
        svc = _mock_service(content="Full response")
        with _patch_build_service(svc):
            with sync_client.websocket_connect("/api/v1/agent/ws") as ws:
                ws.receive_text()  # connected
                ws.send_text(json.dumps({"type": "message", "content": "Hi", "stream": False}))
                msg = json.loads(ws.receive_text())

        assert msg["type"] == "response"
        assert msg["content"] == "Full response"

    def test_invalid_json_receives_error(self, sync_client):
        svc = _mock_service()
        with _patch_build_service(svc):
            with sync_client.websocket_connect("/api/v1/agent/ws") as ws:
                ws.receive_text()  # connected
                ws.send_text("not valid json{{{")
                msg = json.loads(ws.receive_text())

        assert msg["type"] == "error"
        assert "JSON" in msg["message"]

    def test_non_message_type_receives_pong(self, sync_client):
        svc = _mock_service()
        with _patch_build_service(svc):
            with sync_client.websocket_connect("/api/v1/agent/ws") as ws:
                ws.receive_text()  # connected
                ws.send_text(json.dumps({"type": "ping"}))
                msg = json.loads(ws.receive_text())

        assert msg["type"] == "pong"

    def test_empty_content_receives_error(self, sync_client):
        svc = _mock_service()
        with _patch_build_service(svc):
            with sync_client.websocket_connect("/api/v1/agent/ws") as ws:
                ws.receive_text()  # connected
                ws.send_text(json.dumps({"type": "message", "content": "   "}))
                msg = json.loads(ws.receive_text())

        assert msg["type"] == "error"

    def test_with_template_id_checks_access_on_connect(self, sync_client):
        svc = _mock_service()
        with _patch_build_service(svc), _allow_template_access() as mock_check:
            with sync_client.websocket_connect(f"/api/v1/agent/ws?template_id={TEMPLATE_ID}") as ws:
                ws.receive_text()  # connected
        mock_check.assert_awaited_once()

    def test_access_denied_closes_websocket(self, sync_client):
        with _deny_template_access():
            with pytest.raises(Exception):
                # WebSocket should be closed with 4003 before accepting
                with sync_client.websocket_connect(f"/api/v1/agent/ws?template_id={TEMPLATE_ID}") as ws:
                    ws.receive_text()
