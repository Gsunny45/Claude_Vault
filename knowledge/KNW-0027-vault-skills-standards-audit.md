---
type: knowledge
id: KNW-0027
subject: "Vault_Skills audit vs current (5/29/26) power-user standards + gap-fill plan"
confidence: verified
last_verified: 2026-05-29
source: "Live inventory of Vault_Skills 2026-05-29 (Windows-MCP) + web/GitHub research on Agent Skills Open Standard, AGENTS.md, Obsidian Bases"
related:
  - "KNW-0026"
  - "KNW-0024"
  - "DEC-0006"
tags: [vault-skills, standards, audit, agent-skills, skill-md, agents-md, obsidian-bases, gap-plan]
tokens: 2400
---

# Vault_Skills — Standards Audit & Gap-Fill Plan (2026-05-29)

Benchmarks `C:\Users\MarsBase\Documents\Vault_Skills` (repo `Gsunny45/Vault_Skills`) against
current power-user standards. **Audit + plan only — no content changes this round** (per Mars).

## 1. The current standards (researched 5/29/26)

- **Agent Skills Open Standard** — released by Anthropic 2025-12-18; `SKILL.md` = folder + YAML
  frontmatter (`name`, `description` min) + Markdown. **Progressive disclosure**: discovery
  (~100 tok name/desc at startup) → activation (full body <5k tok) → execution (bundled
  scripts/refs loaded on demand). Now read by 32+ tools (Claude Code, Codex, Cursor, Gemini
  CLI, Junie, Kiro, Goose). Authoring rules: start ≤10 lines; split overflow into referenced
  files; keep mutually-exclusive paths separate; use trusted sources only.
- **AGENTS.md** — Linux Foundation (Agentic AI Foundation) stewarded, schema-free Markdown at
  repo root; build/test/style/"do-not-touch" for agents. ~60k repos; read by Codex, Cursor,
  Copilot, Gemini CLI, Aider, Windsurf, Zed, +20 more.
- **Obsidian Bases** — first-party "official Dataview", ships in core; faster than
  Dataview/Datacore, no query language, YAML-property driven. 2026 default for tables/cards;
  Dataview retained only for inline fields, calendar/list views.
- **Skill distribution** — marketplaces + `awesome-agent-skills` style indexes
  (anthropics/skills, VoltAgent, antigravity) are the norm; skills are public, auditable repos.

## 2. Where Vault_Skills already meets standard (keep)
- ✅ Real `SKILL.md` skills with valid `name`/`description` frontmatter in **both** `.agents/skills/`
  and `.claude/skills/` (obsidian-bases, obsidian-cli, obsidian-markdown). Dual-dir = good
  cross-tool coverage.
- ✅ `AGENTS.md` exists at root with a "Rule Zero / read-before-build" enforcement layer and a
  7-layer build protocol — strong, opinionated, matches the AGENTS.md intent.
- ✅ Bases awareness has begun (obsidian-bases skill + 3 doc refs).
- ✅ Rich data bank: 42-plugin catalog, templates, snippets, 8 sub-vault design templates,
  a deep prompt-engineering knowledge set (`Keyboard_AI_Vault/knowledge` + `/prompts`).

## 3. Gaps vs standard (ranked)

### LARGE
1. **Stale + dirty git.** Last commit 2026-05-04 (25 days); **64 uncommitted changes**. The
   methodology repo isn't versioning its own evolution — violates the dev-hygiene baseline and
   risks loss. *(Largest gap.)*
2. **Legacy design system mismatch.** The shipped design system is **`CyberdeckA-Z`** with 13
   files referencing `cyberpunk`/cyberdeck — the palette your own standards mark **deprecated/
   forbidden** (cyan/magenta). Current authority is **HermeticA-Z** (Violet #A855F7 / Sky #38BDF8 /
   Amber #F59E0B on Void Black #080808), canonical under the keyboard harness ([[knowledge/KNW-0026]]).
   A build skill that hands out the forbidden palette will reproduce drift in every new vault.
3. **Dataview-default vs Bases-default.** 123 files lean on Dataview as the primary query layer;
   2026 default is **Bases**. Methodology should make Bases the default and Dataview the
   inline/calendar fallback, or new vaults ship on the old pattern.

### MEDIUM
4. **"Codex"-era framing (8 refs).** AGENTS.md/skills speak of "Codex sessions" and `.Codex/skills/`.
   The 2026 consolidation is the **Agent Skills Open Standard + AGENTS.md** (tool-neutral). Reframe
   to the open standard so the repo isn't pinned to one agent.
5. **No progressive-disclosure discipline on long notes.** Several `02 - Skills/*` and design notes
   are long single files. Standard says keep SKILL.md bodies <5k tokens and push detail into
   referenced files loaded on demand. Audit + split the biggest.
6. **No distribution/manifest.** No marketplace metadata or skill index in the
   `awesome-agent-skills` / `.claude-plugin/marketplace.json` style. The skills aren't installable
   by others or discoverable cross-tool beyond local dirs.

### SMALL (hygiene)
7. **Loose artifacts:** `Vault-Masters.zip ×3`, `README (1).md` (dup), stray `index.html` /
   `graph-views.html` at root. Clutter; some likely belong in `07 - Archive/` or `.gitignore`.
8. **README freshness:** root README vs `README (1).md` — pick one, date it.

## EXECUTION STATUS (2026-05-29)

**Phase A — DONE.** Committed 25 days of pending work (360 files, `678fb49..ddae839`); resumed
versioning. Archived loose artifacts (`Vault-Masters.zip ×3`, `README (1).md`, stray html) to
`07 - Archive/_loose_artifacts_2026-05-29/`; added `*.zip` to `.gitignore`; created a proper
human-facing root `README.md` (AGENTS.md stays agent-facing).

**Phase B — DONE.** Rebranded CyberDeck→HermeticA-Z (`ddae839..303013b`): SKILL.md frontmatter
(`cyberdecka-z-design`→`hermetica-z-design`, palette in description, cyberpunk marked
deprecated), CSS header (AgentA-Z→HermeticA-Z; canonical `--hm-*` palette already present), the
design-system README, 7 live `ui_kits/keyboard/*` files, and 4 design notes (Keyboard_AI_Vault,
Hermes-Phone-Vault). Folder renamed `CyberdeckA-Z Design System`→`HermeticA-Z Design System` via
`git mv`. Live cyberpunk preview marked DEPRECATED (not deleted). **`versions/v1-baseline/` left
untouched** — intentional historical snapshot. Zero residual product-name refs in live files.

**Remaining (Phases C/D/E — not yet done):** Bases-first methodology (gap #3), Codex→open-standard
reframe (gap #4), progressive-disclosure split (gap #5), distribution manifest (gap #6).

## 4. Gap-fill plan (sequenced; effort tags)

**Phase A — Hygiene & versioning (S, do first):**
A1. Commit the 64 pending changes with a clear message; resume regular commits. *(Watch for the
    same reserved-name `nul` gotcha seen in Claude_Vault — use `git add -A -- ':!nul'` if it recurs.)*
A2. Move `Vault-Masters*.zip` + `README (1).md` to `07 - Archive/` or add to `.gitignore`; pick
    one canonical README.

**Phase B — Palette/brand realignment (M, high value):**
B1. Rename/supersede `CyberdeckA-Z Design System` → `HermeticA-Z Design System`; swap the
    palette to Violet/Sky/Amber on Void Black; mark cyberpunk variants legacy/forbidden.
B2. Point the design-system SKILL.md at the canonical harness `Hermetic_A-Z_Vault` authority.

**Phase C — Bases-first methodology (M):**
C1. Update `02 - Skills/Dashboards.md` + `Dataview Dashboard Patterns.md` to make **Bases** the
    default, Dataview the documented fallback (inline fields, calendar/list).
C2. Add a short `Bases Patterns` skill note mirroring the Dataview one.

**Phase D — Standard-conformance (M):**
D1. Reframe AGENTS.md + skills from "Codex" to the tool-neutral Agent Skills Open Standard
    + AGENTS.md language (keep Rule Zero — it's good).
D2. Progressive-disclosure pass: find `02 - Skills/*` notes >~5k tokens, split detail into
    referenced files.

**Phase E — Distribution (M/L, optional):**
E1. Add a skill index / `marketplace.json`-style manifest so the obsidian-* skills are
    installable and discoverable cross-tool (anthropics/skills pattern).
E2. Consider publishing the design-system + vault-build skills to a personal marketplace.

## 5. Reference benchmarks (GitHub)
- `anthropics/skills` — canonical Agent Skills examples + structure.
- `VoltAgent/awesome-agent-skills`, `sickn33/antigravity-awesome-skills` — large curated indexes
  (install patterns, manifests).
- `agentsmd/agents.md` — AGENTS.md spec/examples.

## 6. Recommendation
Do **Phase A now** (it's the largest gap and lowest effort — an unversioned methodology repo is
the real risk). Then **B** (brand drift is actively harmful — the skill ships the forbidden
palette). C/D/E are quality upgrades that can follow. None require rebuilding the repo; it's
fundamentally sound and already standard-aware.
