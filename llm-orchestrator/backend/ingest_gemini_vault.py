#!/usr/bin/env python3
"""
Ingest Gemini_Vault 01_INBOX into Pinecone RAG + training data JSONL.

Usage:
  cd llm-orchestrator/backend
  python ingest_gemini_vault.py
"""

import asyncio
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")
from rag import PineconeRAG

GEMINI_INBOX = Path(r"C:\Users\MarsBase\Documents\Gemini_Vault\01_INBOX")
TRAINING_DIR = Path(__file__).parent.parent / "training_data"
TRAINING_FILE = TRAINING_DIR / "vault_finetune_dataset.jsonl"

# Skip known duplicates
SKIP_FILES = {"Untitled 5.md", "Untitled 7.md", "Untitled 12.md"}

FILE_TOPICS = {
    "Untitled.md":    "WSL path diagnostics and system initialization",
    "Untitled 1.md":  "post-collapse 256GB Lifeboat Drive digital survival kit",
    "Untitled 2.md":  "visual multi-agent CrewAI orchestration platform with React Flow",
    "Untitled 3.md":  "Gemini task template structure",
    "Untitled 4.md":  "Critical Path post-collapse education episode framework",
    "Untitled 6.md":  "post-collapse survival gardening Northern California",
    "Untitled 8.md":  "Project Survival Oracle tiered offline AI architecture",
    "Untitled 9.md":  "Omni-Stream cross-provider meta-prompt extraction protocol",
    "Untitled 10.md": "AI Profile Matrix Engine DeepSeek Gemini LFM2 provider fixes",
    "Untitled 11.md": "Gemini 3 Pro Deep tuning framework and LogicMatrix profiling",
}

async def main():
    print("=" * 60)
    print("Gemini_Vault Inbox Ingestion")
    print("=" * 60)

    rag = PineconeRAG()
    if not rag.available:
        print("ERROR: Pinecone not configured. Check .env")
        return

    stats = await rag.stats()
    print(f"Starting vectors: {stats.get('totalVectorCount', 0)}")

    md_files = sorted(GEMINI_INBOX.glob("*.md"))
    total_rag = 0
    training_pairs = []

    for fp in md_files:
        if fp.name in SKIP_FILES:
            print(f"  SKIP duplicate: {fp.name}")
            continue

        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  ERROR {fp.name}: {e}")
            continue

        if len(text.strip()) < 100:
            continue

        topic = FILE_TOPICS.get(fp.name, fp.stem)

        # RAG: first 8000 chars
        chunks = rag.chunk_text(text[:8000], source=f"gemini_inbox/{fp.name}")
        if chunks:
            for attempt in range(4):
                try:
                    upserted = await rag.upsert(chunks)
                    total_rag += upserted
                    print(f"  {fp.name:25s} {upserted:2d} vectors")
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < 3:
                        wait = 15 * (attempt + 1)
                        print(f"  rate limit {fp.name}, retry in {wait}s...")
                        await asyncio.sleep(wait)
                    else:
                        print(f"  RAG SKIP {fp.name}: {str(e)[:60]}")
                        break

        # Training pairs: multiple sections
        instructions = [
            f"Explain {topic}.",
            f"What does the vault know about {topic}?",
            f"Summarize the technical content on {topic}.",
        ]
        for idx, section in enumerate([text[i:i+3000] for i in range(0, min(len(text), 15000), 3000)]):
            training_pairs.append({
                "instruction": instructions[idx % 3],
                "input": "",
                "output": section,
                "metadata": {
                    "source": f"gemini_inbox/{fp.name}",
                    "type": "gemini_collapse_model",
                    "section": idx,
                    "generated": datetime.now().isoformat(),
                    "id": hashlib.md5(f"{fp.name}:{idx}".encode()).hexdigest()[:12],
                }
            })

    # Append to training dataset
    TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    existing = sum(1 for _ in open(TRAINING_FILE, encoding="utf-8")) if TRAINING_FILE.exists() else 0
    with open(TRAINING_FILE, "a", encoding="utf-8") as f:
        for pair in training_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    final = await rag.stats()
    print(f"\n{'='*60}")
    print(f"RAG vectors added:    {total_rag}")
    print(f"Total RAG vectors:    {final.get('totalVectorCount', '?')}")
    print(f"Training pairs added: {len(training_pairs)}")
    print(f"Total in dataset:     {existing + len(training_pairs)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
