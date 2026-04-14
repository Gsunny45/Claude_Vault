"""
RAG module — Pinecone-backed retrieval-augmented generation.

Flow:
  1. Ingest: document → chunk → embed (via provider) → upsert to Pinecone
  2. Query: user message → embed → top-k similar chunks → inject into prompt
  3. Chat pipeline calls retrieve() before sending to any LLM

Embedding strategy:
  - Primary: Gemini gemini-embedding-001 (free, 768-dim)
  - Fallback: OpenRouter or local tiktoken-based sparse (degraded)
"""

from __future__ import annotations
import hashlib
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx
import tiktoken

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "orchestrator-rag")
PINECONE_HOST = os.getenv("PINECONE_HOST", "")  # e.g. "https://orchestrator-rag-abc123.svc.aped-1234.pinecone.io"

# Embedding config
EMBED_MODEL = "gemini-embedding-001"  # Confirmed available on your key
EMBED_DIM = 768
CHUNK_SIZE = 512       # tokens per chunk
CHUNK_OVERLAP = 64     # token overlap between chunks
TOP_K = 5              # chunks to retrieve


@dataclass
class ChunkResult:
    text: str
    score: float
    source: str
    chunk_id: str


# ---------------------------------------------------------------------------
# Pinecone client (REST — no heavy SDK dependency at import time)
# ---------------------------------------------------------------------------

class PineconeRAG:
    def __init__(self):
        self.api_key = PINECONE_API_KEY
        self.index_name = PINECONE_INDEX_NAME
        self.host = PINECONE_HOST
        self._tokenizer = tiktoken.get_encoding("cl100k_base")

    @property
    def available(self) -> bool:
        return bool(self.api_key and self.host)

    # --- Embedding via Gemini free API ---

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts using Gemini's free embedding model."""
        from config import settings
        gemini_key = settings.api_key_for("gemini")
        if not gemini_key:
            raise RuntimeError("Gemini API key required for embeddings")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBED_MODEL}:batchEmbedContents?key={gemini_key}"

        requests_body = [
            {"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": t}]}}
            for t in texts
        ]

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json={"requests": requests_body})
            resp.raise_for_status()
            data = resp.json()

        return [e["values"] for e in data["embeddings"]]

    # --- Chunking ---

    def chunk_text(self, text: str, source: str = "") -> list[dict]:
        """Split text into overlapping token-based chunks."""
        tokens = self._tokenizer.encode(text)
        chunks = []
        start = 0
        idx = 0

        while start < len(tokens):
            end = min(start + CHUNK_SIZE, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self._tokenizer.decode(chunk_tokens)

            # Generate deterministic ID
            chunk_hash = hashlib.md5(f"{source}:{start}".encode()).hexdigest()[:12]
            chunk_id = f"{source[:40]}_{chunk_hash}"

            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "source": source,
                "token_count": len(chunk_tokens),
                "chunk_index": idx,
            })

            start += CHUNK_SIZE - CHUNK_OVERLAP
            idx += 1

        return chunks

    # --- Pinecone operations ---

    def _headers(self) -> dict:
        return {
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def upsert(self, chunks: list[dict]) -> int:
        """Embed chunks and upsert to Pinecone. Returns count upserted."""
        if not self.available:
            raise RuntimeError("Pinecone not configured")

        texts = [c["text"] for c in chunks]
        embeddings = await self._embed(texts)

        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append({
                "id": chunk["id"],
                "values": embedding,
                "metadata": {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                },
            })

        # Batch upsert (Pinecone max 100 per request)
        upserted = 0
        for i in range(0, len(vectors), 100):
            batch = vectors[i:i + 100]
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.host}/vectors/upsert",
                    headers=self._headers(),
                    json={"vectors": batch, "namespace": "default"},
                )
                resp.raise_for_status()
                upserted += resp.json().get("upsertedCount", len(batch))

        log.info("Upserted %d chunks to Pinecone", upserted)
        return upserted

    async def retrieve(self, query: str, top_k: int = TOP_K) -> list[ChunkResult]:
        """Embed query and retrieve top-k similar chunks."""
        if not self.available:
            return []

        try:
            embeddings = await self._embed([query])
            query_vec = embeddings[0]
        except Exception as e:
            log.warning("Embedding failed, skipping RAG: %s", e)
            return []

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{self.host}/query",
                    headers=self._headers(),
                    json={
                        "vector": query_vec,
                        "topK": top_k,
                        "includeMetadata": True,
                        "namespace": "default",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            log.warning("Pinecone query failed: %s", e)
            return []

        results = []
        for match in data.get("matches", []):
            meta = match.get("metadata", {})
            results.append(ChunkResult(
                text=meta.get("text", ""),
                score=match.get("score", 0),
                source=meta.get("source", ""),
                chunk_id=match.get("id", ""),
            ))

        return results

    async def delete_by_source(self, source: str) -> None:
        """Delete all chunks from a specific source document."""
        if not self.available:
            return
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.host}/vectors/delete",
                headers=self._headers(),
                json={
                    "filter": {"source": {"$eq": source}},
                    "namespace": "default",
                },
            )
            resp.raise_for_status()

    async def stats(self) -> dict:
        """Get index stats."""
        if not self.available:
            return {"status": "not_configured"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.host}/describe_index_stats",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            return {"status": "error", "detail": str(e)}


def build_rag_context(chunks: list[ChunkResult]) -> str:
    """Format retrieved chunks into a system-level context block."""
    if not chunks:
        return ""

    lines = ["[Retrieved context from knowledge base]\n"]
    for i, c in enumerate(chunks, 1):
        source_tag = f" (source: {c.source})" if c.source else ""
        lines.append(f"--- Chunk {i}{source_tag} [relevance: {c.score:.2f}] ---")
        lines.append(c.text.strip())
        lines.append("")

    lines.append("[End of retrieved context]\n")
    return "\n".join(lines)


# Singleton
rag = PineconeRAG()
