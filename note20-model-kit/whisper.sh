#!/usr/bin/env bash
# ============================================================
# whisper.sh — Hardened audio transcription via whisper.cpp
# Usage: bash /sdcard/whisper.sh <audio-file> [output-dir]
# Example: bash /sdcard/whisper.sh /sdcard/Download/recording.wav
# ============================================================
set -u

# -----------------------------------------------------------
# Config
# -----------------------------------------------------------
WHISPER="$HOME/whisper.cpp/build/bin/whisper-cli"
MODEL="$HOME/whisper.cpp/models/ggml-small.en-q5_1.bin"
LOG_FILE="/tmp/whisper-transcribe.log"
LARGE_FILE_WARN_MB=200   # warn if input audio exceeds this size

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

cleanup_tmp() {
    if [ -n "${TMP_WAV:-}" ] && [ -f "$TMP_WAV" ]; then
        rm -f "$TMP_WAV"
        log "Removed temporary WAV: $TMP_WAV"
    fi
}

on_signal() {
    local sig="$1"
    log "Received $sig — aborting transcription and cleaning up..."
    if [ -n "${WHISPER_PID:-}" ] && kill -0 "$WHISPER_PID" 2>/dev/null; then
        kill -TERM "$WHISPER_PID" 2>/dev/null
        sleep 1
        kill -KILL "$WHISPER_PID" 2>/dev/null || true
    fi
    cleanup_tmp
    log "=== whisper.sh aborted ==="
    exit 130
}

trap 'on_signal SIGINT'  INT
trap 'on_signal SIGTERM' TERM
trap 'cleanup_tmp'       EXIT

log "=== Starting whisper.sh ==="

# -----------------------------------------------------------
# Usage / argument check
# -----------------------------------------------------------
if [ -z "${1:-}" ]; then
    echo "Usage: bash /sdcard/whisper.sh <audio-file> [output-dir]"
    echo "  <audio-file>  Path to the audio file to transcribe"
    echo "  [output-dir]  Optional directory for the .txt output"
    echo "                (default: same directory as the input file)"
    echo ""
    echo "Supported inputs: wav (native), mp3/flac/ogg/m4a/etc (auto-converted via ffmpeg)"
    exit 1
fi

INPUT="$1"
OUTPUT_DIR="${2:-}"

# -----------------------------------------------------------
# Existence checks: binary, model, input file
# -----------------------------------------------------------
if [ ! -x "$WHISPER" ]; then
    log "ERROR: whisper-cli binary not found or not executable at: $WHISPER"
    log "       Build whisper.cpp first (see setup-models.sh)."
    exit 1
fi

if [ ! -f "$MODEL" ]; then
    log "ERROR: Whisper model not found: $MODEL"
    log "       Run setup-models.sh to download it."
    exit 1
fi

if [ ! -f "$INPUT" ]; then
    log "ERROR: Input audio file does not exist: $INPUT"
    exit 1
fi

if [ ! -r "$INPUT" ]; then
    log "ERROR: Input audio file is not readable: $INPUT"
    exit 1
fi

log "Binary found: $WHISPER"
log "Model found:  $MODEL"
log "Input file:   $INPUT"

# -----------------------------------------------------------
# Resolve output location: alongside input file as .txt
# (whisper-cli appends .txt to the -of basename, so we pass
#  the basename without extension and let it create <name>.txt)
# -----------------------------------------------------------
INPUT_DIR="$(cd "$(dirname "$INPUT")" 2>/dev/null && pwd)"
INPUT_BASE="$(basename "$INPUT")"
INPUT_STEM="${INPUT_BASE%.*}"

if [ -n "$OUTPUT_DIR" ]; then
    if [ ! -d "$OUTPUT_DIR" ]; then
        log "Output directory does not exist, creating: $OUTPUT_DIR"
        mkdir -p "$OUTPUT_DIR" || { log "ERROR: Could not create output directory: $OUTPUT_DIR"; exit 1; }
    fi
    if [ ! -w "$OUTPUT_DIR" ]; then
        log "ERROR: Output directory is not writable: $OUTPUT_DIR"
        exit 1
    fi
    OUT_PREFIX="$OUTPUT_DIR/$INPUT_STEM"
else
    if [ -z "$INPUT_DIR" ] || [ ! -w "$INPUT_DIR" ]; then
        log "WARNING: Cannot write alongside input file ($INPUT_DIR not writable)."
        OUTPUT_DIR="/tmp"
        log "         Falling back to output directory: $OUTPUT_DIR"
        OUT_PREFIX="$OUTPUT_DIR/$INPUT_STEM"
    else
        OUT_PREFIX="$INPUT_DIR/$INPUT_STEM"
    fi
fi

OUT_TXT="${OUT_PREFIX}.txt"
log "Output will be written to: $OUT_TXT"

if [ -f "$OUT_TXT" ]; then
    log "WARNING: Output file already exists and will be overwritten: $OUT_TXT"
fi

# -----------------------------------------------------------
# Large file check
# -----------------------------------------------------------
INPUT_SIZE_BYTES=$(stat -c %s "$INPUT" 2>/dev/null || stat -f %z "$INPUT" 2>/dev/null || echo 0)
INPUT_SIZE_MB=$((INPUT_SIZE_BYTES / 1024 / 1024))
log "Input file size: ${INPUT_SIZE_MB} MB"

if [ "$INPUT_SIZE_MB" -ge "$LARGE_FILE_WARN_MB" ]; then
    log "WARNING: Input file is large (${INPUT_SIZE_MB} MB >= ${LARGE_FILE_WARN_MB} MB)."
    log "         Transcription may take a long time and use significant RAM/disk"
    log "         (especially during ffmpeg conversion to WAV)."
    read -r -p "Continue anyway? [y/N]: " big_choice
    case "$big_choice" in
        y|Y) log "Continuing with large file (user confirmed)." ;;
        *) log "Aborting at user request (large file)."; exit 1 ;;
    esac
fi

# -----------------------------------------------------------
# Convert to 16kHz mono WAV if needed (requires ffmpeg)
# -----------------------------------------------------------
WAV_INPUT="$INPUT"
TMP_WAV=""

shopt -s nocasematch
if [[ "$INPUT" != *.wav ]]; then
    if ! command -v ffmpeg >/dev/null 2>&1; then
        log "ERROR: Input is not a .wav file and 'ffmpeg' is not installed."
        log "       Install it with: apt install -y ffmpeg"
        log "       Or supply a .wav file directly."
        exit 1
    fi

    TMP_WAV="/tmp/whisper_input_$$.wav"
    WAV_INPUT="$TMP_WAV"
    log "Converting '$INPUT' to 16kHz mono WAV via ffmpeg -> $TMP_WAV"

    if ! ffmpeg -y -i "$INPUT" -ar 16000 -ac 1 "$TMP_WAV" >>"$LOG_FILE" 2>&1; then
        log "ERROR: ffmpeg conversion failed. See $LOG_FILE for details."
        cleanup_tmp
        exit 1
    fi

    if [ ! -s "$TMP_WAV" ]; then
        log "ERROR: ffmpeg produced an empty/missing WAV file."
        cleanup_tmp
        exit 1
    fi
    log "Conversion complete: $TMP_WAV"
else
    log "Input is already a .wav file; skipping conversion."
fi
shopt -u nocasematch

# -----------------------------------------------------------
# Thread count auto-detection
# -----------------------------------------------------------
if command -v nproc >/dev/null 2>&1; then
    CPU_COUNT=$(nproc)
else
    CPU_COUNT=$(grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 4)
fi
if [ "$CPU_COUNT" -gt 1 ]; then
    THREADS=$((CPU_COUNT - 1))
else
    THREADS=1
fi
log "Detected $CPU_COUNT CPU core(s); using --threads $THREADS"

# -----------------------------------------------------------
# Run transcription
# -----------------------------------------------------------
log "Transcribing: $INPUT"
log "Output prefix passed to whisper-cli: $OUT_PREFIX (-> ${OUT_PREFIX}.txt)"
log "Command: $WHISPER -m $MODEL -f $WAV_INPUT --threads $THREADS --print-progress -otxt -of $OUT_PREFIX"

"$WHISPER" -m "$MODEL" -f "$WAV_INPUT" --threads "$THREADS" --print-progress -otxt -of "$OUT_PREFIX" &
WHISPER_PID=$!
wait "$WHISPER_PID"
EXIT_CODE=$?
WHISPER_PID=""

if [ "$EXIT_CODE" -ne 0 ]; then
    log "ERROR: whisper-cli exited with code $EXIT_CODE"
    cleanup_tmp
    trap - EXIT
    exit "$EXIT_CODE"
fi

if [ -f "$OUT_TXT" ]; then
    log "Transcription complete. Output written to: $OUT_TXT"
else
    log "WARNING: whisper-cli reported success but expected output file was not found: $OUT_TXT"
    log "         Check whisper-cli's own output above for the actual file location."
fi

cleanup_tmp
trap - EXIT
log "=== whisper.sh complete ==="
exit 0
