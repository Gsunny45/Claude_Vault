import React, { useState, useRef } from "react";
import Chat from "./components/Chat";
import ModelPicker from "./components/ModelPicker";
import Settings from "./components/Settings";
import { useChat } from "./hooks/useChat";
import { uploadDocument } from "./api";

export default function App() {
  const { messages, isStreaming, send, stop, clear } = useChat();
  const [selectedModel, setSelectedModel] = useState("");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [ragEnabled, setRagEnabled] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const fileInputRef = useRef(null);

  const handleSend = (text) => {
    send(text, { model: selectedModel || undefined, useRag: ragEnabled });
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadStatus("");
    try {
      const result = await uploadDocument(file);
      setUploadStatus(`Ingested "${result.source}" → ${result.chunks_created} chunks`);
      setTimeout(() => setUploadStatus(""), 5000);
    } catch (err) {
      setUploadStatus(`Upload failed: ${err.message}`);
    }
    setUploading(false);
    e.target.value = "";
  };

  return (
    <div className="app">
      <div className="topbar">
        <h1>LLM Orchestrator</h1>
        <div className="topbar-right">
          <ModelPicker value={selectedModel} onChange={setSelectedModel} />

          <label style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={ragEnabled}
              onChange={(e) => setRagEnabled(e.target.checked)}
            />
            RAG
          </label>

          <button
            className="btn btn-secondary"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            style={{ fontSize: 12 }}
            title="Upload document to knowledge base"
          >
            {uploading ? "Uploading..." : "Upload Doc"}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.csv,.json,.py,.js,.html,.xml,.yaml,.yml,.log"
            onChange={handleFileUpload}
            style={{ display: "none" }}
          />

          <button
            className="btn btn-secondary"
            onClick={clear}
            style={{ fontSize: 12 }}
          >
            Clear
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => setSettingsOpen(true)}
            style={{ fontSize: 12 }}
          >
            Settings
          </button>
        </div>
      </div>

      {uploadStatus && (
        <div style={{
          padding: "6px 20px",
          fontSize: 12,
          background: uploadStatus.includes("failed") ? "#2d1215" : "#0d2818",
          color: uploadStatus.includes("failed") ? "#f87171" : "#4ade80",
          textAlign: "center",
        }}>
          {uploadStatus}
        </div>
      )}

      <Chat
        messages={messages}
        isStreaming={isStreaming}
        onSend={handleSend}
        onStop={stop}
        onClear={clear}
        selectedModel={selectedModel}
      />

      <Settings open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}
