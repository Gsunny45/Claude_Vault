#!/usr/bin/env python3
"""
Note Cleaner — bulk process messy vault notes into clean, named, frontmattered files.

What it does:
  1. Reads every .md file in a folder
  2. Auto-detects the topic from first ~500 chars
  3. Generates a proper filename (kebab-case from topic)
  4. Adds YAML frontmatter (type, subject, confidence, tags)
  5. Moves originals to processed/ subfolder
  6. Appends all content to training data JSONL
  7. Optionally ingests into Pinecone RAG

Usage:
  python clean_notes.py "C:\path\to\inbox"
  python clean_notes.py "C:\path\to\inbox" --rag         # also ingest to Pinecone
  python clean_notes.py "C:\path\to\inbox" --dry-run     # preview without moving files
  python clean_notes.py "C:\path\to\inbox" --all-dirs    # recurse into subdirectories
"""

from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TRAINING_DIR = Path(r"C:\Users\MarsBase\Documents\Claude_Vault\llm-orchestrator\training_data")
TRAINING_FILE = TRAINING_DIR / "vault_finetune_dataset.jsonl"


def slugify(text: str, max_len: int = 60) -> str:
    """Convert text to a clean kebab-case filename."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower().strip())
    text = re.sub(r"[-\s]+", "-", text)
    return text[:max_len].rstrip("-")


def detect_topic(text: str) -> str:
    """Extract a topic name from the first meaningful content."""
    # Strip frontmatter if present
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]

    # Skip noise lines (Templater vars, boilerplate, links, short lines)
    skip_patterns = [
        r"\{\{VALUE", r"\{.*VALUE", r"Conversation with Gemini",
        r"^\[", r"^Gemini$", r"^---$", r"^\s*$",
    ]

    # Look for first meaningful heading (not Templater)
    for line in body.split("\n"):
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if any(re.search(p, line) for p in skip_patterns):
            continue
        if line.startswith("#"):
            topic = re.sub(r"^#+\s*", "", line).strip()
            if len(topic) > 5 and "{{" not in topic:
                return topic[:80]

    # Look for first bold text (not Templater)
    bold = re.search(r"\*\*(.{5,80}?)\*\*", body[:3000])
    if bold and "{{" not in bold.group(1):
        return bold.group(1)[:80]

    # First substantial non-noise line
    for line in body.split("\n"):
        line = line.strip()
        if len(line) > 15 and not line.startswith("```"):
            if not any(re.search(p, line) for p in skip_patterns):
                return line[:80]

    return "untitled-note"


def detect_tags(text: str) -> list[str]:
    """Extract existing hashtags from content."""
    tags = re.findall(r"#([\w-]+)", text[:2000])
    # Filter out markdown heading artifacts
    tags = [t for t in tags if len(t) > 2 and t not in ("", "index", "main")]
    return list(set(tags))[:5]


def detect_type(text: str, topic: str) -> str:
    """Guess the note type from content."""
    lower = (text[:3000] + topic).lower()
    if any(w in lower for w in ["build", "generator", "smelter", "construct"]):
        return "knowledge"
    if any(w in lower for w in ["task", "todo", "deadline", "phase"]):
        return "task"
    if any(w in lower for w in ["decision", "rationale", "alternative"]):
        return "decision"
    if any(w in lower for w in ["session", "cowork", "log"]):
        return "session"
    return "knowledge"


def has_frontmatter(text: str) -> bool:
    """Check if the note already has YAML frontmatter."""
    return text.strip().startswith("---") and text.count("---") >= 2


def build_frontmatter(note_type: str, topic: str, tags: list[str],
                      note_id: str) -> str:
    """Generate YAML frontmatter block."""
    tag_str = ", ".join(tags) if tags else "untagged"
    return (
        f"---\n"
        f"type: {note_type}\n"
        f"id: {note_id}\n"
        f"subject: {topic}\n"
        f"confidence: inferred\n"
        f"last_verified: {datetime.now().strftime('%Y-%m-%d')}\n"
        f"tags: [{tag_str}]\n"
        f"---\n\n"
    )


def generate_id(prefix: str, index: int) -> str:
    """Generate a sequential ID like CLN-0001."""
    return f"{prefix}-{index:04d}"


def process_folder(folder: Path, dry_run: bool = False,
                   recurse: bool = False) -> list[dict]:
    """Process all .md files in a folder. Returns training pairs."""

    if recurse:
        md_files = sorted(folder.rglob("*.md"))
    else:
        md_files = sorted(folder.glob("*.md"))

    # Exclude files in processed/ subfolder
    processed_dir = folder / "processed"
    md_files = [f for f in md_files if "processed" not in f.parts]

    if not md_files:
        print(f"  No .md files found in {folder}")
        return []

    print(f"  Found {len(md_files)} files to process")

    training_pairs = []
    cleaned_count = 0
    skipped_count = 0

    for idx, fp in enumerate(md_files, start=1):
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  ERROR reading {fp.name}: {e}")
            continue

        if len(text.strip()) < 50:
            print(f"  SKIP (empty): {fp.name}")
            skipped_count += 1
            continue

        # Detect topic and metadata
        topic = detect_topic(text)
        tags = detect_tags(text)
        note_type = detect_type(text, topic)
        note_id = generate_id("CLN", idx)
        slug = slugify(topic)

        if not slug or slug == "untitled-note":
            slug = f"note-{idx:03d}"

        new_filename = f"{slug}.md"

        # Build clean content
        if has_frontmatter(text):
            clean_text = text  # keep existing frontmatter
        else:
            fm = build_frontmatter(note_type, topic, tags, note_id)
            clean_text = fm + text

        print(f"  {fp.name:30s} -> {new_filename}")
        print(f"    topic: {topic[:60]}")
        print(f"    type: {note_type}, tags: {tags[:3]}")

        if not dry_run:
            # Write clean file (same directory, new name)
            new_path = fp.parent / new_filename
            if new_path.exists() and new_path != fp:
                new_path = fp.parent / f"{slug}-{idx}.md"

            new_path.write_text(clean_text, encoding="utf-8")

            # Move original to processed/
            processed_dir.mkdir(exist_ok=True)
            dest = processed_dir / fp.name
            if dest.exists():
                dest = processed_dir / f"{fp.stem}-{idx}{fp.suffix}"
            shutil.move(str(fp), str(dest))

        cleaned_count += 1

        # Generate training pairs
        instructions = [
            f"Explain {topic}.",
            f"What does the vault know about {topic}?",
        ]
        for inst_idx, section in enumerate(
            [text[i:i+3000] for i in range(0, min(len(text), 12000), 3000)]
        ):
            training_pairs.append({
                "instruction": instructions[inst_idx % len(instructions)],
                "input": "",
                "output": section,
                "metadata": {
                    "source": f"cleaned/{new_filename}",
                    "type": note_type,
                    "original_file": fp.name,
                    "topic": topic,
                    "generated": datetime.now().isoformat(),
                    "id": hashlib.md5(
                        f"{fp.name}:{inst_idx}".encode()
                    ).hexdigest()[:12],
                }
            })

    print(f"\n  Cleaned: {cleaned_count}, Skipped: {skipped_count}")
    return training_pairs


def append_training_data(pairs: list[dict]) -> int:
    """Append pairs to the master training JSONL file."""
    TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    existing = 0
    if TRAINING_FILE.exists():
        with open(TRAINING_FILE, encoding="utf-8") as f:
            existing = sum(1 for _ in f)

    with open(TRAINING_FILE, "a", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    return existing + len(pairs)


def main():
    parser = argparse.ArgumentParser(description="Bulk note cleaner")
    parser.add_argument("folder", type=str, help="Folder of .md files to clean")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without moving files")
    parser.add_argument("--all-dirs", action="store_true",
                        help="Recurse into subdirectories")
    parser.add_argument("--rag", action="store_true",
                        help="Also ingest into Pinecone RAG")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"ERROR: Folder not found: {folder}")
        return

    print("=" * 60)
    print("Note Cleaner")
    print(f"Source:   {folder}")
    print(f"Dry run:  {args.dry_run}")
    print(f"Recurse:  {args.all_dirs}")
    print("=" * 60)

    # Process
    pairs = process_folder(folder, dry_run=args.dry_run, recurse=args.all_dirs)

    if not pairs:
        print("\nNo training pairs generated.")
        return

    # Save training data
    if not args.dry_run:
        total = append_training_data(pairs)
        print(f"\nTraining data: +{len(pairs)} pairs (total: {total})")
        print(f"Saved to: {TRAINING_FILE}")
    else:
        print(f"\n[DRY RUN] Would generate {len(pairs)} training pairs")

    # Optional RAG ingest
    if args.rag and not args.dry_run:
        print("\nRAG ingest requested — run ingest_gemini_vault.py separately")
        print("(Rate limits make inline RAG ingest unreliable for large batches)")

    print(f"\n{'='*60}")
    print("Done.")
    if not args.dry_run:
        print(f"Originals moved to: {folder / 'processed'}")
        print(f"Clean files in: {folder}")
    print("=" * 60)


if __name__ == "__main__":
    main()
