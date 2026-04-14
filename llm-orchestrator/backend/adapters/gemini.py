"""
Google Gemini adapter — direct API via generateContent / streamGenerateContent.
Respects free-tier quotas (15 RPM / 1M TPM for Flash).
"""

from __future__ import annotations
import json
from typing import AsyncIterator

import httpx

from .base import LLMClient, LLMResponse, LLMStreamChunk

FREE_MODELS = {
    "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview",
    "gemini-3-pro-preview", "gemini-flash-latest", "gemini-pro-latest",
}


class GeminiClient(LLMClient):
    provider_name = "gemini"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def _convert_messages(self, messages: list[dict]) -> tuple[str | None, list[dict]]:
        """Convert OpenAI-style messages to Gemini contents format."""
        system_instruction = None
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
                continue
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        return system_instruction, contents

    async def chat(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        system_instruction, contents = self._convert_messages(messages)
        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})
        return LLMResponse(
            content=text,
            model=model,
            provider=self.provider_name,
            tokens_used=usage.get("totalTokenCount", 0),
            is_free=model in FREE_MODELS,
        )

    async def chat_stream(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[LLMStreamChunk]:
        system_instruction, contents = self._convert_messages(messages)
        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = f"{self.base_url}/models/{model}:streamGenerateContent?alt=sse&key={self.api_key}"
        is_free = model in FREE_MODELS

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", url, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    raw = line[6:]
                    try:
                        chunk = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    candidates = chunk.get("candidates", [])
                    if not candidates:
                        continue
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = parts[0].get("text", "") if parts else ""
                    finish = candidates[0].get("finishReason")
                    if text:
                        yield LLMStreamChunk(
                            delta=text,
                            model=model,
                            provider=self.provider_name,
                            is_free=is_free,
                        )
                    if finish and finish != "STOP":
                        continue
                    if finish == "STOP":
                        yield LLMStreamChunk(done=True, model=model, provider=self.provider_name, is_free=is_free)
                        return

        # If we exit without a STOP signal
        yield LLMStreamChunk(done=True, model=model, provider=self.provider_name, is_free=is_free)

    async def is_available(self) -> bool:
        return bool(self.api_key)
