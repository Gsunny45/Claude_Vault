# API Budgets & Credits

Last updated: 2026-05-27 (session-5 state sync — post keyboard project sessions)

## Active Balances

| Provider | Balance | Status | Notes |
|----------|---------|--------|-------|
| **Gemini** | Free tier | ACTIVE | 2-3 keys available. Live in keyboard app triggers.json (priority 4/5). |
| **Groq** | Free tier | ACTIVE | 3 keys available (~160K TPD combined). Live in keyboard app triggers.json (priority 2/3). Primary daily driver. |
| **Pinecone** | $300.00 credit | EXPIRED 2026-05-04 | 21-day grant from 4/13 has lapsed. Evaluate ChromaDB fallback or renew. |
| **Claude API** | $0.00 remaining | EXHAUSTED | Burned across keyboard project sessions. Do NOT route anything here. |
| **DeepSeek** | $0.00 remaining | EXHAUSTED | Confirmed $0. Do NOT use. |
| **OpenRouter** | $10.00 remaining | DEACTIVATED 2026-04-19 | Needs fresh key when re-enabled |
| **Perplexity** | $6.90 remaining | DEACTIVATED 2026-04-19 | Needs fresh key when re-enabled |
| **Grok (xAI)** | Active credits | DEACTIVATED 2026-04-19 | Needs fresh key when re-enabled |
| **Cerebras** | Unknown | ACTIVE in ladder | Priority 6 in keyboard app. Free tier — check if key still valid. |
| **Mistral** | Dead key | Needs $10 | Not operational |
| **LlamaIndex Cloud** | 10,000 credits | Have account | cloud.llamaindex.ai |
| **LangChain** | Have API key | Available | Unknown balance |
| **n8n** | Trial | EXPIRED 2026-04-20 | Trial lapsed. Self-host or renew. |
| **OpenAI** | No key | — | Not configured |

## Claude Usage Context (as of 2026-05-27)
- Claude API balance: $0.00 — EXHAUSTED. Do not route to Anthropic API.
- DeepSeek: $0.00 — EXHAUSTED. Do not route.
- Strategy: Groq (free) → Gemini (free) → Cerebras (free if valid) for all inference
- Hermes desktop config: route generation to Gemini/Groq/Skywork (localhost:43111)
- Keyboard app ladder: local(Note20 Qwen) → groq → groq2 → gemini_1 → gemini_2 → cerebras

## Keys Currently Live in .env
- GEMINI_API_KEY ✓ (rotated/fresh)
- PINECONE_API_KEY ✓ (credit expired 5/4 — key still valid but no credits)
- PINECONE_HOST ✓ (index may be deleted after credit lapse)
- All others: DEACTIVATED by Mars 2026-04-19 — generate fresh keys when ready to re-enable

## Priority Order (cost efficiency)
1. Free forever: Groq, Gemini, OpenRouter free pool, Ollama local
2. Cheap: DeepSeek ($4.99), Claude API ($4.90)
3. Moderate: Perplexity ($6.90), OpenRouter paid ($10)
4. Time-limited: LlamaIndex (10K credits). Pinecone EXPIRED 5/4, n8n EXPIRED 4/20
5. Dormant: Mistral (dead), OpenAI (no key)

## Frontend Token Opportunities (Mars' vision)
The user has historically maintained ~29 API accounts. The goal is to catalog ALL
free-tier frontends and APIs — not just backend keys — to build a "nerve system"
of free tokens across online platforms. This includes:
- AI chat frontends with free tiers (Claude.ai, Gemini, ChatGPT, Poe, etc.)
- Coding assistants (Cursor, Windsurf, GitHub Copilot, etc.)
- Platform-specific free allocations (HuggingFace, Replicate, etc.)
- Online project spaces that grant free compute/tokens

## Infrastructure

### Local — DESKTOP-SH8JARJ
- CPU: 13th Gen i5-1335U (1.30 GHz)
- RAM: 16 GB
- GPU: Intel Iris Xe (128 MB) — no local inference beyond tiny models
- Storage: 453/477 GB used (~24 GB free)
- Runs: Obsidian vaults, Ollama, local dev

### VPS — Hostinger (live as of 2026-04-14)
- URL: https://peachpuff-newt-682861.hostingorsite.com
- IP: 89.117.139.137
- Storage: 50 GB
- Access: hPanel (SSH not yet configured)
- Planned: Full stack deploy (orchestrator + React UI + n8n self-hosted)
- Deploy config: `llm-orchestrator/deploy/` (Docker Compose + Caddy + Dockerfiles)
