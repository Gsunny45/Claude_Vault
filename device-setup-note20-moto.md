# Device Setup — HermeticA-Z Provider Config
_Generated 2026-05-26_

## Device Roles
| Device | Serial | Role | Primary Provider |
|--------|--------|------|-----------------|
| Note20 Ultra | R5CN81CDXJV | Hard testing / main config | Local Qwen + Gemini |
| Moto G 5G | ZY22G7NFLK | Quick UI checks | Groq / Gemma2-9b |

---

## Note20 — Setup Steps

### 1. Install Qwen local inference server (Termux)

```bash
# On Note20 via Termux (or SSH into device)
pkg update && pkg install wget
wget https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-android-arm64.zip
unzip llama-android-arm64.zip -d ~/llama

# Download model (run from WiFi, ~1.5GB)
# Target per triggers.json: Qwen3.5-2B-Q4_K_M.gguf
wget -O ~/qwen.gguf "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"

# Start server on port 8080
~/llama/llama-server -m ~/qwen.gguf --host 127.0.0.1 --port 8080 -c 2048 -ngl 0
```

> Keep Termux running in background. HealthTracker marks local unreachable if not running → falls through to Gemini automatically.

### 2. Inject Gemini keys via ADB (from Windows)

```powershell
$adb = "C:\Users\MarsBase\Android\Sdk\platform-tools\adb.exe"
$pkg = "dev.patrickgold.florisboard.vault.debug"
$serial = "R5CN81CDXJV"

# Inject key 1
& $adb -s $serial shell am start -n $pkg/dev.patrickgold.florisboard.ime.ai.CteKeysActivity `
    --ei inject 1 -e keyRef GEMINI_KEY_1 -e keyValue "YOUR_GEMINI_KEY_1"

# Inject key 2
& $adb -s $serial shell am start -n $pkg/dev.patrickgold.florisboard.ime.ai.CteKeysActivity `
    --ei inject 1 -e keyRef GEMINI_KEY_2 -e keyValue "YOUR_GEMINI_KEY_2"
```

### 3. Note20 active ladder
```
1 → local   Qwen3.5-2B (llama-server :8080)
4 → gemini_1  Gemini 2.0 Flash (KEY_1)
5 → gemini_2  Gemini 2.0 Flash (KEY_2, overflow)
6 → cerebras  fallback if key available
```

---

## Moto G 5G — Setup Steps

### 1. Inject Groq keys via ADB

```powershell
$adb = "C:\Users\MarsBase\Android\Sdk\platform-tools\adb.exe"
$pkg = "dev.patrickgold.florisboard.vault.debug"
$serial = "ZY22G7NFLK"

# Inject Groq key 1
& $adb -s $serial shell am start -n $pkg/dev.patrickgold.florisboard.ime.ai.CteKeysActivity `
    --ei inject 1 -e keyRef GROQ_KEY -e keyValue "YOUR_GROQ_KEY_1"

# Inject Groq key 2
& $adb -s $serial shell am start -n $pkg/dev.patrickgold.florisboard.ime.ai.CteKeysActivity `
    --ei inject 1 -e keyRef GROQ_KEY_2 -e keyValue "YOUR_GROQ_KEY_2"

# Inject Groq key 3
& $adb -s $serial shell am start -n $pkg/dev.patrickgold.florisboard.ime.ai.CteKeysActivity `
    --ei inject 1 -e keyRef GROQ_KEY -e keyValue "YOUR_GROQ_KEY_3"
```

> 3 keys across GROQ_KEY + GROQ_KEY_2 = 160K TPD combined. Third key can rotate via re-inject.

### 2. Moto active ladder
```
1 → local   unreachable (no server) → HealthTracker skips after first miss
2 → groq    Groq / gemma2-9b-it  ← EFFECTIVE PRIMARY
3 → groq2   Groq / gemma2-9b-it  (KEY_2, rate-limit distribution)
4 → gemini_1  fallback
5 → gemini_2  fallback tier 2
```

---

## Fresh Key Sources

| Provider | URL | Free tier |
|----------|-----|-----------|
| Groq | console.groq.com → API Keys | 3 keys = 3× 80K TPD |
| Gemini | aistudio.google.com → Get API Key | ~1M TPD flash |
| Cerebras | cloud.cerebras.ai | free if still active |
| OpenRouter | openrouter.ai/keys | free pool llama-3.3-70b |

---

## Build + Install

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
cd C:\Users\MarsBase\Documents\android-ai-keyboard-harness

# Build once, install to both
.\gradlew assembleDebug

$adb = "C:\Users\MarsBase\Android\Sdk\platform-tools\adb.exe"
$pkg = "dev.patrickgold.florisboard.vault.debug"
$apk = "app\build\outputs\apk\debug\app-debug.apk"

& $adb -s R5CN81CDXJV install -r $apk
& $adb -s ZY22G7NFLK  install -r $apk

# Grant mic on each
& $adb -s R5CN81CDXJV shell pm grant $pkg android.permission.RECORD_AUDIO
& $adb -s ZY22G7NFLK  shell pm grant $pkg android.permission.RECORD_AUDIO
```

---

## Commit Order

```powershell
cd C:\Users\MarsBase\Documents\android-ai-keyboard-harness

# Commit 1 — critical fixes
git add app/build.gradle.kts `
        app/src/main/res/drawable/ic_app_icon_debug_foreground.xml `
        app/src/main/res/drawable/ic_app_icon_beta_foreground.xml `
        app/src/main/assets/cte_defaults/configs/triggers.json
git commit -m "fix: restore debug applicationIdSuffix; distinct icon badges debug/beta; disable anthropic in provider ladder"

# Commit 2 — palette checkpoint
git add -A
git commit -m "chore: Hermetic Violet/Amber palette migration — icons, tokens, CSS, build config"

# Push all 8 pending commits
git push
```
