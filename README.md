# Vault Orchestration System

AI-provider vaults unified under a single Fabric orchestration layer.

## Architecture

```
Vault Orchestration
├── Command_Vault/     ← Fabric harness agent hub (primary home)
├── Claude_Vault/      ← Anthropic Claude provider
├── Gemini_Vault/      ← Google Gemini provider
├── Local_Vault/       ← Local models (Ollama, etc.)
└── RAG_Vault/         ← Retrieval-Augmented Generation
```

All provider vaults share the same Obsidian interface. Command_Vault is the orchestration center — it hosts the Fabric plugin and routes work across providers.

## Prerequisites

1. **Fabric** — install before anything else:
   ```bash
   bash setup/install.sh
   ```

2. **Obsidian** ≥ 1.6.5

## Plugin

The [unofficial-fabric-plugin](https://github.com/chasebank87/unofficial-fabric-plugin) lives in `Command_Vault`. It connects to Fabric's REST API and lets you run patterns against notes, clipboard content, YouTube links, and Tavily search results.

## Setup

```bash
# 1. Install Fabric + download plugin binary
bash setup/install.sh

# 2. Open Command_Vault in Obsidian
# 3. Enable "Unofficial Fabric Integration" in Community Plugins
# 4. Configure API URL + keys in plugin settings
```

## Provider Vaults

Each vault is independently openable in Obsidian and pre-configured for its provider. They are designed to be used alongside Command_Vault, which handles the Fabric orchestration layer.

| Vault | Provider | Notes |
|-------|----------|-------|
| Claude_Vault | Anthropic Claude | Default: claude-sonnet |
| Gemini_Vault | Google Gemini | Default: gemini-pro |
| Local_Vault | Ollama / local | Requires local model server |
| RAG_Vault | Retrieval-Augmented | Requires vector store config |
