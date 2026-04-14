"""
Configuration — loads from environment variables / .env file.
Single-user local mode: keys live in env vars or encrypted local store.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ---------------------------------------------------------------------------
# Provider catalogue — base URLs, model IDs, cost weights
# ---------------------------------------------------------------------------

PROVIDERS: dict[str, dict] = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "openrouter/auto",
        "free_model": "openrouter/auto",
        "cost_weight": 0,
        "supports_streaming": True,
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "free_model": "llama-3.3-70b-versatile",
        "cost_weight": 0,  # free tier
        "supports_streaming": True,
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "default_model": "gemini-3-flash-preview",
        "free_model": "gemini-3-flash-preview",
        "cost_weight": 0,
        "supports_streaming": True,
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "cost_weight": 1,  # very cheap
        "supports_streaming": True,
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "default_model": "mistral-small-latest",
        "cost_weight": 2,
        "supports_streaming": True,
    },
    "perplexity": {
        "base_url": "https://api.perplexity.ai",
        "default_model": "sonar",
        "cost_weight": 3,
        "supports_streaming": True,
    },
    "grok": {
        "base_url": "https://api.x.ai/v1",
        "default_model": "grok-3-mini",
        "cost_weight": 3,
        "supports_streaming": True,
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "cost_weight": 5,
        "supports_streaming": True,
    },
    "ollama": {
        "base_url": "http://localhost:11434",
        "default_model": "qwen2.5-coder:1.5b",
        "free_model": "qwen2.5-coder:1.5b",
        "cost_weight": 0,  # always free, local
        "supports_streaming": True,
    },
}

# Model metadata for the frontend
MODEL_CATALOG: list[dict] = [
    # --- OpenRouter free pool ---
    {"id": "openrouter/auto", "provider": "openrouter", "label": "OpenRouter Auto (Free Pool)", "free": True, "context": 128_000},
    {"id": "meta-llama/llama-4-maverick:free", "provider": "openrouter", "label": "Llama 4 Maverick (Free)", "free": True, "context": 128_000},
    {"id": "deepseek/deepseek-r1:free", "provider": "openrouter", "label": "DeepSeek R1 (Free via OR)", "free": True, "context": 64_000},
    {"id": "google/gemini-2.5-pro-exp-03-25:free", "provider": "openrouter", "label": "Gemini 2.5 Pro (Free via OR)", "free": True, "context": 128_000},
    {"id": "qwen/qwen3-235b-a22b:free", "provider": "openrouter", "label": "Qwen3 235B (Free)", "free": True, "context": 128_000},
    # --- OpenRouter paid ---
    {"id": "anthropic/claude-sonnet-4", "provider": "openrouter", "label": "Claude Sonnet 4 (via OR)", "free": False, "context": 200_000},
    {"id": "openai/gpt-4o", "provider": "openrouter", "label": "GPT-4o (via OR)", "free": False, "context": 128_000},
    # --- Groq (free tier, fast inference) ---
    {"id": "llama-3.3-70b-versatile", "provider": "groq", "label": "Llama 3.3 70B (Groq)", "free": True, "context": 128_000},
    {"id": "llama-3.1-8b-instant", "provider": "groq", "label": "Llama 3.1 8B (Groq)", "free": True, "context": 128_000},
    {"id": "gemma2-9b-it", "provider": "groq", "label": "Gemma 2 9B (Groq)", "free": True, "context": 8_192},
    {"id": "mixtral-8x7b-32768", "provider": "groq", "label": "Mixtral 8x7B (Groq)", "free": True, "context": 32_768},
    # --- Gemini direct (verified from API 2026-04-13) ---
    {"id": "gemini-3-flash-preview", "provider": "gemini", "label": "Gemini 3 Flash", "free": True, "context": 1_000_000},
    {"id": "gemini-3.1-flash-lite-preview", "provider": "gemini", "label": "Gemini 3.1 Flash Lite", "free": True, "context": 1_000_000},
    {"id": "gemini-flash-latest", "provider": "gemini", "label": "Gemini Flash (Latest)", "free": True, "context": 1_000_000},
    {"id": "gemini-3-pro-preview", "provider": "gemini", "label": "Gemini 3 Pro", "free": True, "context": 1_000_000},
    {"id": "gemini-3.1-pro-preview", "provider": "gemini", "label": "Gemini 3.1 Pro", "free": False, "context": 1_000_000},
    {"id": "gemini-pro-latest", "provider": "gemini", "label": "Gemini Pro (Latest)", "free": True, "context": 1_000_000},
    # --- DeepSeek direct ---
    {"id": "deepseek-chat", "provider": "deepseek", "label": "DeepSeek V3 Chat", "free": False, "context": 64_000},
    {"id": "deepseek-reasoner", "provider": "deepseek", "label": "DeepSeek R1 Reasoner", "free": False, "context": 64_000},
    # --- Perplexity (search-grounded) ---
    {"id": "sonar", "provider": "perplexity", "label": "Perplexity Sonar", "free": False, "context": 128_000},
    {"id": "sonar-pro", "provider": "perplexity", "label": "Perplexity Sonar Pro", "free": False, "context": 200_000},
    # --- Mistral ---
    {"id": "mistral-small-latest", "provider": "mistral", "label": "Mistral Small", "free": False, "context": 32_000},
    # --- xAI Grok ---
    {"id": "grok-3-mini", "provider": "grok", "label": "Grok 3 Mini", "free": False, "context": 131_072},
    # --- OpenAI direct ---
    {"id": "gpt-4o-mini", "provider": "openai", "label": "GPT-4o Mini (Direct)", "free": False, "context": 128_000},
    {"id": "gpt-4o", "provider": "openai", "label": "GPT-4o (Direct)", "free": False, "context": 128_000},
    # --- Ollama local (always free, no network needed) ---
    {"id": "qwen2.5-coder:1.5b", "provider": "ollama", "label": "Qwen 2.5 Coder 1.5B (Local)", "free": True, "context": 32_000},
]


@dataclass
class Settings:
    # Platform keys (set in .env)
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")
    grok_api_key: str = os.getenv("GROK_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    perplexity_api_key: str = os.getenv("PERPLEXITY_API_KEY", "")

    # BYO user keys (loaded/saved via encrypted local store)
    user_openai_key: str = ""
    user_gemini_key: str = ""
    user_mistral_key: str = ""
    user_grok_key: str = ""
    user_groq_key: str = ""
    user_deepseek_key: str = ""
    user_perplexity_key: str = ""

    # Encryption key for local key store (auto-generated if missing)
    encryption_key: str = os.getenv("KEY_ENCRYPTION_SECRET", "")

    # Routing
    routing_mode: str = os.getenv("ROUTING_MODE", "FREE_FIRST")

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    cors_origins: list[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","))

    def api_key_for(self, provider: str, prefer_user: bool = True) -> str:
        """Return the best available key for a provider."""
        if provider == "ollama":
            return "local"  # No key needed, always "available"
        user_key = getattr(self, f"user_{provider}_key", "")
        platform_key = getattr(self, f"{provider}_api_key", "")
        if provider == "openrouter":
            return self.openrouter_api_key
        if prefer_user and user_key:
            return user_key
        return platform_key


settings = Settings()
