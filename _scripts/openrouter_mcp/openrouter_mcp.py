#!/usr/bin/env python3
'''
OpenRouter MCP Server — Multi-model AI gateway for Claude Vault orchestration stack.

This is the internet-facing AI layer. One API key, one endpoint, routes to
Claude/Gemini/Llama/Mistral/Qwen and 300+ models. Provides fallback chains,
model discovery, cost tracking, and chat completions.

Part of Mars's resilient local-first system. See KNW-0010 for full architecture.

Hardware constraints (always active):
  CPU: i5-1335U | RAM: 16GB | Storage: 24GB free | GPU: Iris Xe (no CUDA)
  All responses should be storage-conscious. No unbounded data dumps.

Transport: stdio (local integration with Claude Desktop/Cowork/Code)
'''

import json
import os
import time
from typing import Optional, List, Dict, Any
from enum import Enum

import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# ──────────────────────────────────────────────
# Server Initialization
# ──────────────────────────────────────────────

mcp = FastMCP("openrouter_mcp")

# Constants
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Default fallback chain — ordered by cost-efficiency for Mars's use case
DEFAULT_FALLBACK_MODELS = [
    "google/gemini-flash-1.5",       # Fast + cheap
    "google/gemini-pro-1.5",         # Deep reasoning
    "anthropic/claude-3.5-sonnet",   # Balanced
    "meta-llama/llama-3.1-70b-instruct",  # Open-source fallback
]

# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class ResponseFormat(str, Enum):
    '''Output format for tool responses.'''
    MARKDOWN = "markdown"
    JSON = "json"


# ──────────────────────────────────────────────
# Shared Utilities
# ──────────────────────────────────────────────

def _get_headers() -> Dict[str, str]:
    '''Build request headers with API key.'''
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not set. Set it as an environment variable: "
            "export OPENROUTER_API_KEY='your-key-here'"
        )
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://claude-vault.local",
        "X-Title": "Claude Vault Orchestrator",
    }


async def _make_request(
    endpoint: str,
    method: str = "GET",
    json_data: Optional[Dict] = None,
    timeout: float = 60.0
) -> Dict[str, Any]:
    '''Reusable async HTTP request to OpenRouter API.'''
    url = f"{OPENROUTER_BASE_URL}/{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            url,
            headers=_get_headers(),
            json=json_data,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()


def _handle_error(e: Exception) -> str:
    '''Consistent error formatting with actionable guidance.'''
    if isinstance(e, ValueError) and "OPENROUTER_API_KEY" in str(e):
        return (
            "Error: OPENROUTER_API_KEY not set.\n"
            "Fix: export OPENROUTER_API_KEY='sk-or-v1-your-key'\n"
            "Get one at: https://openrouter.ai/keys"
        )
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 401:
            return "Error: Invalid API key. Check OPENROUTER_API_KEY or get a new one at https://openrouter.ai/keys"
        elif status == 402:
            return "Error: Insufficient credits. Add credits at https://openrouter.ai/credits"
        elif status == 429:
            return "Error: Rate limited. Wait 10 seconds and retry."
        elif status == 408:
            return "Error: Request timed out. Try a faster model (e.g., google/gemini-flash-1.5)."
        try:
            body = e.response.json()
            return f"Error ({status}): {body.get('error', {}).get('message', str(e))}"
        except Exception:
            return f"Error: API returned status {status}"
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Try a faster model or shorter prompt."
    return f"Error: {type(e).__name__}: {str(e)}"


def _format_cost(prompt_tokens: int, completion_tokens: int, model_pricing: Dict) -> str:
    '''Calculate and format cost estimate.'''
    prompt_cost = prompt_tokens * float(model_pricing.get("prompt", "0")) / 1_000_000
    completion_cost = completion_tokens * float(model_pricing.get("completion", "0")) / 1_000_000
    total = prompt_cost + completion_cost
    return f"${total:.6f} ({prompt_tokens} in / {completion_tokens} out)"


# ──────────────────────────────────────────────
# Input Models
# ──────────────────────────────────────────────

class ChatInput(BaseModel):
    '''Input for sending a chat completion request.'''
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    model: str = Field(
        default="google/gemini-flash-1.5",
        description="Model ID (e.g., 'google/gemini-flash-1.5', 'anthropic/claude-3.5-sonnet'). "
                    "See openrouter_list_models for available models.",
        min_length=1,
        max_length=200,
    )
    message: str = Field(
        ...,
        description="The user message to send. For multi-turn, use openrouter_chat_multi.",
        min_length=1,
        max_length=100000,
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional system prompt to set context/role for the model.",
        max_length=50000,
    )
    temperature: Optional[float] = Field(
        default=0.7,
        description="Sampling temperature (0.0 = deterministic, 2.0 = max creative).",
        ge=0.0,
        le=2.0,
    )
    max_tokens: Optional[int] = Field(
        default=2048,
        description="Maximum tokens in response. Keep low to save storage/cost.",
        ge=1,
        le=128000,
    )


class ChatMultiInput(BaseModel):
    '''Input for multi-turn chat completion.'''
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    model: str = Field(
        default="google/gemini-flash-1.5",
        description="Model ID to use.",
        min_length=1,
    )
    messages: str = Field(
        ...,
        description='JSON array of messages: [{"role":"system","content":"..."},{"role":"user","content":"..."}]',
        min_length=2,
    )
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=128000)


class FallbackChatInput(BaseModel):
    '''Input for chat with automatic model fallback chain.'''
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    message: str = Field(
        ...,
        description="The message to send. Will try models in order until one succeeds.",
        min_length=1,
        max_length=100000,
    )
    system_prompt: Optional[str] = Field(default=None, max_length=50000)
    models: Optional[str] = Field(
        default=None,
        description="Comma-separated model IDs for fallback chain. "
                    "Default: gemini-flash → gemini-pro → claude-3.5-sonnet → llama-3.1-70b",
    )
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=128000)


class ListModelsInput(BaseModel):
    '''Input for listing available models.'''
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    query: Optional[str] = Field(
        default=None,
        description="Filter models by name/provider (e.g., 'gemini', 'llama', 'anthropic').",
    )
    max_results: Optional[int] = Field(
        default=20,
        description="Maximum models to return. Keep low to save context window.",
        ge=1,
        le=100,
    )
    sort_by: Optional[str] = Field(
        default="name",
        description="Sort by: 'name', 'price', 'context_length'.",
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ModelInfoInput(BaseModel):
    '''Input for getting detailed info about a specific model.'''
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    model_id: str = Field(
        ...,
        description="Full model ID (e.g., 'google/gemini-flash-1.5').",
        min_length=1,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CreditCheckInput(BaseModel):
    '''Input for checking account credits.'''
    model_config = ConfigDict(extra='forbid')
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


# ──────────────────────────────────────────────
# Tools
# ──────────────────────────────────────────────

@mcp.tool(
    name="openrouter_chat",
    annotations={
        "title": "Chat Completion via OpenRouter",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
async def openrouter_chat(params: ChatInput) -> str:
    '''Send a single-turn chat completion to any model via OpenRouter.

    Routes your message to 300+ AI models through one API. Use this for
    quick queries, RAG answers, code generation, or any single-turn task.
    For multi-turn conversations, use openrouter_chat_multi instead.

    Args:
        params (ChatInput): Validated input containing:
            - model (str): Model ID (default: google/gemini-flash-1.5)
            - message (str): The user message
            - system_prompt (Optional[str]): System context
            - temperature (float): 0.0-2.0 (default: 0.7)
            - max_tokens (int): Response limit (default: 2048)

    Returns:
        str: Model response with metadata (model used, tokens, cost estimate)
    '''
    try:
        messages = []
        if params.system_prompt:
            messages.append({"role": "system", "content": params.system_prompt})
        messages.append({"role": "user", "content": params.message})

        data = await _make_request("chat/completions", method="POST", json_data={
            "model": params.model,
            "messages": messages,
            "temperature": params.temperature,
            "max_tokens": params.max_tokens,
        })

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        model_used = data.get("model", params.model)

        result = [
            choice,
            "",
            "---",
            f"**Model**: {model_used}",
            f"**Tokens**: {usage.get('prompt_tokens', '?')} in / {usage.get('completion_tokens', '?')} out",
        ]

        return "\n".join(result)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="openrouter_chat_multi",
    annotations={
        "title": "Multi-Turn Chat via OpenRouter",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
async def openrouter_chat_multi(params: ChatMultiInput) -> str:
    '''Send a multi-turn conversation to any model via OpenRouter.

    Use when you need to maintain conversation context across multiple
    exchanges. Pass the full message history as a JSON array.

    Args:
        params (ChatMultiInput): Validated input containing:
            - model (str): Model ID
            - messages (str): JSON array of {role, content} messages
            - temperature (float): 0.0-2.0
            - max_tokens (int): Response limit

    Returns:
        str: Model response with metadata
    '''
    try:
        messages = json.loads(params.messages)
        if not isinstance(messages, list):
            return "Error: messages must be a JSON array of {role, content} objects."

        data = await _make_request("chat/completions", method="POST", json_data={
            "model": params.model,
            "messages": messages,
            "temperature": params.temperature,
            "max_tokens": params.max_tokens,
        })

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        model_used = data.get("model", params.model)

        result = [
            choice,
            "",
            "---",
            f"**Model**: {model_used}",
            f"**Tokens**: {usage.get('prompt_tokens', '?')} in / {usage.get('completion_tokens', '?')} out",
        ]

        return "\n".join(result)

    except json.JSONDecodeError:
        return "Error: Invalid JSON in messages field. Expected format: [{\"role\":\"user\",\"content\":\"hello\"}]"
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="openrouter_chat_fallback",
    annotations={
        "title": "Chat with Automatic Model Fallback",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
async def openrouter_chat_fallback(params: FallbackChatInput) -> str:
    '''Send a message with automatic fallback across multiple models.

    This is the RESILIENT endpoint. If the first model fails (rate limit,
    timeout, error), it automatically tries the next model in the chain.
    Default chain: Gemini Flash → Gemini Pro → Claude 3.5 Sonnet → Llama 3.1 70B.

    Use this when reliability matters more than model choice.

    Args:
        params (FallbackChatInput): Validated input containing:
            - message (str): The user message
            - system_prompt (Optional[str]): System context
            - models (Optional[str]): Comma-separated fallback chain
            - temperature (float): 0.0-2.0
            - max_tokens (int): Response limit

    Returns:
        str: Response from first succeeding model, with fallback log
    '''
    if params.models:
        model_chain = [m.strip() for m in params.models.split(",")]
    else:
        model_chain = DEFAULT_FALLBACK_MODELS.copy()

    messages = []
    if params.system_prompt:
        messages.append({"role": "system", "content": params.system_prompt})
    messages.append({"role": "user", "content": params.message})

    errors = []

    for model in model_chain:
        try:
            data = await _make_request("chat/completions", method="POST", json_data={
                "model": model,
                "messages": messages,
                "temperature": params.temperature,
                "max_tokens": params.max_tokens,
            }, timeout=30.0)

            choice = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            model_used = data.get("model", model)

            result = [choice, "", "---"]
            result.append(f"**Model**: {model_used}")
            result.append(f"**Tokens**: {usage.get('prompt_tokens', '?')} in / {usage.get('completion_tokens', '?')} out")

            if errors:
                result.append(f"**Fallbacks tried**: {len(errors)} failed → {', '.join(e[0] for e in errors)}")

            return "\n".join(result)

        except Exception as e:
            errors.append((model, str(e)))
            continue

    # All models failed
    error_log = "\n".join(f"  - {m}: {err}" for m, err in errors)
    return f"Error: All {len(model_chain)} models failed.\n\nFailure log:\n{error_log}"


@mcp.tool(
    name="openrouter_list_models",
    annotations={
        "title": "List Available AI Models",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def openrouter_list_models(params: ListModelsInput) -> str:
    '''List available models on OpenRouter, optionally filtered by name/provider.

    Use to discover models, compare pricing, or find alternatives.
    Returns model ID, context length, and pricing per million tokens.

    Args:
        params (ListModelsInput): Validated input containing:
            - query (Optional[str]): Filter by name/provider
            - max_results (int): Limit results (default: 20)
            - sort_by (str): Sort by name/price/context_length
            - response_format: markdown or json

    Returns:
        str: List of matching models with key specs
    '''
    try:
        data = await _make_request("models")
        models = data.get("data", [])

        # Filter by query
        if params.query:
            q = params.query.lower()
            models = [m for m in models if q in m.get("id", "").lower() or q in m.get("name", "").lower()]

        # Sort
        if params.sort_by == "price":
            models.sort(key=lambda m: float(m.get("pricing", {}).get("prompt", "999")))
        elif params.sort_by == "context_length":
            models.sort(key=lambda m: m.get("context_length", 0), reverse=True)
        else:
            models.sort(key=lambda m: m.get("id", ""))

        # Limit
        models = models[:params.max_results]

        if not models:
            return f"No models found matching '{params.query}'." if params.query else "No models available."

        if params.response_format == ResponseFormat.JSON:
            compact = [{
                "id": m["id"],
                "name": m.get("name", ""),
                "context_length": m.get("context_length", 0),
                "pricing_prompt_per_1m": m.get("pricing", {}).get("prompt", "?"),
                "pricing_completion_per_1m": m.get("pricing", {}).get("completion", "?"),
            } for m in models]
            return json.dumps(compact, indent=2)

        # Markdown format
        lines = [f"# Available Models ({len(models)} shown)", ""]
        lines.append("| Model ID | Context | $/1M prompt | $/1M completion |")
        lines.append("|----------|---------|-------------|-----------------|")
        for m in models:
            mid = m["id"]
            ctx = f"{m.get('context_length', 0):,}"
            pp = m.get("pricing", {}).get("prompt", "?")
            pc = m.get("pricing", {}).get("completion", "?")
            lines.append(f"| {mid} | {ctx} | {pp} | {pc} |")

        return "\n".join(lines)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="openrouter_model_info",
    annotations={
        "title": "Get Model Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def openrouter_model_info(params: ModelInfoInput) -> str:
    '''Get detailed information about a specific model.

    Returns pricing, context length, capabilities, and provider info.
    Use before sending expensive requests to understand costs.

    Args:
        params (ModelInfoInput): Validated input containing:
            - model_id (str): Full model ID (e.g., 'google/gemini-flash-1.5')
            - response_format: markdown or json

    Returns:
        str: Detailed model specifications
    '''
    try:
        data = await _make_request("models")
        models = data.get("data", [])
        model = next((m for m in models if m["id"] == params.model_id), None)

        if not model:
            # Fuzzy match suggestion
            close = [m["id"] for m in models if params.model_id.split("/")[-1].lower() in m["id"].lower()][:5]
            suggestion = f"\n\nDid you mean: {', '.join(close)}" if close else ""
            return f"Error: Model '{params.model_id}' not found.{suggestion}"

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(model, indent=2)

        pricing = model.get("pricing", {})
        lines = [
            f"# {model.get('name', model['id'])}",
            f"**ID**: `{model['id']}`",
            f"**Context Length**: {model.get('context_length', 'unknown'):,} tokens",
            f"**Pricing**: ${pricing.get('prompt', '?')}/1M prompt, ${pricing.get('completion', '?')}/1M completion",
        ]
        if model.get("top_provider"):
            tp = model["top_provider"]
            lines.append(f"**Max Completion**: {tp.get('max_completion_tokens', 'unknown')} tokens")
            lines.append(f"**Modality**: {tp.get('modality', 'unknown')}")
        if model.get("description"):
            lines.extend(["", model["description"][:500]])

        return "\n".join(lines)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="openrouter_check_credits",
    annotations={
        "title": "Check OpenRouter Account Credits",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def openrouter_check_credits(params: CreditCheckInput) -> str:
    '''Check your OpenRouter account credit balance and usage.

    Use to monitor spend before running expensive operations.
    Important for staying within budget on Mars's system.

    Returns:
        str: Credit balance and usage info
    '''
    try:
        data = await _make_request("auth/key")

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(data, indent=2)

        info = data.get("data", {})
        lines = [
            "# OpenRouter Account Status",
            f"**Label**: {info.get('label', 'unnamed')}",
            f"**Credits Remaining**: ${info.get('limit_remaining', 'unknown')}",
            f"**Credits Used**: ${info.get('usage', 'unknown')}",
            f"**Rate Limit**: {info.get('rate_limit', {}).get('requests', '?')} req/{info.get('rate_limit', {}).get('interval', '?')}",
        ]

        return "\n".join(lines)

    except Exception as e:
        return _handle_error(e)


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
