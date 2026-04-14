# LLM Orchestrator

**Status:** Active, operational
**Location:** `Claude_Vault/llm-orchestrator/`
**Started:** 2026-04-13
**Runway doc:** `llm-orchestrator/RUNWAY.md` — start here every session

## What It Is
Multi-provider LLM orchestration service with automatic routing, Pinecone RAG, BYO key support, and local Ollama fallback. React chat frontend with streaming.

## Stack
- Backend: Python FastAPI, httpx, Fernet encryption
- Frontend: React 19 + Vite 6
- RAG: Pinecone ($300 credit) + Gemini embeddings (free)
- Local fallback: Ollama (Qwen2.5-Coder-1.5B)

## Providers (9 adapters, 26 models)

| Provider | Adapter | Test Status | Balance |
|----------|---------|-------------|---------|
| OpenRouter | openrouter.py | PASS | $10 |
| Groq | groq.py | PASS | Free |
| Gemini | gemini.py | PASS (fixed 4/13) | Free |
| DeepSeek | deepseek.py | PASS | $4.99 |
| Perplexity | perplexity.py | PASS | $6.90 |
| Mistral | mistral.py | Key dead | Needs $10 |
| Grok | grok.py | PASS | Credits |
| OpenAI | openai_adapter.py | No key | — |
| Ollama | ollama.py | Local | Free forever |

## Key Files
- `RUNWAY.md` — quickstart + full context for any agent
- `ARCHITECTURE.md` — system diagram, budget matrix, routing logic
- `backend/router.py` — FREE_FIRST / CHEAPEST_PAID / VENDOR_PINNED
- `backend/rag.py` — Pinecone chunk/embed/retrieve pipeline
- `backend/test_keys.py` — validates all API keys

## Known Issues
- API keys exposed in Cowork chat 4/13 — MUST ROTATE ALL
- Pinecone index not yet created
- Force Mult v1 not yet indexed for RAG (TSK-0009)

## Future Integrations
- LiteLLM (unified gateway, cost tracking) — replaces custom adapters
- LlamaIndex Cloud (10K credits) — better RAG pipeline
- n8n webhook → FastAPI (trial expires 4/20)
- Obsidian REST API (:27124) → vault-aware chat
- ChromaDB fallback when Pinecone credit expires (~May 4)
