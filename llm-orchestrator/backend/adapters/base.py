"""
Abstract LLMClient interface — every provider adapter implements this.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    is_free: bool = False


@dataclass
class LLMStreamChunk:
    delta: str = ""
    done: bool = False
    model: str = ""
    provider: str = ""
    tokens_used: int = 0
    is_free: bool = False


class LLMClient(ABC):
    """Shared interface for all LLM provider adapters."""

    provider_name: str = "base"

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Non-streaming chat completion."""
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Streaming chat completion — yields delta chunks."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Check whether this adapter has a valid key / can make requests."""
        ...
