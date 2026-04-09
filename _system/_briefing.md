---
type: briefing
compiled: "2026-04-09T05:16:02Z"
token_budget: 8000
token_actual: 7965
scope: auto-compiled
notes_included:
  - "tasks/TSK-0003.md"
  - "knowledge/KNW-0009.md"
  - "inbox/2026-04-08.md"
  - "_templates/rag-question.md"
  - "knowledge/KNW-0013.md"
  - "tasks/TSK-0004.md"
  - "13 keyboard shortcuts.md"
  - "knowledge/KNW-0011.md"
  - "knowledge/KNW-0010.md"
  - "inbox/2026-04-06.md"
  - "sessions/SES-2026-04-06-001.md"
  - "Task_Board.md"
  - "decisions/DEC-0002.md"
  - "knowledge/KNW-0008.md"
  - "inbox/2026-04-05.md"
  - "inbox/2026-04-03.md"
  - "inbox/2026-04-04.md"
  - "knowledge/KNW-0005.md"
  - "tasks/TSK-0002.md"
  - "_templates/task.md"
notes_excluded_reason:
  - path: "inbox/Untitled.md"
    reason: "token budget exceeded (need 12829, remaining 4685)"
  - path: "knowledge/KNW-0003.md"
    reason: "token budget exceeded (need 600, remaining 298)"
  - path: "Dashboard.md"
    reason: "token budget exceeded (need 856, remaining 298)"
  - path: "CLAUDE.md"
    reason: "token budget exceeded (need 1057, remaining 298)"
  - path: "knowledge/KNW-0007.md"
    reason: "token budget exceeded (need 650, remaining 298)"
---

## Vault State

- **Total notes:** 43
- **Open tasks:** 4
- **Recent decisions:** 2

## Changed Since Last Compile

**(root)/**
- [[13 keyboard shortcuts.md]]

**_templates/**
- [[_templates/rag-question.md]]

**inbox/**
- [[inbox/2026-04-08.md]]
- [[inbox/Untitled.md]]

**knowledge/**
- [[knowledge/KNW-0013.md]]
- [[knowledge/KNW-0011.md]]
- [[knowledge/KNW-0010.md]]
- [[knowledge/KNW-0009.md]]

**tasks/**
- [[tasks/TSK-0004.md]]


## Key Context

### [[tasks/TSK-0003.md]]

- **Score:** 0.749 (recency=0.53, delta=0.96, links=1.00, importance=0.50)
- **Tokens:** ~581

Build an Android AI keyboard (agentA-Z) that fuses Typeless-style voice polish, CleverType-style contextual AI, Obsidian Templater-style trigger/template expansion, and local LLM inference (Qwen2.5-Coder-1.5B-Uncensored-DPO Q6_K) into a single orchestrator-first, JSON-driven IME. Two design paths: c...

### [[knowledge/KNW-0009.md]]

- **Score:** 0.730 (recency=0.65, delta=1.00, links=0.67, importance=0.50)
- **Tokens:** ~380

- **Distro:** kali-linux (WSL2) - **User:** biocyberswarwAI@DESKTOP-SH8JARJ - **Path:** /mnt/c/Users/MarsBase/my-agent - **WSL shortcut:** `kali` from PowerShell

### [[inbox/2026-04-08.md]]

- **Score:** 0.700 (recency=1.00, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~18

--- **22:16:00** — Vault opened. Session started.

### [[_templates/rag-question.md]]

- **Score:** 0.699 (recency=1.00, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~69

<% tp.file.cursor() %>

### [[knowledge/KNW-0013.md]]

- **Score:** 0.699 (recency=1.00, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~1500

Obsidian note → n8n reads it → Gemini answers using vault context → answer written back to vault. This is the first working integration that proves the full stack.

### [[tasks/TSK-0004.md]]

- **Score:** 0.690 (recency=0.97, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~767

> **DEADLINE: 2026-04-20** — n8n free trial expires. All workflows must be extracted to offline scripts.

### [[13 keyboard shortcuts.md]]

- **Score:** 0.690 (recency=0.97, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~50

Placeholder note created from template. Originally had duplicate ID KNW-0006 (conflict with Force Multiplication v1 entry). Reassigned to KNW-0012. Needs content or user decision to delete.

### [[knowledge/KNW-0011.md]]

- **Score:** 0.690 (recency=0.97, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~500

Live status of every connection point in the orchestration stack. Update this entry whenever a connection is confirmed, broken, or changed.

### [[knowledge/KNW-0010.md]]

- **Score:** 0.690 (recency=0.97, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~1200

Mars is building a **distributed multi-agent orchestration system** across multiple AI providers, local models, and automation layers. This is not a collection of tools — it is a unified stack where each node has a defined role.

### [[inbox/2026-04-06.md]]

- **Score:** 0.638 (recency=0.57, delta=1.00, links=0.33, importance=0.50)
- **Tokens:** ~18

--- **06:13:45** — Vault opened. Session started.

### [[sessions/SES-2026-04-06-001.md]]

- **Score:** 0.615 (recency=0.53, delta=0.96, links=0.33, importance=0.50)
- **Tokens:** ~469

First Cowork session. Processed TSK-0003 (agentA-Z Keyboard) from inbox research dump into proper vault entries. Created architecture knowledge (KNW-0008), repo inventory (KNW-0009), and FlorisBoard decision (DEC-0002). Updated Task Board. Next: GitHub repo creation and population.

### [[Task_Board.md]]

- **Score:** 0.615 (recency=0.53, delta=0.96, links=0.33, importance=0.50)
- **Tokens:** ~131

- [ ] [[tasks/TSK-0001|Index Force Multiplication v1 vault architecture]] - [ ] [[tasks/TSK-0002|Configure Local REST API for external agent access]]

### [[decisions/DEC-0002.md]]

- **Score:** 0.615 (recency=0.53, delta=0.96, links=0.33, importance=0.50)
- **Tokens:** ~350

Use FlorisBoard as the IME foundation for agentA-Z Keyboard. Fork and extend with: 1. AI orchestration engine (background service reading skills.json) 2. Trigger detection in the NLP/spell-checker layer 3. CoT/ToT reasoning injected into the candidate suggestion bar 4. Voice integration via whisper-...

### [[knowledge/KNW-0008.md]]

- **Score:** 0.615 (recency=0.53, delta=0.96, links=0.33, importance=0.50)
- **Tokens:** ~900

agentA-Z is an Android AI keyboard system with two design paths. Design 1 is cloud-hybrid (ships first), Design 2 is fully local (open-source future). Both share the same 5-layer architecture flowing top-to-bottom.

### [[inbox/2026-04-05.md]]

- **Score:** 0.614 (recency=0.53, delta=0.96, links=0.33, importance=0.50)
- **Tokens:** ~44

--- **22:44:36** — Vault opened. Session started.

### [[inbox/2026-04-03.md]]

- **Score:** 0.490 (recency=0.19, delta=0.66, links=0.67, importance=0.50)
- **Tokens:** ~44

--- **15:30:49** — Vault opened. Session started.

### [[inbox/2026-04-04.md]]

- **Score:** 0.473 (recency=0.28, delta=0.74, links=0.33, importance=0.50)
- **Tokens:** ~31

--- **01:18:26** — Vault opened. Session started.

### [[knowledge/KNW-0005.md]]

- **Score:** 0.467 (recency=0.03, delta=0.52, links=1.00, importance=0.50)
- **Tokens:** ~650

The drift-detector plugin continuously monitors vault integrity. "Drift" is any state where the vault's contents diverge from its intended structure or internal consistency. The plugin runs four independent scanners, each targeting a different failure mode.

### [[tasks/TSK-0002.md]]

- **Score:** 0.402 (recency=0.04, delta=0.53, links=0.67, importance=0.50)
- **Tokens:** ~187

Configure the obsidian-local-rest-api plugin with proper authentication and test that Claude Code can read/write vault notes over HTTP. This enables any Claude instance (Code, Desktop, API) to interact with the vault without filesystem access.

### [[_templates/task.md]]

- **Score:** 0.299 (recency=0.09, delta=0.57, links=0.00, importance=0.50)
- **Tokens:** ~76

<% tp.file.cursor(2) %>

## Open Tasks

- **[[tasks/TSK-0004.md|T-13 Days n8n Extraction and Hardening Protocol]]** — status: in_progress, priority: critical
- **[[tasks/TSK-0003.md|agentA-Z Keyboard — Android AI keyboard orchestration system]]** — status: in_progress, priority: normal
- **[[tasks/TSK-0002.md|Configure Local REST API for external agent access]]** — status: open, priority: normal
- **[[tasks/TSK-0001.md|Index Force Multiplication v1 vault architecture]]** — status: open, priority: normal

## Recent Decisions

- **[[decisions/DEC-0002.md|agentA-Z keyboard — FlorisBoard as IME base over AnySoftKeyboard and from-scratch]]** (2026-04-06): FlorisBoard is Kotlin-native, has an existing Addons Store + extension system, spell-checker hooks we can repurpose for AI injection, and JSON-based theme/layout config that maps directly to our skills.json approach. Active development community. Apache-2.0 license allows unrestricted forking.
- **[[decisions/DEC-0001.md|Vault structure — flat folders over nested hierarchy]]** (2026-04-02): Shallow folders (one level) with rich frontmatter. Deep nesting makes path construction fragile — I'd need to know the full tree to create or find a note. Flat-with-tags loses the ability to scope Dataview queries by folder. One level of semantic folders gives both: folder-scoped queries AND simple paths.

## Drift Warnings

Issues detected in `_system/_drift_report.md`:

- **Critical:** 3
- **High:** 3
- **Medium:** 3
- **Low:** 2
