---
type: knowledge
id: KNW-0026
subject: "Vault ecosystem alignment path plan (doc-vs-reality reconciliation)"
confidence: verified
last_verified: 2026-05-29
source: "Live disk + Moto discovery 2026-05-29 (Windows-MCP), Explore subagent gap analysis, KNW-0022/0024/0025, DEC-0003/0004/0005"
related:
  - "KNW-0022"
  - "KNW-0024"
  - "KNW-0025"
  - "DEC-0006"
tags: [alignment, vault-ecosystem, gap-analysis, reconciliation, path-plan]
tokens: 2200
---

# Vault Ecosystem Alignment Path Plan

Reconciles the Claude_Vault ground-truth docs (CLAUDE.md "4-vault" model) with what
actually exists on the Windows host and the Moto as of 2026-05-29. Safe, pre-authorized
edits (DEC-0004/0005) are **already applied**; structural choices are routed to
[[decisions/DEC-0006]] for Mars's ratification.

## 1. Ground truth (verified on disk 2026-05-29)

### Host vaults / folders
| Entity | Exists | Git repo | Docs said | Gap |
|--------|--------|----------|-----------|-----|
| Claude_Vault | yes | `Gsunny45/Claude_Vault` | yes, has repo | none |
| Command_Vault | **yes** | **none** | "TBD — own repo required" | exists but docs imply not-yet-built |
| Local-Network-Hub | **yes** | **`Gsunny45/Local-Network-Hub`** | "TBD — own repo required" | exists **with repo** |
| RAG_Vault | **yes** | **none** | "TBD — own repo required" | exists but no repo |
| android-ai-keyboard-harness | yes | `Gsunny45/android-ai-keyboard-harness` | "active project" (CLAUDE.md ok) | AGENTS.md/config were stale (fixed) |
| Hermes_Vault | yes | `Gsunny45/Hermes_Vault` | (site-instructions) | not in CLAUDE.md 4-vault model |
| Hermes_Phone_Vault | yes | none | (site-instructions) | not in CLAUDE.md model |
| Vault_Skills | yes | `Gsunny45/Vault_Skills` | (site-instructions) | not in CLAUDE.md model |
| Hermes_Drop_vault (Desktop) | yes | none | delivery target | not in CLAUDE.md model |
| **Hermetic_A-Z_Vault (Pictures)** | **NO** | — | site-instructions: "master visual authority" | **path does not exist** |
| Hermetic_A-Z_Vault (under harness) | yes | (in harness repo) | — | real location of brand/visual assets |
| agentA-Z (ghost) | NO | — | iceboxed target | never scaffolded (matches DEC-0004) |

### Nested-repo hygiene (KNW-0022 called these "pending")
- `llm-orchestrator` → **EXTRACTED** (no longer nested). Done.
- `Claude_on_Claude` → **EXTRACTED** (no longer nested). Done.
- literal-path ghost dir `Claude_Vault\C:\Users\...` → **GONE**. Done.
- `n8n-workflows` → **STILL NESTED** inside Claude_Vault. Only remaining hygiene item.

### Moto (ZY22G7NFLK)
- Obsidian installed (`md.obsidian`).
- Keyboard on-device config tree intact: `files/cte/{configs,docs,evals,plugins,profiles,scripts}`.
- KeyVault: Gemini + Groq keys live (DEC-0005). Provider endpoints reachable.
- No vault directories on `/sdcard` (the "vaults" are host-side Obsidian vaults; the
  Moto holds only the keyboard CTE config, not the Obsidian vaults).

## 2. Safe edits already applied (2026-05-29, per DEC-0004/0005)
- `AGENTS.md`: keyboard line rewritten from iceboxed-`agentA-Z` to active-harness (matches
  CLAUDE.md); repo-status column updated to on-disk reality for Command_Vault /
  Local-Network-Hub / RAG_Vault.
- `_system/vault_config.yaml`: `not_in_system` keyboard entry → active harness; scan_excludes
  comments annotated (llm-orchestrator / Claude_on_Claude marked EXTRACTED, n8n marked still-nested).

## 3. Structural decisions (→ DEC-0006, need Mars ratification)
1. **"4-vault" → N-vault ecosystem.** CLAUDE.md still frames a clean 4-vault model, but
   ~8 host vaults exist plus the keyboard. Recommend reframing CLAUDE.md to a tiered model:
   *core operational* (Claude_Vault), *supporting* (Command_Vault, Local-Network-Hub,
   RAG_Vault), *Hermes layer* (Hermes_Vault, Hermes_Phone_Vault), *build/methodology*
   (Vault_Skills), *delivery* (Hermes_Drop_vault), *boundary project* (keyboard harness).
2. **Repos for Command_Vault & RAG_Vault.** Both exist without git. Decide: init repos now,
   or leave as local-only working dirs. (Local-Network-Hub already has one.)
3. **Hermetic_A-Z visual authority location.** Site-instructions point to a Pictures path
   that does not exist; the real assets live under the harness. Decide canonical home and
   correct the pointer (handoff doc already corrected to the harness path as interim).
4. **n8n-workflows relocation.** Still nested; KNW-0022 says it belongs in Local-Network-Hub.
   Decide: move now or defer.
5. **TSK-0004 (n8n extraction) closure.** 39 days past its 2026-04-20 deadline, still
   `in_progress`, no log since 2026-04-11. Decide: close as superseded, or revive.
6. **FM v1 → RAG ingestion follow-up (TSK-0001).** Decide if any FM v1 material is ever
   ingested into RAG_Vault or it stays permanently excluded.

## 4. Path plan — sequenced phases
**Phase 0 — DONE (2026-05-29):** safe doc edits; keyboard go-live (DEC-0005); this plan + DEC-0006.

**Phase 1 — Ratify & reframe — ✅ DONE (2026-05-29):** all 6 DEC-0006 questions ratified;
CLAUDE.md reframed to tiered N-vault. (Briefing recompile still pending — Obsidian-side.)

**Phase 2 — Repo & hygiene — ✅ DONE (2026-05-29):** Command_Vault + RAG_Vault repos
created + pushed; `n8n-workflows` de-duplicated (canonical already in Local-Network-Hub,
vault copy archived); TSK-0004 closed superseded; TSK-0001 FM-v1 follow-up closed.
(Archiving the obsolete `docs-audit-2026-05-03.md` still optional.)

**Phase 3 — Visual authority & boundaries — ✅ mostly DONE (2026-05-29):** harness path set
canonical, pointers fixed (CLAUDE.md, handoff). Remaining: confirm keyboard↔Local-Network-Hub
orchestration leg (webhook/routing path KNW-0024 assigns to the hub).

**Phase 4 — Keyboard E2E (separate track, DEC-0005 open item):** on-device smoke test —
type a trigger in a focused field, confirm Gemini/Groq response inserted. **Still pending.**

## 5. Drift to clear (mechanical, deferrable)
- Recompile briefing (stale 2026-05-17).
- KNW-0022: downgrade/annotate — 3 of 4 hygiene items now done, only n8n remains.
- TSK-0004: stale `in_progress`, overdue.
- `inbox/docs-audit-2026-05-03.md`: obsolete (pre-DEC-0004), archive.
- `inbox/hermetic_facelift_handoff.md`: Pictures path corrected to harness path.
