import React, { useRef, useEffect, useState } from "react";
import MessageBubble from "./MessageBubble";

export default function Chat({ messages, isStreaming, onSend, onStop, onClear, selectedModel }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll on new content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = () => {
    if (!input.trim() || isStreaming) return;
    onSend(input);
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "42px";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea
  const handleInput = (e) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "42px";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  };

  return (
    <>
      <div className="chat-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <h2>LLM Orchestrator</h2>
            <p>
              Multi-provider chat with automatic routing.
              <br />
              Select a model above or let the router decide.
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="input-bar">
        <div className="input-bar-inner">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Send a message..."
            rows={1}
          />
          {isStreaming ? (
            <button onClick={onStop}>Stop</button>
          ) : (
            <button onClick={handleSubmit} disabled={!input.trim()}>
              Send
            </button>
          )}
        </div>
      </div>
    </>
  );
}
