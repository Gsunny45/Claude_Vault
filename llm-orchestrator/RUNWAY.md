# RUNWAY — Hit the Ground Running

> This doc exists so any agent, any session, any human can pick up this project and be productive in under 2 minutes. Read this first. Always.

## What Is This?

A multi-LLM orchestration service that:
- Routes messages across **9 providers** (8 cloud + 1 local)
- Picks the cheapest/free option automatically
- Falls back gracefully when providers fail
- Injects knowledge from Pinecone RAG before any LLM call
- Serves a React chat UI with streaming, model picker, and BYO key support

## Quickstart (Windows)

```bat
cd C:\Users\MarsBase\Documents\Claude_Vault\llm-orchestrator

:: 1. Backend
cd backend
copy .env.example .env   (if first time — then add your keys)
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

:: 2. Frontend (new terminal)
cd frontend
npm install
npm run dev

:: 3. Open http://localhost:5173
```

Or just run `start.bat` in the project root.

## Current State (as of 2026-04-13)

### What Works
- [x] 7/9 cloud providers passing (OpenRouter, Groq, Gemini, DeepSeek, Perplexity, Grok, Ollama)
- [x] FREE_FIRST / CHEAPEST_PAID / VENDOR_PINNED routing modes
- [x] SSE streaming with provider/model badges
- [x] BYO key encryption (Fernet, stored in `.keystore.enc`)
- [x] RAG pipeline: upload → chunk → embed (Gemini) → Pinecone → inject
- [x] 26 models in catalog, React UI with model picker
- [x] Ollama local fallback (works offline)

### What Needs Work
- [ ] **Mistral key is dead** — needs $10 reload
- [ ] **OpenAI key not configured** — skip or add later
- [ ] **Pinecone index not yet created** — see Setup below
- [ ] **Force Multiplication v1 not yet indexed** — 1,600+ files for RAG (TSK-0009)
- [ ] **LiteLLM integration** — would replace custom adapters with unified gateway + cost tracking
- [ ] **LlamaIndex Cloud** — 10K credits, better RAG pipeline than raw Pinecone REST
- [ ] **n8n workflows** — trial expires 4/20, extract critical ones (TSK-0004, CRITICAL)

## File Map

```
llm-orchestrator/
├── ARCHITECTURE.md        ← System diagram, budget matrix, routing logic
├── RUNWAY.md              ← THIS FILE — start here
├── backend/
│   ├── main.py            ← FastAPI app (chat, stream, RAG, settings endpoints)
│   ├── router.py          ← Routing engine (FREE_FIRST, fallback chains)
│   ├── rag.py             ← Pinecone RAG (chunk, embed, retrieve, inject)
│   ├── crypto.py          ← Fernet key encryption
│   ├── config.py          ← Provider catalog, model list, settings
│   ├── models.py          ← Pydantic request/response models
│   ├── adapters/
│   │   ├── base.py        ← LLMClient ABC interface
│   │   ├── openrouter.py  ← Primary aggregator (paid + free pool)
│   │   ├── groq.py        ← Fast free inference
│   │   ├── gemini.py      ← Google (native API, not OpenAI-compat)
│   │   ├── deepseek.py    ← Cheap reasoning
│   │   ├── perplexity.py  ← Search-grounded
│   │   ├── mistral.py     ← EU models (key dead)
│   │   ├── grok.py        ← xAI
│   │   ├── openai_adapter.py ← Direct OpenAI
│   │   └── ollama.py      ← Local fallback (no network)
│   ├── test_keys.py       ← Validates all API keys
│   ├── list_gemini_models.py ← Discovers available Gemini models
│   ├── .env               ← SECRETS (never commit, rotate after exposure)
│   └── .env.example       ← Template
├── frontend/
│   ├── src/
│   │   ├── App.jsx        ← Main app (model picker, RAG toggle, upload)
│   │   ├── api.js         ← Fetch/stream client
│   │   ├── hooks/useChat.js ← Conversation state + streaming
│   │   ├── components/
│   │   │   ├── Chat.jsx       ← Message list + input
│   │   │   ├── MessageBubble.jsx ← Badges (free/paid/fallback/RAG)
│   │   │   ├── ModelPicker.jsx   ← Dropdown from /api/models
│   │   │   └── Settings.jsx     ← BYO keys + routing mode
│   │   └── styles.css     ← Dark theme
│   └── vite.config.js     ← Dev proxy → :8000
├── start.bat / start.sh   ← Launch both services (local dev)
└── deploy/
    ├── docker-compose.yml ← Full stack: backend + frontend + n8n + Caddy
    ├── Dockerfile.backend ← Python 3.11 slim
    ├── Dockerfile.frontend← Node build → Caddy static serve
    ├── Caddyfile          ← Reverse proxy with auto-HTTPS
    ├── .env.example       ← VPS env template
    └── bootstrap-vps.sh   ← One-shot VPS setup (Docker, firewall, dirs)
```

## VPS Deployment (Hostinger)

**Server:** `89.117.139.137` / `peachpuff-newt-682861.hostingorsite.com` (50GB)

```bash
# 1. SSH into VPS
ssh root@89.117.139.137

# 2. Run bootstrap (installs Docker, opens ports)
bash bootstrap-vps.sh

# 3. Copy project to VPS (from your local machine)
scp -r llm-orchestrator/ root@89.117.139.137:/opt/llm-orchestrator/

# 4. Configure
cd /opt/llm-orchestrator/deploy
cp .env.example .env
nano .env  # paste rotated API keys, set N8N_PASSWORD

# 5. Launch
docker compose up -d --build

# 6. Verify
curl http://localhost/api/health
# Frontend: https://peachpuff-newt-682861.hostingorsite.com
# n8n:      https://peachpuff-newt-682861.hostingorsite.com/n8n/
# API:      https://peachpuff-newt-682861.hostingorsite.com/api/health
```

Caddy auto-provisions HTTPS via Let's Encrypt. n8n self-hosted replaces the dying cloud trial (TSK-0004).

## Adding a New Provider

1. Create `backend/adapters/newprovider.py` implementing `LLMClient`
2. Add to `ADAPTER_MAP` in `adapters/__init__.py`
3. Add provider config in `config.py` → `PROVIDERS` dict
4. Add model entries in `config.py` → `MODEL_CATALOG`
5. Add env var to `.env.example` and `Settings` dataclass
6. Add to `api_key_for()` if it needs special handling
7. Run `python test_keys.py` to validate

## Setting Up Pinecone RAG

```
1. Go to console.pinecone.io → Create Index
   Name: orchestrator-rag
   Dimensions: 768
   Metric: cosine
   Type: serverless (any region)

2. Copy the Host URL from index details

3. Add to .env:
   PINECONE_API_KEY=your-key
   PINECONE_HOST=https://orchestrator-rag-xxxxx.svc.xxx.pinecone.io

4. Upload docs via UI ("Upload Doc" button) or API:
   curl -X POST http://localhost:8000/api/rag/ingest \
     -F "file=@document.txt" -F "source_name=my-doc"

5. Toggle RAG checkbox in chat UI to use retrieved context
```

## Budget Reality Check

| Provider | Balance | Burn Rate | Runway |
|----------|---------|-----------|--------|
| Groq | Free | $0 | Forever |
| Gemini | Free | $0 | Forever (free tier) |
| OR Free Pool | Included in $10 | ~$0 | Forever (free models) |
| Ollama | Free | $0 | Forever (local) |
| DeepSeek | $4.99 | ~$0.14/M tok | Months of light use |
| Perplexity | $6.90 | ~$1/query | ~7 search sessions |
| OpenRouter Paid | $10.00 | Varies | ~100 Claude/GPT queries |
| Pinecone | $300 | Time-limited | Expires ~May 4 |
| LlamaIndex | 10K credits | Unknown | TBD |

**Strategy:** Use free tiers for 90% of traffic. Reserve paid for when you specifically need Claude, GPT-4o, or search grounding.

## New Scripts (run on your machine)

```bat
:: Test the full RAG pipeline (Pinecone + Gemini embeddings)
python test_rag.py

:: Ingest all vault knowledge, tasks, decisions, docs into Pinecone
python ingest_vault.py

:: Validate API keys
python test_keys.py

:: List available Gemini models
python list_gemini_models.py
```

## API Registry

The orchestrator now tracks ALL your services (backend + frontend) via:
- `memory/context/api-registry.md` — master catalog (35+ services)
- `backend/registry.py` — FastAPI module with endpoints:
  - `GET /api/registry` — list all services (filter by type/category)
  - `GET /api/registry/summary` — budget totals, expiring soon
  - `POST /api/registry` — add/update a service
- `backend/registry.json` — persistent JSON store (auto-seeded on first run)

## Obsidian Plugin Recommendations (KNW-0021)

| Plugin | Stars | Why Install |
|--------|-------|-------------|
| **Claudian** | 7.7K | Direct Claude Code ↔ vault integration, MCP support |
| **Copilot Plus** | 6.7K | In-vault AI agent with long-term memory |
| **Text Generator** | 1.9K | Multi-provider inline text gen |

See `knowledge/KNW-0021.md` for full details.

## Related Vault Context

| Resource | Location | Why It Matters |
|----------|----------|----------------|
| API registry | `memory/context/api-registry.md` | Master service catalog (35+) |
| API budgets | `memory/context/api-budgets.md` | Current balances |
| Project status | `memory/projects/llm-orchestrator.md` | Known issues, integration status |
| Glossary | `memory/glossary.md` | Acronyms and service names |
| Vault briefing | `_system/_briefing.md` | Full context (tasks, decisions, knowledge) |
| Plugin research | `knowledge/KNW-0021.md` | Obsidian + Claude plugin recs |
| Task board | `Task_Board.md` | Related tasks (TSK-0004, TSK-0006, TSK-0009) |
| Architecture docs | `claude_on_claude/docs/` | Distributed system design |

## Critical Deadlines

| Deadline | What | Task |
|----------|------|------|
| **2026-04-20** | n8n trial expires (5 DAYS) | TSK-0004 — extract workflows OR deploy self-hosted n8n on VPS |
| **~2026-05-04** | Pinecone $300 credit expires | Migrate to LlamaIndex Cloud or ChromaDB |

## Next Steps (Priority Order)

1. **ROTATE ALL API KEYS** — they were exposed in a Cowork session on 4/13
2. **Get SSH access** to VPS (89.117.139.137) via Hostinger hPanel
3. **Deploy to VPS** — run `bootstrap-vps.sh`, then `docker compose up -d` (kills n8n deadline)
4. **Ingest the vault into Pinecone** — run `python ingest_vault.py` locally
5. **Test RAG chat** — toggle RAG on in UI, ask about your vault content
6. **Install Claudian** in Obsidian — bridges vault ↔ orchestrator
7. **Rotate keys into deploy/.env** for VPS, re-add all provider keys
8. Evaluate LiteLLM as adapter replacement (simpler code, built-in cost tracking)
9. Wire Obsidian REST API (:27124) to orchestrator for vault-aware chat
10. Plan Pinecone → ChromaDB/LlamaIndex migration before credit expiry
11. Catalog remaining ~15 API accounts from your historical 29
