---
type: briefing
compiled: "2026-05-30T20:03:41Z"
token_budget: 8000
token_actual: 7990
scope: auto-compiled
notes_included:
  - "decisions/DEC-0003.md"
  - "decisions/DEC-0006.md"
  - "tasks/TSK-0003.md"
  - "decisions/DEC-0004.md"
  - "knowledge/KNW-0022.md"
  - "knowledge/KNW-0024.md"
  - "decisions/DEC-0005.md"
  - "tasks/TSK-0001.md"
  - "knowledge/KNW-0025-keyboard-vault-injection-tests.md"
  - "inbox/2026-05-30.md"
  - "inbox/2026-05-17.md"
  - "inbox/2026-04-26.md"
  - "inbox/2026-04-20.md"
  - "inbox/2026-04-14.md"
notes_excluded_reason:
  - path: "tasks/TSK-0004.md"
    reason: "token budget exceeded (need 1092, remaining 100)"
  - path: "memory/context/api-budgets.md"
    reason: "token budget exceeded (need 917, remaining 100)"
  - path: "knowledge/GEMINI-MASTER-BUILD.md"
    reason: "token budget exceeded (need 10258, remaining 100)"
  - path: "decisions/DEC-0007.md"
    reason: "token budget exceeded (need 680, remaining 82)"
  - path: "sessions/SES-2026-05-29-001.md"
    reason: "token budget exceeded (need 700, remaining 82)"
---

## Vault State

- **Total notes:** 85
- **Open tasks:** 6
- **Recent decisions:** 5

## Changed Since Last Compile

**(root)/**
- [[GEMINI_ORCHESTRATOR_BUILD_PROMPT.md]]
- [[device-setup-note20-moto.md]]
- [[CLAUDE.md]]
- [[AGENTS.md]]

**decisions/**
- [[decisions/DEC-0007.md]]
- [[decisions/DEC-0006.md]]
- [[decisions/DEC-0005.md]]
- [[decisions/DEC-0004.md]]
- [[decisions/DEC-0003.md]]

**inbox/**
- [[inbox/2026-05-30.md]]
- [[inbox/nous_bug_report.md]]
- [[inbox/hermetic_facelift_handoff.md]]
- [[inbox/gemini_packet_01_ai_screens.md]]

**knowledge/**
- [[knowledge/KNW-0027-vault-skills-standards-audit.md]]
- [[knowledge/KNW-0026-vault-alignment-path-plan.md]]
- [[knowledge/KNW-0025-keyboard-vault-injection-tests.md]]
- [[knowledge/KNW-0024.md]]
- [[knowledge/KNW-0023.md]]
- [[knowledge/KNW-0022.md]]
- [[knowledge/GEMINI-MASTER-BUILD.md]]

**memory/context/**
- [[memory/context/api-budgets.md]]

**sessions/**
- [[sessions/SES-2026-05-29-001.md]]
- [[sessions/SES-2026-05-28-001.md]]
- [[sessions/SES-2026-05-27-001.md]]

**tasks/**
- [[tasks/TSK-0004.md]]
- [[tasks/TSK-0003.md]]
- [[tasks/TSK-0001.md]]


## Key Context

### [[decisions/DEC-0003.md]]

- **Score:** 0.892 (recency=0.97, delta=1.00, links=1.00, importance=0.50)
- **Tokens:** ~650

The vault's own docs (CLAUDE.md, vault_config.yaml, MAD_MAX_STATUS.md, Claude_on_Claude/docs/ARCHITECTURE.md, and ~10 knowledge entries) described a 3-vault ecosystem:

### [[decisions/DEC-0006.md]]

- **Score:** 0.847 (recency=0.99, delta=1.00, links=0.75, importance=0.50)
- **Tokens:** ~700

Safe, pre-authorized edits applied 2026-05-29 (see [[knowledge/KNW-0026]] §2): - `AGENTS.md` keyboard entry un-iceboxed to match CLAUDE.md; repo-status column set to on-disk reality (Command_Vault/RAG_Vault exist sans repo; Local-Network-Hub has a repo). - `_system/vault_config.yaml` `not_in_system`...

### [[tasks/TSK-0003.md]]

- **Score:** 0.817 (recency=0.97, delta=1.00, links=0.63, importance=0.50)
- **Tokens:** ~811

> **REVIVED 2026-05-28** — un-iceboxed (see [[decisions/DEC-0004]]). The project is active at `Documents\android-ai-keyboard-harness\` (FlorisBoard fork, app "HermeticA-Z"), NOT the never-scaffolded `Documents\agentA-Z\` path. Still explicitly NOT part of the 4-vault system. Current state, palette a...

### [[decisions/DEC-0004.md]]

- **Score:** 0.792 (recency=0.97, delta=1.00, links=0.50, importance=0.50)
- **Tokens:** ~500

[[DEC-0003]] (2026-04-19) iceboxed the keyboard, sending it to a new non-vault folder `Documents\agentA-Z\` with its own repo, and moved [[tasks/TSK-0003]] to `cancelled`. That folder was never scaffolded.

### [[knowledge/KNW-0022.md]]

- **Score:** 0.770 (recency=0.98, delta=1.00, links=0.38, importance=0.50)
- **Tokens:** ~900

> **2026-05-29 update (see [[knowledge/KNW-0026]]):** 3 of 4 hygiene items are DONE — > `llm-orchestrator`, `Claude_on_Claude`, and the literal-path ghost dir are no longer > nested in Claude_Vault. **Only `n8n-workflows` remains nested** (relocation to > Local-Network-Hub pending Mars's call in [[d...

### [[knowledge/KNW-0024.md]]

- **Score:** 0.767 (recency=0.97, delta=1.00, links=0.38, importance=0.50)
- **Tokens:** ~1500

> Ground truth for vault structure: **CLAUDE.md (4-vault)**, per [[decisions/DEC-0003]]. This map aligns the injection keyboard to that authority and flags where active reality has drifted from the frozen docs. Moto is **noted, not touched** this pass.

### [[decisions/DEC-0005.md]]

- **Score:** 0.746 (recency=0.99, delta=1.00, links=0.25, importance=0.50)
- **Tokens:** ~600

Following the 2026-05-29 injection test suite ([[knowledge/KNW-0025]]), Mars set two provider keys (Gemini + Groq) and authorized moving the project forward with the recommended fixes. The suite had found the shipped `CteKeysActivity` launch doc-comment was wrong and that injection silently no-ops w...

### [[tasks/TSK-0001.md]]

- **Score:** 0.745 (recency=0.98, delta=1.00, links=0.25, importance=0.50)
- **Tokens:** ~539

> **2026-05-29 ([[decisions/DEC-0006]]):** the FM v1 → RAG ingestion follow-up is **closed** — > FM v1 is permanently excluded from the agent system (read-only legacy reference, never indexed). > This task remains a forward RAG_Vault scaffold/populate task with **purpose-built** content only; > RAG_...

### [[knowledge/KNW-0025-keyboard-vault-injection-tests.md]]

- **Score:** 0.721 (recency=0.99, delta=1.00, links=0.13, importance=0.50)
- **Tokens:** ~1700

> **Boundary note (per [[decisions/DEC-0004]] / [[knowledge/KNW-0024]]):** this is a > *boundary-pointer* test record. The keyboard's code lives at > `Documents\android-ai-keyboard-harness` (not a vault). This doc and the test > scripts describe how to verify the injection contract; they are not key...

### [[inbox/2026-05-30.md]]

- **Score:** 0.700 (recency=1.00, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~18

--- **13:03:40** — Vault opened. Session started.

### [[inbox/2026-05-17.md]]

- **Score:** 0.657 (recency=0.77, delta=1.00, links=0.13, importance=0.50)
- **Tokens:** ~18

--- **11:48:06** — Vault opened. Session started.

### [[inbox/2026-04-26.md]]

- **Score:** 0.250 (recency=0.42, delta=0.00, links=0.13, importance=0.50)
- **Tokens:** ~18

--- **21:29:58** — Vault opened. Session started.

### [[inbox/2026-04-20.md]]

- **Score:** 0.217 (recency=0.31, delta=0.00, links=0.13, importance=0.50)
- **Tokens:** ~18

--- **12:49:42** — Vault opened. Session started.

### [[inbox/2026-04-14.md]]

- **Score:** 0.184 (recency=0.20, delta=0.00, links=0.13, importance=0.50)
- **Tokens:** ~18

--- **01:29:29** — Vault opened. Session started.

## Open Tasks

- **[[tasks/TSK-0010.md|Daily Workflow Nerve — Automated Vault Briefing + Task Triage]]** — status: open, priority: normal
- **[[tasks/TSK-0008.md|Vault Health Sweep — Fix Drift, Schema, Stale Refs]]** — status: open, priority: normal
- **[[tasks/TSK-0006.md|Local LLM Bones — Ollama Service + Model Selection + Always-On Fallback]]** — status: open, priority: high
- **[[tasks/TSK-0005.md|Obsidian Blood Flow — Vault REST API Pipeline for All Agents]]** — status: open, priority: high
- **[[tasks/TSK-0003.md|Injection Keyboard (HermeticA-Z) — Android AI keyboard orchestration system]]** — status: in_progress, priority: normal
- **[[tasks/TSK-0002.md|Configure Local REST API for external agent access]]** — status: open, priority: normal

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
