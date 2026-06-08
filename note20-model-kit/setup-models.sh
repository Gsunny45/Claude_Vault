#!/usr/bin/env bash
# ============================================================
# Gemma 4 E4B + Whisper.cpp setup for Note20 Ultra (hardened)
# Run from INSIDE proot Ubuntu:
#   proot-distro login ubuntu
#   bash /sdcard/setup-models.sh
#
# Hardened for: flaky WiFi, phantom-process kills, limited
# storage/RAM, no root/systemd/Docker, resumable downloads.
# ============================================================
set -u
set -o pipefail

# ------------------------------------------------------------
# Globals / config
# ------------------------------------------------------------
LOG_DIR="/sdcard/Download/models/logs"
mkdir -p "$LOG_DIR" 2>/dev/null || LOG_DIR="$HOME/setup-models-logs" && mkdir -p "$LOG_DIR"
TS="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOG_DIR/setup-models-$TS.log"

MODEL_DIR="/sdcard/Download/models"
WHISPER_DIR="$HOME/whisper.cpp"

GEMMA_URL="https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf/resolve/main/gemma-4-E4B_q4_0-it.gguf"
GEMMA_FILE="$MODEL_DIR/gemma-4-E4B_q4_0-it.gguf"
GEMMA_MIN_BYTES=$((5 * 1024 * 1024 * 1024))          # ~5.15GB advertised; floor at 5GB
GEMMA_SHA256=""                                       # fill in if/when HF publishes a checksum

MMPROJ_URL="https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf/resolve/main/gemma-4-E4B-it-mmproj.gguf"
MMPROJ_FILE="$MODEL_DIR/gemma-4-E4B-it-mmproj.gguf"
MMPROJ_MIN_BYTES=$((900 * 1024 * 1024))              # ~992MB advertised; floor at 900MB
MMPROJ_SHA256=""

WHISPER_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en-q5_1.bin"
WHISPER_FILE="$WHISPER_DIR/models/ggml-small.en-q5_1.bin"
WHISPER_MIN_BYTES=$((150 * 1024 * 1024))             # ~200MB advertised; floor at 150MB
WHISPER_SHA256=""

TOTAL_DOWNLOAD_KB=$(( (5300 + 1020 + 210) * 1024 ))   # rough KB estimate of all 3 downloads
REQUIRED_FREE_KB=$(( TOTAL_DOWNLOAD_KB + 2 * 1024 * 1024 ))  # + 2GB headroom for build/tmp

WGET_RETRIES=6
WGET_TIMEOUT=60          # per-attempt connection/read timeout (seconds)
WGET_WAITRETRY=15        # seconds to wait between retries (grows with backoff)

# Track partial files so we can clean them up on interrupt
declare -a PARTIAL_FILES=()
CURRENT_TMP=""

# ------------------------------------------------------------
# Logging — tee everything to a log file
# ------------------------------------------------------------
exec > >(tee -a "$LOG_FILE") 2>&1
echo "=== setup-models.sh started $(date -Is) ==="
echo "Log file: $LOG_FILE"

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
warn() { echo "[$(date '+%H:%M:%S')] WARNING: $*" >&2; }
err()  { echo "[$(date '+%H:%M:%S')] ERROR: $*" >&2; }
die()  { err "$*"; exit 1; }

# ------------------------------------------------------------
# Signal handling — clean up partial downloads on Ctrl+C / kill
# ------------------------------------------------------------
cleanup_on_interrupt() {
    local sig="$1"
    echo ""
    warn "Caught signal $sig — cleaning up partial downloads..."
    if [ -n "$CURRENT_TMP" ] && [ -f "$CURRENT_TMP" ]; then
        warn "Removing in-progress file: $CURRENT_TMP"
        rm -f "$CURRENT_TMP" "${CURRENT_TMP}.tmp" 2>/dev/null || true
    fi
    for f in "${PARTIAL_FILES[@]:-}"; do
        [ -n "$f" ] && [ -f "${f}.incomplete" ] && rm -f "${f}.incomplete" 2>/dev/null || true
    done
    err "Interrupted. Re-run this script to resume — completed files are preserved."
    exit 130
}
trap 'cleanup_on_interrupt SIGINT'  INT
trap 'cleanup_on_interrupt SIGTERM' TERM
trap 'cleanup_on_interrupt SIGHUP'  HUP

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

# Bytes free on the filesystem backing a path (best effort, portable awk)
free_bytes() {
    local path="$1"
    df -Pk "$path" 2>/dev/null | awk 'NR==2 {print $4 * 1024}'
}

human_gb() {
    awk -v b="$1" 'BEGIN { printf "%.2f GB", b / (1024*1024*1024) }'
}

# Retry wrapper around an arbitrary command
with_retries() {
    local desc="$1"; shift
    local attempt=1
    local max="$WGET_RETRIES"
    while [ "$attempt" -le "$max" ]; do
        log "  -> $desc (attempt $attempt/$max)"
        if "$@"; then
            return 0
        fi
        warn "$desc failed on attempt $attempt/$max"
        if [ "$attempt" -lt "$max" ]; then
            local backoff=$(( WGET_WAITRETRY * attempt ))
            log "  -> waiting ${backoff}s before retry (network may be flaky)..."
            sleep "$backoff"
        fi
        attempt=$(( attempt + 1 ))
    done
    return 1
}

# Resumable, retried, timeout-bounded download with size verification
# Usage: download_file <url> <dest_file> <min_expected_bytes> [sha256]
download_file() {
    local url="$1"
    local dest="$2"
    local min_bytes="$3"
    local sha256="${4:-}"

    PARTIAL_FILES+=("$dest")
    CURRENT_TMP="$dest"

    if [ -f "$dest" ]; then
        local existing_size
        existing_size=$(stat -c%s "$dest" 2>/dev/null || echo 0)
        if [ "$existing_size" -ge "$min_bytes" ]; then
            log "  Already present and looks complete ($(human_gb "$existing_size")): $dest"
            if [ -n "$sha256" ]; then
                verify_sha256 "$dest" "$sha256" || {
                    warn "Checksum mismatch on existing file — re-downloading."
                    rm -f "$dest"
                }
            fi
            [ -f "$dest" ] && { CURRENT_TMP=""; return 0; }
        else
            warn "Existing file looks truncated ($(human_gb "$existing_size") < $(human_gb "$min_bytes")). Resuming."
        fi
    fi

    wget_attempt() {
        wget --continue \
             --tries=1 \
             --timeout="$WGET_TIMEOUT" \
             --read-timeout="$WGET_TIMEOUT" \
             --no-verbose \
             --show-progress \
             -O "$dest" \
             "$url"
    }

    if ! with_retries "Downloading $(basename "$dest")" wget_attempt; then
        err "Failed to download $(basename "$dest") after $WGET_RETRIES attempts."
        err "Partial file kept at: $dest (re-run script to resume with wget -c)."
        CURRENT_TMP=""
        return 1
    fi

    CURRENT_TMP=""

    # Verify size
    local final_size
    final_size=$(stat -c%s "$dest" 2>/dev/null || echo 0)
    if [ "$final_size" -lt "$min_bytes" ]; then
        err "$(basename "$dest") is smaller than expected ($(human_gb "$final_size") < $(human_gb "$min_bytes"))."
        err "Download likely incomplete or the remote file changed. Not marking as done."
        return 1
    fi
    log "  Size check OK: $(human_gb "$final_size")"

    if [ -n "$sha256" ]; then
        verify_sha256 "$dest" "$sha256" || return 1
    else
        log "  (No SHA256 provided for this asset — skipping checksum verification.)"
    fi

    return 0
}

verify_sha256() {
    local file="$1"
    local expected="$2"
    if ! command -v sha256sum >/dev/null 2>&1; then
        warn "sha256sum not available — skipping checksum verification for $(basename "$file")."
        return 0
    fi
    log "  Verifying SHA256 for $(basename "$file")..."
    local actual
    actual=$(sha256sum "$file" | awk '{print $1}')
    if [ "$actual" = "$expected" ]; then
        log "  Checksum OK."
        return 0
    else
        err "Checksum MISMATCH for $(basename "$file")"
        err "  expected: $expected"
        err "  actual:   $actual"
        return 1
    fi
}

# ------------------------------------------------------------
# Pre-flight checks
# ------------------------------------------------------------
preflight_checks() {
    log "=== Pre-flight checks ==="

    # 1. Network connectivity
    log "Checking network connectivity..."
    local net_ok=0
    if command -v wget >/dev/null 2>&1; then
        wget -q --spider --timeout=15 --tries=1 "https://huggingface.co" && net_ok=1
    fi
    if [ "$net_ok" -ne 1 ] && command -v curl >/dev/null 2>&1; then
        curl -sSf --max-time 15 -o /dev/null "https://huggingface.co" && net_ok=1
    fi
    if [ "$net_ok" -ne 1 ]; then
        die "No network connectivity to huggingface.co. Check WiFi and re-run."
    fi
    log "  Network OK."

    # 2. Disk space on /sdcard (model downloads) and $HOME (build + whisper model)
    log "Checking disk space..."
    local sdcard_free home_free
    sdcard_free=$(free_bytes /sdcard)
    home_free=$(free_bytes "$HOME")

    if [ -z "$sdcard_free" ]; then
        warn "Could not determine free space on /sdcard — proceeding cautiously."
    else
        log "  /sdcard free: $(human_gb "$sdcard_free")"
        if [ "$sdcard_free" -lt $(( (5300 + 1020) * 1024 * 1024 + 1024*1024*1024 )) ]; then
            die "Not enough free space on /sdcard for Gemma + mmproj (need ~7.3GB incl. headroom, have $(human_gb "$sdcard_free")). Free up space and re-run."
        fi
    fi

    if [ -z "$home_free" ]; then
        warn "Could not determine free space on \$HOME — proceeding cautiously."
    else
        log "  \$HOME free: $(human_gb "$home_free")"
        if [ "$home_free" -lt $(( (210 + 500) * 1024 * 1024 + 512*1024*1024 )) ]; then
            die "Not enough free space in \$HOME for whisper.cpp build + model (need ~1.2GB, have $(human_gb "$home_free")). Free up space and re-run."
        fi
    fi

    # 3. RAM check (advisory — phone has 10GB total / ~6.4GB free historically)
    log "Checking available RAM..."
    if [ -r /proc/meminfo ]; then
        local mem_avail_kb
        mem_avail_kb=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
        if [ -n "$mem_avail_kb" ]; then
            local mem_avail_gb
            mem_avail_gb=$(awk -v k="$mem_avail_kb" 'BEGIN{printf "%.2f", k/1024/1024}')
            log "  MemAvailable: ${mem_avail_gb} GB"
            if awk -v k="$mem_avail_kb" 'BEGIN{exit !(k < 1500*1024)}'; then
                warn "Less than ~1.5GB RAM available right now. The build step (cmake/make -j4)"
                warn "may be slow or get OOM-killed by the Android phantom process monitor."
                warn "Consider closing background apps before continuing."
            fi
        else
            warn "Could not parse MemAvailable from /proc/meminfo."
        fi
    else
        warn "/proc/meminfo not readable — skipping RAM check."
    fi

    log "Pre-flight checks complete."
}

# ------------------------------------------------------------
# Dependency installation (with verification, not just best-effort)
# ------------------------------------------------------------
ensure_deps() {
    log "=== Checking build/runtime dependencies ==="
    local missing=()
    for bin in wget cmake git make g++ sha256sum df awk stat; do
        command -v "$bin" >/dev/null 2>&1 || missing+=("$bin")
    done

    if [ "${#missing[@]}" -gt 0 ]; then
        log "Missing tools: ${missing[*]} — attempting install via apt..."
        if with_retries "apt-get update" apt-get update -y; then
            :
        else
            warn "apt-get update failed — will still try to install (cached index may work)."
        fi
        if ! with_retries "apt-get install build deps" apt-get install -y wget cmake git build-essential; then
            warn "apt-get install reported failure. Re-checking individual tools..."
        fi

        missing=()
        for bin in wget cmake git make g++; do
            command -v "$bin" >/dev/null 2>&1 || missing+=("$bin")
        done
        if [ "${#missing[@]}" -gt 0 ]; then
            die "Still missing required tools after install attempt: ${missing[*]}. Install manually (apt-get install -y ${missing[*]}) and re-run."
        fi
    fi
    log "All required tools present."
}

# ------------------------------------------------------------
# Banner / confirmation
# ------------------------------------------------------------
show_banner() {
    echo ""
    echo "=== Note20 Model Setup (hardened) ==="
    echo "This will download:"
    echo "  1. Gemma 4 E4B QAT (Q4_0)        — ~5.15 GB"
    echo "  2. Gemma 4 E4B mmproj (multimodal) — ~992 MB"
    echo "  3. Whisper small.en (Q5_1)       — ~200 MB"
    echo "  4. Build whisper.cpp from source"
    echo ""
    echo "Total download: ~6.3 GB"
    echo "Log file: $LOG_FILE"
    echo ""
    if [ -t 0 ]; then
        echo "Press Enter to continue, Ctrl+C to cancel..."
        read -r _
    else
        log "Non-interactive shell detected — skipping confirmation prompt."
    fi
}

# ------------------------------------------------------------
# Phase 1: Gemma 4 E4B downloads
# ------------------------------------------------------------
phase_download_gemma() {
    echo ""
    log "[1/4] Downloading Gemma 4 E4B QAT Q4_0..."
    mkdir -p "$MODEL_DIR"
    if ! download_file "$GEMMA_URL" "$GEMMA_FILE" "$GEMMA_MIN_BYTES" "$GEMMA_SHA256"; then
        die "Gemma model download failed/incomplete. Re-run the script to resume (wget -c will continue from where it left off)."
    fi
    GEMMA_OK=1

    echo ""
    log "[2/4] Downloading Gemma 4 E4B mmproj (multimodal)..."
    if ! download_file "$MMPROJ_URL" "$MMPROJ_FILE" "$MMPROJ_MIN_BYTES" "$MMPROJ_SHA256"; then
        die "mmproj download failed/incomplete. Re-run the script to resume."
    fi
    MMPROJ_OK=1
}

# ------------------------------------------------------------
# Phase 2: whisper.cpp build
# ------------------------------------------------------------
phase_build_whisper() {
    echo ""
    log "[3/4] Building whisper.cpp..."

    if [ -d "$WHISPER_DIR/.git" ]; then
        log "  whisper.cpp repo exists, pulling latest..."
        if ! ( cd "$WHISPER_DIR" && with_retries "git pull" git pull --ff-only ); then
            warn "git pull failed (offline or diverged). Continuing with existing checkout."
        fi
    elif [ -d "$WHISPER_DIR" ]; then
        warn "$WHISPER_DIR exists but isn't a git repo — leaving it as-is and attempting build."
    else
        if ! with_retries "git clone whisper.cpp" git clone --depth 1 https://github.com/ggml-org/whisper.cpp.git "$WHISPER_DIR"; then
            die "Failed to clone whisper.cpp after $WGET_RETRIES attempts. Check network and re-run."
        fi
    fi

    [ -d "$WHISPER_DIR" ] || die "whisper.cpp directory missing after clone attempt — cannot continue."

    cd "$WHISPER_DIR" || die "Cannot cd into $WHISPER_DIR"

    log "  Configuring with cmake..."
    if ! cmake -B build > "$LOG_DIR/whisper-cmake-$TS.log" 2>&1; then
        err "cmake configuration failed. See $LOG_DIR/whisper-cmake-$TS.log"
        err "This is often caused by missing build deps (build-essential, cmake) or low memory."
        err "Try: apt-get install -y build-essential cmake   then re-run this script."
        WHISPER_BUILD_OK=0
    else
        log "  Building whisper-cli (this can take a while on-device)..."
        if cmake --build build -j2 --target whisper-cli > "$LOG_DIR/whisper-build-$TS.log" 2>&1; then
            WHISPER_BUILD_OK=1
            log "  Build succeeded."
        else
            warn "Parallel build (-j2) failed — retrying single-threaded (more stable on low-RAM devices)..."
            if cmake --build build -j1 --target whisper-cli >> "$LOG_DIR/whisper-build-$TS.log" 2>&1; then
                WHISPER_BUILD_OK=1
                log "  Single-threaded build succeeded."
            else
                err "whisper.cpp build failed. See $LOG_DIR/whisper-build-$TS.log"
                err "The phantom process monitor may have killed the compiler, or deps are missing."
                err "You can retry later with:"
                err "  cd $WHISPER_DIR && cmake --build build -j1 --target whisper-cli"
                WHISPER_BUILD_OK=0
            fi
        fi
    fi

    if [ "$WHISPER_BUILD_OK" -ne 1 ]; then
        warn "Continuing setup without a working whisper-cli binary."
        warn "The whisper.sh launcher will still be created, but transcription will not work until the build succeeds."
    fi
}

# ------------------------------------------------------------
# Phase 2b: whisper model download
# ------------------------------------------------------------
phase_download_whisper_model() {
    echo ""
    log "[4/4] Downloading whisper small.en model..."
    mkdir -p "$WHISPER_DIR/models"
    if ! download_file "$WHISPER_URL" "$WHISPER_FILE" "$WHISPER_MIN_BYTES" "$WHISPER_SHA256"; then
        warn "Whisper model download failed/incomplete. whisper.sh will not work until this succeeds."
        warn "Re-run this script to retry just this step (earlier completed steps are skipped)."
        WHISPER_MODEL_OK=0
    else
        WHISPER_MODEL_OK=1
    fi
}

# ------------------------------------------------------------
# Phase 3: Launcher scripts — written atomically (tmp + mv)
# Only overwrite an existing launcher if its prerequisites are
# actually satisfied, so a failed run never clobbers a working
# go.sh with a broken one.
# ------------------------------------------------------------
write_atomic() {
    local dest="$1"
    local tmp="${dest}.tmp.$$"
    cat > "$tmp"
    chmod +x "$tmp"
    mv -f "$tmp" "$dest"
}

phase_write_launchers() {
    echo ""
    log "Creating launcher scripts (atomic write — won't clobber a working setup on failure)..."

    # --- go.sh (text-only Gemma) ---
    if [ "${GEMMA_OK:-0}" -eq 1 ]; then
        write_atomic /sdcard/go.sh << 'GOSCRIPT'
#!/usr/bin/env bash
set -e
MODEL=/sdcard/Download/models/gemma-4-E4B_q4_0-it.gguf
SERVER=/root/llama.cpp/build/bin/llama-server

if [ ! -f "$MODEL" ]; then
    echo "ERROR: model not found at $MODEL" >&2
    exit 1
fi
if [ ! -x "$SERVER" ]; then
    echo "ERROR: llama-server binary not found/executable at $SERVER" >&2
    echo "Build llama.cpp first, or update SERVER path in this script." >&2
    exit 1
fi

echo "Starting Gemma 4 E4B on port 8080..."
exec "$SERVER" -m "$MODEL" --host 0.0.0.0 --port 8080 -c 2048 -n 512 --threads 4
GOSCRIPT
        log "  Wrote /sdcard/go.sh"
    else
        warn "Skipping go.sh — Gemma model is not confirmed present/valid (won't overwrite any existing working launcher)."
    fi

    # --- go-vision.sh (multimodal Gemma) ---
    if [ "${GEMMA_OK:-0}" -eq 1 ] && [ "${MMPROJ_OK:-0}" -eq 1 ]; then
        write_atomic /sdcard/go-vision.sh << 'VSCRIPT'
#!/usr/bin/env bash
set -e
MODEL=/sdcard/Download/models/gemma-4-E4B_q4_0-it.gguf
MMPROJ=/sdcard/Download/models/gemma-4-E4B-it-mmproj.gguf
SERVER=/root/llama.cpp/build/bin/llama-server

for f in "$MODEL" "$MMPROJ"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: required file not found: $f" >&2
        exit 1
    fi
done
if [ ! -x "$SERVER" ]; then
    echo "ERROR: llama-server binary not found/executable at $SERVER" >&2
    exit 1
fi

echo "Starting Gemma 4 E4B (multimodal) on port 8080..."
exec "$SERVER" -m "$MODEL" --mmproj "$MMPROJ" --host 0.0.0.0 --port 8080 -c 2048 -n 512 --threads 4
VSCRIPT
        log "  Wrote /sdcard/go-vision.sh"
    else
        warn "Skipping go-vision.sh — Gemma model and/or mmproj not confirmed present/valid."
    fi

    # --- whisper.sh (transcription) ---
    write_atomic /sdcard/whisper.sh << 'WSCRIPT'
#!/usr/bin/env bash
set -e
# Usage: bash /sdcard/whisper.sh <audio-file>
# Example: bash /sdcard/whisper.sh /sdcard/Download/recording.wav
WHISPER="$HOME/whisper.cpp/build/bin/whisper-cli"
MODEL="$HOME/whisper.cpp/models/ggml-small.en-q5_1.bin"

if [ -z "${1:-}" ]; then
    echo "Usage: bash /sdcard/whisper.sh <audio-file>"
    echo "Supported: wav, mp3, flac, ogg (converts via ffmpeg)"
    exit 1
fi

if [ ! -x "$WHISPER" ]; then
    echo "ERROR: whisper-cli binary not found/executable at $WHISPER" >&2
    echo "Build whisper.cpp first: cd \$HOME/whisper.cpp && cmake -B build && cmake --build build -j1 --target whisper-cli" >&2
    exit 1
fi
if [ ! -f "$MODEL" ]; then
    echo "ERROR: whisper model not found at $MODEL" >&2
    echo "Re-run setup-models.sh to download it." >&2
    exit 1
fi

INPUT="$1"
if [ ! -f "$INPUT" ]; then
    echo "ERROR: input file not found: $INPUT" >&2
    exit 1
fi

WAV_INPUT="$INPUT"

# Convert to 16kHz mono WAV if not already
if [[ "$INPUT" != *.wav ]]; then
    if ! command -v ffmpeg >/dev/null 2>&1; then
        echo "ERROR: ffmpeg not found — cannot convert $INPUT to WAV." >&2
        echo "Install with: apt-get install -y ffmpeg" >&2
        exit 1
    fi
    WAV_INPUT="/tmp/whisper_input_$$.wav"
    echo "Converting to WAV..."
    if ! ffmpeg -y -i "$INPUT" -ar 16000 -ac 1 "$WAV_INPUT" 2>/dev/null; then
        echo "ERROR: ffmpeg conversion failed for $INPUT" >&2
        rm -f "$WAV_INPUT"
        exit 1
    fi
    trap 'rm -f "$WAV_INPUT"' EXIT
fi

echo "Transcribing: $INPUT"
"$WHISPER" -m "$MODEL" -f "$WAV_INPUT" --threads 4 --print-progress
WSCRIPT
    log "  Wrote /sdcard/whisper.sh"
}

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------
print_summary() {
    echo ""
    echo "=== Setup Summary ==="
    echo "Gemma model:        $([ "${GEMMA_OK:-0}" -eq 1 ] && echo OK || echo 'MISSING/FAILED')"
    echo "mmproj:             $([ "${MMPROJ_OK:-0}" -eq 1 ] && echo OK || echo 'MISSING/FAILED')"
    echo "whisper.cpp build:  $([ "${WHISPER_BUILD_OK:-0}" -eq 1 ] && echo OK || echo 'FAILED — see logs')"
    echo "whisper model:      $([ "${WHISPER_MODEL_OK:-0}" -eq 1 ] && echo OK || echo 'MISSING/FAILED')"
    echo ""
    echo "Launchers (only created when prerequisites were satisfied):"
    [ -f /sdcard/go.sh ]        && echo "  bash /sdcard/go.sh             — Gemma 4 E4B (text only, lighter)"
    [ -f /sdcard/go-vision.sh ] && echo "  bash /sdcard/go-vision.sh      — Gemma 4 E4B (multimodal, +1GB RAM)"
    [ -f /sdcard/whisper.sh ]   && echo "  bash /sdcard/whisper.sh <file> — Transcribe audio"
    echo ""
    echo "Remember: run go.sh from inside Ubuntu proot:"
    echo "  proot-distro login ubuntu"
    echo "  bash /sdcard/go.sh"
    echo ""
    echo "ADB port forwards (run from PC):"
    echo "  adb -s R5CN81CDXJV forward tcp:8080 tcp:8080"
    echo ""
    echo "Full log saved to: $LOG_FILE"

    if [ "${GEMMA_OK:-0}" -ne 1 ] || [ "${MMPROJ_OK:-0}" -ne 1 ] || [ "${WHISPER_BUILD_OK:-0}" -ne 1 ] || [ "${WHISPER_MODEL_OK:-0}" -ne 1 ]; then
        echo ""
        echo "NOTE: One or more steps did not complete successfully."
        echo "This script is idempotent — simply re-run it; completed steps are skipped"
        echo "and partial downloads resume automatically."
        return 1
    fi
    return 0
}

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
GEMMA_OK=0
MMPROJ_OK=0
WHISPER_BUILD_OK=0
WHISPER_MODEL_OK=0

main() {
    ensure_deps
    preflight_checks
    show_banner

    phase_download_gemma
    phase_build_whisper
    phase_download_whisper_model
    phase_write_launchers

    if print_summary; then
        log "=== Setup complete — all components OK ==="
        exit 0
    else
        warn "=== Setup finished with one or more incomplete components — re-run to retry ==="
        exit 1
    fi
}

main "$@"
