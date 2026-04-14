# API & Token Registry

Master registry of all API accounts, free tiers, and frontend token opportunities across AI services. This is a living document tracking up to 29+ service subscriptions.

**Last Updated:** 2026-04-14  
**Total Services:** 35+  
**Active Keys in .env:** 2 live (Gemini, Pinecone), 5 need rotation  
**Expiring Soon:** n8n trial (Apr 20), Pinecone $300 (~May 4)  
**Total API credits:** ~$336.79 | **Free forever platforms:** 12+

---

## Backend APIs (with API keys)

| Service | URL | Status | Credits/Balance | Rate Limits | Expires | Category | Notes |
|---------|-----|--------|-----------------|-------------|---------|----------|-------|
| **OpenRouter** | https://openrouter.ai | `rotate_key` | $10.00 | 1000 RPM | N/A | LLM Router | Paid + free model pool |
| **Groq** | https://console.groq.com | `rotate_key` | Free tier | 30 RPM free | N/A | LLM (Fast) | Llama 3.3 70B, Mixtral, Gemma |
| **Google Gemini** | https://aistudio.google.com | `live` | Free tier | 15 RPM, 1M TPM | N/A | LLM + Embed | gemini-3-flash-preview confirmed |
| **DeepSeek** | https://platform.deepseek.com | `rotate_key` | $4.99 | — | — | LLM | ~$0.14/M input tokens |
| **Perplexity** | https://perplexity.ai/api | `rotate_key` | $6.90 | — | — | LLM (Search) | Sonar models, web-grounded |
| **Mistral AI** | https://console.mistral.ai | `dead` | $0 | — | — | LLM | Needs $10 to reactivate |
| **Grok / xAI** | https://console.x.ai | `rotate_key` | Credits | $25/mo free | Monthly | LLM | grok-3-mini confirmed |
| **OpenAI** | https://platform.openai.com | `no_key` | — | — | — | LLM + Embed | Not configured |
| **Pinecone** | https://console.pinecone.io | `live` | $300.00 | — | ~May 4 | Vector DB | 768-dim index created |
| **LlamaIndex Cloud** | https://cloud.llamaindex.ai | `have_acct` | 10K credits | — | TBD | RAG Platform | Post-Pinecone migration option |
| **LangChain** | https://smith.langchain.com | `have_key` | Unknown | — | — | Orchestration | LangSmith tracing |
| **Anthropic (Claude)** | https://console.anthropic.com | `available` | $4.90 | — | — | LLM | Claude API credits |
| **n8n** | https://n8n.io | `trial` | — | — | **Apr 20!** | Workflow | CRITICAL: extract before expiry |
| **Cloudflare** | https://cloudflare.com | `have_acct` | Free | 100K req/day | — | Edge Compute | Workers, R2, D1, KV |
| **HuggingFace** | https://huggingface.co | `have_acct` | Free | Free inference | — | Models/Inference | 200K+ models |
| **Ollama (local)** | localhost:11434 | `active` | Free | Unlimited | N/A | Local LLM | Qwen2.5-Coder-1.5B |

---

## Frontend / Web Platforms (No API Key Needed)

| Service | URL | Access | Free Tier Limits | Status | Category | Notes |
|---------|-----|--------|------------------|--------|----------|-------|
| **Claude.ai** | https://claude.ai | Browser | 100 msgs/day (free), unlimited (pro) | `active` | LLM (Chat) | Web interface; high-quality responses |
| **ChatGPT** | https://chat.openai.com | Browser | 3-hour limit, older GPT-3.5 | `active` | LLM (Chat) | Free tier has rate limits; GPT-4 requires subscription |
| **Google Gemini Web** | https://gemini.google.com | Browser | Unlimited | `active` | LLM (Chat) | Search-integrated; fast responses |
| **Perplexity Web** | https://perplexity.ai | Browser | 5 pro queries/day free | `active` | LLM + Search | Web search built-in; cite sources |
| **Poe** | https://poe.com | Browser | Free + credits | `active` | LLM Aggregator | Access to GPT, Claude, Gemini all in one UI |
| **HuggingFace Inference** | https://huggingface.co | Browser + API | Free with limits | `active` | Model Hub + Inference | Serverless inference on 200k+ models |
| **GitHub Copilot** | https://copilot.github.com | VSCode/IDE Plugin | Free (public repos), $10/mo (pro) | `active` | Code Generation | Integrated in VSCode, Neovim, JetBrains |
| **Cursor** | https://www.cursor.sh | IDE/App | Free (limited), $20/mo | `active` | AI Code Editor | VSCode fork with built-in AI; Ctrl+K shortcuts |
| **Windsurf / Codeium** | https://windsurf.dev | IDE/App | Free tier available | `active` | Code Generation + IDE | Web development focus; real-time collaboration |
| **Replit** | https://replit.com | Browser | Free (public), $7/mo (pro) | `active` | Cloud IDE + Hosting | Built-in Ghostwriter AI; full dev environment |
| **Vercel** | https://vercel.com | Dashboard + CLI | Free ($0 tier) | `active` | Deployment + Hosting | Next.js optimization; serverless functions |
| **Cloudflare Workers** | https://workers.cloudflare.com | Dashboard + CLI | 100K requests/day free | `active` | Serverless + Edge | Global CDN; R2 object storage, KV, D1 DB |
| **Google Colab** | https://colab.research.google.com | Browser | T4 GPU free, 12 hours | `active` | Jupyter + GPU | Free tier sufficient for experiments; no signup needed |
| **Kaggle** | https://kaggle.com | Browser + API | Free + $20 GPUs | `active` | Data Science + Notebooks | Datasets, competitions, notebooks; GPU available |
| **Replicate** | https://replicate.com | Browser + API | Free tier available | `active` | Model Deployment | Run open-source models; dreambooth, stable diffusion |

---

## Embedded / One-Off Services

| Service | Purpose | Status | Notes |
|---------|---------|--------|-------|
| **n8n** | Workflow automation | `active` | Self-hosted or cloud; integrates with any API |
| **Make (formerly Integromat)** | Workflow automation | `active` | Visual workflow builder; free tier available |
| **Zapier** | No-code automation | `active` | Triggers, actions, filters; connects 10k+ apps |

---

## Status Legend

- `active` — Key loaded, available, tested within last 7 days
- `expired` — Key or free tier expired; needs reload or refresh
- `needs_reload` — Account exists but API key not yet stored in orchestrator
- `inactive` — Deprecated or deprecated in favor of another service
- `untested` — Key exists but not validated against live API

---

## Quick Audit Checklist

Before running the orchestrator:

- [ ] OpenRouter balance > $5
- [ ] Groq free tier still available (check limits)
- [ ] Gemini $300 credits tracking (console.cloud.google.com)
- [ ] OpenAI balance > $0
- [ ] Perplexity API key valid
- [ ] Mistral AI key valid
- [ ] Pinecone serverless index accessible
- [ ] No keys expired (check expires column above)
- [ ] All frontend platforms reachable (browser check)

---

## How to Use This Registry

1. **Manual audit**: Compare this table with `/registry.json` (live config)
2. **API integration**: Use `/api/registry` endpoints to query programmatically
3. **Update frequency**: Refresh `last_verified` field in `registry.json` after testing each service
4. **Add new services**: Create entry above, add to `registry.json`, test via `POST /api/registry`

---

## Adding a New Service

Template:

```json
{
  "id": "service-slug",
  "name": "Service Full Name",
  "url": "https://example.com",
  "type": "backend|frontend",
  "category": "LLM|Embedding|VectorDB|Code|Orchestration|etc",
  "api_key_required": true,
  "api_key": null,
  "status": "active|expired|needs_reload",
  "free_tier": {
    "available": true,
    "rate_limits": "e.g. 1000 RPM, 10M TPM",
    "daily_quota": null
  },
  "paid_tier": {
    "available": false,
    "balance": 0,
    "currency": "USD"
  },
  "expires_at": null,
  "last_verified": "2026-04-13",
  "notes": ""
}
```

---

## Integration Points

- **LLM Router**: Uses backend APIs (OpenRouter, Groq, Gemini, etc.)
- **RAG Pipeline**: Pinecone vector DB + LlamaIndex Cloud
- **Fallback Strategy**: Routes to cheapest/free option if primary fails
- **Frontend Testing**: Check web platforms manually via browser
- **Automation**: n8n, Make, Zapier for cross-service workflows

---

## Known Gaps / Future Additions

- [ ] Anthropic API (claude-3-opus, embeddings) — needs key registration
- [ ] AWS Bedrock — Lambda + Claude integration
- [ ] Azure OpenAI — private deployment option
- [ ] Together.ai — open-source model hosting
- [ ] Modal — serverless GPU
- [ ] Supabase — Postgres + vector extensions
- [ ] Weaviate — self-hosted vector DB
- [ ] Qdrant — vector DB alternative
- [ ] Milvus — open-source vector DB
- [ ] Hugging Face Private Spaces — private model deployment
