#!/usr/bin/env python3
"""
Ingest script for Claude Vault knowledge base.

Reads all .md files from:
  - /sessions/peaceful-gallant-hawking/mnt/Claude_Vault/knowledge/ (KNW-XXXX files)
  - /sessions/peaceful-gallant-hawking/mnt/Claude_Vault/claude_on_claude/docs/ (key docs)

Chunks each file and upserts to Pinecone.
Reports: total files processed, total chunks created, total vectors upserted.
"""

import asyncio
import sys
from pathlib import Path
from typing import List

# Add backend to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from rag import PineconeRAG, PINECONE_API_KEY, PINECONE_HOST


async def read_files(directories: List[Path]) -> dict[str, str]:
    """Read all .md files from the given directories."""
    files = {}
    for directory in directories:
        if not directory.exists():
            print(f"    WARNING: Directory not found: {directory}")
            continue

        md_files = sorted(directory.glob("*.md"))
        print(f"    Found {len(md_files)} .md files in {directory.name}")

        for filepath in md_files:
            try:
                content = filepath.read_text(encoding="utf-8")
                files[str(filepath)] = content
            except Exception as e:
                print(f"    ERROR reading {filepath.name}: {e}")

    return files


async def main():
    print("=" * 70)
    print("Claude Vault Ingestion")
    print("=" * 70)

    # --- 1. Config Check ---
    print("\n[1] Configuration Check")
    print(f"    Gemini API Key:     {'OK' if settings.gemini_api_key else 'MISSING'}")
    print(f"    Pinecone API Key:   {'OK' if PINECONE_API_KEY else 'MISSING'}")
    print(f"    Pinecone Host:      {PINECONE_HOST[:40] + '...' if PINECONE_HOST else 'MISSING'}")

    # --- 2. Initialize RAG ---
    rag = PineconeRAG()
    print(f"\n[2] RAG Initialization")
    print(f"    RAG Available:      {rag.available}")

    if not rag.available:
        print("\n    ERROR: Pinecone or Gemini not configured!")
        return

    # --- 3. Verify Pinecone Connection ---
    print("\n[3] Pinecone Connection Verification")
    try:
        stats = await rag.stats()
        if "status" in stats and stats["status"] == "error":
            print(f"    ERROR: {stats.get('detail', 'Unknown error')}")
            return
        print(f"    Status:             Connected")
    except Exception as e:
        print(f"    ERROR:              {e}")
        return

    # --- 4. Load Files ---
    print("\n[4] Loading Files")
    # Resolve vault root relative to this script (backend/ → llm-orchestrator/ → Claude_Vault/)
    vault_root = Path(__file__).parent.parent.parent
    knowledge_dir = vault_root / "knowledge"
    docs_dir = vault_root / "claude_on_claude" / "docs"
    tasks_dir = vault_root / "tasks"
    decisions_dir = vault_root / "decisions"
    memory_dir = vault_root / "memory"

    files = await read_files([knowledge_dir, docs_dir, tasks_dir, decisions_dir, memory_dir])
    print(f"    Total files loaded: {len(files)}")

    if not files:
        print("\n    ERROR: No files found to ingest!")
        return

    # --- 5. Chunk and Upsert ---
    print("\n[5] Chunking and Upserting")
    total_chunks = 0
    total_upserted = 0
    errors = []

    for filepath_str, content in sorted(files.items()):
        filepath = Path(filepath_str)
        source_name = filepath.name

        try:
            # Chunk the document
            chunks = rag.chunk_text(content, source=source_name)
            total_chunks += len(chunks)

            # Upsert in batches
            if chunks:
                upserted = await rag.upsert(chunks)
                total_upserted += upserted
                print(f"    {source_name:30s}  chunks={len(chunks):3d}  upserted={upserted:3d}")
            else:
                print(f"    {source_name:30s}  (empty file)")

        except Exception as e:
            error_msg = f"{source_name}: {str(e)[:60]}"
            errors.append(error_msg)
            print(f"    {source_name:30s}  ERROR: {str(e)[:40]}")

    # --- 6. Summary ---
    print("\n" + "=" * 70)
    print("Ingestion Summary")
    print("=" * 70)
    print(f"Total files processed:          {len(files)}")
    print(f"Total chunks created:           {total_chunks}")
    print(f"Total vectors upserted:         {total_upserted}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\nStatus:                         SUCCESS - No errors")

    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
