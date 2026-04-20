#!/usr/bin/env python3
"""
ElectroScavengeNexus Vault Builder — cross-platform (Windows / Termux / Linux).

Builds a structured Obsidian vault of post-collapse electronics salvage knowledge,
exports as JSONL for fine-tuning, and optionally ingests into Pinecone RAG.

Usage:
  python build_nexus_vault.py                    # build vault + export JSONL
  python build_nexus_vault.py --ingest           # also push to Pinecone RAG
  python build_nexus_vault.py --path /custom/path  # custom vault location
  python build_nexus_vault.py --termux           # use Termux default path
"""

from __future__ import annotations
import argparse
import asyncio
import json
import os
import platform
import random
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path detection — Windows, Linux, Termux
# ---------------------------------------------------------------------------

VAULT_NAME = "ElectroScavengeNexus"

def detect_platform_path() -> Path:
    """Pick the right default path for the current platform."""
    if os.environ.get("TERMUX_VERSION"):
        return Path("/storage/emulated/0/Obsidian") / VAULT_NAME
    elif platform.system() == "Windows":
        return Path(os.environ.get("USERPROFILE", "C:/Users/MarsBase")) / "Documents" / VAULT_NAME
    else:
        return Path.home() / "Obsidian" / VAULT_NAME

FOLDERS = ["Setup", "Skills", "Tools", "Builds", "Unexpected", "Other", "Prompts"]

# ---------------------------------------------------------------------------
# Content — structured survival knowledge with frontmatter
# ---------------------------------------------------------------------------

CONTENT = {
    "Setup": {
        "TabletPrep.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-SETUP-001",
                "subject": "Android Tablet Field Prep",
                "confidence": "verified",
                "tags": ["setup-tablet"],
            },
            "body": (
                "# Android Tablet Prep\n\n"
                "1. **Device:** Old tablet (4GB RAM, Android 8+), Airplane Mode.\n"
                "2. **Install:** Obsidian (APK sideload), Termux (APK from F-Droid).\n"
                "3. **Vault:** Create 'ElectroScavengeNexus'.\n"
                "4. **Plugins:** Dataview, Advanced Tables.\n\n"
                "Ref: [[NexusIndex]]"
            ),
        },
    },
    "Skills": {
        "Scouting.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-SKL-001",
                "subject": "Location Scouting & Safe Entry",
                "confidence": "verified",
                "tags": ["scavenge-skill", "location"],
            },
            "body": (
                "# Location Scouting & Safe Entry\n\n"
                "- **Target:** Abandoned homes, basements, faraday-like cars (pre-1980s).\n"
                "- **Safety:** Stick probes for traps; enter via windows.\n"
                "- **Priority:** Unplugged devices (EMP survival).\n"
                "- **Twist:** Fossil tech (Nokias) that endure.\n\n"
                "Ref: [[Tools-Motors]]"
            ),
        },
        "Extraction.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-SKL-002",
                "subject": "Component Extraction with Primitive Tools",
                "confidence": "verified",
                "tags": ["dismantle-primitive", "skill"],
            },
            "body": (
                "# Component Extraction\n\n"
                "- **Tools:** Stone chisel, fire-heated desoldering.\n"
                "- **Targets:** Copper wire, capacitors, rare earths (magnets).\n"
                "- **Life/Death:** Wires for snares/fishing.\n"
                "- **Twist:** Primitive batteries from extraction byproducts.\n\n"
                "Ref: [[Builds-Generator]]"
            ),
        },
        "Testing.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-SKL-003",
                "subject": "Electronics Testing & EMP Shielding",
                "confidence": "verified",
                "tags": ["emp-protect", "testing"],
            },
            "body": (
                "# Basic Testing & Shielding\n\n"
                "- **Test:** Rub wires for static spark; listen for radio static.\n"
                "- **Shield:** Foil/cloth wrap, bury in metal cans.\n"
                "- **Revive:** Dry wet items fully.\n"
                "- **Twist:** Shielded phones as signal mirrors.\n\n"
                "Ref: [[Unexpected-Networks]]"
            ),
        },
    },
    "Tools": {
        "Motors.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-TL-001",
                "subject": "Salvaged Electric Motors",
                "confidence": "verified",
                "tags": ["salvage-tool", "swiss-use"],
            },
            "body": (
                "# Electric Motors (Appliances)\n\n"
                "- **Source:** Fans, washers.\n"
                "- **Use:** Manual generators, pumps, wind grinding.\n"
                "- **Twist:** Weights for traps or sound alarms.\n\n"
                "Ref: [[Builds-Pump]]"
            ),
        },
        "Radios.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-TL-002",
                "subject": "Tube & Survival Radios",
                "confidence": "verified",
                "tags": ["comm-tool"],
            },
            "body": (
                "# Tube & Survival Radios\n\n"
                "- **Source:** Vintage receivers, crank radios.\n"
                "- **Use:** Short-wave signals, morale, coordination.\n"
                "- **Twist:** Antenna as fishing pole.\n\n"
                "Ref: [[Builds-Network]]"
            ),
        },
        "Batteries.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-TL-003",
                "subject": "Batteries & Capacitors Salvage",
                "confidence": "verified",
                "tags": ["energy-tool"],
            },
            "body": (
                "# Batteries & Capacitors\n\n"
                "- **Source:** Disposables, electronics.\n"
                "- **Use:** Power tiny lights, igniters.\n"
                "- **Twist:** Chemical sources from household materials."
            ),
        },
    },
    "Builds": {
        "Generator.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-BLD-001",
                "subject": "Hand-Crank Generator Build",
                "confidence": "verified",
                "tags": ["power-build"],
            },
            "body": (
                "# Hand-Crank Generator\n\n"
                "1. Salvage motor & wires.\n"
                "2. Attach crank (stick/pedal).\n"
                "3. Test for voltage.\n\n"
                "- **Use:** Charge lights/small devices.\n"
                "- **Twist:** Muscle trainer or alarm spinner.\n\n"
                "Ref: [[Skills-Extraction]]"
            ),
        },
        "Network.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-BLD-002",
                "subject": "Primitive Communication Network",
                "confidence": "verified",
                "tags": ["comm-build"],
            },
            "body": (
                "# Primitive Network Hub\n\n"
                "1. Gather old servers/hubs.\n"
                "2. Run copper lines between camps.\n"
                "3. Power with hand-crank.\n\n"
                "- **Use:** Coordinate raids, trap signaling.\n"
                "- **Twist:** Radiation mapping network.\n\n"
                "Ref: [[Tools-Radios]]"
            ),
        },
        "Smelter.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-BLD-003",
                "subject": "Gold Recovery Smelter",
                "confidence": "verified",
                "tags": ["resource-build"],
            },
            "body": (
                "# Gold Recovery Smelter\n\n"
                "1. Crush boards to powder.\n"
                "2. Smelt in fire pit with charcoal.\n"
                "3. Extract flakes for barter/antibiotic coating."
            ),
        },
    },
    "Other": {
        "Mindsets.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-OTH-001",
                "subject": "Scavenger Mindsets & Challenges",
                "confidence": "inferred",
                "tags": ["nexus-core"],
            },
            "body": (
                "# Mindsets & Challenges\n\n"
                "- **Forgotten:** Resource exhaustion, restarting tech is hard.\n"
                "- **Twist:** Baghdad battery analogs.\n\n"
                "Ref: [[NexusIndex]]"
            ),
        },
    },
    "Prompts": {
        "ExpansionTemplates.md": {
            "frontmatter": {
                "type": "knowledge",
                "id": "NEX-PRM-001",
                "subject": "LLM Expansion Prompt Templates",
                "confidence": "verified",
                "tags": ["gemini-expand"],
            },
            "body": (
                "# LLM Prompt Templates for Knowledge Expansion\n\n"
                "1. \"Deepen [skill] with [twist]?\"\n"
                "2. \"What if salvaged chips enable [biological function]?\"\n"
                "3. \"Unthinkable extraction for [resource]?\"\n"
                "4. \"How would you adapt [build] for [climate zone]?\"\n"
                "5. \"What pre-industrial technique maps to [modern process]?\""
            ),
        },
    },
}

RANDOM_TWISTS = [
    "\n\n---\n**Random Twist:** Use screen glass for solar stills.",
    "\n\n---\n**Random Twist:** Speaker magnets for locking mechanisms.",
    "\n\n---\n**Random Twist:** PCBs sharpened as projectile points.",
    "\n\n---\n**Random Twist:** Hard drive platters as signal mirrors.",
    "\n\n---\n**Random Twist:** Transformer coils for induction heating.",
]


# ---------------------------------------------------------------------------
# Vault builder
# ---------------------------------------------------------------------------

def format_frontmatter(fm: dict) -> str:
    """Format frontmatter dict to YAML block."""
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)


def build_vault(base_path: Path) -> bool:
    """Create vault folder structure and populate notes."""
    print(f"[*] Building vault at: {base_path}")

    try:
        base_path.mkdir(parents=True, exist_ok=True)
        for folder in FOLDERS:
            (base_path / folder).mkdir(exist_ok=True)
    except PermissionError:
        print("[!] Permission Denied. On Termux, run 'termux-setup-storage' first.")
        return False
    except Exception as e:
        print(f"[!] Error creating folders: {e}")
        return False

    print("  Folders created.")

    file_count = 0
    for folder, notes in CONTENT.items():
        for filename, data in notes.items():
            filepath = base_path / folder / filename
            fm_text = format_frontmatter(data["frontmatter"])
            body = data["body"]
            twist = random.choice(RANDOM_TWISTS)

            filepath.write_text(fm_text + body + twist, encoding="utf-8")
            file_count += 1

    print(f"  {file_count} notes created with frontmatter + random twists.")

    # Create index
    index_path = base_path / "NexusIndex.md"
    index_content = """---
type: knowledge
id: NEX-INDEX
subject: ElectroScavengeNexus Master Index
confidence: verified
tags: [index-main]
---

# ElectroScavenge Nexus Index

## Skills
```dataview
LIST FROM "Skills"
```

## Tools
```dataview
LIST FROM "Tools"
```

## Builds
```dataview
LIST FROM "Builds"
```

## All Scavenge Tags
```dataview
LIST FROM "" WHERE contains(tags, "scavenge") OR contains(tags, "skill")
SORT file.name ASC
```
"""
    index_path.write_text(index_content, encoding="utf-8")
    print("  NexusIndex.md created.")
    return True


# ---------------------------------------------------------------------------
# JSONL export
# ---------------------------------------------------------------------------

def export_jsonl(base_path: Path) -> Path:
    """Export vault content as fine-tuning JSONL."""
    dataset = []
    for folder, notes in CONTENT.items():
        for name, data in notes.items():
            dataset.append({
                "instruction": f"Explain post-collapse survival regarding {data['frontmatter']['subject']}.",
                "input": "",
                "output": data["body"],
                "metadata": {
                    "source": f"ElectroScavengeNexus/{folder}/{name}",
                    "type": "nexus_survival",
                    "id": data["frontmatter"]["id"],
                }
            })

    jsonl_path = base_path / "nexus_finetune.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"  JSONL exported: {len(dataset)} pairs -> {jsonl_path}")
    return jsonl_path


# ---------------------------------------------------------------------------
# RAG ingestion (optional — pushes to Pinecone via the orchestrator module)
# ---------------------------------------------------------------------------

async def ingest_to_rag(base_path: Path) -> None:
    """Ingest Nexus content into Pinecone RAG."""
    # Import from the orchestrator backend
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))

    try:
        from dotenv import load_dotenv
        load_dotenv(backend_dir / ".env")
        # Reload rag module with fresh env
        import importlib
        import rag as rag_mod
        importlib.reload(rag_mod)
        from rag import PineconeRAG
    except ImportError:
        print("  [!] Cannot import rag module. Run from llm-orchestrator/backend/.")
        return

    rag = PineconeRAG()
    if not rag.available:
        print("  [!] Pinecone not configured. Skipping RAG ingest.")
        return

    total_chunks = 0
    total_upserted = 0

    for folder, notes in CONTENT.items():
        for name, data in notes.items():
            source = f"nexus/{folder}/{name}"
            text = data["body"]
            chunks = rag.chunk_text(text, source=source)
            if chunks:
                upserted = await rag.upsert(chunks)
                total_chunks += len(chunks)
                total_upserted += upserted
                print(f"    {source:40s} chunks={len(chunks)} upserted={upserted}")

    print(f"\n  RAG ingest: {total_chunks} chunks, {total_upserted} vectors upserted.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ElectroScavengeNexus Vault Builder")
    parser.add_argument("--path", type=str, default=None,
                        help="Custom vault path")
    parser.add_argument("--termux", action="store_true",
                        help="Use Termux default path")
    parser.add_argument("--ingest", action="store_true",
                        help="Also ingest into Pinecone RAG")
    args = parser.parse_args()

    if args.path:
        base_path = Path(args.path)
    elif args.termux:
        base_path = Path("/storage/emulated/0/Obsidian") / VAULT_NAME
    else:
        base_path = detect_platform_path()

    print("=" * 60)
    print("ElectroScavengeNexus Vault Builder")
    print(f"Platform: {platform.system()}")
    print(f"Target:   {base_path}")
    print("=" * 60)

    if not build_vault(base_path):
        return

    jsonl_path = export_jsonl(base_path)

    if args.ingest:
        print("\n[RAG] Ingesting into Pinecone...")
        asyncio.run(ingest_to_rag(base_path))

    print(f"\n{'='*60}")
    print("[SUCCESS] ElectroScavengeNexus built.")
    print(f"Vault:   {base_path}")
    print(f"JSONL:   {jsonl_path}")
    print(f"{'='*60}")
    print("Open Obsidian and select the vault folder.")


if __name__ == "__main__":
    main()
