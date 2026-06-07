---
type: knowledge
id: KNW-0028
subject: "Framework + gateway survey for multiplexing 5 free Gemini AI Studio keys across project use cases"
confidence: verified
last_verified: 2026-05-31
source: "Two sub-agent sweeps of GitHub + web (orchestration frameworks; multi-key gateways), 2026-05-31. Model-version section re-verified 2026-05-31 (Gemini 3.5 Flash GA 2026-05-19) after an initial stale-data error."
related:
  - "KNW-0027"
  - "project_wsl_stack"
tags: [gemini, free-tier, key-rotation, agent-orchestration, litellm, gemini-balance, langgraph, pydantic-ai, agno, gateway, multiplex]
tokens: 2600
---

# Multiplexing 5 Free Gemini Keys — Framework & Gateway Survey (2026-05-31)

Goal: pick a stack that adapts across many project use cases and has real orchestration
depth (Mars' stated priorities), while leveraging **5x free Gemini AI Studio keys**.

## 0. Model facts (corrected 2026-05-31)

**Gemini 3.5 Flash is real and current** — it reached general availability **2026-05-19**
(Google I/O '26), skipping a preview tag. It's Google's new default, agent/coding-focused,
~3x the price of 3 Flash Preview (paid tier ~$1.50/M in, $9/M out). Current siblings:
**Gemini 3.1 Pro** (reasoning, GA Feb 2026) and **3.1 Flash-Lite**.
*(An earlier draft of this note wrongly claimed "3.5 Flash doesn't exist" — that came from
stale 2.5-era search results and is now fixed. The key Mars has been using is fine.)*

**Free-tier caveat — verify live, do NOT trust old numbers:** Google has historically applied
rate limits **per project, not per API key**, so 5 keys inside one GCP project share one quota
(no multiplication); 5 *separate* projects give real parallel quota. But 3.5 Flash is brand-new
and pricier, so whether it has a free tier — and its exact RPM/RPD/TPM — must be confirmed on
your own AI Studio quota dashboard before assuming any ~5x gain. The 2.5-era limit tables
floating around the web no longer apply.

## 1. The right architecture: split into two layers

**No mainstream agent framework does round-robin key rotation natively.** They do *model*
fallback, not *credential* load-balancing. So decouple:

- **Layer A — key-pool gateway** (one OpenAI-compatible endpoint, rotates the 5 keys, fails over on 429).
- **Layer B — orchestration framework** (points at Layer A's `base_url`; never sees the keys).

This keeps key management orthogonal, lets Mars swap frameworks freely against the same pool,
and slots into the already-installed **smolagents + qwen-agent** (both consume OpenAI-compat).

## 2. Layer A — gateway shortlist (pool the 5 keys)

| Tool | Stars | Fit | Notes |
|------|-------|-----|-------|
| **gemini-balance** (snailyp) | ~5.9k | Best zero-config Gemini-only | Drop 5 keys in `API_KEYS`, round-robin + auto-retry + auto-disable/recover, OpenAI **and** native Gemini endpoints, SQLite mode, key-status dashboard, 1 Docker container. **License CC BY-NC** (personal/dev only). |
| **LiteLLM** (BerriAI) | ~49k | Best general / future-proof | Router pattern: define same model alias 5× with 5 keys → load-balances (`simple-shuffle`/`least-busy`/latency), retries+fallbacks. MIT. Not Gemini-locked. Already in Mars' mental model via smolagents. |
| **gpt-load** (tbphp) | growing | Light multi-provider middle ground | Single Go binary, key-pool + blacklist/recovery, native Gemini channel, encrypted key store. |
| **Portkey Gateway** (OSS) | ~11.7k | Tiny fast gateway | ~100kb TS, weighted load-balance + fallback across keys, Apache-2.0. |

Smaller Gemini rotators if you want something tiny/readable: `lehuygiang28/gemini-proxy`,
`p32929/rotato` (zero-dep Node), `TerrenceMiao/gemini-proxy`, `mxyhi/token_proxy`.
**Skip:** Kong / Higress (too heavy for 16GB no-GPU), RouteLLM (quality router, not key pooling),
OpenRouter / Cloudflare AI Gateway (hosted; don't pool *your own* keys).

## 3. Layer B — orchestration framework shortlist

Weighted for **adaptability + orchestration depth + Gemini compat** on i5/16GB/no-GPU:

| Rank | Framework | Stars | Orchestration | Gemini | Why |
|------|-----------|-------|---------------|--------|-----|
| 1 | **LangGraph** | ~13k | graph/state (deepest) | native (`langchain-google-genai`) | Cycles, persistence, human-in-loop; Google ships an official quickstart. Default when depth is the priority. |
| 2 | **Agno** (ex-Phidata) | ~39k | multi-agent teams + workflows + memory | native | Claims ~24x lower RAM than LangGraph → ideal for 16GB. Best adaptability-per-resource. |
| 3 | **Pydantic-AI** | active | single+tools, compose to multi | native (`google-gla`) | Cleanest to embed typed agents across many projects; `FallbackModel`+retry. Tiny footprint. |
| 4 | **Google ADK** | active | multi-agent + workflow agents | best-in-class native | Safest long-term Gemini bet; slight Vertex/GCP pull. |
| 5 | **CrewAI** | ~31k | multi-agent (roles/crews) | native | Fastest path to multi-agent results; approachable, small deps. |

Ultra-light / honorable mentions: **smolagents** (already installed; code-as-action),
**Atomic Agents** (schema-driven, minimal), **qwen-agent** (already installed; best if also
running local Qwen), **DSPy** (uses LiteLLM internally → synergizes with the key pool; great if
prompt-optimization/quality matters and you want many cheap calls). Note: original Microsoft
AutoGen is now maintenance-mode → merged into **Microsoft Agent Framework** (GA Apr 2026); use
**AG2** fork or the new MS framework if going that route.

## 4. Recommendation

- **Quickest win, Gemini-only:** `gemini-balance` + **Pydantic-AI** (or LangGraph). Almost no config.
- **Most future-proof / multi-provider:** **LiteLLM proxy** (5 projects → 5 keys → 1 alias) +
  **LangGraph** for depth, or **Agno** if RAM headroom matters most.
- **Hard prerequisite either way:** create the 5 keys in **5 separate GCP projects**, or the
  rotation buys nothing.

## 5. Open follow-ups
- Confirm whether Mars' 5 keys are already in separate projects (decides if a quota gain is even possible).
- If yes → stand up LiteLLM/gemini-balance on WSL, wire one framework, benchmark aggregate RPM.
- Possible DEC entry if a framework is adopted as the standard harness.
