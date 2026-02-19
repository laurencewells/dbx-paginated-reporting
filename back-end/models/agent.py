"""
Pydantic domain models for the Agent (Model Serving chat) feature.
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, ConfigDict


class ChatMessage(BaseModel):
    """A single message in a conversation (user, assistant, or system)."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )
    role: str
    content: Optional[str] = None


class ChatRequest(BaseModel):
    """Request body for POST /agent/chat."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096


class ChatResult(BaseModel):
    """Internal result returned by AgentService."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )
    content: Optional[str] = None
    usage: Optional[Dict] = None


class ChatResponse(BaseModel):
    """Response body for POST /agent/chat and WebSocket responses."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )
    success: bool
    content: Optional[str] = None
    usage: Optional[Dict] = None
    model: Optional[str] = None
