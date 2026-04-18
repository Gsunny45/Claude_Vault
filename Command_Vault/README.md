# Command_Vault

Orchestration hub for the Vault system. Fabric is installed here and routes patterns across all provider vaults.

## Fabric Plugin

The `unofficial-fabric-plugin` lives at `.obsidian/plugins/unofficial-fabric-plugin/`. After running `setup/install.sh` from the repo root, the compiled `main.js` will be downloaded into this directory automatically.

## Plugin Settings (configure in Obsidian)

| Setting | Description |
|---------|-------------|
| API URL | Fabric REST API endpoint (default: `http://localhost:8080`) |
| Output Folder | Where processed notes are saved |
| YouTube Detection | Auto-detect YT links in notes |
| Tavily Search | Web search integration (requires Tavily API key) |

## Usage

1. Open this vault in Obsidian
2. Enable **Unofficial Fabric Integration** under Settings → Community Plugins
3. Run Fabric server: `fabric --serve`
4. Use the Fabric panel (ribbon icon) to process notes
