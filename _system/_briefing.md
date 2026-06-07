---
type: briefing
compiled: "2026-06-05T02:41:33Z"
token_budget: 8000
token_actual: 7941
scope: auto-compiled
notes_included:
  - "CLAUDE.md"
  - "decisions/DEC-0006.md"
  - "knowledge/KNW-0029-cte-fix-trigger-deadend.md"
  - "decisions/DEC-0005.md"
  - "decisions/DEC-0003.md"
  - "sessions/HANDOFF-claude-design-landing-2026-05-30.md"
  - "decisions/DEC-0004.md"
  - "knowledge/KNW-0012.md"
notes_excluded_reason:
  - path: "knowledge/KNW-0028-gemini-multikey-framework-survey.md"
    reason: "token budget exceeded (need 2600, remaining 2009)"
  - path: "knowledge/KNW-0025-keyboard-vault-injection-tests.md"
    reason: "token budget exceeded (need 1700, remaining 609)"
  - path: "knowledge/KNW-0024.md"
    reason: "token budget exceeded (need 1500, remaining 109)"
  - path: "tasks/TSK-0003.md"
    reason: "token budget exceeded (need 811, remaining 109)"
  - path: "sessions/NEXT-SESSION-cte-audit-handoff.md"
    reason: "token budget exceeded (need 1500, remaining 109)"
---

## Vault State

- **Total notes:** 69
- **Open tasks:** 6
- **Recent decisions:** 5

## Changed Since Last Compile

**(root)/**
- [[CLAUDE.md]]

**knowledge/**
- [[knowledge/KNW-0029-cte-fix-trigger-deadend.md]]


## Key Context

### [[CLAUDE.md]]

- **Score:** 0.700 (recency=1.00, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~2541

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

### [[decisions/DEC-0006.md]]

- **Score:** 0.699 (recency=0.91, delta=0.42, links=1.00, importance=0.50)
- **Tokens:** ~700

Safe, pre-authorized edits applied 2026-05-29 (see [[knowledge/KNW-0026]] §2): - `AGENTS.md` keyboard entry un-iceboxed to match CLAUDE.md; repo-status column set to on-disk reality (Command_Vault/RAG_Vault exist sans repo; Local-Network-Hub has a repo). - `_system/vault_config.yaml` `not_in_system`...

### [[knowledge/KNW-0029-cte-fix-trigger-deadend.md]]

- **Score:** 0.697 (recency=0.99, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~1500

Live-debugged on the Note 20 Ultra (`R5CN81CDXJV`) 2026-06-03. The "nothing happens" on `/fix` was **four stacked bugs**, each confirmed by logcat. Detection itself works; the failures are config + routing + a self-inflicted regression.

### [[decisions/DEC-0005.md]]

- **Score:** 0.610 (recency=0.91, delta=0.39, links=0.60, importance=0.50)
- **Tokens:** ~600

Following the 2026-05-29 injection test suite ([[knowledge/KNW-0025]]), Mars set two provider keys (Gemini + Groq) and authorized moving the project forward with the recommended fixes. The suite had found the shipped `CteKeysActivity` launch doc-comment was wrong and that injection silently no-ops w...

### [[decisions/DEC-0003.md]]

- **Score:** 0.609 (recency=0.90, delta=0.27, links=0.80, importance=0.50)
- **Tokens:** ~650

The vault's own docs (CLAUDE.md, vault_config.yaml, MAD_MAX_STATUS.md, Claude_on_Claude/docs/ARCHITECTURE.md, and ~10 knowledge entries) described a 3-vault ecosystem:

### [[sessions/HANDOFF-claude-design-landing-2026-05-30.md]]

- **Score:** 0.578 (recency=0.93, delta=0.60, links=0.10, importance=0.50)
- **Tokens:** ~1400

**Hand this to Claude Design.** It is a *gap brief*, not a brand re-explanation — the full brand brief already exists and should be read alongside this:

### [[decisions/DEC-0004.md]]

- **Score:** 0.570 (recency=0.90, delta=0.27, links=0.60, importance=0.50)
- **Tokens:** ~500

[[DEC-0003]] (2026-04-19) iceboxed the keyboard, sending it to a new non-vault folder `Documents\agentA-Z\` with its own repo, and moved [[tasks/TSK-0003]] to `cancelled`. That folder was never scaffolded.

### [[knowledge/KNW-0012.md]]

- **Score:** 0.129 (recency=0.10, delta=0.00, links=0.00, importance=0.50)
- **Tokens:** ~50

Placeholder note created from template. Originally had duplicate ID KNW-0006 (conflict with Force Multiplication v1 entry). Reassigned to KNW-0012. Needs content or user decision to delete.

## Open Tasks

- **[[tasks/TSK-0005.md|Obsidian Blood Flow — Vault REST API Pipeline for All Agents]]** — status: open, priority: high
- **[[tasks/TSK-0010.md|Daily Workflow Nerve — Automated Vault Briefing + Task Triage]]** — status: open, priority: normal
- **[[tasks/TSK-0002.md|Configure Local REST API for external agent access]]** — status: open, priority: normal
- **[[tasks/TSK-0008.md|Vault Health Sweep — Fix Drift, Schema, Stale Refs]]** — status: open, priority: normal
- **[[tasks/TSK-0006.md|Local LLM Bones — Ollama Service + Model Selection + Always-On Fallback]]** — status: open, priority: high
- **[[tasks/TSK-0003.md|Injection Keyboard (HermeticA-Z) — Android AI keyboard orchestration system]]** — status: in_progress, priority: normal

## Recent Decisions

- **[[decisions/DEC-0006.md|Vault ecosystem alignment — safe edits applied, structural choices opened]]** (2026-05-29): Docs must describe reality, but the architecture framing (4-vault vs N-vault), whether to init repos, and where the visual authority lives are design choices that change the system's contract — those belong to Mars. Mechanical fixes that DEC-0004/0005 already authorize were applied immediately.
- **[[decisions/DEC-0007.md|Canonical keyboard vault = harness Hermetic_A-Z_Vault; Hermes_Phone_Vault name-collision resolved; injection wiring confirmed shipped]]** (2026-05-29): The injection vault already exists, is already in the project folder, is bridge-compatible (40/40 injectable notes use flat key:value frontmatter), and the consuming code is already wired. Merging would duplicate, not stabilize. Lowest-confusion path is to bless what exists, keep the device-ops vault separate, and retire the never-built merge design. Boundary from DEC-0003/0006 stands: the harness vault is content beside the code, not a vault-of-record inside Claude_Vault.
- **[[decisions/DEC-0005.md|Keyboard go-live: keys set, injection path fixed and verified]]** (2026-05-29): The injection path is the keyboard<->vault contract. With provider keys now live, the path must be reliable, not just demonstrable from a cold start. Fixes are small, compile clean, and were verified on the Moto.
- **[[decisions/DEC-0004.md|Un-icebox the injection keyboard — active project at android-ai-keyboard-harness]]** (2026-05-28): Docs must describe reality. The keyboard is active; the agentA-Z path never existed. Adopt the working harness name and mark TSK-0003 in_progress, while preserving the DEC-0003 boundary that the keyboard is not a vault and its code/internals stay out of Claude_Vault.
- **[[decisions/DEC-0003.md|4-vault architecture correction — Command_Vault + Local-Network-Hub + Claude_Vault + RAG_Vault]]** (2026-04-19): Each vault gets one role: Command_Vault monitors, Local-Network-Hub orchestrates, Claude_Vault is AI ops, RAG_Vault is retrieval. Removes FM v1 dependency. Enables clean repo-per-vault.

## Drift Warnings

Issues detected in `_system/_drift_report.md`:

- **Critical:** 2
- **High:** 3
- **Medium:** 3
- **Low:** 3
