"""
Routing engine — selects provider + model based on cost mode,
user preference, task type, and context length.

Routing modes:
  FREE_FIRST    — prefer openrouter free pool / gemini free tier, then cheapest paid
  CHEAPEST_PAID — pick lowest cost_weight provider with a valid key
  VENDOR_PINNED — user explicitly chooses a provider; use their BYO key
"""

from __future__ import annotations
import logging
from typing import Optional

from config import PROVIDERS, MODEL_CATALOG, settings
from models import RoutingMode
from adapters import ADAPTER_MAP, LLMClient

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Fallback chain — ordered preference when primary fails
# ---------------------------------------------------------------------------
FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("openrouter", "openrouter/auto"),          # free pool
    ("groq", "llama-3.3-70b-versatile"),        # groq free tier
    ("gemini", "gemini-3-flash-preview"),        # gemini free tier
    ("openrouter", "meta-llama/llama-4-maverick:free"),
    ("openrouter", "deepseek/deepseek-r1:free"),
    ("ollama", "qwen2.5-coder:1.5b"),           # local last resort — no network needed
]


def _resolve_model_entry(model_id: str) -> dict | None:
    """Look up a model in the catalog."""
    for entry in MODEL_CATALOG:
        if entry["id"] == model_id:
            return entry
    return None


def _build_client(provider: str) -> LLMClient | None:
    """Instantiate an adapter with the best available key."""
    cls = ADAPTER_MAP.get(provider)
    if not cls:
        return None
    key = settings.api_key_for(provider)
    if not key:
        return None
    return cls(api_key=key)


class Router:
    """Stateless router — call route() to get (client, model, is_free)."""

    def route(
        self,
        *,
        model: str | None = None,
        provider: str | None = None,
        mode: RoutingMode | None = None,
        context_needed: int = 0,
    ) -> tuple[LLMClient, str, bool]:
        """
        Returns (client, model_id, is_free).
        Raises RuntimeError if no provider is available.
        """
        effective_mode = mode or RoutingMode(settings.routing_mode)

        # --- VENDOR_PINNED: explicit provider + model ---
        if effective_mode == RoutingMode.VENDOR_PINNED or provider:
            return self._route_pinned(provider or "openrouter", model)

        # --- Explicit model requested but no provider pin ---
        if model:
            entry = _resolve_model_entry(model)
            if entry:
                client = _build_client(entry["provider"])
                if client:
                    return client, model, entry.get("free", False)
            # Try openrouter as proxy
            client = _build_client("openrouter")
            if client:
                return client, model, False

        # --- FREE_FIRST ---
        if effective_mode == RoutingMode.FREE_FIRST:
            return self._route_free_first(context_needed)

        # --- CHEAPEST_PAID ---
        return self._route_cheapest(context_needed)

    def _route_pinned(self, provider: str, model: str | None) -> tuple[LLMClient, str, bool]:
        client = _build_client(provider)
        if not client:
            raise RuntimeError(f"No API key configured for provider: {provider}")
        model_id = model or PROVIDERS.get(provider, {}).get("default_model", "")
        entry = _resolve_model_entry(model_id)
        is_free = entry.get("free", False) if entry else False
        return client, model_id, is_free

    def _route_free_first(self, context_needed: int) -> tuple[LLMClient, str, bool]:
        # 1. Try free catalog entries
        free_models = [m for m in MODEL_CATALOG if m.get("free") and m["context"] >= context_needed]
        # Sort: openrouter free pool first, then gemini
        free_models.sort(key=lambda m: (0 if m["provider"] == "openrouter" else 1))
        for entry in free_models:
            client = _build_client(entry["provider"])
            if client:
                return client, entry["id"], True

        # 2. Fallback chain
        return self._try_fallbacks()

    def _route_cheapest(self, context_needed: int) -> tuple[LLMClient, str, bool]:
        # Sort providers by cost_weight ascending
        sorted_providers = sorted(PROVIDERS.items(), key=lambda kv: kv[1].get("cost_weight", 99))
        for prov_name, prov_cfg in sorted_providers:
            client = _build_client(prov_name)
            if client:
                model_id = prov_cfg.get("default_model", "")
                entry = _resolve_model_entry(model_id)
                if entry and entry["context"] >= context_needed:
                    is_free = entry.get("free", False) if entry else False
                    return client, model_id, is_free
        return self._try_fallbacks()

    def _try_fallbacks(self) -> tuple[LLMClient, str, bool]:
        for prov, model_id in FALLBACK_CHAIN:
            client = _build_client(prov)
            if client:
                log.warning("Using fallback: %s / %s", prov, model_id)
                return client, model_id, True
        raise RuntimeError("No LLM provider available — check your API keys.")


router = Router()
