# LLM Orchestrator — Master Architecture

> The brain that routes, remembers, retrieves, and relays across every provider, vault, and agent in the system.

## System Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DESKTOP-SH8JARJ                              │
│                  i5-1335U · 16GB · Iris Xe · Windows                │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   LLM ORCHESTRATOR (FastAPI :8000)            │   │
│  │                                                              │   │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────────────────┐  │   │
│  │  │ ROUTER   │  │ LiteLLM   │  │ ADAPTERS                 │  │   │
│  │  │          │→→│ Gateway   │→→│ OpenRouter ✓  ($10)      │  │   │
│  │  │ FREE_    │  │           │  │ Groq ✓       (free)      │  │   │
│  │  │ FIRST    │  │ Cost      │  │ Gemini ✓     (free)      │  │   │
│  │  │          │  │ Tracking  │  │ DeepSeek ✓   ($4.99)     │  │   │
│  │  │ CHEAPEST │  │           │  │ Perplexity ✓ ($6.90)     │  │   │
│  │  │ _PAID    │  │ Caching   │  │ Grok ✓       (credits)   │  │   │
│  │  │          │  │           │  │ Mistral ✗    (needs $10) │  │   │
│  │  │ VENDOR_  │  │ Fallback  │  │ OpenAI ✗     (no key)    │  │   │
│  │  │ PINNED   │  │ Chains    │  │                          │  │   │
│  │  └──────────┘  └───────────┘  └──────────────────────────┘  │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐    │   │
│  │  │ RAG PIPELINE (LlamaIndex → Pinecone)                 │    │   │
│  │  │                                                      │    │   │
│  │  │  Ingest → Chunk (512tok) → Embed (gemini-embedding)  │    │   │
│  │  │     → Upsert to Pinecone (768-dim, cosine)           │    │   │
│  │  │                                                      │    │   │
│  │  │  Query → Embed → Top-K → Inject as system context    │    │   │
│  │  │                                                      │    │   │
│  │  │  Sources: Force Mult v1 (1600+ files)                │    │   │
│  │  │           Claude Vault knowledge/                     │    │   │
│  │  │           Uploaded documents                          │    │   │
│  │  │                                                      │    │   │
│  │  │  Budget: $300 Pinecone (expires ~May 4)               │    │   │
│  │  │          10K LlamaIndex Cloud credits                 │    │   │
│  │  └──────────────────────────────────────────────────────┘    │   │
│  │                                                              │   │
│  │  ┌──────────────────────┐  ┌─────────────────────────────┐   │   │
│  │  │ MEMORY               │  │ ENDPOINTS                   │   │   │
│  │  │                      │  │                             │   │   │
│  │  │ Conversation context │  │ POST /api/chat/stream  SSE  │   │   │
│  │  │ (in-process + Redis) │  │ POST /api/chat         sync │   │   │
│  │  │                      │  │ POST /api/rag/ingest   docs │   │   │
│  │  │ Vault memory/        │  │ POST /api/rag/query    test │   │   │
│  │  │ glossary.md          │  │ GET  /api/models       list │   │   │
│  │  │ context/             │  │ GET  /api/settings          │   │   │
│  │  │ projects/            │  │ POST /api/settings          │   │   │
│  │  └──────────────────────┘  │ GET  /api/health            │   │   │
│  │                             └─────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐    │
│  │ REACT UI (:5173)     │  │ OBSIDIAN VAULTS                  │    │
│  │                      │  │                                  │    │
│  │ Chat + streaming     │  │ Claude Vault (this vault)        │    │
│  │ Model picker (25)    │  │   ├ _system/ (briefings, drift)  │    │
│  │ RAG toggle + upload  │  │   ├ tasks/ (10 tasks)            │    │
│  │ Provider badges      │  │   ├ knowledge/ (20 entries)      │    │
│  │ Settings (BYO keys)  │  │   ├ decisions/ (2 decisions)     │    │
│  │                      │  │   └ claude_on_claude/             │    │
│  └──────────────────────┘  │                                  │    │
│                             │ Local-Network-Hub (:27124 REST)  │    │
│  ┌──────────────────────┐  │                                  │    │
│  │ OLLAMA (:11434)      │  │ Force Multiplication v1          │    │
│  │ Local fallback       │  │   (1,600+ files, human KB)       │    │
│  │ Qwen2.5-Coder-1.5B  │  └──────────────────────────────────┘    │
│  └──────────────────────┘                                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ WORKFLOW LAYER                                                │   │
│  │                                                              │   │
│  │ n8n (cloud, trial expires 4/20)  →  webhook → FastAPI        │   │
│  │ OpenClaw (agent harness)         →  REST → vault + LLM       │   │
│  │ Hostinger VPS (provisioning)     →  Cloudflare Tunnel        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Provider Budget Matrix

| Provider | Balance | $/1M tokens (approx) | Best For | Priority |
|----------|---------|----------------------|----------|----------|
| Groq | Free | $0 | Fast inference, simple tasks | 1 |
| Gemini | Free | $0 | Long context (1M), embeddings | 1 |
| OpenRouter Free | Included | $0 | Diverse free models | 1 |
| DeepSeek | $4.99 | ~$0.14 input / $0.28 output | Reasoning, coding | 2 |
| Perplexity | $6.90 | ~$1/query | Search-grounded answers | 3 |
| OpenRouter Paid | $10.00 | Varies by model | Claude, GPT-4o access | 3 |
| Grok | Credits | ~$5 | xAI models | 4 |
| Mistral | Dead | Needs $10 | EU models | 5 (dormant) |

## Routing Decision Tree

```
User message arrives
  │
  ├─ User pinned a provider? → VENDOR_PINNED → use that adapter
  │
  ├─ User picked a specific model? → resolve provider → call it
  │
  └─ Auto-route (FREE_FIRST default):
       │
       ├─ 1. OpenRouter free pool (openrouter/auto, :free models)
       ├─ 2. Groq (llama-3.3-70b, free tier)
       ├─ 3. Gemini (gemini-3-flash-preview, free tier)
       ├─ 4. DeepSeek (cheapest paid, $0.14/M)
       ├─ 5. Perplexity (search tasks only)
       └─ 6. OpenRouter paid (Claude/GPT-4o, last resort)
       
  On failure: auto-fallback, flag response as fallback
```

## RAG Strategy

### Phase 1: Current (Pinecone + Gemini Embeddings)
- Embedding: `gemini-embedding-001` (free, 768-dim)
- Storage: Pinecone serverless ($300 credit, ~21 days)
- Chunking: 512 tokens, 64 overlap
- Retrieval: cosine similarity, top-5

### Phase 2: Post-Pinecone (after ~May 4)
- Migrate to LlamaIndex Cloud (10K credits remaining)
- Or self-host with ChromaDB (free, runs locally, ~200MB RAM)
- Keep embedding model the same (Gemini free)

### Priority Ingestion Targets
1. Force Multiplication v1 vault (1,600+ files) → TSK-0009
2. Claude Vault knowledge/ entries (20 files)
3. claude_on_claude/ docs (architecture, handoff, n8n migration)
4. Any uploaded reference docs

## Integration Points

| System | Connection | Status |
|--------|-----------|--------|
| Obsidian REST API | localhost:27124 | Active (TSK-0005) |
| Ollama | localhost:11434 | Active (TSK-0006) |
| n8n | Cloud (webhook → FastAPI) | Trial, expires 4/20 (TSK-0004) |
| OpenClaw | REST → vault + LLM | Needs update |
| Hostinger VPS | Cloudflare Tunnel | Provisioning (TSK-0007) |
| Prometheus/Grafana | vault_exporter.py :9090 | Configured |

## Model Catalog (25 models across 8 providers)

See `backend/config.py` → `MODEL_CATALOG` for the full list.
Frontend model picker shows all available models with free/paid badges.
