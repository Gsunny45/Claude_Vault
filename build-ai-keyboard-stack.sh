#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# build-ai-keyboard-stack.sh — Orchestration for AI Keyboard Project
# ═══════════════════════════════════════════════════════════════════
#
# Assembles the existing monitoring, keyboard, and inference stack
# WITHOUT recreating scripts that already exist.
#
# Environments:
#   Laptop (WSL/PowerShell):  ./build-ai-keyboard-stack.sh laptop
#   Termux (phone):           ./build-ai-keyboard-stack.sh termux
#   Check everything:         ./build-ai-keyboard-stack.sh status
#   Generate Claude handover: ./build-ai-keyboard-stack.sh handover
#
# Existing infrastructure this script references (does NOT recreate):
#   _system/start_monitoring.sh   — Prometheus + Grafana + vault_exporter
#   _system/docker-compose.yml    — Prometheus v2.53.0 + Grafana 11.1.0
#   _system/vault_monitor.py      — Watchdog/polling vault filesystem monitor
#   _system/vault_exporter.py     — Prometheus metrics exporter (port 9100)
#   _system/prometheus.yml        — Scrape config for vault_exporter
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

# ─── Detect environment ──────────────────────────────────────────
detect_env() {
    if [ -d "/data/data/com.termux" ]; then
        echo "termux"
    elif grep -qi microsoft /proc/version 2>/dev/null; then
        echo "wsl"
    elif [ "$(uname -o 2>/dev/null)" = "Msys" ] || [ -n "${WINDIR:-}" ]; then
        echo "windows"
    else
        echo "linux"
    fi
}

ENV="${1:-$(detect_env)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_DIR="$SCRIPT_DIR/_system"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# ─── Paths by environment ────────────────────────────────────────
case "$ENV" in
    termux)
        KEYBOARD_CONFIG="$HOME/.ai-keyboard-config.json"
        MONITOR_DIR="$HOME/.monitor"
        ADB_BIN=""  # phone doesn't ADB itself
        HARNESS_DIR=""
        ;;
    wsl|windows|laptop)
        ENV="laptop"  # normalize
        KEYBOARD_CONFIG="$HOME/.ai-keyboard-config.json"
        MONITOR_DIR="$SYSTEM_DIR"
        ADB_BIN="/mnt/c/Users/MarsBase/Android/Sdk/platform-tools/adb.exe"
        HARNESS_DIR="/mnt/c/Users/MarsBase/Documents/android-ai-keyboard-harness"
        # Windows native paths (for PowerShell/ADB commands)
        ADB_WIN='C:\Users\MarsBase\Android\Sdk\platform-tools\adb.exe'
        HARNESS_WIN='C:\Users\MarsBase\Documents\android-ai-keyboard-harness'
        ;;
    status|handover)
        # handled below
        ;;
    *)
        echo "Usage: $0 {laptop|termux|status|handover}"
        exit 1
        ;;
esac

# ─── Color helpers ────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { printf "${GREEN}✓${NC} %s\n" "$1"; }
warn() { printf "${YELLOW}⚠${NC} %s\n" "$1"; }
fail() { printf "${RED}✗${NC} %s\n" "$1"; }

# ═══════════════════════════════════════════════════════════════════
# STATUS — check all components across both environments
# ═══════════════════════════════════════════════════════════════════
cmd_status() {
    echo "═══ AI Keyboard Stack Status ($TIMESTAMP) ═══"
    echo ""

    # Existing monitoring scripts
    echo "── Monitoring Infrastructure ──"
    for f in start_monitoring.sh docker-compose.yml vault_monitor.py vault_exporter.py prometheus.yml; do
        if [ -f "$SYSTEM_DIR/$f" ]; then
            ok "$f present"
        else
            fail "$f MISSING"
        fi
    done

    # Docker stack
    if command -v docker &>/dev/null; then
        if docker ps --filter "name=vault-prometheus" --format '{{.Status}}' 2>/dev/null | grep -q "Up"; then
            ok "Prometheus container running"
        else
            warn "Prometheus container not running"
        fi
        if docker ps --filter "name=vault-grafana" --format '{{.Status}}' 2>/dev/null | grep -q "Up"; then
            ok "Grafana container running"
        else
            warn "Grafana container not running"
        fi
    else
        warn "Docker not available in this environment"
    fi

    # Vault monitor state
    local state_file="$SYSTEM_DIR/_monitor_state.json"
    if [ -f "$state_file" ]; then
        local age_days
        age_days=$(( ( $(date +%s) - $(stat -c %Y "$state_file" 2>/dev/null || stat -f %m "$state_file" 2>/dev/null || echo 0) ) / 86400 ))
        if [ "$age_days" -lt 2 ]; then
            ok "Monitor state fresh (${age_days}d old)"
        else
            warn "Monitor state stale (${age_days}d old)"
        fi
    else
        fail "No monitor state file"
    fi

    # Keyboard harness
    echo ""
    echo "── Keyboard Harness ──"
    local harness_check="${HARNESS_DIR:-/mnt/c/Users/MarsBase/Documents/android-ai-keyboard-harness}"
    if [ -d "$harness_check" ]; then
        ok "Harness repo present: $harness_check"
        if [ -f "$harness_check/app/src/main/assets/cte_defaults/configs/triggers.json" ]; then
            ok "Bundled triggers.json exists"
        else
            warn "Bundled triggers.json missing"
        fi
    else
        warn "Harness repo not found at expected path"
    fi

    # ADB + devices
    echo ""
    echo "── ADB / Devices ──"
    local adb="${ADB_BIN:-}"
    if [ -z "$adb" ] && command -v adb &>/dev/null; then
        adb="adb"
    fi
    if [ -n "$adb" ] && [ -x "$adb" ] 2>/dev/null || command -v "$adb" &>/dev/null; then
        local devices
        devices=$($adb devices 2>/dev/null | grep -c 'device$' || echo 0)
        if [ "$devices" -gt 0 ]; then
            ok "$devices device(s) connected"
            $adb devices -l 2>/dev/null | grep 'device ' || true
        else
            warn "No ADB devices connected"
        fi
    else
        warn "ADB not available"
    fi

    # Ollama (local LLM — TSK-0006)
    echo ""
    echo "── Local LLM (Ollama) ──"
    if curl -sf http://localhost:11434/api/version &>/dev/null; then
        ok "Ollama responding on :11434"
        local models
        models=$(curl -sf http://localhost:11434/api/tags 2>/dev/null | python3 -c "import sys,json; print(', '.join(m['name'] for m in json.load(sys.stdin).get('models',[])))" 2>/dev/null || echo "unknown")
        ok "Models: $models"
    else
        warn "Ollama not running (TSK-0006: not yet set up as always-on)"
    fi

    echo ""
    echo "═══ End Status ═══"
}

# ═══════════════════════════════════════════════════════════════════
# LAPTOP — start monitoring stack + validate ADB bridge
# ═══════════════════════════════════════════════════════════════════
cmd_laptop() {
    echo "═══ Laptop Stack Assembly ($TIMESTAMP) ═══"

    # 1. Start existing monitoring (don't recreate)
    echo ""
    echo "── Step 1: Monitoring Stack ──"
    if [ -x "$SYSTEM_DIR/start_monitoring.sh" ]; then
        ok "Using existing start_monitoring.sh"
        bash "$SYSTEM_DIR/start_monitoring.sh" start
    else
        fail "start_monitoring.sh not found or not executable"
        echo "  Expected at: $SYSTEM_DIR/start_monitoring.sh"
        exit 1
    fi

    # 2. Validate ADB bridge for keyboard injection
    echo ""
    echo "── Step 2: ADB Bridge ──"
    if [ -n "${ADB_BIN:-}" ]; then
        if $ADB_BIN devices 2>/dev/null | grep -q 'device$'; then
            ok "ADB bridge active"
            echo "  Injection command template:"
            echo "    $ADB_WIN -s <SERIAL> shell am start -n dev.patrickgold.florisboard.vault.debug/.ime.cte.CteKeysActivity --ei inject 1 -e keyRef <REF> -e keyValue <VALUE>"
            echo ""
            echo "  Known serials:"
            echo "    Note20 Ultra: R5CN81CDXJV (primary — DO NOT live-debug, use Moto)"
            echo "    Moto G 5G:    ZY22G7NFLK  (test target)"
        else
            warn "ADB available but no devices connected"
            echo "  Connect via: $ADB_WIN connect <DEVICE_IP>:5555"
        fi
    else
        warn "ADB path not found — set ADB_BIN or ensure adb is on PATH"
    fi

    # 3. Check Ollama for local inference fallback
    echo ""
    echo "── Step 3: Local LLM Check ──"
    if curl -sf http://localhost:11434/api/version &>/dev/null; then
        ok "Ollama running — available as local fallback"
    else
        warn "Ollama not running"
        echo "  Start with: ollama serve &"
        echo "  Pull models: ollama pull llama3.1:8b-instruct-q4_K_M"
        echo "  See TSK-0006 for full setup"
    fi

    echo ""
    echo "═══ Laptop stack ready ═══"
    echo "  Grafana:    http://localhost:3000"
    echo "  Prometheus: http://localhost:9091"
    echo "  Exporter:   http://localhost:9100/metrics"
}

# ═══════════════════════════════════════════════════════════════════
# TERMUX — phone-side setup + inference validation
# ═══════════════════════════════════════════════════════════════════
cmd_termux() {
    echo "═══ Termux Stack Assembly ($TIMESTAMP) ═══"

    # 1. Prerequisites
    echo ""
    echo "── Step 1: Prerequisites ──"
    for pkg in jq curl python; do
        if command -v "$pkg" &>/dev/null; then
            ok "$pkg installed"
        else
            warn "$pkg missing — installing..."
            pkg install -y "$pkg" 2>/dev/null || apt install -y "$pkg" 2>/dev/null || fail "Could not install $pkg"
        fi
    done

    # 2. Keyboard config validation
    echo ""
    echo "── Step 2: Keyboard Config ──"
    if [ -f "$KEYBOARD_CONFIG" ]; then
        ok "Config found: $KEYBOARD_CONFIG"
        if jq empty "$KEYBOARD_CONFIG" 2>/dev/null; then
            ok "Valid JSON"
            # Check for required keys
            for key in laptop_ip providers; do
                if jq -e ".$key" "$KEYBOARD_CONFIG" &>/dev/null; then
                    ok "  .$key present"
                else
                    warn "  .$key missing"
                fi
            done
        else
            fail "Invalid JSON in $KEYBOARD_CONFIG"
        fi
    else
        warn "No keyboard config at $KEYBOARD_CONFIG"
        echo "  Create one with: { \"laptop_ip\": \"<YOUR_IP>\", \"providers\": {} }"
    fi

    # 3. CTE triggers.json state (the KNW-0029 chain)
    echo ""
    echo "── Step 3: CTE Trigger State ──"
    local cte_config_dir="$HOME/.config/florisboard/cte/configs"  # typical Termux path
    local alt_cte="/data/data/dev.patrickgold.florisboard.vault.debug/files/cte/configs"
    local triggers_path=""

    for candidate in "$cte_config_dir/triggers.json" "$alt_cte/triggers.json"; do
        if [ -f "$candidate" ]; then
            triggers_path="$candidate"
            break
        fi
    done

    if [ -n "$triggers_path" ]; then
        local has_triggers
        has_triggers=$(jq 'has("triggers")' "$triggers_path" 2>/dev/null || echo "false")
        if [ "$has_triggers" = "true" ]; then
            local count
            count=$(jq '.triggers | length' "$triggers_path" 2>/dev/null || echo 0)
            ok "triggers.json has triggers section ($count entries)"
        else
            fail "triggers.json MISSING triggers section (KNW-0029 bug #1)"
            echo "  The config writer stripped the triggers key."
            echo "  Fix: restore from bundled asset or re-inject."
        fi
    else
        warn "triggers.json not found at expected paths"
        echo "  Checked: $cte_config_dir, $alt_cte"
    fi

    # 4. Local inference (llama.cpp / llama-server)
    echo ""
    echo "── Step 4: Local Inference ──"
    if curl -sf http://127.0.0.1:8080/health &>/dev/null; then
        ok "llama-server responding on :8080"
    else
        warn "No local inference server on :8080"
        echo "  Note: KNW-0029 bug #3 — /fix routes to local:8080 which is dead"
        echo "  Cloud providers (Gemini/Groq) are the active path"
    fi

    echo ""
    echo "═══ Termux setup checked ═══"
}

# ═══════════════════════════════════════════════════════════════════
# HANDOVER — generate accurate Claude co-work document
# ═══════════════════════════════════════════════════════════════════
cmd_handover() {
    local outfile="$SCRIPT_DIR/claude-cowork-handover.md"

    cat > "$outfile" << 'HANDOVER_EOF'
# AI Keyboard Stack — Claude Co-Work Handover

Generated by `build-ai-keyboard-stack.sh handover`. Read alongside:
- `Claude_Vault/knowledge/KNW-0029` (CTE bug chain — MUST READ)
- `Claude_Vault/knowledge/KNW-0024` (injection ↔ vault alignment map)
- `Claude_Vault/tasks/TSK-0003` (keyboard task — in_progress)
- `Claude_Vault/tasks/TSK-0006` (local LLM bones — open)

## Project State (Honest)

The AI keyboard (HermeticA-Z, FlorisBoard fork) is **active but CTE/AI injection is parked** pending 4 stacked bugs (KNW-0029). Plain typing works. The facelift (palette, theme, logo, icon) is deployed. The monitoring stack (Prometheus + Grafana + vault_monitor) is built and operational on the laptop.

### What Works
- HermeticA-Z installed on Note 20 Ultra + Moto G 5G
- Plain typing stable
- Provider keys set (Gemini + Groq) via CteKeysActivity ADB injection
- Laptop monitoring: Prometheus v2.53.0 + Grafana 11.1.0 + vault_exporter (port 9100)
- vault_monitor.py (watchdog/polling, JSONL event log, state snapshots)

### What's Broken (KNW-0029 — priority order)
1. **Config writer strips triggers.** The CteKeys/CteSettings save path rewrites `triggers.json` and drops the `"triggers"` section — only `"providers"` survives. Detection gets an empty map. **Root cause. Fix first.**
2. **Self-heal blocks main thread.** `CteEngine.detectTrigger` self-heal calls `awaitSeedComplete(2000)` on main thread → 21 ANR warnings → IME glitches. **Must move off main thread before commit.**
3. **`/fix` routes to dead local server.** Defined `provider: local`, `budget: cheap` → `llama.cpp 127.0.0.1:8080` which is not installed on Note 20 → connection hang. Router should skip `local` when unreachable.
4. **Cloud-routed config crashes IME.** Editing triggers.json to repoint to `groq` crashed keyboard + Samsung BrailleIme took over as default. Likely `buildPipeline` chokes with routing.json `default: "local"` still set.

### Device Safety Rules
- **NEVER live-debug on the Note 20 Ultra** — it has only 2 IMEs (HermeticA-Z + BrailleIme). If the keyboard crashes, there's no normal fallback.
- **Test on Moto G 5G (ZY22G7NFLK)** or via code/unit tests.
- Note 20 serial: R5CN81CDXJV — daily driver, keep stable.

## Claude Co-Work Integration Points

### 1. ADB Injection Bridge (laptop → phone)
The primary laptop↔phone interface. PowerShell on DESKTOP-SH8JARJ runs:
```powershell
# Inject a provider key
& 'C:\Users\MarsBase\Android\Sdk\platform-tools\adb.exe' -s ZY22G7NFLK shell am start -n dev.patrickgold.florisboard.vault.debug/.ime.cte.CteKeysActivity --ei inject 1 -e keyRef gemini -e keyValue <KEY>
```
Claude can generate these commands but CANNOT execute them (no ADB in sandbox). Output them for Mars to run.

### 2. Kotlin Code Review / Fixes
Harness source at `C:\Users\MarsBase\Documents\android-ai-keyboard-harness`.
Key files for the KNW-0029 fix chain:
- `app/src/main/kotlin/.../ime/cte/CteEngine.kt` — trigger detection, self-heal
- `app/src/main/kotlin/.../ime/cte/CteKeysActivity.kt` — key injection, config writer (BUG #1)
- `app/src/main/kotlin/.../ime/cte/ProviderRouter.kt` — provider routing (BUG #3)
- `app/src/main/kotlin/.../FlorisImeService.kt` — IME lifecycle
- `app/src/main/assets/cte_defaults/configs/triggers.json` — bundled default triggers (11396 bytes, correct)

### 3. Monitoring Extension
Existing stack uses vault_exporter.py → Prometheus → Grafana. To add keyboard metrics:
- Extend vault_exporter.py OR create a sibling keyboard_exporter.py
- Push from Termux: `curl -X POST http://<LAPTOP_IP>:9091/metrics/job/termux_keyboard`
  (requires adding Pushgateway to docker-compose.yml — NOT yet done)
- Exporter runs on port 9100 (env EXPORTER_PORT), Prometheus scrapes host.docker.internal:9100

### 4. Vault Context Injection (Layer 2)
`skills.json` + `triggers.json` render vault context at the system-prompt level.
When the keyboard's config writer is fixed (bug #1), Claude can help design:
- Trigger → provider routing tables
- Per-app tone/context templates
- CoT/ToT reasoning chains

### 5. Ollama / Local Fallback (TSK-0006)
Not yet set up as always-on. Hardware: i5-1335U, 16GB RAM, no GPU.
Target: Ollama on WSL, llama3.1:8b-instruct-q4_K_M + qwen2.5-coder:1.5b-q8.
Claude can help with systemd service config and benchmark scripts.

## Prioritized Task List for Claude

1. **Fix CteKeysActivity config writer** — find where it rewrites triggers.json and make it round-trip all sections (not just providers). This is KNW-0029 bug #1.
2. **Move self-heal off main thread** — `detectTrigger`'s `awaitSeedComplete` must not block IME UI thread. Coroutine or background handler.
3. **Cloud-only provider routing** — make ProviderRouter skip `local` when no local server responds, regardless of `standaloneMode`. Update `routing.json` defaults for keyless-local devices.
4. **Unit tests for trigger detection** — test `detectTrigger` with empty, partial, and full triggers.json so we don't regress.
5. **Pushgateway integration** — add to docker-compose.yml, write Termux push script, scrape in Prometheus.
6. **Ollama always-on service** — systemd user service for WSL, model pull, benchmark (TSK-0006).

## What NOT to Do
- Don't recreate `start_monitoring.sh` or `docker-compose.yml` — they exist and work
- Don't modify Note 20 device state without explicit confirmation
- Don't commit the uncommitted CteEngine.kt self-heal edits without the main-thread fix
- Don't add Loki/Pushgateway until the core bugs are fixed — it's scope creep
HANDOVER_EOF

    ok "Handover written: $outfile"
    echo "  Copy content to a new Claude session for co-work."
    echo "  Pair with: KNW-0029, KNW-0024, TSK-0003 for full context."
}

# ═══════════════════════════════════════════════════════════════════
# Main dispatch
# ═══════════════════════════════════════════════════════════════════
echo "═══ AI Keyboard Stack Builder — $(date '+%Y-%m-%d %H:%M') ═══"
echo "Environment: $ENV"
echo ""

case "$ENV" in
    status)   cmd_status ;;
    laptop)   cmd_laptop ;;
    termux)   cmd_termux ;;
    handover) cmd_handover ;;
    *)
        echo "Usage: $0 {laptop|termux|status|handover}"
        exit 1
        ;;
esac
