"""
Free-Tier Provider Router — routes tasks to the cheapest capable provider.

Goal: Claude (Cowork/API) is the token budget. Everything else is free.
Use Claude only for orchestration decisions, complex reasoning, and vault ops.
Offload everything else to the free tier ladder below.

Provider ladder (cheapest first, per task type):
  Research/search   → Perplexity free (Sonar) → Grok free → Gemini Flash
  Code review/gen   → Groq Llama (free) → DeepSeek V3 → OpenRouter free pool
  Step-by-step      → Le Chat Mistral (generous limits) → Gemini Flash
  Heavy reasoning   → DeepSeek R1 (free) → Groq → Gemini Pro
  Vault ops / orch  → Claude (this system) — only when necessary
  Offline / no net  → Ollama local (Qwen3:8b, LFM2-2b, coder-1.5b)

Usage:
  from free_tier_router import route_task, TaskType
  provider, model = route_task(TaskType.CODE_REVIEW)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TaskType(str, Enum):
    # Use free search providers
    RESEARCH        = "research"         # Perplexity, Grok Deep Search
    WEB_SEARCH      = "web_search"       # Perplexity basic, Grok

    # Use free code providers
    CODE_REVIEW     = "code_review"      # Groq Llama, DeepSeek V3
    CODE_GEN        = "code_gen"         # DeepSeek V3, Groq
    REPO_TASK       = "repo_task"        # DeepSeek via GitHub Copilot free

    # Use free general providers
    STEP_BY_STEP    = "step_by_step"     # Mistral Le Chat (most generous)
    SUMMARIZE       = "summarize"        # Gemini Flash, Mistral
    TRANSLATE       = "translate"        # Gemini Flash

    # Reasoning-heavy (still free)
    HARD_REASONING  = "hard_reasoning"   # DeepSeek R1 (free), Groq
    DEEP_RESEARCH   = "deep_research"    # Gemini Pro 5/day, Perplexity Pro 5/day

    # Reserve for Claude only
    ORCHESTRATION   = "orchestration"    # Claude — vault ops, routing decisions
    VAULT_WRITE     = "vault_write"      # Claude — writing to vaults
    COMPLEX_AGENT   = "complex_agent"    # Claude — multi-step agent chains


@dataclass
class ProviderRoute:
    provider: str           # provider key in orchestrator config
    model: str              # specific model ID
    context_window: int     # max tokens
    free_limit: str         # human description of free limit
    notes: str              # quirks or requirements


# ---------------------------------------------------------------------------
# Routing table — primary + fallback per task type
# ---------------------------------------------------------------------------

ROUTES: dict[TaskType, list[ProviderRoute]] = {

    TaskType.RESEARCH: [
        ProviderRoute("perplexity", "sonar",
            8192, "~5 Pro/day, unlimited basic",
            "Best for web-grounded research; use basic tier for vault questions"),
        ProviderRoute("openrouter", "x-ai/grok-3-mini-beta",
            131072, "daily quota, stricter peak hours",
            "Grok deep search; good for X/Twitter sources"),
        ProviderRoute("gemini", "gemini-2.0-flash",
            1048576, "generous free tier",
            "Fallback; massive context window"),
    ],

    TaskType.WEB_SEARCH: [
        ProviderRoute("perplexity", "sonar",
            8192, "unlimited basic search",
            "Primary search provider; no Pro needed for basic"),
        ProviderRoute("openrouter", "x-ai/grok-3-mini-beta",
            131072, "daily quota",
            "Good real-time awareness"),
    ],

    TaskType.CODE_REVIEW: [
        ProviderRoute("groq", "llama-3.3-70b-versatile",
            32768, "free tier, fast",
            "Fast inference; good code understanding"),
        ProviderRoute("deepseek", "deepseek-chat",
            65536, "free API (rate limited)",
            "DeepSeek V3; strong on code"),
        ProviderRoute("openrouter", "deepseek/deepseek-chat-v3-0324:free",
            65536, "OpenRouter free pool",
            "DeepSeek V3 via OpenRouter free tier"),
    ],

    TaskType.CODE_GEN: [
        ProviderRoute("deepseek", "deepseek-chat",
            65536, "free API",
            "DeepSeek V3 best free code gen"),
        ProviderRoute("groq", "qwen-qwq-32b",
            32768, "free tier",
            "Qwen reasoning good for code"),
        ProviderRoute("ollama", "qwen2.5-coder:7b",
            32768, "local, unlimited, offline",
            "Offline fallback; no API needed"),
    ],

    TaskType.REPO_TASK: [
        ProviderRoute("deepseek", "deepseek-chat",
            65536, "~2000 completions/month via Copilot free",
            "Use GitHub Copilot free tier for repo context"),
        ProviderRoute("groq", "llama-3.3-70b-versatile",
            32768, "free tier",
            "Fallback when Copilot quota used"),
    ],

    TaskType.STEP_BY_STEP: [
        ProviderRoute("mistral", "mistral-large-latest",
            32768, "most generous free limits of any provider",
            "Le Chat Mistral; best free-tier limits for sequential tasks"),
        ProviderRoute("gemini", "gemini-2.0-flash",
            1048576, "generous",
            "Flash is fast and free; huge context"),
        ProviderRoute("groq", "llama-3.3-70b-versatile",
            32768, "free",
            "Fast fallback"),
    ],

    TaskType.SUMMARIZE: [
        ProviderRoute("gemini", "gemini-2.0-flash",
            1048576, "generous free tier",
            "Best context window for long doc summarization"),
        ProviderRoute("mistral", "mistral-medium-latest",
            32768, "generous",
            "Good summarization; Le Chat"),
        ProviderRoute("groq", "llama-3.3-70b-versatile",
            32768, "free",
            "Fast"),
    ],

    TaskType.TRANSLATE: [
        ProviderRoute("gemini", "gemini-2.0-flash",
            1048576, "free",
            "Best multilingual model on free tier"),
    ],

    TaskType.HARD_REASONING: [
        ProviderRoute("deepseek", "deepseek-reasoner",
            65536, "free API (R1)",
            "DeepSeek R1 — chain-of-thought reasoning, free tier"),
        ProviderRoute("groq", "qwen-qwq-32b",
            32768, "free",
            "Qwen QwQ reasoning model on Groq"),
        ProviderRoute("openrouter", "deepseek/deepseek-r1:free",
            65536, "OpenRouter free pool",
            "R1 via OpenRouter if DeepSeek direct is rate-limited"),
        ProviderRoute("ollama", "deepseek-r1-7b",
            32768, "local, unlimited",
            "Offline R1 distill; already installed"),
    ],

    TaskType.DEEP_RESEARCH: [
        ProviderRoute("gemini", "gemini-2.0-pro-exp",
            2097152, "5 requests/day",
            "Gemini Pro Deep Research; use sparingly"),
        ProviderRoute("perplexity", "sonar-pro",
            8192, "~5 Pro searches/day",
            "Perplexity Pro search; use for external research"),
        ProviderRoute("openrouter", "x-ai/grok-3-beta",
            131072, "daily quota",
            "Grok 3 full for deep search when others exhausted"),
    ],

    # Claude reserved — don't route away from these
    TaskType.ORCHESTRATION: [
        ProviderRoute("claude", "claude-haiku-4-5-20251001",
            200000, "paid — use sparingly",
            "Haiku: cheapest Claude; for routing decisions and light vault ops"),
    ],
    TaskType.VAULT_WRITE: [
        ProviderRoute("claude", "claude-sonnet-4-6",
            200000, "paid — reserve for vault writes",
            "Sonnet: vault writes, decisions, structured knowledge"),
    ],
    TaskType.COMPLEX_AGENT: [
        ProviderRoute("claude", "claude-sonnet-4-6",
            200000, "paid — last resort",
            "Full agent chains; only when free tiers genuinely can't handle it"),
    ],
}


def route_task(task_type: TaskType,
               prefer_offline: bool = False,
               exclude_providers: list[str] | None = None) -> ProviderRoute:
    """
    Return the best available route for a task type.

    Args:
        task_type: The type of task to route
        prefer_offline: If True, prefer Ollama local over API providers
        exclude_providers: List of provider keys to skip (e.g. rate-limited ones)

    Returns:
        ProviderRoute with provider, model, and context info
    """
    exclude = set(exclude_providers or [])
    candidates = ROUTES.get(task_type, [])

    if prefer_offline:
        # Reorder: offline first
        candidates = sorted(candidates,
                             key=lambda r: 0 if r.provider == "ollama" else 1)

    for route in candidates:
        if route.provider not in exclude:
            return route

    # Absolute fallback: local Ollama
    return ProviderRoute(
        "ollama", "lfm2-2b",
        4096, "local unlimited",
        "Emergency fallback — all providers excluded or unavailable"
    )


def print_routing_table():
    """Print the full routing table for reference."""
    print("\n" + "=" * 70)
    print("FREE-TIER PROVIDER ROUTING TABLE")
    print("=" * 70)
    print(f"{'Task Type':<20} {'Primary Provider':<15} {'Model':<35} {'Free Limit'}")
    print("-" * 70)
    for task_type, routes in ROUTES.items():
        primary = routes[0]
        print(f"{task_type.value:<20} {primary.provider:<15} {primary.model:<35} {primary.free_limit}")
    print("=" * 70)
    print("\nClaude (paid) reserved for: orchestration, vault_write, complex_agent")
    print("Offline (Ollama) available for all task types via prefer_offline=True")


# ---------------------------------------------------------------------------
# Cost guard — warns when Claude is about to be used
# ---------------------------------------------------------------------------

PAID_PROVIDERS = {"claude", "openai"}

def cost_guard(route: ProviderRoute) -> bool:
    """Returns True if this route uses a paid provider. Log before using."""
    return route.provider in PAID_PROVIDERS


if __name__ == "__main__":
    print_routing_table()

    print("\n--- Example routing decisions ---")
    examples = [
        (TaskType.RESEARCH, False, None),
        (TaskType.CODE_GEN, False, None),
        (TaskType.CODE_GEN, True, None),          # offline preferred
        (TaskType.HARD_REASONING, False, None),
        (TaskType.STEP_BY_STEP, False, ["mistral"]),  # Mistral excluded
        (TaskType.DEEP_RESEARCH, False, None),
        (TaskType.ORCHESTRATION, False, None),
    ]
    for task, offline, excl in examples:
        r = route_task(task, prefer_offline=offline, exclude_providers=excl)
        paid = " [PAID]" if cost_guard(r) else " [FREE]"
        offline_tag = " (offline)" if r.provider == "ollama" else ""
        print(f"  {task.value:<20} -> {r.provider}/{r.model}{paid}{offline_tag}")
