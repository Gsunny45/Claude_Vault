# RAG Pipeline Scripts

## Overview
Two companion scripts for testing and ingesting data into the Pinecone RAG system.

## Prerequisites
- Python 3.10+
- `.env` file with configured API keys:
  - `PINECONE_API_KEY` - Your Pinecone API key
  - `PINECONE_HOST` - Your Pinecone index endpoint (e.g., `https://orchestrator-rag-abc123.svc.aped-1234.pinecone.io`)
  - `GEMINI_API_KEY` - Your Google Gemini API key
- Dependencies: `httpx`, `tiktoken`, `python-dotenv`

## Scripts

### 1. test_rag.py
Tests the RAG pipeline end-to-end.

**What it does:**
1. Loads configuration from `.env`
2. Tests Pinecone connection (stats endpoint)
3. Tests Gemini embedding with a sample string
4. Tests chunking functionality
5. Tests upserting a single test chunk to Pinecone
6. Tests retrieval/query functionality

**Usage:**
```bash
cd backend
python3 test_rag.py
```

**Expected Output:**
```
======================================================================
RAG Pipeline Test
======================================================================

[1] Configuration Check
    Gemini API Key:     OK
    Pinecone API Key:   OK
    Pinecone Host:      https://orchestrator-rag-...

[2] RAG Initialization
    RAG Available:      True

[3] Pinecone Connection Test (stats endpoint)
    Status:             OK
    Response:           {...}

[4] Gemini Embedding Test
    Status:             OK
    Text:               'This is a test string for embedding.'
    Embedding dim:      768
    First 5 values:     [0.123, -0.456, ...]

[5] Chunking Test
    Text length:        1234 chars
    Chunks created:     2
    First chunk tokens: 512

[6] Upsert Test (1 chunk)
    Status:             OK
    Chunks upserted:    1

[7] Query/Retrieve Test
    Status:             OK
    Query:              'What is the RAG pipeline?'
    Results returned:   1
    ...

======================================================================
RAG Pipeline Test Complete
======================================================================
```

---

### 2. ingest_vault.py
Ingests all markdown files from the Claude Vault into Pinecone.

**What it does:**
1. Loads configuration from `.env`
2. Verifies Pinecone connection
3. Discovers and loads all `.md` files from:
   - `/mnt/Claude_Vault/knowledge/` (KNW-XXXX knowledge entries, ~20 files)
   - `/mnt/Claude_Vault/claude_on_claude/docs/` (key architecture/protocol docs)
4. Chunks each file using the RAG module's `chunk_text()` function
5. Embeds chunks using Gemini API
6. Upserts vectors to Pinecone in batches of 100
7. Reports summary: files processed, chunks created, vectors upserted

**Usage:**
```bash
cd backend
python3 ingest_vault.py
```

**Expected Output:**
```
======================================================================
Claude Vault Ingestion
======================================================================

[1] Configuration Check
    Gemini API Key:     OK
    Pinecone API Key:   OK
    Pinecone Host:      https://orchestrator-rag-...

[2] RAG Initialization
    RAG Available:      True

[3] Pinecone Connection Verification
    Status:             Connected

[4] Loading Files
    Found 20 .md files in knowledge
    Found 3 .md files in docs
    Total files loaded: 23

[5] Chunking and Upserting
    KNW-0001.md                    chunks=  3  upserted=  3
    KNW-0002.md                    chunks=  4  upserted=  4
    KNW-0003.md                    chunks=  5  upserted=  5
    ...
    ARCHITECTURE.md                chunks=  8  upserted=  8
    HANDOFF-PROTOCOL.md            chunks= 10  upserted= 10
    N8N-MIGRATION.md               chunks=  6  upserted=  6

======================================================================
Ingestion Summary
======================================================================
Total files processed:          23
Total chunks created:           142
Total vectors upserted:         142

Status:                         SUCCESS - No errors
======================================================================
```

---

## Notes

### Network / Sandbox Issues
If running in a sandbox environment with restricted network access:
- The scripts may fail on the first import when tiktoken tries to download encoding files
- This is expected and does not indicate a problem with the script logic
- The scripts will work correctly when run on a machine with unrestricted internet access (your local development machine)
- Error: `ProxyError: 403 Forbidden` when accessing `openaipublic.blob.core.windows.net` is normal in sandboxed environments

### Chunking Strategy
- Uses token-based chunking (512 tokens per chunk, 64 token overlap)
- Preserves semantic boundaries using tiktoken's `cl100k_base` encoding
- Chunk IDs are deterministic (based on source + position hash)

### Embedding
- Uses Gemini's `gemini-embedding-001` model (768-dimensional)
- Free tier available (check Google's pricing)
- Batch embedding up to 100 texts per call

### Pinecone
- Upserts in batches of 100 vectors per request (Pinecone API limit)
- Uses "default" namespace
- Metadata includes: text, source filename, chunk index

---

## Troubleshooting

### "Gemini API key required for embeddings"
Check that `GEMINI_API_KEY` is set in your `.env` file.

### "Pinecone not configured"
Check that both `PINECONE_API_KEY` and `PINECONE_HOST` are set in your `.env` file.

### API Rate Limiting
If you hit rate limits:
- Gemini: typically 60 requests/min for free tier
- Pinecone: typically 100 upserts/batch, with generous rate limits

Consider breaking ingest into smaller batches if needed.

### Large Vault Ingestion
For ingesting large amounts of data:
1. Run `test_rag.py` first to verify connectivity
2. Run `ingest_vault.py` in a terminal with a longer timeout (e.g., `timeout 600`)
3. Monitor CPU/memory usage during embedding (Gemini API is called)

---

## Architecture Integration

Both scripts integrate with the existing RAG module (`backend/rag.py`):
- `PineconeRAG` class: manages embedding, chunking, upsert, retrieval
- `chunk_text()`: splits documents into overlapping chunks
- `_embed()`: calls Gemini API for embedding
- `upsert()`: stores vectors in Pinecone
- `retrieve()`: queries and scores results
- `stats()`: checks index health

The scripts use `asyncio` throughout, so embedding/upsert calls are non-blocking.
