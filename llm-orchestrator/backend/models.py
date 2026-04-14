"""Pydantic models shared across the backend."""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RoutingMode(str, Enum):
    FREE_FIRST = "FREE_FIRST"
    CHEAPEST_PAID = "CHEAPEST_PAID"
    VENDOR_PINNED = "VENDOR_PINNED"


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    model: Optional[str] = None          # explicit model ID or None for auto
    provider: Optional[str] = None       # pin to provider
    routing_mode: Optional[RoutingMode] = None  # override global setting
    stream: bool = True
    temperature: float = 0.7
    max_tokens: int = 4096
    use_rag: bool = False                # inject Pinecone knowledge context


class ChatResponseMeta(BaseModel):
    provider: str
    model: str
    is_fallback: bool = False
    free_tier: bool = False
    tokens_used: Optional[int] = None


class ChatResponse(BaseModel):
    content: str
    meta: ChatResponseMeta


class StreamChunk(BaseModel):
    """Single SSE chunk."""
    delta: str = ""
    meta: Optional[ChatResponseMeta] = None
    done: bool = False
    error: Optional[str] = None


class UserKeysPayload(BaseModel):
    openai_key: Optional[str] = None
    gemini_key: Optional[str] = None
    mistral_key: Optional[str] = None
    grok_key: Optional[str] = None
    groq_key: Optional[str] = None
    deepseek_key: Optional[str] = None
    perplexity_key: Optional[str] = None


class SettingsPayload(BaseModel):
    routing_mode: Optional[RoutingMode] = None
    keys: Optional[UserKeysPayload] = None
