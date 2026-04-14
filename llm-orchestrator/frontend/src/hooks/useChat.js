import { useState, useRef, useCallback } from "react";
import { streamChat } from "../api";

/**
 * useChat hook — manages conversation state and streaming.
 */
export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const controllerRef = useRef(null);

  const send = useCallback((userText, { model, routingMode, useRag } = {}) => {
    if (!userText.trim() || isStreaming) return;

    const userMsg = { role: "user", content: userText };
    const assistantMsg = { role: "assistant", content: "", meta: null };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    // Build full message history for the API
    const apiMessages = [...messages, userMsg].map((m) => ({
      role: m.role,
      content: m.content,
    }));

    controllerRef.current = streamChat({
      messages: apiMessages,
      model,
      routingMode,
      useRag,
      onDelta: (delta, meta) => {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          last.content += delta;
          if (meta) last.meta = meta;
          return updated;
        });
      },
      onDone: (meta) => {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (meta) last.meta = { ...last.meta, ...meta };
          return updated;
        });
        setIsStreaming(false);
      },
      onError: (error) => {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          last.content += `\n\n[Error: ${error}]`;
          last.meta = { ...last.meta, error: true };
          return updated;
        });
        setIsStreaming(false);
      },
    });
  }, [messages, isStreaming]);

  const stop = useCallback(() => {
    controllerRef.current?.abort();
    setIsStreaming(false);
  }, []);

  const clear = useCallback(() => {
    controllerRef.current?.abort();
    setMessages([]);
    setIsStreaming(false);
  }, []);

  return { messages, isStreaming, send, stop, clear };
}
