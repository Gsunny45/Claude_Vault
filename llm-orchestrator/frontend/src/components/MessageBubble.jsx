import React from "react";

function Badge({ type, label }) {
  return <span className={`badge ${type}`}>{label}</span>;
}

export default function MessageBubble({ message }) {
  const { role, content, meta } = message;

  return (
    <div className={`message ${role}`}>
      <div className="message-bubble">{content || "..."}</div>
      {role === "assistant" && meta && (
        <div className="message-meta">
          <span>{meta.provider}/{meta.model}</span>
          {meta.free_tier && <Badge type="free" label="free tier" />}
          {!meta.free_tier && <Badge type="paid" label="paid" />}
          {meta.is_fallback && <Badge type="fallback" label="fallback" />}
          {meta.rag_used && <Badge type="rag" label="RAG" />}
        </div>
      )}
    </div>
  );
}
