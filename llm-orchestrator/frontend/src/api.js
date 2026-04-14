/**
 * API client — talks to the FastAPI orchestrator backend.
 */

const BASE = "/api";

export async function fetchModels() {
  const res = await fetch(`${BASE}/models`);
  if (!res.ok) throw new Error("Failed to fetch models");
  return res.json();
}

export async function fetchSettings() {
  const res = await fetch(`${BASE}/settings`);
  if (!res.ok) throw new Error("Failed to fetch settings");
  return res.json();
}

export async function saveSettings(payload) {
  const res = await fetch(`${BASE}/settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to save settings");
  return res.json();
}

/**
 * Stream a chat completion via SSE.
 * @param {Object} params
 * @param {Array}  params.messages
 * @param {string} params.model
 * @param {string} params.routingMode
 * @param {function} params.onDelta  — called with (deltaText, meta)
 * @param {function} params.onDone   — called with final meta
 * @param {function} params.onError  — called with error string
 * @returns {AbortController}
 */
export async function uploadDocument(file, sourceName) {
  const form = new FormData();
  form.append("file", file);
  if (sourceName) form.append("source_name", sourceName);
  const res = await fetch(`${BASE}/rag/ingest`, { method: "POST", body: form });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchRagStats() {
  const res = await fetch(`${BASE}/rag/stats`);
  return res.json();
}

export function streamChat({ messages, model, routingMode, useRag, onDelta, onDone, onError }) {
  const controller = new AbortController();

  const body = {
    messages,
    stream: true,
    temperature: 0.7,
    max_tokens: 4096,
    use_rag: !!useRag,
  };
  if (model) body.model = model;
  if (routingMode) body.routing_mode = routingMode;

  fetch(`${BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const text = await res.text();
        onError?.(text || `HTTP ${res.status}`);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;
          try {
            const chunk = JSON.parse(raw);
            if (chunk.error) {
              onError?.(chunk.error);
              return;
            }
            if (chunk.delta) {
              onDelta?.(chunk.delta, chunk.meta);
            }
            if (chunk.done) {
              onDone?.(chunk.meta);
              return;
            }
          } catch {
            // skip malformed chunks
          }
        }
      }
      // If stream ended without done signal
      onDone?.({});
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        onError?.(err.message);
      }
    });

  return controller;
}
