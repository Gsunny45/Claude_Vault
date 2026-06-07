#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
HERMETIC OS — Token Synchronization Pipeline
═══════════════════════════════════════════════════════════════════════════════

Reads tokens.yaml and emits platform-specific outputs:
  - obsidian/theme.css      (CSS custom properties + dashboard framework)
  - compose/Color.kt        (Android Compose color constants)
  - compose/Theme.kt        (Material3 dark color scheme + extended colors)
  - snygg/hermetic-theme.json (FlorisBoard/Snygg keyboard theme)

Usage:
    python sync-tokens.py                       # sync all targets
    python sync-tokens.py --target css          # only CSS
    python sync-tokens.py --target kotlin       # only Kotlin
    python sync-tokens.py --target snygg        # only Snygg JSON
    python sync-tokens.py --dry-run             # preview without writing
    python sync-tokens.py --diff                # show what would change

Requirements:
    pip install pyyaml

═══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
TOKENS_FILE = SCRIPT_DIR / "tokens.yaml"

TARGETS = {
    "css":    SCRIPT_DIR / "obsidian" / "theme.css",
    "kotlin": SCRIPT_DIR / "compose",   # directory: Color.kt + Theme.kt
    "snygg":  SCRIPT_DIR / "snygg" / "hermetic-theme.json",
}

HEADER_COMMENT = {
    "css": (
        "/* ═══════════════════════════════════════════════════════════════\n"
        " * HERMETIC OS — Obsidian Theme (auto-generated)\n"
        " * Generated: {timestamp}\n"
        " * Source: tokens.yaml\n"
        " * DO NOT EDIT — regenerate with: python sync-tokens.py --target css\n"
        " * ═══════════════════════════════════════════════════════════════ */\n\n"
    ),
    "kotlin": (
        "// ═══════════════════════════════════════════════════════════════\n"
        "// HERMETIC OS — {file_desc} (auto-generated)\n"
        "// Generated: {timestamp}\n"
        "// Source: tokens.yaml\n"
        "// DO NOT EDIT — regenerate with: python sync-tokens.py --target kotlin\n"
        "// ═══════════════════════════════════════════════════════════════\n\n"
    ),
    "snygg_meta": {
        "generated": None,  # filled at runtime
        "source": "tokens.yaml",
        "warning": "DO NOT EDIT — regenerate with: python sync-tokens.py --target snygg",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Token Loader
# ─────────────────────────────────────────────────────────────────────────────

def load_tokens(path: Path) -> dict:
    """Load and validate tokens.yaml."""
    if not path.exists():
        print(f"ERROR: Token file not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        tokens = yaml.safe_load(f)

    # Basic validation
    required_keys = ["color", "typography", "spacing", "radius", "elevation", "glow", "animation"]
    missing = [k for k in required_keys if k not in tokens]
    if missing:
        print(f"ERROR: tokens.yaml missing required sections: {', '.join(missing)}")
        sys.exit(1)

    return tokens


def resolve_ref(tokens: dict, ref: str) -> str:
    """Resolve a {section.path.key} reference to its value."""
    if not ref.startswith("{") or not ref.endswith("}"):
        return ref

    path = ref[1:-1].split(".")
    current = tokens
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return ref  # unresolvable — return as-is

    if isinstance(current, str):
        # Recursive resolution
        if current.startswith("{"):
            return resolve_ref(tokens, current)
        return current
    return str(current)


def flatten_colors(primitives: dict, prefix: str = "") -> list[tuple[str, str]]:
    """Flatten nested color dict to (css-name, hex-value) pairs."""
    result = []
    for key, value in primitives.items():
        name = f"{prefix}-{key}" if prefix else key
        if isinstance(value, dict):
            result.extend(flatten_colors(value, name))
        else:
            result.append((name, value))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# CSS Generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_css(tokens: dict) -> str:
    """Generate complete Obsidian theme CSS from tokens."""
    lines = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines.append(HEADER_COMMENT["css"].format(timestamp=ts))

    lines.append(":root {")

    # Primitive colors
    for family_name, family in tokens["color"]["primitive"].items():
        lines.append(f"\n  /* ── Primitive: {family_name.title()} ── */")
        if isinstance(family, dict):
            for shade, hex_val in family.items():
                css_name = f"--{family_name}-{shade}"
                lines.append(f"  {css_name}: {hex_val};")
        else:
            lines.append(f"  --{family_name}: {family};")

    # Semantic colors
    lines.append("\n  /* ── Semantic Colors ── */")
    for group_name, group in tokens["color"]["semantic"].items():
        if isinstance(group, dict):
            for key, ref in group.items():
                resolved = resolve_ref(tokens, ref)
                css_name = f"--{group_name}-{key}".replace("_", "-")
                lines.append(f"  {css_name}: {resolved};")
        else:
            resolved = resolve_ref(tokens, group)
            css_name = f"--{group_name}".replace("_", "-")
            lines.append(f"  {css_name}: {resolved};")

    # Typography
    lines.append("\n  /* ── Typography ── */")
    for key, val in tokens["typography"]["family"].items():
        lines.append(f"  --font-{key}: {val};")
    for key, scale in tokens["typography"]["scale"].items():
        if isinstance(scale, dict):
            lines.append(f"  --text-{key}: {scale.get('size', '14px')};")
            lines.append(f"  --leading-{key}: {scale.get('line_height', '22px')};")

    # Spacing
    lines.append("\n  /* ── Spacing ── */")
    for key, val in tokens["spacing"].items():
        if key.replace(".", "").replace("_", "").replace(" ", "").isdigit() or "." in key:
            css_key = key.replace(".", "-")
            lines.append(f"  --space-{css_key}: {val};")
        elif not key[0].isdigit():
            lines.append(f"  --space-{key.replace('_', '-')}: {val};")
        else:
            lines.append(f"  --space-{key}: {val};")

    # Radius
    lines.append("\n  /* ── Border Radius ── */")
    for key, val in tokens["radius"].items():
        lines.append(f"  --radius-{key}: {val};")

    # Elevation
    lines.append("\n  /* ── Elevation ── */")
    for key, val in tokens["elevation"].items():
        lines.append(f"  --shadow-{key.replace('_', '-')}: {val};")

    # Glow
    lines.append("\n  /* ── Glow ── */")
    for color_name, intensities in tokens["glow"].items():
        if isinstance(intensities, dict):
            for intensity, val in intensities.items():
                lines.append(f"  --glow-{color_name}-{intensity}: {val};")

    # Gradients
    if "gradient" in tokens:
        lines.append("\n  /* ── Gradients ── */")
        for key, val in tokens["gradient"].items():
            lines.append(f"  --gradient-{key.replace('_', '-')}: {val};")

    # Animation
    lines.append("\n  /* ── Animation ── */")
    for key, val in tokens["animation"]["duration"].items():
        lines.append(f"  --duration-{key}: {val};")
    for key, val in tokens["animation"]["easing"].items():
        lines.append(f"  --ease-{key.replace('_', '-')}: {val};")

    # Z-index
    if "z_index" in tokens:
        lines.append("\n  /* ── Z-Index ── */")
        for key, val in tokens["z_index"].items():
            lines.append(f"  --z-{key}: {val};")

    lines.append("}")
    lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Kotlin Generator
# ─────────────────────────────────────────────────────────────────────────────

def hex_to_argb(hex_str: str) -> str:
    """Convert #RRGGBB to 0xFFRRGGBB Kotlin format."""
    hex_clean = hex_str.lstrip("#")
    if len(hex_clean) == 6:
        return f"0xFF{hex_clean.upper()}"
    elif len(hex_clean) == 8:
        return f"0x{hex_clean.upper()}"
    return f"0xFF{hex_clean.upper()}"


def to_kotlin_name(family: str, shade: str) -> str:
    """Convert family+shade to PascalCase Kotlin name."""
    family_pascal = family.title().replace("_", "").replace("-", "")
    return f"{family_pascal}{shade}"


def generate_color_kt(tokens: dict) -> str:
    """Generate Color.kt from tokens."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        HEADER_COMMENT["kotlin"].format(timestamp=ts, file_desc="Color Tokens"),
        "package com.hermetic.designsystem.theme\n",
        "import androidx.compose.ui.graphics.Color\n",
    ]

    # Primitive colors
    for family_name, family in tokens["color"]["primitive"].items():
        lines.append(f"\n// ── Primitive: {family_name.title()} ──")
        if isinstance(family, dict):
            for shade, hex_val in family.items():
                kt_name = to_kotlin_name(family_name, shade)
                argb = hex_to_argb(hex_val)
                lines.append(f"val {kt_name} = Color({argb})")

    return "\n".join(lines) + "\n"


def generate_snygg_json(tokens: dict) -> str:
    """Generate Snygg keyboard theme JSON from tokens."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build @defines from primitive colors
    defines = {}
    for family_name, family in tokens["color"]["primitive"].items():
        if isinstance(family, dict):
            for shade, hex_val in family.items():
                key = f"{family_name}{shade}"
                defines[key] = hex_val

    # Add spacing/radius tokens
    if "component" in tokens and "key" in tokens["component"]:
        key_tokens = tokens["component"]["key"]
        if "radius" in key_tokens:
            defines["keyRadius"] = int(resolve_ref(tokens, key_tokens["radius"]).replace("px", ""))
        if "gap" in key_tokens:
            defines["keyGap"] = int(resolve_ref(tokens, key_tokens["gap"]).replace("px", ""))

    theme = {
        "$schema": "https://florisboard.org/schemas/snygg/v1",
        "_meta": {
            "name": "Hermetic OS",
            "version": tokens.get("meta", {}).get("version", "1.0.0"),
            "generated": ts,
            "source": "tokens.yaml",
        },
        "@defines": defines,
    }

    return json.dumps(theme, indent=2, ensure_ascii=False) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# File Writer
# ─────────────────────────────────────────────────────────────────────────────

def write_if_changed(path: Path, content: str, dry_run: bool = False) -> bool:
    """Write file only if content has changed. Returns True if written."""
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        existing = path.read_text(encoding="utf-8")
        # Strip timestamp lines for comparison
        existing_clean = re.sub(r"(Generated|generated):.*", "", existing)
        content_clean = re.sub(r"(Generated|generated):.*", "", content)
        if existing_clean.strip() == content_clean.strip():
            return False

    if dry_run:
        print(f"  [DRY RUN] Would write: {path}")
        return True

    path.write_text(content, encoding="utf-8")
    return True


def show_diff(path: Path, new_content: str):
    """Show a simple diff of changes."""
    if not path.exists():
        print(f"  [NEW] {path}")
        return

    existing_lines = path.read_text(encoding="utf-8").splitlines()
    new_lines = new_content.splitlines()

    added = 0
    removed = 0
    for line in new_lines:
        if line not in existing_lines:
            added += 1
    for line in existing_lines:
        if line not in new_lines:
            removed += 1

    if added == 0 and removed == 0:
        print(f"  [UNCHANGED] {path}")
    else:
        print(f"  [CHANGED] {path}: +{added} -{removed} lines")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hermetic OS Token Sync Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sync-tokens.py                  # sync all targets
  python sync-tokens.py --target css     # only regenerate CSS
  python sync-tokens.py --dry-run        # preview changes
  python sync-tokens.py --diff           # show what would change
        """,
    )
    parser.add_argument(
        "--target",
        choices=["css", "kotlin", "snygg", "all"],
        default="all",
        help="Which target to generate (default: all)",
    )
    parser.add_argument(
        "--tokens",
        type=Path,
        default=TOKENS_FILE,
        help=f"Path to tokens.yaml (default: {TOKENS_FILE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing files",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Show what would change",
    )

    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════╗")
    print("║  HERMETIC OS — Token Synchronization Pipeline       ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    # Load tokens
    print(f"Loading tokens from: {args.tokens}")
    tokens = load_tokens(args.tokens)
    version = tokens.get("meta", {}).get("version", "unknown")
    print(f"Token version: {version}")
    print()

    targets = ["css", "kotlin", "snygg"] if args.target == "all" else [args.target]
    files_written = 0
    files_unchanged = 0

    for target in targets:
        print(f"━━━ Target: {target.upper()} ━━━")

        if target == "css":
            content = generate_css(tokens)
            path = TARGETS["css"]
            if args.diff:
                show_diff(path, content)
            elif write_if_changed(path, content, args.dry_run):
                print(f"  ✓ Written: {path}")
                files_written += 1
            else:
                print(f"  · Unchanged: {path}")
                files_unchanged += 1

        elif target == "kotlin":
            color_content = generate_color_kt(tokens)
            color_path = TARGETS["kotlin"] / "Color.kt"
            if args.diff:
                show_diff(color_path, color_content)
            elif write_if_changed(color_path, color_content, args.dry_run):
                print(f"  ✓ Written: {color_path}")
                files_written += 1
            else:
                print(f"  · Unchanged: {color_path}")
                files_unchanged += 1

            # Theme.kt is partially hand-crafted (imports, composable structure)
            # The sync pipeline generates Color.kt; Theme.kt references it.
            print(f"  ℹ Theme.kt references Color.kt — verify imports after color changes.")

        elif target == "snygg":
            content = generate_snygg_json(tokens)
            path = TARGETS["snygg"]
            if args.diff:
                show_diff(path, content)
            elif write_if_changed(path, content, args.dry_run):
                print(f"  ✓ Written: {path}")
                files_written += 1
            else:
                print(f"  · Unchanged: {path}")
                files_unchanged += 1

        print()

    # Summary
    print("─" * 54)
    if args.dry_run:
        print(f"DRY RUN complete. {files_written} file(s) would be written.")
    elif args.diff:
        print("Diff complete.")
    else:
        print(f"Sync complete. {files_written} written, {files_unchanged} unchanged.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
