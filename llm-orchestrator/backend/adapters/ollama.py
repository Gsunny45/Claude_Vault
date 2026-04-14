"""
Ollama adapter — local inference fallback.
Connects to localhost:11434 (always free, always available).
Works with Qwen2.5-Coder-1.5B or any pulled model.
"""

from __future__ import annotations
import json
from typing import AsyncIterator

import httpx

from .base import LLMClient, LLMResponse, LLMStreamChunk


class OllamaClient(LLMClient):
    provider_name = "ollama"

    def __init__(self, api_key: str = ""):
        # No key needed — local service
        self.base_url = "http://localhost:11434"

    async def chat(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        payload = {
            "model": model,
            "messages": messages,
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        return LLMResponse(
            content=data["message"]["content"],
            model=model,
            provider=self.provider_name,
            tokens_used=data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
            is_free=True,
        )

    async def chat_stream(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[LLMStreamChunk]:
        payload = {
            "model": model,
            "messages": messages,
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    content = chunk.get("message", {}).get("content", "")
                    done = chunk.get("done", False)
                    if content:
                        yield LLMStreamChunk(
                            delta=content,
                            model=model,
                            provider=self.provider_name,
                            is_free=True,
                        )
                    if done:
                        yield LLMStreamChunk(
                            done=True,
                            model=model,
                            provider=self.provider_name,
                            is_free=True,
                            tokens_used=chunk.get("eval_count", 0),
                        )
                        return

    async def is_available(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
