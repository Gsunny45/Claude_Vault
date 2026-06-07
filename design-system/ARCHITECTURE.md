# Hermetic OS Design System — Architecture Document

**Version:** 1.0.0  
**Aesthetic:** Cyber-mystic / Arcane  
**Philosophy:** "Power user light with options."

---

## §1  Design System Overview

The Hermetic OS Design System is the single source of truth for visual identity across three distinct rendering targets: Android Compose (Kotlin/Material3), Snygg Keyboard Theme Engine (HermeticA-Z / FlorisBoard), and Obsidian.md (CSS custom properties). Every color, spacing value, glow intensity, and animation curve traces back to one canonical file: `tokens.yaml`.

### Core Philosophy

**High visual density.** Every pixel earns its space. Default padding is compact (12px cards, 16px panels). Typography starts at 14px base — smaller than Material3's default 16px — because power users read fast and need more on screen. White space is structural (separating semantic groups), never decorative.

**Layered depth.** Surfaces stack in a 5-tier depth model: base → raised → elevated → overlay → modal. Each tier is a discrete step darker-to-lighter within the void palette. Glow effects provide the illusion of luminescence without breaking the depth hierarchy.

**Arcane luminescence.** The glow system is the visual signature. Four intensity levels (subtle, default, strong, intense) per accent color. Glows are additive — they combine with shadows, never replace them. The `composite` glow tokens pre-combine shadow + glow for common card use cases.

**Constraint-driven color.** Four colors. No more. Void Black (#080808) is the canvas. Violet (#8C7BFF) is primary action. Sky-Blue (#52C7FF) is secondary/informational. Amber (#D2B35E) is accent/warning. Status colors (success green, error red) are functional additions, not brand colors.

### Visual Density Rules

| Rule | Value | Rationale |
|------|-------|-----------|
| Base font size | 14px | Dense reading; power-user default |
| Card padding | 12px | Tight but breathable |
| Panel padding | 16px | One step above card |
| Minimum touch target | 36px (mobile), 28px (desktop) | Accessibility floor |
| Grid unit | 4px | All spacing is a multiple of 4 |
| Maximum content width | None enforced | Dashboards use the full viewport |
| Default border-radius | 8px (buttons/inputs), 12px (cards/panels) | Soft but not rounded |

---

## §2  Token Architecture

The token system uses three abstraction layers:

```
PRIMITIVE  →  SEMANTIC  →  COMPONENT
   │              │             │
   │   Raw hex    │  Role-based │  Per-widget
   │   values     │  aliases    │  presets
   │              │             │
   ▼              ▼             ▼
 #8C7BFF   color.primary   button.bg
```

**Primitives** are the raw palette: 19 shades per color family (void, violet, sky, amber), plus status colors and pure references (white, black, transparent).

**Semantic tokens** map primitives to roles: `surface.base`, `primary.default`, `text.muted`, `border.focus`. Components never reference primitives directly — always semantic tokens.

**Component tokens** are pre-composed per-widget: `button.height.md = 36px`, `card.radius = 12px`, `key.font_size.alpha = 18sp`. These exist for convenience; they resolve to semantic + spacing tokens.

### Token File: `tokens.yaml`

The master file contains 9 top-level sections:

| Section | Purpose |
|---------|---------|
| `meta` | Name, version, targets |
| `color.primitive` | Raw hex palette (void, violet, sky, amber, status, pure) |
| `color.semantic` | Role-based color mapping (surface, primary, secondary, accent, text, border, state, interactive) |
| `typography` | Font families, modular scale (minor third from 14px base), weights, composite text styles |
| `spacing` | 4px grid with named stops (0–128px) + semantic aliases |
| `radius` | Border-radius scale + semantic per-component aliases |
| `elevation` | 6-level shadow system (0–5) + semantic component shadows |
| `glow` | 4-intensity glow per accent color + composites + border-glows |
| `animation` | Durations, easing curves (including `arcane`), named transitions, keyframe definitions |
| `gradient` | Surface gradients, hero gradients, shimmer, keyboard-specific |
| `component` | Pre-composed tokens per widget (button, card, input, badge, tooltip, modal, metric_card, key) |
| `breakpoint` | Responsive breakpoints (xs–2xl) |
| `z_index` | Layering constants |

---

## §3  File/Folder Structure

```
hermetic-os-design-system/
├── tokens.yaml                  # ★ Single source of truth
├── sync-tokens.py               # ★ Auto-generation pipeline
├── ARCHITECTURE.md              # This document
│
├── obsidian/
│   └── theme.css                # Generated: CSS variables + dashboard framework
│
├── compose/
│   ├── Color.kt                 # Generated: primitive + semantic color vals
│   ├── Theme.kt                 # Semi-generated: Material3 scheme + extended colors
│   └── DashboardComponents.kt   # Example: GlowingMetricCard, StatusBadge, etc.
│
├── snygg/
│   └── hermetic-theme.json      # Generated: FlorisBoard/Snygg keyboard theme
│
├── assets/                      # (future) Icon set, font files
│   ├── fonts/
│   │   ├── JetBrainsMono/
│   │   └── Inter/
│   └── icons/
│
└── docs/                        # (future) Storybook / catalog
    ├── color-palette.md
    ├── component-catalog.md
    └── glow-reference.md
```

**Conventions:**
- Files marked ★ are hand-edited. All others are generated or semi-generated.
- Generated files carry a `DO NOT EDIT` header comment.
- `Theme.kt` is semi-generated: Color references are auto-updated, but the Composable structure and extended color data class are hand-maintained.

---

## §4  Semantic Color Language

The four primitive families map to semantic roles as follows:

### Surface (Void family)

| Token | Resolved | Usage |
|-------|----------|-------|
| `surface.base` | `void.950` #080808 | App background, canvas |
| `surface.raised` | `void.900` #0D0D0F | Cards, panels, sidebars |
| `surface.elevated` | `void.800` #16161A | Modals, popovers, code blocks |
| `surface.overlay` | `void.750` #1C1C22 | Dropdowns, tooltips, menus |
| `surface.scrim` | `rgba(8,8,8,0.72)` | Backdrop behind modals |

### Primary Action (Violet family)

| Token | Resolved | Usage |
|-------|----------|-------|
| `primary.default` | `violet.500` #8C7BFF | CTA buttons, active nav, focus ring |
| `primary.hover` | `violet.400` #A296FF | Hover state |
| `primary.pressed` | `violet.600` #7464D9 | Active/pressed state |
| `primary.disabled` | `violet.800` #42358C | Disabled buttons |
| `primary.subtle` | `violet.900` #2D2466 | Selected row bg, subtle highlights |

### Secondary (Sky family)

| Token | Resolved | Usage |
|-------|----------|-------|
| `secondary.default` | `sky.500` #52C7FF | Info badges, links, secondary CTA |
| `secondary.hover` | `sky.400` #74D4FF | Hover |
| `secondary.subtle` | `sky.900` #0F3752 | Info background |

### Accent (Amber family)

| Token | Resolved | Usage |
|-------|----------|-------|
| `accent.default` | `amber.500` #D2B35E | Warnings, highlights, decorative |
| `accent.hover` | `amber.400` #DCCA7E | Hover |
| `accent.subtle` | `amber.900` #3E3115 | Warning background |

### Text Hierarchy

| Token | Resolved | Usage |
|-------|----------|-------|
| `text.primary` | `void.50` #DCDCE6 | Main body text, headings |
| `text.secondary` | `void.200` #8E8E9E | Labels, descriptions, metadata |
| `text.muted` | `void.300` #6A6A7A | Placeholders, timestamps |
| `text.disabled` | `void.400` #4E4E5C | Disabled controls |
| `text.link` | `violet.500` #8C7BFF | Internal links |

---

## §6  Dashboard Framework

The Obsidian CSS includes a complete dashboard framework activated via `cssclasses: [hermetic-dashboard]` in note frontmatter. It provides:

### Panel Architecture

Dashboards use a CSS Grid layout with three columns by default, collapsing to 2 at 1024px and 1 at 768px. Panels are the primary container unit.

**Panel variants:**
- `.panel` — base: raised surface, default border, shadow-2
- `.panel--violet` — left accent border + violet gradient fade
- `.panel--sky` — left accent border + sky gradient fade
- `.panel--amber` — left accent border + amber gradient fade
- `.panel--glow-violet` — composite glow shadow + tinted border

**Metric cards** (`.metric` inside a panel) display a KPI with overline label, large value, and delta indicator. The delta colorizes automatically: green for up, red for down, muted for neutral.

**Data tables** get tighter padding, monospace column headers, hover-row highlighting, and subtle row borders.

**Progress bars** (`.progress` + `.progress-bar--{color}`) are 6px tall with full-radius caps.

**Status badges** (`.badge--{variant}`) are 20px height, full-radius pills with dim background and bright text.

---

## §9  Landing Page Governance

Rules for any landing page, hero section, or marketing surface rendered through the design system:

### Gradient Behavior

- **Hero sections** use `gradient.hero_radial` or `gradient.hero_mesh`. Never flat color for hero backgrounds.
- **Mesh gradients** use 3 overlapping radial-gradients at 12%/8%/6% opacity for violet/sky/amber respectively. The effect is subtle atmospheric depth, not a color show.
- **Section transitions** use `gradient.void_depth` (top-to-bottom void-900 → void-950) for a gravity-pull effect.
- **Loading states** use `gradient.arcane_shimmer` animated at 200% width for a sweeping luminescence effect.

### Shadow Standards

- Cards on dark backgrounds: `elevation.2` minimum.
- Floating elements (dropdowns, tooltips): `elevation.3` + `glow.{color}.subtle` combined.
- Hero CTAs: `glow.violet.strong` — the button should visibly glow.
- Never use `elevation.5` on more than one element per viewport.

### Animation Language

- **Micro-interactions** (hover, focus, toggle): `duration.fast` (100ms) + `ease.default`.
- **State transitions** (expand, collapse, page switch): `duration.normal` (200ms) + `ease.decelerate`.
- **Glow pulses** (attention, status indicators): `duration.cinematic` (1000ms) + `ease.arcane`.
- **Page entrance**: `duration.slow` (350ms) + `ease.decelerate`, staggered 50ms per element.
- **No animation** on anything that updates > 1Hz (live data, counters).

---

## §10  Component Standards

### Button Geometry

| Size | Height | Padding-H | Font Size | Icon Size | Icon Gap |
|------|--------|-----------|-----------|-----------|----------|
| sm | 28px | 12px | 11px | 14px | 6px |
| md | 36px | 16px | 12px | 16px | 6px |
| lg | 44px | 24px | 14px | 20px | 6px |

- Border-radius: 8px (all sizes).
- Font-weight: 600 (semibold).
- Primary variant: violet-500 bg, void-950 text.
- Secondary variant: transparent bg, violet-500 text, 1px violet-700 border.
- Ghost variant: transparent bg, text-secondary color, no border. Hover: hover-overlay bg.

### Card Specifications

- Border-radius: 12px.
- Padding: 12px.
- Border: 1px solid border-default (void-700).
- Background: surface-raised (void-900).
- Shadow: elevation-2.
- Hover: border-strong (void-500), elevation-3.
- Min-width: 200px (prevents squished cards in grids).

### Icon Usage

- Default icon size: 16px (matches md button icon).
- Icon color inherits `text.secondary` unless inside a button (inherits button foreground).
- Interactive icons: 20px size, 36px touch target (invisible padding).
- Never use icons without an accessible label (aria-label or visually-hidden text).

---

## §11  Synchronization Pipeline

The pipeline script `sync-tokens.py` is the automated bridge from tokens to targets.

### Flow

```
tokens.yaml
    │
    ▼
sync-tokens.py
    │
    ├──→ obsidian/theme.css      (CSS custom properties)
    ├──→ compose/Color.kt        (Kotlin Color vals)
    └──→ snygg/hermetic-theme.json (Snygg @defines)
```

### CLI Commands

```bash
# Full sync — all targets
python sync-tokens.py

# Single target
python sync-tokens.py --target css
python sync-tokens.py --target kotlin
python sync-tokens.py --target snygg

# Preview mode (no file writes)
python sync-tokens.py --dry-run

# Show diff summary
python sync-tokens.py --diff

# Custom token file path
python sync-tokens.py --tokens /path/to/tokens.yaml
```

### Pipeline Behavior

1. **Load** tokens.yaml via PyYAML.
2. **Validate** required top-level sections exist.
3. **Resolve** `{token.path}` references recursively.
4. **Generate** target-specific output string.
5. **Compare** against existing file (ignoring timestamp lines).
6. **Write** only if content changed (idempotent).
7. **Report** summary: files written vs. unchanged.

### Requirements

```
pip install pyyaml
```

---

## §12  Expansion Roadmap

### Phase 1: Foundation (Current)

- [x] Master tokens.yaml with full primitive + semantic + component layers
- [x] Obsidian CSS theme with dashboard framework
- [x] Compose Color.kt + Theme.kt with Material3 dark scheme
- [x] Snygg keyboard theme JSON
- [x] Python sync pipeline (tokens → CSS/Kotlin/JSON)

### Phase 2: Enrichment (Next)

- [ ] **Icon system:** Curated subset of Lucide or Phosphor, exported as Android vector drawables and SVG sprite for Obsidian
- [ ] **Motion library:** Compose `AnimationSpec` presets matching the CSS easing/duration tokens
- [ ] **Figma sync:** Token Studio integration — push tokens.yaml to Figma variables, pull design changes back
- [ ] **Storybook/Catalog:** HTML page auto-generated from tokens showing every color, spacing, glow in a visual reference
- [ ] **Dark/Light mode:** Light theme variant (high-contrast void inversion) stored as `tokens-light.yaml`

### Phase 3: Multi-Platform (Future)

- [ ] **iOS/SwiftUI target:** Generate `Color+Hermetic.swift` and `HermeticTheme.swift`
- [ ] **Web/CSS-in-JS target:** Generate `tokens.ts` (styled-components / Stitches / Vanilla Extract)
- [ ] **Tailwind preset:** Generate `tailwind.config.js` extending the default theme with Hermetic tokens
- [ ] **Design lint:** CI step that validates Compose/CSS code references only semantic tokens, never raw hex
- [ ] **Versioned releases:** Publish tokens as an npm/Maven/CocoaPods package with semver

---

## Appendix A: Token Reference Summary

| Token Path | CSS Variable | Kotlin Constant | Snygg @define |
|------------|-------------|-----------------|---------------|
| `color.primitive.void.950` | `--void-950` | `Void950` | `@defines/void950` |
| `color.primitive.violet.500` | `--violet-500` | `Violet500` | `@defines/violet500` |
| `color.primitive.sky.500` | `--sky-500` | `Sky500` | `@defines/sky500` |
| `color.primitive.amber.500` | `--amber-500` | `Amber500` | `@defines/amber500` |
| `color.semantic.surface.base` | `--surface-base` | `SurfaceBase` | (uses @defines/void950) |
| `color.semantic.primary.default` | `--primary` | `PrimaryDefault` | (uses @defines/violet500) |
| `spacing.4` | `--space-4` | `HermeticSpacing.Lg` | `16` (inline) |
| `radius.card` | `--radius-lg` | `HermeticRadius.Card` | `@defines/keyRadius` |
| `glow.violet.default` | `--glow-violet-default` | (custom drawBehind) | `shadowBlur: 12` |

## Appendix B: Heading Color Hierarchy (Obsidian)

| Level | Color | Token | Rationale |
|-------|-------|-------|-----------|
| H1 | Violet 400 #A296FF | `--h1-color` | Primary accent — top-level sections |
| H2 | Sky 400 #74D4FF | `--h2-color` | Secondary — subsections |
| H3 | Amber 400 #DCCA7E | `--h3-color` | Accent — detail headings |
| H4–H6 | Text primary → muted | `--h4/5/6-color` | Diminishing hierarchy |
