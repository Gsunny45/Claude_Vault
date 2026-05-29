# Documents Directory Audit
**Date:** 2026-05-03  
**Scope:** Cross-analysis of all vaults against GitHub repository best-practice standards  
**Auditor:** Claude (Sonnet 4.6)

---

## Repo & Documentation Coverage Matrix

| Vault | .git | README | CLAUDE.md | AGENTS.md | LICENSE | CONTRIBUTING | .github/ | CHANGELOG |
|-------|------|--------|-----------|-----------|---------|--------------|----------|-----------|
| Claude_Vault | ✅ | ✅ | ✅ 114L | ❌ | ❌ | ❌ | ❌ | ❌ |
| Local-Network-Hub | ✅ | ✅ | ✅ 47L | ✅ | ❌ | ❌ | ❌ | ❌ |
| Claude_on_Claude | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Command_Vault | ❌ | ✅ | ✅ 54L | ❌ | ❌ | ❌ | ❌ | ❌ |
| RAG_Vault | ❌ | ❌ | ✅ 107L | ❌ | ❌ | ❌ | ❌ | ❌ |
| Engineering-Knowledge-Graph | ❌ | ✅ | ✅ 74L | ❌ | ❌ | ❌ | ❌ | ❌ |
| Gemini_Vault | ❌ | ❌ | ✅ 73L | ❌ | ❌ | ❌ | ❌ | ❌ |
| Base Note20 Ultra | ❌ | ✅ | ✅ 60L | ❌ | ❌ | ❌ | ❌ | ❌ |
| llm-orchestrator | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Score: 3/9 have git | 1/9 have AGENTS.md | 1/9 have LICENSE | 0/9 have .github/**

---

## CLAUDE.md Quality Assessment

All existing CLAUDE.md files pass the 2026 best-practice line limit (target: under 300L, hard cap: never exceed 500L). Quality varies by vault purpose.

| Vault | Lines | Identity Clear | Schema Defined | Rules Present | Session Protocol | Commands Listed | Score |
|-------|-------|---------------|----------------|---------------|-----------------|-----------------|-------|
| Claude_Vault | 114 | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5** |
| RAG_Vault | 107 | ✅ | ✅ | ✅ | ✅ | ❌ | **4/5** |
| Engineering-KG | 74 | ✅ | ✅ | ✅ | ✅ | ❌ | **4/5** |
| Gemini_Vault | 73 | ✅ | ✅ | ✅ | ✅ | ❌ | **4/5** |
| Base Note20 Ultra | 60 | ✅ | ❌ | ✅ | ❌ | ❌ | **2/5** |
| Command_Vault | 54 | ✅ | ❌ | ✅ | ❌ | ❌ | **2/5** |
| Local-Network-Hub | 47 | ✅ | ✅ | ✅ | ✅ | ❌ | **4/5** |
| Claude_on_Claude | N/A | — | — | — | — | — | **0/5 — MISSING** |
| llm-orchestrator | N/A | — | — | — | — | — | **0/5 — MISSING** |

---

## Critical Gaps by Category

### 1. Missing Git Initialization (6 vaults)
Command_Vault, RAG_Vault, Engineering-Knowledge-Graph, Gemini_Vault, Base Note20 Ultra, llm-orchestrator have no `.git`. Per Claude_Vault's own CLAUDE.md, Command_Vault and RAG_Vault need their own repos. None have been created.

**Fix:** `git init` + create GitHub repos for Command_Vault and RAG_Vault at minimum.

---

### 2. AGENTS.md — Emerging 2026 Standard (1/9 present)
As of December 2025, AGENTS.md was donated to the Agentic AI Foundation (Linux Foundation). It is now the cross-tool standard for AI agent context files — readable by Claude Code, Cursor, Copilot, Gemini CLI, and others. Only **Local-Network-Hub** has one.

Your CLAUDE.md files are excellent but are Anthropic-specific. AGENTS.md provides the same context to every agent tool. For a multi-AI architecture like yours (Claude + Gemini + Grok + local models), this is a significant gap.

**Fix:** Add AGENTS.md to every vault that has an AI operational role. Content can be a condensed version of the existing CLAUDE.md — strip Anthropic-specific syntax, keep role/rules/schema/session protocol.

Priority order: Claude_Vault → RAG_Vault → Gemini_Vault → Engineering-KG → Local-Network-Hub (already has it)

---

### 3. LICENSE Missing in All Active Repos (1/9 present)
`Claude_on_Claude` has a license. `Claude_Vault` (public GitHub repo: `github.com/Gsunny45/Claude_Vault`) has none. Publishing a repo without a license means no one can legally use, modify, or contribute to it — and you have no legal protection either.

**Fix:** Add `LICENSE` to Claude_Vault and any repo you intend to keep public. MIT is the lowest-friction choice. Apache 2.0 if you want patent protection.

---

### 4. No .github/ Directory Anywhere (0/9)
None of your repos have `.github/`. This means no CI/CD, no issue templates, no PR templates, no Dependabot, no Actions workflows. For the repos that are actively developed (Claude_Vault, Local-Network-Hub, Claude_on_Claude), this is a meaningful gap.

**Minimum viable .github/ setup for Claude_Vault:**
```
.github/
  ISSUE_TEMPLATE/
    bug_report.md
    feature_request.md
  pull_request_template.md
  workflows/
    lint.yml        # markdown lint on push
```

---

### 5. Missing README.md (2 vaults)
- **RAG_Vault** — no README despite being described as "the masterpiece vault"
- **Gemini_Vault** — no README
- **llm-orchestrator** — no README, no anything

---

### 6. CHANGELOG.md Missing Everywhere (0/9)
No vault tracks version history. For Claude_Vault specifically — which has a `decisions/` folder with DEC-NNNN records and a last architecture correction date — a CHANGELOG is a natural fit. Decisions already contain the raw material; a CHANGELOG just surfaces them in chronological order for humans.

---

### 7. No CONTRIBUTING.md Anywhere (0/9)
Lower priority for personal vaults, but Claude_Vault is a public GitHub repo. Without CONTRIBUTING.md, there are no stated contribution guidelines. At minimum, a one-page CONTRIBUTING.md pointing contributors to the CLAUDE.md rules and frontmatter schema would close this gap.

---

### 8. Structural Issues (Known + New)

| Issue | Status | Location |
|-------|--------|----------|
| `Claude_on_Claude` nested inside `Claude_Vault` | Known — KNW-0022 | Claude_Vault/CLAUDE.md |
| `llm-orchestrator` nested inside `Claude_Vault` | Known — KNW-0022 | Claude_Vault/CLAUDE.md |
| `Claude_on_Claude` has no CLAUDE.md | **NEW — not previously flagged** | — |
| `llm-orchestrator` has no CLAUDE.md, README, or git | **NEW — not previously flagged** | — |
| WSL path bug in `vault_monitor.py` | Known | Claude_Vault/CLAUDE.md |
| `agentA-Z` listed as iceboxed in CLAUDE.md | Status mismatch — user is actively working on it | Claude_Vault/CLAUDE.md |

---

## Priority Action List

**High — do these first:**
1. Add `AGENTS.md` to Claude_Vault, RAG_Vault, Gemini_Vault (multi-AI compatibility)
2. Add `LICENSE` to Claude_Vault (it's public on GitHub — no license = no protection)
3. Create `CLAUDE.md` for `Claude_on_Claude` and `llm-orchestrator`
4. Update `agentA-Z` status in Claude_Vault/CLAUDE.md from "iceboxed" to active

**Medium — next pass:**
5. `git init` + create GitHub repos for Command_Vault and RAG_Vault
6. Add `README.md` to RAG_Vault and Gemini_Vault
7. Add `.github/` with issue templates and a lint workflow to Claude_Vault

**Low — when time allows:**
8. Add `CHANGELOG.md` to Claude_Vault (pull from decisions/ records)
9. Add `CONTRIBUTING.md` to Claude_Vault (point to CLAUDE.md rules + frontmatter schema)
10. Extract nested repos (`Claude_on_Claude`, `llm-orchestrator`) per KNW-0022

---

## What's Working Well

- **CLAUDE.md quality is above average.** All 7 existing files are under 200 lines, have clear identity statements, and define rules for AI agents. Claude_Vault's is the best-structured CLAUDE.md in the audit set.
- **Frontmatter schemas are consistent** across Claude_Vault, Gemini_Vault, and Engineering-KG — shared ID conventions (DEC/KNW/TSK/SES) reduce cross-vault friction.
- **RAG_Vault's multi-AI delegation model** is well-designed. Assigning each AI a specific role and storing prompts per-AI in `00_CORE/prompts/` is a best practice not commonly documented.
- **Session protocols exist** in 4 of 7 CLAUDE.md files — most repos don't have any.
- **Local-Network-Hub is the most GitHub-complete vault** — git, README, CLAUDE.md, and AGENTS.md. Use it as the template for the others.

---

*Sources: GitHub Docs, Anthropic Claude Code Best Practices, Augment Code AGENTS.md Guide, standard-readme spec*
