# Glossary

Workplace shorthand, acronyms, API services, and internal language.

## Service Acronyms
| Term | Meaning | Context |
|------|---------|---------|
| OR | OpenRouter | LLM aggregator, Mars is paying |
| RAG | Retrieval-Augmented Generation | Pinecone-backed knowledge injection |
| BYO | Bring Your Own (keys) | Users supply their own API keys |
| FM v1 | Force Multiplication v1 | Legacy 4,351-file knowledge base, deprecated per DEC-0003 |
| WSL | Windows Subsystem for Linux | Kali/Ubuntu execution environment on DESKTOP-SH8JARJ |
| MCP | Model Context Protocol | Tool/connector standard for LLM agents |
| VPS | Virtual Private Server | Hostinger KVM 2 — the spine for remote services |

## API Services & Platforms
| Service | What | Status |
|---------|------|--------|
| OpenRouter | LLM aggregator/router | Active, $10 remaining |
| Groq | Fast inference (free tier) | Active, free |
| Gemini | Google AI models | Active, free tier |
| DeepSeek | Cheap LLM provider | Active, $4.99 remaining |
| Perplexity | Search-grounded LLM | Active, $6.90 remaining |
| Mistral | EU-based LLM | Dead key, needs $10 reload |
| Grok | xAI LLM | Active |
| Pinecone | Vector DB for RAG | $300 credit, 21 days from 4/13 (expires ~5/4) |
| LlamaIndex Cloud | LLM framework cloud | 10,000 credits remaining |
| LangChain | LLM orchestration framework | Have API key |
| n8n | Workflow automation | Trial EXPIRED 2026-04-20. Self-host planned on Hostinger VPS |
| Hostinger | VPS hosting provider | KVM 2 VPS for n8n, Docker, remote agents. Refund/repurchase pending |
| Cloudflare Tunnel | Secure public access to private services | Planned for vault REST API (:27124) exposure |
| Docker | Container runtime | Deployment target on Hostinger VPS |
| Caddy | Reverse proxy / TLS terminator | Docker stack on VPS, config in llm-orchestrator/deploy/ |
| ChromaDB | Open-source vector DB | Planned Pinecone fallback after credit expiry |
| Obsidian | Knowledge management platform | Runs 3+ vaults locally, REST API on :27123 |

## Project Codenames
| Codename | Project |
|----------|---------|
| LLM Orchestrator | Multi-provider chat service + React UI |
| Claude Vault | AI operational layer (Obsidian vault) |
| RAG_Vault | Dedicated retrieval corpus — replaces FM v1 (per DEC-0003) |
| Command_Vault | Monitoring/observability control plane — not yet scaffolded |
| Local-Network-Hub | Orchestration — REST API, webhooks, cross-vault routing |
| Claude_on_Claude | Self-referential LLM project — nested repo, extraction pending |
| agentA-Z | Android AI keyboard — iceboxed, own repo at Documents\agentA-Z\ |

## Vault Concepts
| Term | Meaning |
|------|---------|
| Drift | Stale references, schema violations, orphan notes — detected by drift-detector plugin |
| Briefing | Token-budgeted warm-start doc compiled by context-compiler plugin |
| TSK/KNW/DEC/SES | Vault ID prefixes: tasks, knowledge, decisions, sessions (4-digit zero-padded) |
