# Vault Ecosystem Alignment — Full Scope (2026-05-29)

Consolidated record of the alignment pass: what was discovered, what was fixed, what
needs your ratification, and recommended next steps. Canonical schema-compliant copies
live at `knowledge/KNW-0026` (plan) and `decisions/DEC-0006` (reconciliation).

---

## A. What I did this session (gaps filled)

**Keyboard go-live track (prior turn, DEC-0005):** verified Gemini+Groq keys in the
encrypted KeyVault; fixed 3 `CteKeysActivity` bugs (stale doc-comment, singleTask
re-inject gap, untrimmed char-count log); rebuilt + installed on the Moto; verified the
re-inject fix live (`onNewIntent`).

**Alignment track (this turn):**
- Discovered real on-disk state of all host vaults + the Moto (Windows-MCP).
- Ran an Explore subagent for a doc-vs-reality gap analysis.
- Applied safe, pre-authorized edits (DEC-0004/0005):
  - `AGENTS.md` — keyboard un-iceboxed to match CLAUDE.md; repo-status column corrected.
  - `_system/vault_config.yaml` — keyboard `not_in_system` entry → active harness;
    scan_excludes annotated (extractions done vs n8n still nested).
  - `knowledge/KNW-0022` — confidence downgraded to `inferred`; 3-of-4 hygiene items
    marked done, n8n flagged as the only remainder.
  - `inbox/hermetic_facelift_handoff.md` — flagged the non-existent Pictures path.
- Wrote `knowledge/KNW-0026` (path plan) and `decisions/DEC-0006` (reconciliation).

## B. Ground truth vs docs (key gaps found)

| Item | Docs said | Reality (2026-05-29) |
|------|-----------|----------------------|
| Command_Vault | "TBD — repo required" | EXISTS, no repo |
| Local-Network-Hub | "TBD — repo required" | EXISTS, has repo |
| RAG_Vault | "TBD — repo required" | EXISTS, no repo |
| llm-orchestrator / Claude_on_Claude / ghost-dir | "extraction pending" | already EXTRACTED |
| n8n-workflows | "belongs in Local-Network-Hub" | still NESTED in Claude_Vault |
| Hermetic_A-Z (Pictures) | "master visual authority" | path does NOT exist (real one is under harness) |
| keyboard (AGENTS.md/config) | iceboxed at agentA-Z | active harness (CLAUDE.md was already right) |
| ~8 host vaults exist | "4-vault architecture" | model under-describes reality |

## C. The 6 structural decisions — ALL RATIFIED & EXECUTED (DEC-0006, 2026-05-29)

1. Architecture framing → **Tiered N-vault.** CLAUDE.md reframed. ✅
2. Repos for Command_Vault + RAG_Vault → **init both.** Created + pushed to GitHub (private). ✅
3. Visual authority → **harness path canonical.** Pointers fixed; Pictures path retired. ✅
4. n8n-workflows → **relocate now.** Canonical already in Local-Network-Hub; vault dup archived. ✅
5. TSK-0004 → **close as superseded.** ✅
6. FM v1 → RAG → **permanent exclusion.** TSK-0001 follow-up closed. ✅

## D. Remaining next steps

1. **Recompile the briefing** — `_system/_briefing.md` is 12 days stale (missing DEC-0005/0006).
   This is an Obsidian-side command (`Ctrl+Shift+B`) I can't trigger from here.
2. **Keyboard E2E smoke test** (DEC-0005 open item): type a trigger in a focused field,
   confirm a Gemini/Groq response is inserted. Only thing not yet exercised end-to-end.
3. *Optional:* archive `inbox/docs-audit-2026-05-03.md` (obsolete, pre-DEC-0004).
4. *Optional:* a scheduled daily health check that pings provider endpoints + flags vault
   drift, writing to Command_Vault (its intended control-plane role).

## E. Files in this scope
- `knowledge/KNW-0026-vault-alignment-path-plan.md` — the plan
- `decisions/DEC-0006.md` — reconciliation decision (proposed)
- `knowledge/KNW-0025-keyboard-vault-injection-tests.md` — keyboard test plan + results
- `decisions/DEC-0005.md` — keyboard go-live
- `exports/test_key_injection.ps1` / `.py` — injection test harness
- Edited: `AGENTS.md`, `_system/vault_config.yaml`, `knowledge/KNW-0022.md`, `inbox/hermetic_facelift_handoff.md`
