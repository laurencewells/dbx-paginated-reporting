"""
Service layer for the Agent (Model Serving chat) feature.

Orchestrates the ModelServingConnector and converts raw responses
into domain-level ChatResult objects.  Supports both non-streaming
and streaming (async generator) modes.
"""

from typing import AsyncGenerator, Dict, List, Optional, Tuple

from common.connectors.model_serving import ModelServingConnector
from common.logger import log as L
from models.agent import ChatMessage, ChatResult


class AgentService:
    """
    Stateless service for chat completions via Databricks Model Serving.

    Prepends a system prompt and delegates to ModelServingConnector.

    Attributes:
        connector: ModelServingConnector instance
        system_prompt: System message prepended to every request
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful AI assistant powered by Databricks Model Serving. "
        "Provide clear, concise, and accurate responses. "
        "Use markdown formatting when appropriate for readability."
    )

    def __init__(
        self,
        connector: Optional[ModelServingConnector] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialise AgentService.

        Args:
            connector: Optional ModelServingConnector (created with defaults if omitted).
            system_prompt: Optional override for the system prompt.
        """
        self.connector = connector or ModelServingConnector()
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        L.info("AgentService initialised")

    # ── Helpers ───────────────────────────────────────────────────────────

    def _prepare_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """
        Convert domain ChatMessage list to plain dicts and prepend system prompt.

        Returns:
            List of {"role": ..., "content": ...} dicts ready for the connector.
        """
        prepared = [{"role": "system", "content": self.system_prompt}]
        for m in messages:
            prepared.append({"role": m.role, "content": m.content or ""})
        return prepared

    # ── Chat Completion ───────────────────────────────────────────────────

    async def get_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> ChatResult:
        """
        Send a chat completion and return the full response.

        Returns:
            ChatResult containing the assistant's content and usage stats.
        """
        prepared = self._prepare_messages(messages)
        L.info(f"[AgentService] Sending {len(prepared)} messages to model serving")

        content, usage = await self.connector.chat_completion(
            prepared, temperature=temperature, max_tokens=max_tokens
        )

        return ChatResult(content=content, usage=usage)

    # ── Streaming ─────────────────────────────────────────────────────────

    async def stream_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[Tuple[str, Optional[str], Optional[Dict]], None]:
        """
        Stream a chat completion token-by-token.

        Yields:
            (type, content_or_none, payload_or_none) tuples where type is
            "delta"  — content holds the token text
            "done"   — payload holds usage dict (content is None)
        """
        prepared = self._prepare_messages(messages)
        L.info(f"[AgentService] Streaming {len(prepared)} messages")

        last_usage = None

        async for content, finish_reason, usage in self.connector.stream_chat_completion(
            prepared, temperature=temperature, max_tokens=max_tokens
        ):
            if usage:
                last_usage = usage

            if content:
                yield ("delta", content, None)

            if finish_reason and finish_reason in ("stop", "length"):
                yield ("done", None, last_usage)
                return

        # Iterator exhausted without explicit finish_reason
        yield ("done", None, last_usage)
