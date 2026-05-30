# Session Handoff — 2026-05-29 (context-rich warm-start for next session)

> Read this first next session. It is the single source of "where we are" across the three
> threads worked this session: **keyboard go-live**, **multi-vault alignment**, and
> **Vault_Skills vs current power-user standards**. Canonical records are linked; this is the map.

## TL;DR state
- **Keyboard:** GO. Gemini + Groq keys live on the Moto; injection path fixed + verified. Only
  the on-device E2E smoke test remains. ([[decisions/DEC-0005]], [[knowledge/KNW-0025-keyboard-vault-injection-tests]])
- **Multi-vault:** reframed 4-vault → tiered **N-vault** model; all 6 structural questions ratified
  and executed. ([[decisions/DEC-0006]], [[knowledge/KNW-0026]])
- **Vault_Skills:** audited vs 2026 standards; Phase A (versioning/hygiene) + Phase B (HermeticA-Z
  rebrand) DONE. Phases C/D/E pending. ([[knowledge/KNW-0027]])

---

## 1. Vault logic & design — current truth
CLAUDE.md now describes a **Tiered N-Vault Architecture** (was "4-vault"), ratified in DEC-0006:
- **Core operational:** Claude_Vault (this; AI ops layer — decisions/knowledge/sessions/tasks).
- **Supporting:** Command_Vault (monitoring/control plane — repo `Gsunny45/Command_Vault`, init this session),
  Local-Network-Hub (orchestration, owns `n8n-workflows` — repo exists), RAG_Vault (retrieval —
  repo `Gsunny45/RAG_Vault`, init this session).
- **Hermes/methodology/delivery:** Hermes_Vault, Hermes_Phone_Vault, Vault_Skills, Hermes_Drop_vault.
- **Boundary project (NOT a vault):** android-ai-keyboard-harness — holds the canonical
  Hermetic_A-Z_Vault visual authority.

Separation-of-concerns from DEC-0003 still governs: operational ≠ monitoring ≠ orchestration ≠
retrieval. The keyboard's code never enters Claude_Vault; only knowledge/handoff pointers do.

**Schema/IDs unchanged:** DEC-NNNN, KNW-NNNN, TSK-NNNN, SES-YYYY-MM-DD-NNN. Latest: DEC-0006,
KNW-0027, TSK-0010.

## 2. Multi-vault ↔ keyboard alignment (your main concern)
The keyboard (HermeticA-Z, FlorisBoard fork on the Moto) connects to the vault system via **two
injection senses** (do not conflate — [[knowledge/KNW-0024]]):
- **Key/config injection:** host PowerShell → ADB intent → `CteKeysActivity` → encrypted KeyVault.
  Verified working contract (the shipped doc-comment was WRONG): explicit component **+** action+data
  `-a android.intent.action.VIEW -d "ui://hermetica-z/cte/keys"`. Inject logic now also in
  `onNewIntent` (singleTask re-inject gap fixed this session, DEC-0005).
- **Prompt/context injection:** on-device `files/cte/configs/{triggers,routing,skills}.json` rendered
  at system-prompt level. Routing default = `gemini_1`, `standaloneMode: true` (skips dead local
  llama-server), cheap ladder `gemini_1 → gemini_2 → groq`, anthropic dormant (budget-safe).

**Visual authority alignment (resolved this session):** canonical = `android-ai-keyboard-harness\
Hermetic_A-Z_Vault`. The `Pictures\Hermetic_A-Z_Vault` path in older docs/site-instructions does
NOT exist and is retired. Palette = Violet `#A855F7` / Sky-Blue `#38BDF8` / Amber `#F59E0B` on
Void Black `#080808`. **Legacy CyberDeck cyan/magenta = forbidden/deprecated.** Vault_Skills'
design system was rebranded CyberDeckA-Z → HermeticA-Z this session to stop it shipping the
forbidden palette into every new vault it builds.

## 3. Power-user standards status (your main concern)
Benchmarked 5/29/26 ([[knowledge/KNW-0027]]):
- **Agent Skills Open Standard** (Anthropic, 2025-12-18): SKILL.md + YAML frontmatter + progressive
  disclosure (discovery ~100 tok / activation <5k tok / execution). Read by 32+ tools. — Vault_Skills
  already conforms (real SKILL.md skills in `.agents/` and `.claude/`).
- **AGENTS.md** (Linux Foundation, ~60k repos, schema-free): Vault_Skills has a strong one ("Rule Zero").
- **Obsidian Bases** (first-party Dataview replacement, 2026 default): Vault_Skills still
  Dataview-default (123 files) — **Phase C gap, not yet done.**

## 4. What's DONE vs OPEN

### Done this session (committed + pushed)
- Keyboard: 3 CteKeysActivity bugs fixed, rebuilt + installed, re-inject verified.
- Claude_Vault: AGENTS.md/vault_config un-iceboxed keyboard; CLAUDE.md → N-vault; KNW-0022/0024/0025/0026/0027,
  DEC-0005/0006; TSK-0004 closed (superseded), TSK-0001 FM-v1 follow-up closed. Pushed.
- Command_Vault + RAG_Vault: repos created + pushed.
- n8n-workflows: de-duplicated (canonical already in Local-Network-Hub; vault copy archived).
- Vault_Skills: Phase A (committed 360 files, hygiene, README) + Phase B (HermeticA-Z rebrand). Pushed.

### Open / next-session pickup (priority order)
1. **Vault_Skills Phase C — Bases-first methodology** (largest remaining standards gap): make
   Obsidian Bases the default in `02 - Skills/Dashboards.md` + `Dataview Dashboard Patterns.md`;
   add a `Bases Patterns` skill note; Dataview → documented fallback (inline fields, calendar/list).
2. **Vault_Skills Phase D** — reframe AGENTS.md/skills from "Codex" (8 refs) to tool-neutral Agent
   Skills Open Standard; progressive-disclosure split of any `02 - Skills/*` note >~5k tokens.
3. **Vault_Skills Phase E (optional)** — distribution manifest (`marketplace.json` / awesome-skills
   style) so the obsidian-* skills are installable cross-tool.
4. **Keyboard E2E smoke test** (DEC-0005 open): type a trigger in a focused field on the Moto,
   confirm a Gemini/Groq response is inserted. Only thing not yet exercised end-to-end.
5. **Recompile `_system/_briefing.md`** — 12 days stale (last 2026-05-17), missing DEC-0005/0006 and
   KNW-0025/0026/0027. Obsidian-side: `Ctrl+Shift+B`. (Agent can't trigger Obsidian commands.)
6. **Local-Network-Hub has 43 uncommitted changes** (incl. the n8n relocation). Not committed this
   session — it's a separate repo; next session should review + commit there with Mars's intent.
7. *Optional:* delete the reserved-name `nul` ghost file in Claude_Vault root (breaks `git add -A`;
   needs `del \\?\C:\Users\MarsBase\Documents\Claude_Vault\nul` from cmd). Worked around with `-- ':!nul'`.

## 5. Gotchas to carry forward
- `git add -A` in Claude_Vault fails on the `nul` file → use `git add -A -- ':!nul'`.
- Long ops via Windows-MCP exceed the 45s cap → use `Start-Process` detached + poll the log.
- ADB inject needs component+action+data together, and force-stop (or rely on the new onNewIntent).
- Vault_Skills `versions/v1-baseline/` is intentional history — do NOT rewrite it.
- Files written UTF-8 then read by PowerShell 5.x: use ASCII for `.ps1` to avoid em-dash breakage.

## 6. Artifacts location
- Vault records: `Claude_Vault/{decisions,knowledge}/` (canonical, schema-compliant).
- Readable scope + scripts: `Claude_Vault/exports/` and `Desktop/Hermes_Drop_vault/`
  (ALIGNMENT_SCOPE_2026-05-29.md, KNW-0026, KNW-0027, DEC-0006, test_key_injection.ps1/.py).
