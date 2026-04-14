#!/usr/bin/env python3
"""
Test script for RAG pipeline.
- Loads config
- Tests Pinecone connection (stats endpoint)
- Tests embedding with Gemini
- Tests a small upsert (1 chunk) and query cycle
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from rag import PineconeRAG, PINECONE_API_KEY, PINECONE_HOST


async def main():
    print("=" * 70)
    print("RAG Pipeline Test")
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

    # --- 3. Test Pinecone Connection (stats) ---
    print("\n[3] Pinecone Connection Test (stats endpoint)")
    try:
        stats = await rag.stats()
        print(f"    Status:             OK")
        if "status" in stats and stats["status"] != "error":
            print(f"    Response:           {stats}")
        else:
            print(f"    Response:           {stats}")
    except Exception as e:
        print(f"    ERROR:              {e}")
        return

    # --- 4. Test Embedding with Gemini ---
    print("\n[4] Gemini Embedding Test")
    test_text = "This is a test string for embedding."
    try:
        embeddings = await rag._embed([test_text])
        print(f"    Status:             OK")
        print(f"    Text:               '{test_text}'")
        print(f"    Embedding dim:      {len(embeddings[0]) if embeddings else 0}")
        print(f"    First 5 values:     {embeddings[0][:5] if embeddings else []}")
    except Exception as e:
        print(f"    ERROR:              {e}")
        return

    # --- 5. Test Chunking ---
    print("\n[5] Chunking Test")
    sample_doc = """
    This is a sample document about the RAG pipeline.

    The RAG pipeline is a retrieval-augmented generation system that combines
    the power of vector search with large language models. It works in two phases:

    1. Ingestion: Documents are chunked and embedded into vectors, then stored in Pinecone.
    2. Query: User questions are embedded and matched against stored vectors to retrieve context.

    This allows the LLM to have access to domain-specific knowledge without fine-tuning.
    """ * 2  # Repeat to get more tokens

    chunks = rag.chunk_text(sample_doc, source="test_doc.md")
    print(f"    Text length:        {len(sample_doc)} chars")
    print(f"    Chunks created:     {len(chunks)}")
    if chunks:
        print(f"    First chunk tokens: {chunks[0]['token_count']}")
        print(f"    First chunk ID:     {chunks[0]['id']}")

    # --- 6. Test Upsert ---
    print("\n[6] Upsert Test (1 chunk)")
    try:
        test_chunk = {
            "id": "test_chunk_001",
            "text": test_text,
            "source": "test_rag.py",
            "token_count": 10,
            "chunk_index": 0,
        }
        upserted = await rag.upsert([test_chunk])
        print(f"    Status:             OK")
        print(f"    Chunks upserted:    {upserted}")
    except Exception as e:
        print(f"    ERROR:              {e}")
        return

    # --- 7. Test Query/Retrieve ---
    print("\n[7] Query/Retrieve Test")
    query = "What is the RAG pipeline?"
    try:
        results = await rag.retrieve(query, top_k=3)
        print(f"    Status:             OK")
        print(f"    Query:              '{query}'")
        print(f"    Results returned:   {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"\n    Result {i}:")
            print(f"      Score:            {result.score:.4f}")
            print(f"      Source:           {result.source}")
            print(f"      Text preview:     {result.text[:60]}...")
    except Exception as e:
        print(f"    ERROR:              {e}")
        return

    print("\n" + "=" * 70)
    print("RAG Pipeline Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
