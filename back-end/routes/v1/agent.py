"""
Agent routes — Model Serving chat via WebSocket and REST.

WebSocket /api/v1/agent/ws   – streaming chat (token-by-token deltas)
POST     /api/v1/agent/chat  – non-streaming chat (for testing / simple clients)

When a `template_id` is provided (query param), the system prompt is injected
with the structure fields, template HTML, and SQL context so the agent can
give precise help with Mustache and data queries.
"""

import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query, Request

from common.authorization import get_user_email, check_template_read_access
from services.agent import AgentService
from services.prompt_builder import build_report_agent_prompt
from common.config import get_model_serving_endpoint
from common.logger import log as L
from models.agent import ChatMessage, ChatRequest, ChatResponse
from repositories.projects import ProjectsRepository
from repositories.structures import StructuresRepository
from repositories.templates import TemplatesRepository

router = APIRouter(prefix="/agent", tags=["agent"])


async def _build_service(template_id: Optional[UUID] = None) -> AgentService:
    """Create an AgentService, optionally with a template-aware system prompt."""
    if not template_id:
        return AgentService()

    tmpl_repo = TemplatesRepository()
    struct_repo = StructuresRepository()

    template = await tmpl_repo.get_by_id(template_id)
    if not template:
        return AgentService()

    structure = await struct_repo.get_by_id(template.structure_id)
    if not structure:
        return AgentService()

    prompt = build_report_agent_prompt(structure, template)
    return AgentService(system_prompt=prompt)


# ── POST (non-streaming) ─────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse, operation_id="agentChat")
async def agent_chat(req: ChatRequest, request: Request, template_id: Optional[UUID] = Query(None)):
    """
    Chat completion.

    Send a list of messages and receive the full response at once.
    Pass `template_id` query param to get context-aware Mustache/SQL help.
    """
    email = get_user_email(request)
    if template_id:
        await check_template_read_access(
            template_id, email,
            TemplatesRepository(), StructuresRepository(), ProjectsRepository(),
        )

    if not req.messages:
        raise HTTPException(status_code=400, detail="messages list is required")

    L.info(f"[agent/chat] {len(req.messages)} messages, temp={req.temperature}, max_tokens={req.max_tokens}")

    try:
        service = await _build_service(template_id)
        result = await service.get_response(
            messages=req.messages,
            temperature=req.temperature or 0.7,
            max_tokens=req.max_tokens or 4096,
        )
        return ChatResponse(
            success=True,
            content=result.content,
            usage=result.usage,
            model=get_model_serving_endpoint(),
        )
    except Exception:
        L.exception("Agent chat error")
        raise HTTPException(status_code=502, detail="Agent service unavailable")


# ── WebSocket ─────────────────────────────────────────────────────────────

def _get_ws_user_email(websocket: WebSocket) -> str:
    """Extract the authenticated user's email from WebSocket headers."""
    from common.config import is_development

    email = websocket.headers.get("X-Forwarded-Email")
    if not email and is_development():
        email = "dev.user@databricks.com"
    return email or ""


@router.websocket("/ws")
async def agent_websocket(websocket: WebSocket, template_id: Optional[UUID] = Query(None)):
    """
    WebSocket endpoint for streaming chat completions.

    Pass `template_id` query param to get context-aware Mustache/SQL help.

    Protocol:
        -> Server sends on connect:
            {"type": "connected", "model": "<endpoint>"}

        <- Client sends a message:
            {"type": "message", "content": "Hello!", "stream": true}

        -> If stream=true (default), server streams token-by-token:
            {"type": "delta", "content": "Hi"}        (repeated)
            {"type": "done", "usage": {...}}           (once, at the end)

        -> If stream=false, server sends full response:
            {"type": "response", "content": "Hi there!", "usage": {...}}

        -> On error:
            {"type": "error", "message": "..."}

        <- Any other message type:
            -> {"type": "pong"}
    """
    # Authenticate before accepting
    email = _get_ws_user_email(websocket)
    if not email:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    if template_id:
        try:
            await check_template_read_access(
                template_id, email,
                TemplatesRepository(), StructuresRepository(), ProjectsRepository(),
            )
        except HTTPException:
            await websocket.close(code=4003, reason="Access denied")
            return

    await websocket.accept()
    endpoint = get_model_serving_endpoint()
    L.info(f"[agent/ws] Client connected, model={endpoint}")

    await websocket.send_text(json.dumps({
        "type": "connected",
        "model": endpoint,
    }))

    conversation: list[ChatMessage] = []
    service = await _build_service(template_id)

    try:
        while True:
            raw = await websocket.receive_text()

            # ── Parse incoming message ────────────────────────────────
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                L.warning("[agent/ws] Invalid JSON received")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON",
                }))
                continue

            msg_type = msg.get("type")
            if msg_type != "message":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            content = (msg.get("content") or "").strip()
            if not content:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Empty message content",
                }))
                continue

            # ── Append user message to history ────────────────────────
            conversation.append(ChatMessage(role="user", content=content))
            stream = msg.get("stream", True)
            L.info(f"[agent/ws] User message ({len(content)} chars), history={len(conversation)}, stream={stream}")

            # ── Get or stream the response ────────────────────────────
            try:

                if stream:
                    # Streaming — send deltas token-by-token
                    full_response = ""
                    async for chunk_type, chunk_content, chunk_payload in service.stream_response(conversation):
                        if chunk_type == "delta" and chunk_content:
                            full_response += chunk_content
                            await websocket.send_text(json.dumps({
                                "type": "delta",
                                "content": chunk_content,
                            }))
                        elif chunk_type == "done":
                            await websocket.send_text(json.dumps({
                                "type": "done",
                                "usage": chunk_payload,
                            }))
                else:
                    # Non-streaming — send full response at once
                    result = await service.get_response(conversation)
                    full_response = result.content or ""
                    await websocket.send_text(json.dumps({
                        "type": "response",
                        "content": result.content,
                        "usage": result.usage,
                    }))

            except Exception:
                L.exception("[agent/ws] Chat error")
                full_response = ""
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "An error occurred processing your request",
                }))
                continue

            # ── Append assistant response to history ──────────────────
            if full_response:
                conversation.append(ChatMessage(role="assistant", content=full_response))
                L.info(f"[agent/ws] Assistant response ({len(full_response)} chars)")

    except WebSocketDisconnect:
        L.info("[agent/ws] Client disconnected")
