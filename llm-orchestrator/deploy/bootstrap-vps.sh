#!/bin/bash
# ============================================================
# LLM Orchestrator — VPS Bootstrap Script
# Run this ONCE on a fresh Hostinger VPS via SSH.
#
# What it does:
#   1. Installs Docker + Docker Compose
#   2. Creates project directory
#   3. Copies the deploy config
#   4. Launches the full stack
#
# Usage:
#   ssh root@89.117.139.137
#   curl -sSL https://raw.githubusercontent.com/YOUR_REPO/deploy/bootstrap-vps.sh | bash
#   OR: copy this file to the VPS and run: bash bootstrap-vps.sh
# ============================================================

set -euo pipefail

echo "=== LLM Orchestrator VPS Bootstrap ==="
echo "Host: $(hostname)"
echo "OS:   $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 || uname -a)"
echo ""

# --- 1. Install Docker ---
if ! command -v docker &> /dev/null; then
    echo "[1/5] Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "  Docker installed: $(docker --version)"
else
    echo "[1/5] Docker already installed: $(docker --version)"
fi

# --- 2. Install Docker Compose plugin ---
if ! docker compose version &> /dev/null; then
    echo "[2/5] Installing Docker Compose plugin..."
    apt-get update -qq && apt-get install -y -qq docker-compose-plugin
else
    echo "[2/5] Docker Compose already available: $(docker compose version)"
fi

# --- 3. Create project directory ---
PROJECT_DIR=/opt/llm-orchestrator
echo "[3/5] Setting up project at $PROJECT_DIR..."
mkdir -p "$PROJECT_DIR"

# --- 4. Prompt for .env ---
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "=== IMPORTANT ==="
    echo "You need to create $PROJECT_DIR/.env with your API keys."
    echo "Copy the .env.example from the deploy directory and fill in your keys."
    echo ""
    echo "Minimum required:"
    echo "  GEMINI_API_KEY=      (for embeddings + free chat)"
    echo "  PINECONE_API_KEY=    (for RAG)"
    echo "  PINECONE_HOST=       (your index URL)"
    echo "  N8N_PASSWORD=        (change from default!)"
    echo ""
fi

# --- 5. System tuning ---
echo "[4/5] System tuning..."
# Increase file watch limit (for n8n and uvicorn)
echo "fs.inotify.max_user_watches=524288" >> /etc/sysctl.conf 2>/dev/null || true
sysctl -p 2>/dev/null || true

# Open firewall if ufw is active
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo "  Firewall: ports 80, 443 opened"
fi

echo "[5/5] Ready!"
echo ""
echo "=== Next Steps ==="
echo "1. Copy the project files to $PROJECT_DIR/"
echo "   scp -r llm-orchestrator/ root@89.117.139.137:$PROJECT_DIR/"
echo ""
echo "2. Create .env from template:"
echo "   cp $PROJECT_DIR/deploy/.env.example $PROJECT_DIR/deploy/.env"
echo "   nano $PROJECT_DIR/deploy/.env"
echo ""
echo "3. Launch:"
echo "   cd $PROJECT_DIR/deploy"
echo "   docker compose up -d --build"
echo ""
echo "4. Verify:"
echo "   curl http://localhost/api/health"
echo "   # Frontend: https://peachpuff-newt-682861.hostingorsite.com"
echo "   # n8n:      https://peachpuff-newt-682861.hostingorsite.com/n8n/"
echo ""
echo "=== Storage Note ==="
echo "VPS has 50GB. Docker images + n8n + data will use ~3-5GB."
echo "Remaining ~45GB available for RAG documents and n8n workflow data."
