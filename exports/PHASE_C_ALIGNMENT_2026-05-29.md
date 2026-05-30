# Phase C — Android HermeticA-Z / Obsidian Multi-Vault Ecosystem Alignment & Plan

> Compiled 2026-05-29 (same-day continuation of `_system/_SESSION_HANDOFF_2026-05-29.md`).
> Mode: **align + plan first** — this session verified live state and sequenced the work; it did
> **not** mutate Vault_Skills or other vaults. Canonical records: [[knowledge/KNW-0026]],
> [[knowledge/KNW-0027]], [[decisions/DEC-0006]], [[decisions/DEC-0005]].

---

## 0. What "Phase C" means (disambiguation)

The handoff defines **Phase C** precisely: **Vault_Skills — Bases-first methodology** (KNW-0027
gap #3, the largest remaining standards gap). The session title also frames the broader
*Android HermeticA-Z / multi-vault* thread, so this plan reconciles **both**: the named Phase C
task *and* the wider 7-item pickup list, against state verified on disk and on-device today.

---

## 1. Verified ground truth (probed live 2026-05-29, this session)

| Area | Probe result | Delta vs handoff |
|------|--------------|------------------|
| **Moto device** | `ZY22G7NFLK` connected **and** WiFi ADB `192.168.1.105:5555` live | Phone now connected both USB + WiFi |
| **Keyboard install** | `dev.patrickgold.florisboard.vault.debug` installed | Confirms DEC-0005 build present |
| **Active IME** | Default input method **= the HermeticA-Z keyboard** (`…vault.debug/…FlorisImeService`) | **New: keyboard is the selected IME** → E2E fully unblocked |
| **CTE config read** | `run-as` blocked (NO_RUNAS) under bare pkg name; private storage not externally listed | Cosmetic only — config verified intact last session (KNW-0026) |
| **Vault_Skills git** | Clean tree (0 uncommitted); HEAD `303013b` = Phase A/B commit | Confirms A/B done + pushed; Phase C is genuinely next |
| **Local-Network-Hub** | **43 uncommitted changes** | Unchanged — still open (pickup #6) |
| **`nul` ghost file** | `Test-Path … \nul` → **False** | **Resolved** — pickup #7 no longer needed |
| **Briefing** | Still dated 2026-05-17 | Unchanged — stale (pickup #5), Obsidian-side recompile |

**Headline:** the keyboard is installed *and* set as the active keyboard on the Moto, with USB +
WiFi ADB both live. The DEC-0005 E2E smoke test has **zero remaining blockers** — it just needs a
trigger typed into a focused field with injection confirmed.

---

## 2. Pickup list — reconciled status

| # | Item | Status now | Notes |
|---|------|-----------|-------|
| 1 | **Vault_Skills Phase C — Bases-first** | **OPEN — primary** | Repo clean & ready; see §3 |
| 2 | Vault_Skills Phase D — Codex→open-standard + disclosure split | OPEN | Follows C |
| 3 | Vault_Skills Phase E — distribution manifest | OPEN (optional) | Quality upgrade |
| 4 | **Keyboard E2E smoke test** (DEC-0005) | **OPEN — now unblocked** | Device + IME confirmed ready |
| 5 | Recompile `_system/_briefing.md` | OPEN | Obsidian-side (`Ctrl+Shift+B`); agent can't trigger |
| 6 | Local-Network-Hub — 43 uncommitted | OPEN | Separate repo; commit with Mars's intent |
| 7 | `nul` ghost cleanup | **DONE** | Verified gone today |

---

## 3. Phase C execution spec (Vault_Skills — Bases-first methodology)

Target repo: `C:\Users\MarsBase\Documents\Vault_Skills` (`Gsunny45/Vault_Skills`). Effort: **M**.
Goal: make **Obsidian Bases** the default query/dashboard layer in the build methodology, and
demote Dataview to a documented fallback (inline fields, calendar/list) — so newly-built vaults
ship on the 2026 default instead of Dataview-first.

**C1 — Dashboards default → Bases.**
Edit `02 - Skills/Dashboards.md` and `02 - Skills/Dataview Dashboard Patterns.md`:
- Lead with Bases (YAML-property-driven, no query language) as the primary table/card pattern.
- Reframe Dataview sections as "fallback / when to still use" (inline fields, calendar, list views).
- Cross-link to the existing `obsidian-bases` SKILL.md so the skill and the methodology agree.

**C2 — Add a `Bases Patterns` skill note.**
Mirror the existing Dataview pattern note: a short reference of common Base definitions (filtered
table, card view, grouped-by-status board) using the vault's frontmatter schema.

**C3 — Consistency sweep.**
Confirm the `obsidian-bases` SKILL.md in both `.agents/skills/` and `.claude/skills/` points at the
new default; ensure no new contradiction with the 123 Dataview-leaning files (those stay valid as
fallback, not rewritten).

**Verification:** open one generated dashboard pattern in Obsidian to confirm the Base renders;
`git add -A -- ':!nul'` + commit with a KNW-0027-referencing message; push.

---

## 4. Sequenced plan for the execution session

Execution path: **Windows-MCP PowerShell on the real vaults** (Vault_Skills, harness, LNH are
outside the mounted Claude_Vault). Use `Start-Process` + log-poll for any op >45s; ASCII for `.ps1`.

1. **Keyboard E2E smoke test first** (fastest win, fully unblocked). Focus a text field on the
   Moto via ADB, type/inject a configured trigger, confirm a Gemini/Groq completion is inserted.
   Close DEC-0005. Capture the transcript to `_system/logs/` (training-data: do not prune).
2. **Vault_Skills Phase C** (§3) — C1 → C2 → C3 → verify → commit/push.
3. **Vault_Skills Phase D** — reframe the 8 "Codex" refs to the tool-neutral Agent Skills Open
   Standard + AGENTS.md language (keep Rule Zero); split any `02 - Skills/*` note >~5k tokens via
   progressive disclosure.
4. **Local-Network-Hub** — review the 43 uncommitted changes *with Mars's intent* (incl. the n8n
   relocation) and commit in that repo. **Do not** auto-commit without confirmation.
5. **Briefing recompile** — Obsidian-side `Ctrl+Shift+B` (then `Ctrl+Shift+D` drift). Agent cannot
   trigger Obsidian commands; flag for Mars to run, or note it stays stale.
6. **Phase E (optional)** — `marketplace.json` / awesome-skills-style manifest for the obsidian-* skills.

---

## 5. Decisions / inputs needed from Mars

- **Commit autonomy for Local-Network-Hub (#6):** review-and-report, or commit on your behalf once
  reviewed? (Default: review + report, no auto-commit.)
- **E2E trigger choice:** which configured trigger word + target app to use for the smoke test
  (default routing is `gemini_1`, ladder → `gemini_2` → `groq`).
- **Phase E scope:** build the distribution manifest this cycle, or defer as optional.

---

## 6. Guardrails carried forward (from handoff §5)

- `git add -A` in vaults fails on reserved-name `nul` → use `git add -A -- ':!nul'`.
- Multiple ADB devices attached (Moto USB + WiFi) → **always target `-s ZY22G7NFLK`**, or
  `adb shell` errors "more than one device".
- Long Windows-MCP ops exceed 45s → `Start-Process` detached + poll the log.
- `versions/v1-baseline/` in Vault_Skills is intentional history — do **not** rewrite.
- Vault boundaries (DEC-0003/0006): keyboard code never enters Claude_Vault; Bases methodology
  lives in Vault_Skills, not here.
