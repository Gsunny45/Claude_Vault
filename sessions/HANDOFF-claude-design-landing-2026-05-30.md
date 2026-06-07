---
type: session
id: HANDOFF-DESIGN-LANDING-2026-05-30
date: 2026-05-30
agent: claude
status: handoff
title: Claude-design — push Hermetic OS landing page to a more aligned state
tokens: 1400
---

# Handoff → Claude Design: Hermetic OS Landing Page Alignment

**Hand this to Claude Design.** It is a *gap brief*, not a brand re-explanation —
the full brand brief already exists and should be read alongside this:

- **Brand brief (read first):** `C:\Users\MarsBase\Pictures\Hermetic_OS_Vault\_system\HANDOFF_CLAUDE_DESIGN.md`
- **Target file (edit this):** `C:\Users\MarsBase\Pictures\Hermetic_OS_Vault\Hermetic_OS_Landing.html`
  (V0.0.2, 1182 lines, 55 KB, standalone — nav · hero · #stack · #modes · #agents · #academy · footer)
- **Canonical design tokens (source of truth):** `C:\Users\MarsBase\Documents\android-ai-keyboard-harness\Hermetic_A-Z_Vault\.obsidian\snippets\hermetic-os.css`
- **Android token parity:** `...\app\src\main\java\dev\patrickgold\florisboard\ime\ai\theme\HermeticTokens.kt`

> **Path note:** the site-instruction path `C:\Users\MarsBase\Pictures\Hermetic_A-Z_Vault\Hermetic_OS_Landing.html`
> **does not exist.** The real Pictures vault is `Hermetic_OS_Vault`. Use the paths above.

## Audit result — the page is already largely aligned

A 2026-05-30 audit of the live HTML against the canonical tokens + brief found:

- ✅ **No legacy CyberDeck palette.** Zero `#00FFFF` / `#FF00FF` / cyberdeck hits.
- ✅ **Canonical palette dominant:** violet `#A855F7` (11×), sky `#38BDF8` (10×),
  amber `#F59E0B` (8×) on void `#080808`. Matches the 70/20/10 ratio.
- ✅ **Fonts are brief-sanctioned:** Inter (body), Space Grotesk (display),
  Orbitron (hero-only), JetBrains Mono (code). All four are in the brief's type table.
- ✅ **Off-palette swatches** (`#7C3AED`/`#22D3EE`/`#F472B6`/`#FACC15`/`#10B981`/`#F97316`)
  are **intentional** — they live inside the JS theme-preset object for the
  Oracle / Synthwave / Prism alternate palettes (brief §11). Leave them.

**Do not "re-align" the above — it's correct. Re-doing it is the failure mode.**

## Actual gaps to close (priority order)

These come straight from the brief's own "P1 — Landing Page Iteration" plus two nits:

1. **Animation refinement** — glow "breathing" on the hero emblem and accent
   elements; smooth section-enter transitions on scroll. Keep it 10% cinematic,
   not gamer-RGB. Subtle edge glow on interactive elements only.
2. **Interactive tweaks panel** — wire the palette-preset toggle
   (Hermetic / Oracle / Synthwave / Prism / Mono) the preset object already
   defines, so a visitor can switch live. Controls specced in brand brief §11.
3. **Agent constellation (`#agents`) interactivity** — real hover states +
   connection lines between the agent nodes (Hermes Core/Flow/Forge/Relay/
   Thread/Nexus/Archive). Currently static.
4. **NIT — dim-text token drift:** `--txt-dim: #6B7280` should be the canonical
   muted token **`#9CA3AF`** (matches `--text-muted` in hermetic-os.css). One-line fix.
5. **NIT — void-black usage:** `#080808` appears only once. Confirm the page
   background and large surfaces resolve to the canonical stack
   (`#080808` primary → `#121212` secondary → `#16141B`/`#1A1A2E` cards),
   not ad-hoc darks.

## Guardrails (from the brief — non-negotiable)

- Aesthetic ratio **70% Claude-UI calm / 20% cyber-mysticism / 10% synthwave glow**.
- Avoid: gamer RGB, crypto look, cluttered cyberpunk, hacker-terminal chaos,
  corporate SaaS blandness.
- Typography feel: surgical, elegant, large spacing, lightweight headers,
  restrained uppercase, subtle tracking.
- Orbitron is **hero-only** — do not spread it into body or section titles.

## Return contract

When done, return: changed file path, a 1-line-per-section summary of what moved,
and a before/after screenshot if possible. The landing page is the master visual
authority — changes here propagate expectations to the Android surface, so keep
it disciplined.
