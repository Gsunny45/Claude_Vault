#!/bin/bash
# ═══════════════════════════════════════════════════════════
# Claude Vault — Monitoring Stack Launcher
# ═══════════════════════════════════════════════════════════
#
# Starts: vault_exporter (Python) + Prometheus + Grafana (Docker)
#
# Prerequisites:
#   pip install prometheus_client
#   docker / docker compose
#
# Access:
#   Prometheus:  http://localhost:9091
#   Grafana:     http://localhost:3000 (admin / vaultops)
#   Exporter:    http://localhost:9090/metrics
#
# Usage:
#   ./start_monitoring.sh          # Start everything
#   ./start_monitoring.sh stop     # Stop everything
#   ./start_monitoring.sh status   # Check status
# ═══════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORTER_PID_FILE="$SCRIPT_DIR/.exporter.pid"

case "${1:-start}" in
  start)
    echo "Starting vault monitoring stack..."

    # Start vault exporter in background
    if [ -f "$EXPORTER_PID_FILE" ] && kill -0 "$(cat "$EXPORTER_PID_FILE")" 2>/dev/null; then
      echo "  Exporter already running (PID $(cat "$EXPORTER_PID_FILE"))"
    else
      echo "  Starting vault exporter..."
      python3 "$SCRIPT_DIR/vault_exporter.py" &
      echo $! > "$EXPORTER_PID_FILE"
      echo "  Exporter started (PID $!)"
    fi

    # Start Docker stack
    echo "  Starting Prometheus + Grafana..."
    cd "$SCRIPT_DIR" && docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null

    echo ""
    echo "Monitoring stack running:"
    echo "  Exporter:    http://localhost:9090/metrics"
    echo "  Prometheus:  http://localhost:9091"
    echo "  Grafana:     http://localhost:3000 (admin / vaultops)"
    ;;

  stop)
    echo "Stopping vault monitoring stack..."

    if [ -f "$EXPORTER_PID_FILE" ]; then
      kill "$(cat "$EXPORTER_PID_FILE")" 2>/dev/null
      rm -f "$EXPORTER_PID_FILE"
      echo "  Exporter stopped"
    fi

    cd "$SCRIPT_DIR" && docker compose down 2>/dev/null || docker-compose down 2>/dev/null
    echo "  Docker stack stopped"
    ;;

  status)
    echo "Vault monitoring status:"

    if [ -f "$EXPORTER_PID_FILE" ] && kill -0 "$(cat "$EXPORTER_PID_FILE")" 2>/dev/null; then
      echo "  Exporter:   RUNNING (PID $(cat "$EXPORTER_PID_FILE"))"
    else
      echo "  Exporter:   STOPPED"
    fi

    docker ps --filter "name=vault-" --format "  {{.Names}}: {{.Status}}" 2>/dev/null || echo "  Docker: not available"
    ;;

  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
