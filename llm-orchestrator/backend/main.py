"""
LLM Orchestrator — FastAPI backend.
Endpoints:
  POST /api/chat          — non-streaming chat
  POST /api/chat/stream   — SSE streaming chat
  GET  /api/models        — list available models
  GET  /api/settings      — get current settings
  POST /api/settings      — update routing mode + BYO keys
  GET  /api/health        — health check
  --- RAG ---
  POST /api/rag/ingest    — upload document → chunk → embed → Pinecone
  POST /api/rag/query     — test retrieval without chat
  GET  /api/rag/stats     — Pinecone index stats
  DELETE /api/rag/source  — remove a document's chunks
"""

from __future__ import annotations
import json
import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from config import settings, MODEL_CATALOG, PROVIDERS
from models import (
    ChatRequest, ChatResponse, ChatResponseMeta,
    SettingsPayload, RoutingMode,
)
from router import router as llm_router
from crypto import apply_user_keys_to_settings, save_user_keys
from rag import rag, build_rag_context
from registry import registry, bootstrap_registry, ServiceEntry, RegistryManager

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    apply_user_keys_to_settings()
    bootstrap_registry()
    log.info("LLM Orchestrator started — mode=%s, rag=%s, registry=%d services",
             settings.routing_mode, rag.available, len(registry.services))
    yield


app = FastAPI(title="LLM Orchestrator", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper: inject RAG context into messages
# ---------------------------------------------------------------------------

async def _maybe_inject_rag(messages: list[dict], use_rag: bool) -> tuple[list[dict], list]:
    """If RAG is enabled and available, retrieve context and prepend as system message."""
    if not use_rag or not rag.available:
        return messages, []

    # Use the last user message as the retrieval query
    user_msgs = [m for m in messages if m["role"] == "user"]
    if not user_msgs:
        return messages, []

    query = user_msgs[-1]["content"]
    chunks = await rag.retrieve(query)
    if not chunks:
        return messages, []

    context_block = build_rag_context(chunks)
    rag_system = {"role": "system", "content": context_block}

    # Insert RAG context as first system message
    augmented = [rag_system] + messages
    return augmented, chunks


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "routing_mode": settings.routing_mode,
        "rag_available": rag.available,
    }


# ---------------------------------------------------------------------------
# Models catalog
# ---------------------------------------------------------------------------

@app.get("/api/models")
async def list_models():
    result = []
    for entry in MODEL_CATALOG:
        provider = entry["provider"]
        has_key = bool(settings.api_key_for(provider))
        result.append({**entry, "available": has_key})
    return {"models": result}


# ---------------------------------------------------------------------------
# Chat — non-streaming
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    messages = [{"role": m.role.value, "content": m.content} for m in req.messages]
    messages, rag_chunks = await _maybe_inject_rag(messages, req.use_rag)
    mode = req.routing_mode or RoutingMode(settings.routing_mode)

    is_fallback = False
    try:
        client, model_id, is_free = llm_router.route(
            model=req.model, provider=req.provider, mode=mode,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        resp = await client.chat(
            messages, model_id,
            temperature=req.temperature, max_tokens=req.max_tokens,
        )
    except Exception as exc:
        log.warning("Primary failed (%s/%s): %s — trying fallback", client.provider_name, model_id, exc)
        try:
            client, model_id, is_free = llm_router._try_fallbacks()
            resp = await client.chat(
                messages, model_id,
                temperature=req.temperature, max_tokens=req.max_tokens,
            )
            is_fallback = True
        except Exception:
            raise HTTPException(status_code=502, detail=f"All providers failed: {exc}")

    return ChatResponse(
        content=resp.content,
        meta=ChatResponseMeta(
            provider=resp.provider, model=resp.model,
            is_fallback=is_fallback, free_tier=resp.is_free,
            tokens_used=resp.tokens_used,
        ),
    )


# ---------------------------------------------------------------------------
# Chat — SSE streaming
# ---------------------------------------------------------------------------

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    messages = [{"role": m.role.value, "content": m.content} for m in req.messages]
    messages, rag_chunks = await _maybe_inject_rag(messages, req.use_rag)
    mode = req.routing_mode or RoutingMode(settings.routing_mode)

    try:
        client, model_id, is_free = llm_router.route(
            model=req.model, provider=req.provider, mode=mode,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    async def event_generator():
        is_fallback = False
        active_client = client
        active_model = model_id
        active_free = is_free

        try:
            stream = active_client.chat_stream(
                messages, active_model,
                temperature=req.temperature, max_tokens=req.max_tokens,
            )
        except Exception as exc:
            log.warning("Stream init failed: %s — fallback", exc)
            try:
                active_client, active_model, active_free = llm_router._try_fallbacks()
                stream = active_client.chat_stream(
                    messages, active_model,
                    temperature=req.temperature, max_tokens=req.max_tokens,
                )
                is_fallback = True
            except Exception:
                yield f"data: {json.dumps({'error': str(exc), 'done': True})}\n\n"
                return

        try:
            async for chunk in stream:
                payload = {
                    "delta": chunk.delta,
                    "done": chunk.done,
                    "meta": {
                        "provider": chunk.provider or active_client.provider_name,
                        "model": chunk.model or active_model,
                        "is_fallback": is_fallback,
                        "free_tier": chunk.is_free or active_free,
                        "rag_used": bool(rag_chunks),
                    },
                }
                yield f"data: {json.dumps(payload)}\n\n"
                if chunk.done:
                    return
        except Exception as exc:
            log.error("Stream error: %s", traceback.format_exc())
            yield f"data: {json.dumps({'error': str(exc), 'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

@app.get("/api/settings")
async def get_settings():
    return {
        "routing_mode": settings.routing_mode,
        "rag_available": rag.available,
        "keys": {
            "openrouter": bool(settings.openrouter_api_key),
            "openai": bool(settings.user_openai_key or settings.openai_api_key),
            "gemini": bool(settings.user_gemini_key or settings.gemini_api_key),
            "groq": bool(settings.user_groq_key or settings.groq_api_key),
            "deepseek": bool(settings.user_deepseek_key or settings.deepseek_api_key),
            "perplexity": bool(settings.user_perplexity_key or settings.perplexity_api_key),
            "mistral": bool(settings.user_mistral_key or settings.mistral_api_key),
            "grok": bool(settings.user_grok_key or settings.grok_api_key),
        },
    }


@app.post("/api/settings")
async def update_settings(payload: SettingsPayload):
    if payload.routing_mode:
        settings.routing_mode = payload.routing_mode.value

    if payload.keys:
        keys_to_save = {}
        for provider in ("openai", "gemini", "mistral", "grok", "groq", "deepseek", "perplexity"):
            val = getattr(payload.keys, f"{provider}_key", None)
            if val is not None:
                setattr(settings, f"user_{provider}_key", val)
                keys_to_save[f"{provider}_key"] = val
        if keys_to_save:
            save_user_keys(keys_to_save)

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# RAG endpoints
# ---------------------------------------------------------------------------

@app.post("/api/rag/ingest")
async def rag_ingest(
    file: UploadFile = File(...),
    source_name: Optional[str] = Form(None),
):
    """Upload a text file → chunk → embed → upsert to Pinecone."""
    if not rag.available:
        raise HTTPException(status_code=503, detail="Pinecone not configured. Set PINECONE_API_KEY and PINECONE_HOST.")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Only UTF-8 text files supported (.txt, .md, .csv, etc.)")

    source = source_name or file.filename or "unknown"
    chunks = rag.chunk_text(text, source=source)

    if not chunks:
        raise HTTPException(status_code=400, detail="File produced no chunks (empty or too short)")

    try:
        count = await rag.upsert(chunks)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Pinecone upsert failed: {e}")

    return {
        "status": "ok",
        "source": source,
        "chunks_created": len(chunks),
        "vectors_upserted": count,
    }


class RagQueryRequest(BaseModel):
    query: str
    top_k: int = 5


@app.post("/api/rag/query")
async def rag_query(req: RagQueryRequest):
    """Test retrieval — returns top-k chunks without calling an LLM."""
    if not rag.available:
        raise HTTPException(status_code=503, detail="Pinecone not configured")

    chunks = await rag.retrieve(req.query, top_k=req.top_k)
    return {
        "results": [
            {"text": c.text, "score": c.score, "source": c.source, "id": c.chunk_id}
            for c in chunks
        ]
    }


@app.get("/api/rag/stats")
async def rag_stats():
    """Pinecone index stats."""
    return await rag.stats()


class RagDeleteRequest(BaseModel):
    source: str


@app.delete("/api/rag/source")
async def rag_delete_source(req: RagDeleteRequest):
    """Delete all chunks from a specific source document."""
    if not rag.available:
        raise HTTPException(status_code=503, detail="Pinecone not configured")
    await rag.delete_by_source(req.source)
    return {"status": "ok", "deleted_source": req.source}


# ---------------------------------------------------------------------------
# Registry endpoints
# ---------------------------------------------------------------------------

@app.get("/api/registry")
async def list_registry(type: Optional[str] = None, category: Optional[str] = None):
    """List all services, optionally filtered by type or category."""
    if type:
        services = registry.get_by_type(type)
    elif category:
        services = registry.get_by_category(category)
    else:
        services = registry.list_all()
    return {"services": [s.model_dump(exclude={"api_key"}) for s in services]}


@app.get("/api/registry/summary")
async def registry_summary():
    """Budget summary: total available, free count, expiring soon."""
    return registry.summary().model_dump()


@app.post("/api/registry")
async def update_registry(entry: ServiceEntry):
    """Add or update a service in the registry."""
    # Never store raw API keys through this endpoint
    entry.api_key = None
    updated = registry.add_or_update(entry)
    return {"status": "ok", "service": updated.model_dump(exclude={"api_key"})}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
