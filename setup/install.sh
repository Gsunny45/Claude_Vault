#!/usr/bin/env bash
set -euo pipefail

PLUGIN_VERSION="1.3.3"
PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)/Command_Vault/.obsidian/plugins/unofficial-fabric-plugin"
PLUGIN_REPO="chasebank87/unofficial-fabric-plugin"

echo "==> Vault Orchestration Setup"
echo ""

# ── 1. Fabric ─────────────────────────────────────────────────────────────────
echo "[1/2] Checking Fabric installation..."

if command -v fabric &>/dev/null; then
  echo "    fabric $(fabric --version 2>/dev/null || echo 'installed') — OK"
else
  echo "    Fabric not found. Installing via Go..."

  if ! command -v go &>/dev/null; then
    echo ""
    echo "    ERROR: Go is required to install Fabric."
    echo "    Install Go from https://go.dev/dl/ then re-run this script."
    echo ""
    echo "    Alternatively, install Fabric via:"
    echo "      macOS:   brew install danielmiessler/fabric/fabric"
    echo "      Arch:    yay -S fabric-ai"
    echo "      Windows: winget install danielmiessler.fabric"
    echo "      Docker:  docker pull ghcr.io/danielmiessler/fabric:latest"
    exit 1
  fi

  go install github.com/danielmiessler/fabric/cmd/fabric@latest
  echo "    Fabric installed. Run 'fabric --setup' to configure providers."
fi

echo ""

# ── 2. Plugin binary ──────────────────────────────────────────────────────────
echo "[2/2] Installing unofficial-fabric-plugin v${PLUGIN_VERSION}..."

MAIN_JS="${PLUGIN_DIR}/main.js"

if [[ -f "$MAIN_JS" ]]; then
  echo "    main.js already present — skipping download."
else
  BASE_URL="https://github.com/${PLUGIN_REPO}/releases/download/${PLUGIN_VERSION}"

  echo "    Downloading main.js..."
  curl -fsSL "${BASE_URL}/main.js" -o "${MAIN_JS}"

  echo "    Verifying download..."
  if [[ ! -s "$MAIN_JS" ]]; then
    echo "    ERROR: Download failed or file is empty."
    rm -f "$MAIN_JS"
    exit 1
  fi

  echo "    Plugin installed at: ${PLUGIN_DIR}"
fi

echo ""
echo "==> Setup complete."
echo ""
echo "Next steps:"
echo "  1. Run 'fabric --setup' to configure your AI providers (if not done)"
echo "  2. Start the Fabric server: fabric --serve"
echo "  3. Open Command_Vault in Obsidian"
echo "  4. Enable 'Unofficial Fabric Integration' under Settings → Community Plugins"
echo "  5. Configure the API URL (default: http://localhost:8080) in plugin settings"
echo ""
