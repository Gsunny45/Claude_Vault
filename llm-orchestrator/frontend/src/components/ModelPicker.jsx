import React, { useState, useEffect } from "react";
import { fetchModels } from "../api";

export default function ModelPicker({ value, onChange }) {
  const [models, setModels] = useState([]);

  useEffect(() => {
    fetchModels()
      .then((data) => setModels(data.models || []))
      .catch(() => setModels([]));
  }, []);

  const available = models.filter((m) => m.available);

  return (
    <select
      className="model-select"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    >
      <option value="">Auto (router decides)</option>
      {available.map((m) => (
        <option key={m.id} value={m.id}>
          {m.label} {m.free ? "  ✦ free" : ""}
        </option>
      ))}
    </select>
  );
}
