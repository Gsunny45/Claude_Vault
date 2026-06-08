#!/usr/bin/env bash
# ============================================================
# go.sh — Hardened launcher for Gemma 4 E4B (text-only)
# Run from INSIDE proot Ubuntu:
#   proot-distro login ubuntu
#   bash /sdcard/go.sh
# ============================================================
set -u

# -----------------------------------------------------------
# Config
# -----------------------------------------------------------
MODEL=/sdcard/Download/models/gemma-4-E4B_q4_0-it.gguf
SERVER=/root/llama.cpp/build/bin/llama-server
HOST=0.0.0.0
PORT=8080
CTX=2048
NPRED=512
MIN_FREE_RAM_MB=5120   # 5 GB threshold for text-only model
LOG_FILE="/tmp/go-gemma.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# -----------------------------------------------------------
# 1. Existence checks
# -----------------------------------------------------------
log "=== Starting go.sh (Gemma 4 E4B text-only) ==="

if [ ! -x "$SERVER" ]; then
    log "ERROR: llama-server binary not found or not executable at: $SERVER"
    log "       Build llama.cpp first (see setup-models.sh) or check the path."
    exit 1
fi

if [ ! -f "$MODEL" ]; then
    log "ERROR: Model file not found: $MODEL"
    log "       Run setup-models.sh to download it, or check /sdcard/Download/models/."
    exit 1
fi

log "Binary found:  $SERVER"
log "Model found:   $MODEL"

# -----------------------------------------------------------
# 2. Port conflict check
# -----------------------------------------------------------
port_in_use() {
    if command -v ss >/dev/null 2>&1; then
        ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$PORT$"
    elif command -v netstat >/dev/null 2>&1; then
        netstat -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$PORT$"
    else
        # Fallback: try binding with bash /dev/tcp (best-effort, not fully reliable)
        (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null && { exec 3>&-; return 0; } || return 1
    fi
}

find_free_port() {
    local p="$1"
    while port_in_use_on "$p"; do
        p=$((p + 1))
    done
    echo "$p"
}

port_in_use_on() {
    local check_port="$1"
    if command -v ss >/dev/null 2>&1; then
        ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$check_port$"
    elif command -v netstat >/dev/null 2>&1; then
        netstat -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$check_port$"
    else
        (exec 3<>"/dev/tcp/127.0.0.1/$check_port") 2>/dev/null && { exec 3>&-; return 0; } || return 1
    fi
}

if port_in_use; then
    log "WARNING: Port $PORT appears to already be in use."
    PID_INFO=""
    if command -v fuser >/dev/null 2>&1; then
        PID_INFO=$(fuser -n tcp "$PORT" 2>/dev/null | tr -s ' ')
    fi
    [ -n "$PID_INFO" ] && log "  Process(es) using port $PORT: $PID_INFO"

    echo ""
    echo "Port $PORT is busy. Choose an option:"
    echo "  [k] Kill the process(es) holding port $PORT and continue"
    echo "  [n] Pick the next free port automatically"
    echo "  [q] Quit"
    read -r -p "Choice [k/n/q]: " choice
    case "$choice" in
        k|K)
            if command -v fuser >/dev/null 2>&1; then
                log "Killing process(es) on port $PORT..."
                fuser -k -n tcp "$PORT" 2>/dev/null || true
                sleep 1
                if port_in_use; then
                    log "ERROR: Port $PORT is still in use after kill attempt. Aborting."
                    exit 1
                fi
                log "Port $PORT freed."
            else
                log "ERROR: 'fuser' not available; cannot kill process automatically."
                log "       Install psmisc (apt install -y psmisc) or free the port manually."
                exit 1
            fi
            ;;
        n|N)
            NEW_PORT=$(find_free_port $((PORT + 1)))
            log "Switching to free port: $NEW_PORT"
            PORT="$NEW_PORT"
            ;;
        *)
            log "Aborting at user request (port conflict)."
            exit 1
            ;;
    esac
else
    log "Port $PORT is free."
fi

# -----------------------------------------------------------
# 3. RAM awareness
# -----------------------------------------------------------
FREE_RAM_MB=0
if [ -r /proc/meminfo ]; then
    # MemAvailable is the best estimate of usable RAM; fall back to MemFree
    AVAIL_KB=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
    if [ -z "$AVAIL_KB" ]; then
        AVAIL_KB=$(awk '/^MemFree:/ {print $2}' /proc/meminfo)
    fi
    FREE_RAM_MB=$((AVAIL_KB / 1024))
    log "Free/available RAM: ${FREE_RAM_MB} MB (threshold: ${MIN_FREE_RAM_MB} MB)"
else
    log "WARNING: /proc/meminfo not readable; skipping RAM check."
fi

if [ "$FREE_RAM_MB" -gt 0 ] && [ "$FREE_RAM_MB" -lt "$MIN_FREE_RAM_MB" ]; then
    log "WARNING: Free RAM (${FREE_RAM_MB} MB) is below the recommended ${MIN_FREE_RAM_MB} MB"
    log "         for the text-only Gemma 4 E4B model. The server may be slow, swap heavily,"
    log "         or be killed by the OOM killer."
    read -r -p "Continue anyway? [y/N]: " ram_choice
    case "$ram_choice" in
        y|Y) log "Continuing despite low RAM (user confirmed)." ;;
        *) log "Aborting at user request (low RAM)."; exit 1 ;;
    esac
fi

# -----------------------------------------------------------
# 7. Thread count auto-detection
# -----------------------------------------------------------
if command -v nproc >/dev/null 2>&1; then
    CPU_COUNT=$(nproc)
else
    CPU_COUNT=$(grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 4)
fi
# Leave one core free for the OS/UI when possible
if [ "$CPU_COUNT" -gt 1 ]; then
    THREADS=$((CPU_COUNT - 1))
else
    THREADS=1
fi
log "Detected $CPU_COUNT CPU core(s); using --threads $THREADS"

# -----------------------------------------------------------
# 4. Graceful shutdown handling
# -----------------------------------------------------------
SERVER_PID=""

cleanup() {
    local sig="$1"
    log "Received $sig — shutting down llama-server..."
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill -TERM "$SERVER_PID" 2>/dev/null
        # Give it a moment to exit cleanly, then force kill if needed
        for _ in 1 2 3 4 5; do
            kill -0 "$SERVER_PID" 2>/dev/null || break
            sleep 1
        done
        if kill -0 "$SERVER_PID" 2>/dev/null; then
            log "Server did not exit in time; sending SIGKILL."
            kill -KILL "$SERVER_PID" 2>/dev/null
        fi
    fi
    log "=== go.sh shutdown complete ==="
    exit 0
}

trap 'cleanup SIGINT'  INT
trap 'cleanup SIGTERM' TERM
trap 'cleanup EXIT'    EXIT

# -----------------------------------------------------------
# 5. Launch
# -----------------------------------------------------------
log "Starting Gemma 4 E4B (text-only) on ${HOST}:${PORT} ..."
log "Command: $SERVER -m $MODEL --host $HOST --port $PORT -c $CTX -n $NPRED --threads $THREADS"

"$SERVER" -m "$MODEL" --host "$HOST" --port "$PORT" -c "$CTX" -n "$NPRED" --threads "$THREADS" &
SERVER_PID=$!

log "llama-server started (PID $SERVER_PID). Logs: $LOG_FILE"
log "Press Ctrl+C to stop."

wait "$SERVER_PID"
EXIT_CODE=$?
log "llama-server exited with code $EXIT_CODE"
trap - EXIT
exit "$EXIT_CODE"
