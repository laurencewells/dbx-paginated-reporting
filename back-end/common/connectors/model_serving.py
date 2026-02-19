"""
Connector for Databricks Model Serving endpoints.

Uses WorkspaceConnector for authentication and
WorkspaceClient.serving_endpoints.query() for chat completions.
Supports both non-streaming and streaming (via asyncio.Queue producer/consumer).
"""

import asyncio
import json
import threading
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import requests as http_requests
from databricks.sdk.service.serving import ChatMessage as SdkChatMessage, ChatMessageRole

from common.connectors.workspace import WorkspaceConnector
from common.config import get_model_serving_endpoint
from common.logger import log as L

_ROLE_MAP = {
    "system": ChatMessageRole.SYSTEM,
    "user": ChatMessageRole.USER,
    "assistant": ChatMessageRole.ASSISTANT,
}


class ModelServingConnector:
    """
    Connector for Databricks Model Serving chat completions.

    Delegates authentication to WorkspaceConnector and exposes both
    non-streaming and streaming methods for querying a chat/completions
    serving endpoint.

    Attributes:
        workspace: WorkspaceConnector instance
        client: Authenticated Databricks WorkspaceClient (from workspace connector)
        endpoint_name: The serving endpoint name (from config / env)
    """

    def __init__(self, workspace_connector: Optional[WorkspaceConnector] = None):
        """
        Initialize ModelServingConnector.

        Args:
            workspace_connector: Optional WorkspaceConnector instance.
                Created with defaults if omitted.
        """
        self.workspace = workspace_connector or WorkspaceConnector()
        self.client = self.workspace.client
        self.endpoint_name = get_model_serving_endpoint()
        L.info(f"ModelServingConnector initialized for endpoint '{self.endpoint_name}'")

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _build_sdk_messages(messages: List[Dict[str, str]]) -> List[SdkChatMessage]:
        """Convert plain dicts to SDK ChatMessage objects with enum roles."""
        return [
            SdkChatMessage(
                role=_ROLE_MAP[m["role"]],
                content=m.get("content") or "",
            )
            for m in messages
        ]

    @staticmethod
    def _parse_response(response: Any) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Extract (content, usage) from a QueryEndpointResponse.

        Handles SDK dataclass objects and plain dicts.

        Returns:
            Tuple of (full_content, usage_dict). Either may be None.
        """
        # Normalise to dict
        if hasattr(response, "as_dict"):
            response = response.as_dict()
        elif not isinstance(response, dict):
            response = {
                "choices": getattr(response, "choices", None),
                "usage": getattr(response, "usage", None),
            }

        # Extract content from choices
        content = None
        choices = response.get("choices")
        if choices and isinstance(choices, list) and len(choices) > 0:
            choice = choices[0]
            if isinstance(choice, dict):
                message = choice.get("message") or {}
                content = message.get("content") if isinstance(message, dict) else getattr(message, "content", None)
            else:
                message = getattr(choice, "message", None)
                content = getattr(message, "content", None) if message else None

        # Extract usage
        usage = None
        usage_raw = response.get("usage")
        if usage_raw:
            if isinstance(usage_raw, dict):
                usage = usage_raw
            else:
                usage = {
                    "prompt_tokens": getattr(usage_raw, "prompt_tokens", None),
                    "completion_tokens": getattr(usage_raw, "completion_tokens", None),
                    "total_tokens": getattr(usage_raw, "total_tokens", None),
                }

        return content, usage

    @staticmethod
    def _parse_chunk(chunk: Any) -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        """
        Extract (delta_content, finish_reason, usage) from a single streaming chunk.

        Handles SDK dataclass objects, plain dicts, and raw SSE data strings.

        Returns:
            (delta_content, finish_reason, usage_dict) — any element may be None.
        """
        # ── Handle raw SSE string ────────────────────────────────────
        if isinstance(chunk, (str, bytes)):
            text = chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("data:"):
                    payload = line[len("data:"):].strip()
                    if payload == "[DONE]":
                        return None, "stop", None
                    try:
                        chunk = json.loads(payload)
                    except json.JSONDecodeError:
                        return None, None, None
                    break
            else:
                return None, None, None

        # ── Normalise to dict ────────────────────────────────────────
        if hasattr(chunk, "as_dict"):
            chunk = chunk.as_dict()
        elif not isinstance(chunk, dict):
            chunk = {
                "choices": getattr(chunk, "choices", None),
                "usage": getattr(chunk, "usage", None),
            }

        choices = chunk.get("choices")
        if not choices or not isinstance(choices, list) or len(choices) == 0:
            return None, None, None

        choice = choices[0]
        content = None
        finish_reason = None

        if isinstance(choice, dict):
            # Streaming uses "delta"; non-streaming uses "message"
            delta = choice.get("delta") or choice.get("message") or {}
            content = delta.get("content") if isinstance(delta, dict) else getattr(delta, "content", None)
            finish_reason = choice.get("finish_reason")
        else:
            delta = getattr(choice, "delta", None) or getattr(choice, "message", None)
            content = getattr(delta, "content", None) if delta else None
            finish_reason = getattr(choice, "finish_reason", None)

        # Usage (usually only on the final chunk)
        usage = None
        usage_raw = chunk.get("usage")
        if usage_raw:
            if isinstance(usage_raw, dict):
                usage = usage_raw
            else:
                usage = {
                    "prompt_tokens": getattr(usage_raw, "prompt_tokens", None),
                    "completion_tokens": getattr(usage_raw, "completion_tokens", None),
                    "total_tokens": getattr(usage_raw, "total_tokens", None),
                }

        return content, finish_reason, usage

    # ── Non-streaming ─────────────────────────────────────────────────────

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Non-streaming chat completion.

        Returns:
            (full_content, usage_dict)
        """
        L.info(
            f"[ModelServing] Query to '{self.endpoint_name}' "
            f"({len(messages)} messages, temp={temperature}, max_tokens={max_tokens})"
        )

        sdk_messages = self._build_sdk_messages(messages)

        response = await asyncio.to_thread(
            self.client.serving_endpoints.query,
            name=self.endpoint_name,
            messages=sdk_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content, usage = self._parse_response(response)
        L.info(f"[ModelServing] Response received ({len(content or '')} chars)")
        return content, usage

    # ── Streaming (producer / consumer via asyncio.Queue) ─────────────────

    _SENTINEL = object()  # signals the producer thread is done

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[Tuple[Optional[str], Optional[str], Optional[Dict]], None]:
        """
        Async generator that yields (delta_content, finish_reason, usage)
        tuples from a streaming chat completion.

        A background thread runs the blocking SDK call with stream=True
        and pushes parsed chunks onto an asyncio.Queue.  The async side
        awaits items from the queue and yields them to the caller.

        Args:
            messages: Conversation messages as dicts.
            temperature: Sampling temperature (0.0 – 2.0).
            max_tokens: Maximum tokens to generate.

        Yields:
            (delta_content | None, finish_reason | None, usage_dict | None)
        """
        loop = asyncio.get_running_loop()
        q: asyncio.Queue = asyncio.Queue()

        # Build the raw HTTP request body (SDK doesn't handle streaming)
        sdk_messages = self._build_sdk_messages(messages)
        body = {
            "messages": [m.as_dict() for m in sdk_messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        url = f"{self.client.config.host}/serving-endpoints/{self.endpoint_name}/invocations"

        def _producer():
            """Runs in a daemon thread — raw HTTP SSE stream."""
            try:
                L.info(
                    f"[ModelServing] Streaming request to '{self.endpoint_name}' "
                    f"({len(sdk_messages)} msgs, temp={temperature}, max_tokens={max_tokens})"
                )

                # Get auth headers from the SDK config
                headers = self.client.config.authenticate()
                headers["Content-Type"] = "application/json"
                headers["Accept"] = "text/event-stream"

                resp = http_requests.post(url, json=body, headers=headers, stream=True)
                resp.raise_for_status()


                # SSE is always UTF-8 by spec; force it so iter_lines
                # doesn't fall back to Latin-1 when the Content-Type
                # header omits charset (which would mangle £, €, etc.).
                resp.encoding = "utf-8"

                for line in resp.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data:"):
                        continue
                    payload = line[len("data:"):].strip()
                    if payload == "[DONE]":
                        loop.call_soon_threadsafe(
                            q.put_nowait, (None, "stop", None)
                        )
                        break
                    try:
                        chunk = json.loads(payload)
                        parsed = self._parse_chunk(chunk)
                        loop.call_soon_threadsafe(q.put_nowait, parsed)
                    except json.JSONDecodeError:
                        continue

            except Exception as exc:
                L.error(f"[ModelServing] Streaming error: {exc}", exc_info=True)
                loop.call_soon_threadsafe(q.put_nowait, exc)
            finally:
                loop.call_soon_threadsafe(q.put_nowait, self._SENTINEL)

        thread = threading.Thread(target=_producer, daemon=True)
        thread.start()

        try:
            while True:
                item = await q.get()

                if item is self._SENTINEL:
                    break

                if isinstance(item, Exception):
                    raise item

                yield item  # (content, finish_reason, usage)
        finally:
            thread.join(timeout=10)
