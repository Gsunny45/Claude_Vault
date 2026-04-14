"""
API Registry Module

Manages a master registry of all API accounts, free tiers, and token opportunities.
Supports in-memory CRUD operations backed by persistent JSON storage.

Endpoints to be integrated into main.py:
  GET  /api/registry              — list all services
  GET  /api/registry/summary      — budget summary, expiring soon, free tier status
  POST /api/registry              — add or update a service entry
"""

from __future__ import annotations
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any
from pydantic import BaseModel, Field


log = logging.getLogger(__name__)

# Default location for registry storage
REGISTRY_PATH = Path(__file__).parent / "registry.json"


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class FreeTier(BaseModel):
    """Free tier constraints for a service."""
    available: bool = True
    rate_limits: Optional[str] = None  # e.g., "1000 RPM, 10M TPM"
    daily_quota: Optional[int] = None  # requests per day
    monthly_quota: Optional[int] = None  # requests per month
    note: Optional[str] = None


class PaidTier(BaseModel):
    """Paid tier / account balance tracking."""
    available: bool = False
    balance: float = 0.0  # current credits / balance
    currency: str = "USD"
    monthly_spend_limit: Optional[float] = None
    note: Optional[str] = None


class ServiceEntry(BaseModel):
    """A single API service in the registry."""
    id: str = Field(..., description="Unique slug (e.g., 'openrouter', 'groq')")
    name: str = Field(..., description="Full service name")
    url: str = Field(..., description="Service URL / console link")
    type: str = Field(..., description="'backend' (requires API key) or 'frontend' (web browser)")
    category: str = Field(
        ...,
        description="Category: LLM, Embedding, VectorDB, Code, Orchestration, Workflow, etc.",
    )
    api_key_required: bool = True
    api_key: Optional[str] = Field(None, description="Stored API key (encrypted in practice)")
    status: str = Field(
        "active",
        description="'active' | 'expired' | 'needs_reload' | 'inactive' | 'untested'",
    )
    free_tier: Optional[FreeTier] = Field(default_factory=FreeTier)
    paid_tier: Optional[PaidTier] = Field(default_factory=PaidTier)
    expires_at: Optional[str] = Field(None, description="ISO 8601 timestamp; None = no expiry")
    last_verified: Optional[str] = Field(None, description="ISO 8601 timestamp of last test")
    notes: str = ""


class RegistrySummary(BaseModel):
    """High-level summary of registry state."""
    total_services: int
    active_services: int
    services_with_keys: int
    total_free_tier_services: int
    total_paid_balance: float
    currency: str = "USD"
    expiring_soon: list[str] = Field(default_factory=list)  # service names expiring in 7 days
    last_updated: str


class RegistryResponse(BaseModel):
    """Response wrapper for registry operations."""
    status: str = "ok"
    message: Optional[str] = None
    data: Any = None


# ---------------------------------------------------------------------------
# Registry Manager
# ---------------------------------------------------------------------------

class RegistryManager:
    """
    Thread-safe in-memory registry with JSON persistence.

    Loads from JSON on init, can be updated via POST, and persists to disk.
    """

    def __init__(self, path: Path = REGISTRY_PATH):
        self.path = Path(path)
        self.services: dict[str, ServiceEntry] = {}
        self.load()

    def load(self) -> None:
        """Load registry from JSON file; create empty if missing."""
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    data = json.load(f)
                self.services = {
                    entry["id"]: ServiceEntry(**entry)
                    for entry in data.get("services", [])
                }
                log.info(f"Loaded {len(self.services)} services from {self.path}")
            except Exception as e:
                log.error(f"Failed to load registry from {self.path}: {e}")
                self.services = {}
        else:
            log.info(f"Registry file {self.path} not found; starting with empty registry")
            self.services = {}

    def save(self) -> None:
        """Persist registry to JSON file."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "last_updated": datetime.utcnow().isoformat(),
                "services": [s.model_dump() for s in self.services.values()],
            }
            with open(self.path, "w") as f:
                json.dump(data, f, indent=2)
            log.info(f"Saved registry to {self.path}")
        except Exception as e:
            log.error(f"Failed to save registry: {e}")

    def list_all(self) -> list[ServiceEntry]:
        """Return all services sorted by name."""
        return sorted(self.services.values(), key=lambda s: s.name)

    def get(self, service_id: str) -> Optional[ServiceEntry]:
        """Get a service by ID."""
        return self.services.get(service_id)

    def add_or_update(self, entry: ServiceEntry) -> ServiceEntry:
        """Add a new service or update an existing one."""
        entry.last_verified = datetime.utcnow().isoformat()
        self.services[entry.id] = entry
        self.save()
        return entry

    def delete(self, service_id: str) -> bool:
        """Delete a service by ID."""
        if service_id in self.services:
            del self.services[service_id]
            self.save()
            return True
        return False

    def summary(self) -> RegistrySummary:
        """Generate a summary of registry state."""
        services = list(self.services.values())
        total = len(services)
        active = sum(1 for s in services if s.status == "active")
        with_keys = sum(1 for s in services if s.api_key)
        free_tier_count = sum(1 for s in services if s.free_tier and s.free_tier.available)
        total_paid = sum(s.paid_tier.balance for s in services if s.paid_tier)

        # Find services expiring within 7 days
        expiring_soon = []
        cutoff = datetime.utcnow() + timedelta(days=7)
        for s in services:
            if s.expires_at:
                try:
                    exp_date = datetime.fromisoformat(s.expires_at)
                    if exp_date <= cutoff:
                        expiring_soon.append(s.name)
                except ValueError:
                    pass

        return RegistrySummary(
            total_services=total,
            active_services=active,
            services_with_keys=with_keys,
            total_free_tier_services=free_tier_count,
            total_paid_balance=total_paid,
            expiring_soon=sorted(expiring_soon),
            last_updated=datetime.utcnow().isoformat(),
        )

    def get_by_category(self, category: str) -> list[ServiceEntry]:
        """Get all services in a category (case-insensitive)."""
        return [s for s in self.services.values() if s.category.lower() == category.lower()]

    def get_by_type(self, type_: str) -> list[ServiceEntry]:
        """Get all services of a type ('backend' or 'frontend')."""
        return [s for s in self.services.values() if s.type == type_]

    def get_active_with_keys(self) -> list[ServiceEntry]:
        """Get all active services with stored API keys."""
        return [s for s in self.services.values() if s.status == "active" and s.api_key]

    def health_check(self) -> dict[str, Any]:
        """Quick health check: file exists, readable, parseable."""
        return {
            "registry_file_exists": self.path.exists(),
            "services_loaded": len(self.services),
            "latest_summary": self.summary().model_dump(),
        }


# ---------------------------------------------------------------------------
# Global Instance
# ---------------------------------------------------------------------------

registry = RegistryManager(REGISTRY_PATH)


# ---------------------------------------------------------------------------
# Default Services (Initial Seed Data)
# ---------------------------------------------------------------------------

DEFAULT_SERVICES = [
    ServiceEntry(
        id="openrouter",
        name="OpenRouter",
        url="https://openrouter.ai",
        type="backend",
        category="LLM Router",
        api_key_required=True,
        status="active",
        free_tier=FreeTier(available=True, rate_limits="1000 RPM, 10M TPM"),
        notes="Best value for routing; aggregates 100+ models",
    ),
    ServiceEntry(
        id="groq",
        name="Groq",
        url="https://console.groq.com",
        type="backend",
        category="LLM",
        api_key_required=True,
        status="active",
        free_tier=FreeTier(available=True, rate_limits="30 req/min free"),
        notes="Fastest LLM inference on Mixtral-8x7b, Token500",
    ),
    ServiceEntry(
        id="gemini",
        name="Google Gemini",
        url="https://console.cloud.google.com",
        type="backend",
        category="LLM + Embedding",
        api_key_required=True,
        status="active",
        free_tier=FreeTier(available=True, daily_quota=None),
        notes="Multimodal; $300 free credits for new accounts",
    ),
    ServiceEntry(
        id="deepseek",
        name="DeepSeek",
        url="https://platform.deepseek.com",
        type="backend",
        category="LLM",
        api_key_required=True,
        status="active",
        notes="Chinese LLM with strong reasoning; API available",
    ),
    ServiceEntry(
        id="perplexity",
        name="Perplexity",
        url="https://perplexity.ai/api",
        type="backend",
        category="LLM + Search",
        api_key_required=True,
        status="active",
        notes="Web search integrated; cite sources",
    ),
    ServiceEntry(
        id="mistral",
        name="Mistral AI",
        url="https://console.mistral.ai",
        type="backend",
        category="LLM",
        api_key_required=True,
        status="active",
        notes="Open models via API; EU-based",
    ),
    ServiceEntry(
        id="grok",
        name="Grok / xAI",
        url="https://console.x.ai",
        type="backend",
        category="LLM",
        api_key_required=True,
        status="active",
        notes="Real-time web access",
    ),
    ServiceEntry(
        id="openai",
        name="OpenAI",
        url="https://platform.openai.com",
        type="backend",
        category="LLM + Embedding + Vision",
        api_key_required=True,
        status="active",
        free_tier=FreeTier(available=True, daily_quota=None),
        notes="GPT-4o, o1-preview, text-embedding-3-large",
    ),
    ServiceEntry(
        id="anthropic",
        name="Anthropic (Claude)",
        url="https://console.anthropic.com",
        type="backend",
        category="LLM + Embedding",
        api_key_required=True,
        status="active",
        notes="Claude 3.5 Sonnet, Opus, Haiku",
    ),
    ServiceEntry(
        id="pinecone",
        name="Pinecone",
        url="https://console.pinecone.io",
        type="backend",
        category="Vector DB",
        api_key_required=True,
        status="active",
        free_tier=FreeTier(available=True),
        notes="Serverless or pods; embedded in RAG pipeline",
    ),
    ServiceEntry(
        id="llamaindex",
        name="LlamaIndex Cloud",
        url="https://llamaindex.cloud",
        type="backend",
        category="RAG + Orchestration",
        api_key_required=True,
        status="active",
        notes="Managed RAG, index hosting, evaluation tools",
    ),
    ServiceEntry(
        id="langchain",
        name="LangChain",
        url="https://smith.langchain.com",
        type="backend",
        category="LLM Orchestration",
        api_key_required=True,
        status="active",
        notes="LangSmith for tracing, evals, dataset management",
    ),
    ServiceEntry(
        id="n8n",
        name="n8n",
        url="https://n8n.io",
        type="backend",
        category="Workflow Automation",
        api_key_required=False,
        status="active",
        notes="Self-hosted or cloud; integrates with any API",
    ),
    ServiceEntry(
        id="claude-web",
        name="Claude.ai",
        url="https://claude.ai",
        type="frontend",
        category="LLM (Chat)",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True, daily_quota=100),
        notes="100 msgs/day free, unlimited with Pro subscription",
    ),
    ServiceEntry(
        id="chatgpt-web",
        name="ChatGPT",
        url="https://chat.openai.com",
        type="frontend",
        category="LLM (Chat)",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True),
        notes="GPT-3.5 free, GPT-4 requires subscription",
    ),
    ServiceEntry(
        id="gemini-web",
        name="Google Gemini Web",
        url="https://gemini.google.com",
        type="frontend",
        category="LLM (Chat)",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True, monthly_quota=None),
        notes="Search-integrated",
    ),
    ServiceEntry(
        id="perplexity-web",
        name="Perplexity Web",
        url="https://perplexity.ai",
        type="frontend",
        category="LLM + Search",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True, daily_quota=5),
        notes="5 pro queries/day free",
    ),
    ServiceEntry(
        id="poe",
        name="Poe",
        url="https://poe.com",
        type="frontend",
        category="LLM Aggregator",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True),
        notes="Access to GPT, Claude, Gemini all in one UI",
    ),
    ServiceEntry(
        id="huggingface",
        name="HuggingFace Inference",
        url="https://huggingface.co",
        type="frontend",
        category="Model Hub + Inference",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True),
        notes="Serverless inference on 200k+ models",
    ),
    ServiceEntry(
        id="github-copilot",
        name="GitHub Copilot",
        url="https://copilot.github.com",
        type="frontend",
        category="Code Generation",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True),
        notes="Integrated in VSCode, Neovim, JetBrains",
    ),
    ServiceEntry(
        id="cursor",
        name="Cursor",
        url="https://www.cursor.sh",
        type="frontend",
        category="AI Code Editor",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True),
        notes="VSCode fork with built-in AI",
    ),
    ServiceEntry(
        id="colab",
        name="Google Colab",
        url="https://colab.research.google.com",
        type="frontend",
        category="Jupyter + GPU",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True),
        notes="T4 GPU free, 12 hours per session",
    ),
    ServiceEntry(
        id="kaggle",
        name="Kaggle",
        url="https://kaggle.com",
        type="frontend",
        category="Data Science + Notebooks",
        api_key_required=False,
        status="active",
        free_tier=FreeTier(available=True),
        notes="Datasets, competitions, notebooks; GPU available",
    ),
    ServiceEntry(
        id="replicate",
        name="Replicate",
        url="https://replicate.com",
        type="backend",
        category="Model Deployment",
        api_key_required=True,
        status="active",
        free_tier=FreeTier(available=True),
        notes="Run open-source models; dreambooth, stable diffusion",
    ),
]


# ---------------------------------------------------------------------------
# Helper: Bootstrap Registry
# ---------------------------------------------------------------------------

def bootstrap_registry() -> None:
    """
    Populate registry with default services if empty.
    Useful on first run to seed the system.
    """
    if not registry.services:
        log.info(f"Bootstrapping registry with {len(DEFAULT_SERVICES)} default services")
        for svc in DEFAULT_SERVICES:
            registry.add_or_update(svc)
    else:
        log.info(f"Registry already populated with {len(registry.services)} services")
