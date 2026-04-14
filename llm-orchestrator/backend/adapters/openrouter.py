"""
OpenRouter adapter — primary aggregator.
Supports the free model pool and paid models.
Uses OpenAI-compatible /chat/completions endpoint.
"""

from __future__ import annotations
import json
from typing import AsyncIterator

import httpx

from .base import LLMClient, LLMResponse, LLMStreamChunk


class OpenRouterClient(LLMClient):
    provider_name = "openrouter"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "LLM Orchestrator",
        }

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
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})
        is_free = ":free" in model or model == "openrouter/auto"

        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", model),
            provider=self.provider_name,
            tokens_used=usage.get("total_tokens", 0),
            is_free=is_free,
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
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        is_free = ":free" in model or model == "openrouter/auto"
        resolved_model = model

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    raw = line[6:]
                    if raw.strip() == "[DONE]":
                        yield LLMStreamChunk(
                            done=True,
                            model=resolved_model,
                            provider=self.provider_name,
                            is_free=is_free,
                        )
                        return
                    try:
                        chunk = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if "model" in chunk:
                        resolved_model = chunk["model"]
                    delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        yield LLMStreamChunk(
                            delta=delta,
                            model=resolved_model,
                            provider=self.provider_name,
                            is_free=is_free,
                        )

    async def is_available(self) -> bool:
        return bool(self.api_key)
