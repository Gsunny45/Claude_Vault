#!/usr/bin/env python3
"""
Training Data Capture Pipeline — generates fine-tuning JSONL from the vault ecosystem.

Sources:
  1. All 5 Obsidian vaults (knowledge, decisions, tasks, sessions, docs)
  2. ElectroScavengeNexus survival knowledge
  3. RAG query/response pairs (logged by the orchestrator)
  4. Manual instruction/output pairs

Output: JSONL in Alpaca format (instruction, input, output) — ready for QLoRA fine-tuning.

Usage:
  python capture_training_data.py                    # harvest all vaults
  python capture_training_data.py --source vault     # only vault content
  python capture_training_data.py --source rag-log   # only RAG conversation logs
  python capture_training_data.py --source nexus     # only ElectroScavengeNexus
  python capture_training_data.py --stats            # show dataset statistics
"""

from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Config — vault paths and output
# ---------------------------------------------------------------------------

VAULT_ROOTS = {
    "claude_vault": Path(os.getenv(
        "CLAUDE_VAULT", r"C:\Users\MarsBase\Documents\Claude_Vault")),
    "local_hub": Path(os.getenv(
        "LOCAL_HUB_VAULT", r"C:\Users\MarsBase\Documents\Local-Network-Hub")),
    "force_mult": Path(os.getenv(
        "FORCE_MULT_VAULT", r"C:\Users\MarsBase\Documents\Force Multiplication v1")),
}

# Subdirectories to harvest from each vault
HARVEST_DIRS = {
    "claude_vault": ["knowledge", "decisions", "tasks", "sessions",
                     "claude_on_claude/docs", "memory"],
    "local_hub": ["00-System", "01-Projects", "Sessions"],
    "force_mult": ["."],  # scan everything
}

OUTPUT_DIR = Path(os.getenv(
    "TRAINING_DATA_DIR",
    r"C:\Users\MarsBase\Documents\Claude_Vault\llm-orchestrator\training_data"))

RAG_LOG_PATH = OUTPUT_DIR / "rag_conversation_log.jsonl"
DATASET_PATH = OUTPUT_DIR / "vault_finetune_dataset.jsonl"

# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown."""
    fm = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    fm[key.strip()] = val.strip()
            body = parts[2].strip()
    return fm, body


def generate_id(text: str) -> str:
    """Deterministic ID from content for dedup."""
    return hashlib.md5(text.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Vault harvesting — turns markdown notes into instruction/output pairs
# ---------------------------------------------------------------------------

INSTRUCTION_TEMPLATES = {
    "knowledge": [
        "Explain {subject} based on the vault knowledge base.",
        "What does the vault know about {subject}?",
        "Summarize the knowledge entry for {subject}.",
    ],
    "decision": [
        "What decision was made about {title} and why?",
        "Explain the rationale behind decision {id}: {title}.",
        "What alternatives were considered for {title}?",
    ],
    "task": [
        "What is the current status of task {id}: {title}?",
        "Describe the work needed for {title}.",
        "What are the acceptance criteria for task {id}?",
    ],
    "session": [
        "Summarize session {id}.",
        "What was accomplished in this session?",
    ],
    "general": [
        "Explain the contents of {filename}.",
        "What information does {filename} contain?",
    ],
}


def vault_note_to_pairs(filepath: Path) -> list[dict]:
    """Convert a single vault note into training pairs."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    if len(text.strip()) < 50:
        return []

    fm, body = parse_frontmatter(text)
    note_type = fm.get("type", "general")
    templates = INSTRUCTION_TEMPLATES.get(note_type, INSTRUCTION_TEMPLATES["general"])

    # Build template variables
    vars_ = {
        "subject": fm.get("subject", filepath.stem),
        "title": fm.get("title", filepath.stem),
        "id": fm.get("id", filepath.stem),
        "filename": filepath.name,
    }

    pairs = []
    for tmpl in templates:
        instruction = tmpl.format(**vars_)
        pair = {
            "instruction": instruction,
            "input": "",
            "output": body[:4000],  # cap at ~1K tokens
            "metadata": {
                "source": str(filepath.name),
                "type": note_type,
                "vault": filepath.parts[-3] if len(filepath.parts) > 3 else "unknown",
                "generated": datetime.now().isoformat(),
                "id": generate_id(instruction + body[:200]),
            }
        }
        pairs.append(pair)

    return pairs


def harvest_vaults() -> list[dict]:
    """Scan all configured vaults and generate training pairs."""
    all_pairs = []

    for vault_key, root in VAULT_ROOTS.items():
        if not root.exists():
            print(f"  SKIP {vault_key}: {root} not found")
            continue

        dirs = HARVEST_DIRS.get(vault_key, ["."])
        file_count = 0

        for subdir in dirs:
            scan_path = root / subdir
            if not scan_path.exists():
                continue

            md_files = list(scan_path.glob("*.md"))
            for fp in md_files:
                pairs = vault_note_to_pairs(fp)
                all_pairs.extend(pairs)
                if pairs:
                    file_count += 1

        print(f"  {vault_key}: {file_count} files -> {len([p for p in all_pairs if p['metadata'].get('vault', '').lower() in vault_key.lower() or True])} pairs")

    return all_pairs


# ---------------------------------------------------------------------------
# RAG conversation logging — call this from the orchestrator
# ---------------------------------------------------------------------------

def log_rag_conversation(query: str, rag_context: str, response: str,
                         model: str = "unknown") -> None:
    """Append a RAG-augmented conversation to the log file.
    Call this from main.py after each RAG-enhanced response."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "instruction": query,
        "input": rag_context[:2000],
        "output": response[:4000],
        "metadata": {
            "source": "rag_conversation",
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "id": generate_id(query + response[:200]),
        }
    }

    with open(RAG_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def load_rag_log() -> list[dict]:
    """Load previously logged RAG conversations."""
    if not RAG_LOG_PATH.exists():
        return []
    pairs = []
    with open(RAG_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    pairs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return pairs


# ---------------------------------------------------------------------------
# ElectroScavengeNexus integration
# ---------------------------------------------------------------------------

NEXUS_CONTENT = {
    "Skills": {
        "Scouting": {
            "instruction": "Explain post-collapse location scouting and safe entry for electronics salvage.",
            "output": (
                "**Location Scouting & Safe Entry**\n"
                "- Target: Abandoned homes, basements, faraday-like cars (pre-1980s).\n"
                "- Safety: Stick probes for traps; enter via windows.\n"
                "- Priority: Unplugged devices (EMP survival).\n"
                "- Twist: Fossil tech (Nokias) that endure.\n"
                "- Advanced: Hidden scouting for quantum-resistant relics."
            ),
        },
        "Extraction": {
            "instruction": "How do you extract useful electronic components with primitive tools after societal collapse?",
            "output": (
                "**Component Extraction**\n"
                "- Tools: Stone chisel, fire-heated desoldering.\n"
                "- Targets: Copper wire, capacitors, rare earths (magnets).\n"
                "- Life/Death: Wires for snares/fishing.\n"
                "- Advanced: Primitive batteries from extraction byproducts."
            ),
        },
        "Testing": {
            "instruction": "How do you test and shield salvaged electronics from EMP damage?",
            "output": (
                "**Basic Testing & Shielding**\n"
                "- Test: Rub wires for static spark; listen for radio static.\n"
                "- Shield: Foil/cloth wrap, bury in metal cans.\n"
                "- Revive: Dry wet items fully.\n"
                "- Twist: Shielded phones as signal mirrors."
            ),
        },
    },
    "Tools": {
        "Motors": {
            "instruction": "What survival uses do salvaged electric motors have after collapse?",
            "output": (
                "**Electric Motors (Appliances)**\n"
                "- Source: Fans, washers.\n"
                "- Use: Manual generators, pumps, wind grinding.\n"
                "- Twist: Weights for traps or sound alarms.\n"
                "- Advanced: Motor fusion with ancient mechanical tech."
            ),
        },
        "Radios": {
            "instruction": "How do you establish communication using salvaged radio equipment post-collapse?",
            "output": (
                "**Tube & Survival Radios**\n"
                "- Source: Vintage receivers, crank radios.\n"
                "- Use: Short-wave signals, morale, coordination.\n"
                "- Twist: Antenna as fishing pole or signal tower."
            ),
        },
        "Batteries": {
            "instruction": "How do you salvage and repurpose batteries and capacitors for survival power?",
            "output": (
                "**Batteries & Capacitors**\n"
                "- Source: Disposables, electronics.\n"
                "- Use: Power tiny lights, igniters.\n"
                "- Twist: Chemical sources from household materials."
            ),
        },
    },
    "Builds": {
        "Generator": {
            "instruction": "How do you build a hand-crank generator from salvaged parts?",
            "output": (
                "**Hand-Crank Generator**\n"
                "1. Salvage motor & wires from appliances.\n"
                "2. Attach crank (stick/pedal) to motor shaft.\n"
                "3. Test for voltage with LED or spark test.\n"
                "- Use: Charge lights/small devices.\n"
                "- Twist: Double as muscle trainer or alarm spinner."
            ),
        },
        "Network": {
            "instruction": "How do you build a primitive communication network from salvaged server hardware?",
            "output": (
                "**Primitive Network Hub**\n"
                "1. Gather old servers/hubs from office buildings.\n"
                "2. Run copper lines between camps.\n"
                "3. Power with hand-crank generator.\n"
                "- Use: Coordinate raids, trap signaling.\n"
                "- Twist: Radiation mapping network."
            ),
        },
        "Smelter": {
            "instruction": "How do you recover gold and rare metals from circuit boards post-collapse?",
            "output": (
                "**Gold Recovery Smelter**\n"
                "1. Crush boards to powder.\n"
                "2. Smelt in fire pit with charcoal bellows.\n"
                "3. Extract flakes for barter/antibiotic coating.\n"
                "- Advanced: Adapt smelter for rare earth extraction."
            ),
        },
    },
}


def generate_nexus_pairs() -> list[dict]:
    """Generate training pairs from ElectroScavengeNexus content."""
    pairs = []
    for category, items in NEXUS_CONTENT.items():
        for name, data in items.items():
            pair = {
                "instruction": data["instruction"],
                "input": "",
                "output": data["output"],
                "metadata": {
                    "source": f"ElectroScavengeNexus/{category}/{name}",
                    "type": "nexus_survival",
                    "generated": datetime.now().isoformat(),
                    "id": generate_id(data["instruction"]),
                }
            }
            pairs.append(pair)
    return pairs


# ---------------------------------------------------------------------------
# Dataset management
# ---------------------------------------------------------------------------

def merge_and_dedup(all_pairs: list[dict]) -> list[dict]:
    """Deduplicate by content ID."""
    seen = set()
    unique = []
    for pair in all_pairs:
        pid = pair.get("metadata", {}).get("id", generate_id(pair["instruction"]))
        if pid not in seen:
            seen.add(pid)
            unique.append(pair)
    return unique


def write_dataset(pairs: list[dict], path: Path) -> None:
    """Write JSONL dataset."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")


def print_stats(pairs: list[dict]) -> None:
    """Print dataset statistics."""
    sources = {}
    types = {}
    for p in pairs:
        meta = p.get("metadata", {})
        src = meta.get("source", "unknown")
        src_key = src.split("/")[0] if "/" in src else src.split(".")[0] if "." in src else src
        sources[src_key] = sources.get(src_key, 0) + 1
        t = meta.get("type", "unknown")
        types[t] = types.get(t, 0) + 1

    total_chars = sum(len(p.get("output", "")) for p in pairs)

    print(f"\n{'='*60}")
    print(f"Training Dataset Statistics")
    print(f"{'='*60}")
    print(f"Total pairs:          {len(pairs)}")
    print(f"Total output chars:   {total_chars:,}")
    print(f"Est. tokens:          ~{total_chars // 4:,}")
    print(f"\nBy type:")
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t:25s} {count:4d}")
    print(f"\nBy source (top 15):")
    for s, count in sorted(sources.items(), key=lambda x: -x[1])[:15]:
        print(f"  {s:25s} {count:4d}")
    print(f"{'='*60}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Training data capture pipeline")
    parser.add_argument("--source", choices=["vault", "rag-log", "nexus", "all"],
                        default="all", help="Which source to harvest")
    parser.add_argument("--stats", action="store_true", help="Show dataset stats only")
    parser.add_argument("--output", type=str, default=None, help="Custom output path")
    args = parser.parse_args()

    output_path = Path(args.output) if args.output else DATASET_PATH

    # Stats only mode
    if args.stats:
        if output_path.exists():
            pairs = []
            with open(output_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        pairs.append(json.loads(line))
            print_stats(pairs)
        else:
            print(f"No dataset found at {output_path}")
        return

    print("="*60)
    print("Training Data Capture Pipeline")
    print("="*60)

    all_pairs = []

    # 1. Vault harvest
    if args.source in ("vault", "all"):
        print("\n[1] Harvesting vaults...")
        vault_pairs = harvest_vaults()
        all_pairs.extend(vault_pairs)
        print(f"    Vault pairs: {len(vault_pairs)}")

    # 2. RAG conversation log
    if args.source in ("rag-log", "all"):
        print("\n[2] Loading RAG conversation log...")
        rag_pairs = load_rag_log()
        all_pairs.extend(rag_pairs)
        print(f"    RAG log pairs: {len(rag_pairs)}")

    # 3. ElectroScavengeNexus
    if args.source in ("nexus", "all"):
        print("\n[3] Generating ElectroScavengeNexus pairs...")
        nexus_pairs = generate_nexus_pairs()
        all_pairs.extend(nexus_pairs)
        print(f"    Nexus pairs: {len(nexus_pairs)}")

    # 4. Dedup and write
    print("\n[4] Deduplicating...")
    unique_pairs = merge_and_dedup(all_pairs)
    print(f"    Before dedup: {len(all_pairs)}")
    print(f"    After dedup:  {len(unique_pairs)}")

    print(f"\n[5] Writing to {output_path}...")
    write_dataset(unique_pairs, output_path)

    print_stats(unique_pairs)
    print(f"\nDataset saved to: {output_path}")
    print("Ready for QLoRA fine-tuning with Gemma 3 4B.")


if __name__ == "__main__":
    main()
