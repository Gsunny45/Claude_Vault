import React, { useState, useEffect } from "react";
import { fetchSettings, saveSettings } from "../api";

const PROVIDERS = [
  { key: "openai", label: "OpenAI", placeholder: "sk-..." },
  { key: "gemini", label: "Google Gemini", placeholder: "AIza..." },
  { key: "groq", label: "Groq", placeholder: "gsk_..." },
  { key: "deepseek", label: "DeepSeek", placeholder: "sk-..." },
  { key: "perplexity", label: "Perplexity", placeholder: "pplx-..." },
  { key: "mistral", label: "Mistral", placeholder: "..." },
  { key: "grok", label: "xAI Grok", placeholder: "xai-..." },
];

export default function Settings({ open, onClose }) {
  const [routingMode, setRoutingMode] = useState("FREE_FIRST");
  const [keys, setKeys] = useState({});
  const [keyStatus, setKeyStatus] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    fetchSettings().then((data) => {
      setRoutingMode(data.routing_mode || "FREE_FIRST");
      setKeyStatus(data.keys || {});
    });
  }, [open]);

  const handleSave = async () => {
    setSaving(true);
    const payload = { routing_mode: routingMode };
    const hasKeys = Object.values(keys).some((v) => v);
    if (hasKeys) {
      payload.keys = {
        openai_key: keys.openai || null,
        gemini_key: keys.gemini || null,
        mistral_key: keys.mistral || null,
        grok_key: keys.grok || null,
      };
    }
    await saveSettings(payload);
    setSaving(false);
    onClose();
  };

  if (!open) return null;

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-panel" onClick={(e) => e.stopPropagation()}>
        <h2>Settings</h2>

        <label>Routing Mode</label>
        <select
          value={routingMode}
          onChange={(e) => setRoutingMode(e.target.value)}
        >
          <option value="FREE_FIRST">Free First</option>
          <option value="CHEAPEST_PAID">Cheapest Paid</option>
          <option value="VENDOR_PINNED">Vendor Pinned</option>
        </select>

        <h3 style={{ marginTop: 20, fontSize: 15 }}>API Keys (BYO)</h3>
        <p style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 8 }}>
          Keys are encrypted and stored locally. Never sent to the browser.
        </p>

        {PROVIDERS.map((p) => (
          <div key={p.key}>
            <label>
              {p.label}
              {keyStatus[p.key] && (
                <span style={{ color: "var(--green)", marginLeft: 8, fontSize: 11 }}>
                  configured
                </span>
              )}
            </label>
            <input
              type="password"
              placeholder={p.placeholder}
              value={keys[p.key] || ""}
              onChange={(e) =>
                setKeys((prev) => ({ ...prev, [p.key]: e.target.value }))
              }
            />
          </div>
        ))}

        <div className="settings-actions">
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>
    </div>
  );
}
