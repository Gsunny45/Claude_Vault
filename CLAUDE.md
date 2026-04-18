# Vault Orchestration System — Claude Code Guide

## What This Repo Is

Five Obsidian vaults unified under a Fabric AI orchestration layer. Each vault opens independently in Obsidian and is pre-configured for a specific AI provider.

## Vault Map

| Directory | Purpose |
|-----------|---------|
| `Command_Vault/` | **Primary hub.** Hosts the Fabric harness agent plugin. Run `fabric --serve` and open this vault to orchestrate work across providers. |
| `Claude_Vault/` | Anthropic Claude provider vault |
| `Gemini_Vault/` | Google Gemini provider vault |
| `Local_Vault/` | Local models via Ollama or compatible server |
| `RAG_Vault/` | Retrieval-Augmented Generation vault |

## Key Files

- `setup/install.sh` — installs Fabric and downloads the plugin binary into `Command_Vault`
- `Command_Vault/.obsidian/plugins/unofficial-fabric-plugin/` — plugin home (manifest + styles committed; `main.js` fetched by install script)

## First-Time Setup

```bash
bash setup/install.sh
fabric --setup        # configure AI providers
fabric --serve        # start REST API (default: http://localhost:8080)
```

Then open `Command_Vault` in Obsidian and enable **Unofficial Fabric Integration** under Settings → Community Plugins.

## Provider Vaults

Each provider vault uses the same Obsidian interface. To add the Fabric plugin to a provider vault, copy `Command_Vault/.obsidian/plugins/unofficial-fabric-plugin/` into the target vault's `.obsidian/plugins/` directory after running the install script.

## Dependencies

- [danielmiessler/fabric](https://github.com/danielmiessler/fabric) — AI orchestration framework (Go-based)
- [chasebank87/unofficial-fabric-plugin](https://github.com/chasebank87/unofficial-fabric-plugin) — Obsidian harness agent (v1.3.3)
- Obsidian ≥ 1.6.5
