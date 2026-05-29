---
type: knowledge
id: KNW-GEMINI-MASTER
subject: Gemini AI Studio Master Build Reference — Android, Termux, Obsidian, Edge
confidence: verified
last_verified: 2026-05-25
tags: [gemini, android, termux, obsidian, edge, fdroid, developer]
---

# Gemini AI Studio — Master Developer Build Reference
*Compiled: 2026-05-25 | Target: Heavy dev, Android 13, Termux, Obsidian multi-vault*

---

## TABLE OF CONTENTS
1. [AI Studio API + Rate Limits](#1-ai-studio-api--rate-limits)
2. [Model Roster](#2-model-roster)
3. [gemini-cli (Official)](#3-gemini-cli-official)
4. [Official SDKs](#4-official-sdks)
5. [Integration Workarounds & Proxies](#5-integration-workarounds--proxies)
6. [Android + Termux Stack](#6-android--termux-stack)
7. [Termux:API ↔ Gemini Automation](#7-termuxapi--gemini-automation)
8. [F-Droid + FOSS Android Apps](#8-f-droid--foss-android-apps)
9. [Background + Push Workarounds (Android 13)](#9-background--push-workarounds-android-13)
10. [On-Device Edge Builds](#10-on-device-edge-builds)
11. [Obsidian + Gemini Ecosystem](#11-obsidian--gemini-ecosystem)
12. [Top GitHub Repos](#12-top-github-repos)
13. [Multi-Provider Routing: Gemini → Codex → Ernie → Local](#13-multi-provider-routing-gemini--codex--ernie--local)
14. [smolagents + qwen-agent + Gemini](#14-smolagents--qwen-agent--gemini)
15. [Advanced Patterns](#15-advanced-patterns)

---

## 1. AI Studio API + Rate Limits

**API Key:** https://aistudio.google.com/app/apikey

```bash
export GEMINI_API_KEY="AIza..."
export GOOGLE_API_KEY="AIza..."   # also recognized
```

### Free Tier Limits (per project, not per key)

| Model | RPM | RPD | TPM | Context |
|-------|-----|-----|-----|---------|
| gemini-2.5-pro | 5 | 50–100 | 250,000 | 1M |
| gemini-2.5-flash | 10 | 250 | 250,000 | 1M |
| gemini-2.5-flash-lite | 15 | 1,000 | 250,000 | 1M |
| gemini-2.0-flash | 15 | 1,000–1,500 | 1,000,000 | 1M |

> **Critical:** Dec 2025 update cut daily quotas 50–80%. RPD resets midnight Pacific. Limits are per-**project** — multiple keys in the same project share the same quota.

### Paid Tier Pricing

| Model | Input /1M | Output /1M |
|-------|-----------|------------|
| gemini-2.5-pro | $1.25 (<200K ctx) / $2.50 | $10.00 / $15.00 |
| gemini-2.5-flash | $0.30 | $2.50 |
| gemini-2.5-flash-lite | $0.10 | $0.40 |

**Batch API: 50% discount on all input/output.**

---

## 2. Model Roster

### Stable / GA

| Model ID | Notes |
|----------|-------|
| `gemini-2.5-pro` | State-of-art reasoning; 2M ctx window |
| `gemini-2.5-flash` | Best price/perf; 1M ctx |
| `gemini-2.5-flash-lite` | Cheapest, fastest; GA May 2026 |
| `gemini-2.0-flash` | **Shutting down June 1, 2026** |
| `gemini-2.0-flash-lite` | **Shutting down June 1, 2026** |

### Embedding Models

| Model | Dimensions | Status |
|-------|-----------|--------|
| `gemini-embedding-001` | 3072 (truncatable to 768/1536) | **Use this** — leads MTEB multilingual |
| `text-embedding-004` | 768 | Retiring Aug 14, 2025 |

---

## 3. gemini-cli (Official)

**GitHub:** https://github.com/google-gemini/gemini-cli | **Stars: ~76,300**

```bash
npm install -g @google/gemini-cli
npx @google/gemini-cli          # no install
```

### Auth

```bash
# OAuth (personal account — more generous: 60 RPM, 1000 RPD with Gemini 2.5 Pro)
gemini

# API key (CI/CD, non-interactive)
export GEMINI_API_KEY="your_key"
gemini

# Vertex AI / ADC
gcloud auth application-default login
export GOOGLE_GENAI_USE_ENTERPRISE=true
export GOOGLE_CLOUD_PROJECT="my-project"
```

### Key Flags

```bash
gemini -m gemini-2.5-flash
gemini --include-directories ../lib,../docs
gemini --output-format json
gemini -p "one-shot prompt"
```

### GEMINI.md Context System

```
~/.gemini/GEMINI.md        # global (all projects)
<project_root>/GEMINI.md   # project (searched up to git root)
<subdir>/GEMINI.md         # component-level
```

Generate: `gemini` then `/init`

### MCP Config (`~/.gemini/settings.json`)

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "your-key",
        "OBSIDIAN_HOST": "https://127.0.0.1:27124"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    }
  }
}
```

### Key Slash Commands

| Command | Action |
|---------|--------|
| `/init` | Generate GEMINI.md for project |
| `/memory show` | Show loaded instructions |
| `/memory refresh` | Reload from disk |
| `/chat save <name>` | Save session |
| `/tools` | List available tools |

`@file.py` = reference file. `!git status` = run shell command.

---

## 4. Official SDKs

### Python (`google-genai`)

```bash
pip install google-genai
pip install "google-genai[aiohttp]"  # async
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Basic generation
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello",
    config=types.GenerateContentConfig(
        system_instruction="You are a coding assistant.",
        temperature=0.3,
    )
)
print(response.text)

# Streaming
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash", contents="Write a long essay"
):
    print(chunk.text, end="", flush=True)

# Async
async for chunk in await client.aio.models.generate_content_stream(...):
    print(chunk.text, end="")

# Chat session (auto-maintains history)
chat = client.chats.create(model="gemini-2.5-flash")
response = chat.send_message("Hello")
```

**GitHub:** https://github.com/googleapis/python-genai | **Stars: ~3,700**

### JavaScript (`@google/genai`)

```bash
npm install @google/genai
```

```typescript
import { GoogleGenAI } from "@google/genai";
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const response = await ai.models.generateContent({
  model: "gemini-2.5-flash",
  contents: "Hello from Node"
});
console.log(response.text);
```

**GitHub:** https://github.com/googleapis/js-genai | **Stars: ~1,400**

### Go (`google.golang.org/genai`)

```bash
go get google.golang.org/genai
```

> Old `github.com/google/generative-ai-go` is deprecated. Use `google.golang.org/genai`.

### REST API

```bash
# Non-streaming
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'

# Streaming SSE
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?alt=sse&key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'

# Count tokens (free to call)
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:countTokens?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Count these"}]}]}'
```

### OpenAI-Compatible Endpoint (Drop-in)

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "Hello"}]
)
```

Supports: `/v1/chat/completions`, `/v1/embeddings`, `/v1/models`, Batch API JSONL.

---

## 5. Integration Workarounds & Proxies

### LiteLLM

```bash
pip install litellm
```

```python
import litellm
response = litellm.completion(
    model="gemini/gemini-2.5-flash",
    messages=[{"role": "user", "content": "Hello"}],
    api_key=os.environ["GEMINI_API_KEY"]
)
```

**LiteLLM proxy config YAML:**
```yaml
model_list:
  - model_name: gemini-flash
    litellm_params:
      model: gemini/gemini-2.5-flash
      api_key: os.environ/GEMINI_API_KEY
  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: os.environ/GEMINI_API_KEY
```

**Full docs:** https://docs.litellm.ai/docs/providers/gemini

### Cloudflare Workers Proxies

| Repo | Stars | Notes |
|------|-------|-------|
| [PublicAffairs/openai-gemini](https://github.com/PublicAffairs/openai-gemini) | ~3–4k | Best all-around CF Workers proxy |
| [zuisong/gemini-openai-proxy](https://github.com/zuisong/gemini-openai-proxy) | ~1–1.5k | Deno Deploy live demo available |
| [zhu327/gemini-openai-proxy](https://github.com/zhu327/gemini-openai-proxy) | ~1.2k | Go single binary, low memory |
| [zxcloli666/AI-Worker-Proxy](https://github.com/zxcloli666/AI-Worker-Proxy) | — | Multi-provider + key rotation on CF |

**Deploy PublicAffairs proxy:**
```bash
git clone https://github.com/PublicAffairs/openai-gemini
cd openai-gemini
wrangler secret put GEMINI_API_KEY
wrangler deploy
# → https://openai-gemini.<yoursubdomain>.workers.dev
```

**CF free tier note:** 100k req/day on CF free tier. Gemini free tier (1,500 RPD Flash) is your actual ceiling — CF is not the bottleneck.

### Key Rotation Pattern

```python
# Keys MUST be from different Google accounts/projects to genuinely multiply quota
GEMINI_KEY_POOL = [os.environ[k] for k in os.environ if k.startswith("GEMINI_KEY_")]
_idx = 0

async def generate_with_rotation(prompt):
    global _idx
    for _ in range(len(GEMINI_KEY_POOL)):
        try:
            key = GEMINI_KEY_POOL[_idx % len(GEMINI_KEY_POOL)]
            _idx += 1
            client = genai.Client(api_key=key)
            return client.models.generate_content(model="gemini-2.5-flash", contents=prompt).text
        except ResourceExhausted:
            await asyncio.sleep(2 ** _)
    raise RuntimeError("All keys exhausted")
```

---

## 6. Android + Termux Stack

> **CRITICAL:** Get Termux from **F-Droid or GitHub releases** — NOT Play Store (abandoned, broken packages).
> - F-Droid: https://f-droid.org/packages/com.termux/
> - GitHub APK: https://github.com/termux/termux-app/releases

### CLI Tools in Termux

#### aichat (Best all-in-one)
```bash
pkg install aichat
```
Config: `~/.config/aichat/config.yaml`
```yaml
model: gemini:gemini-2.5-flash
clients:
  - type: gemini
    api_key: $GEMINI_API_KEY
```
GitHub: https://github.com/sigoden/aichat

#### llm + llm-gemini (Simon Willison)
```bash
pip install llm
llm install llm-gemini
llm keys set gemini
llm -m gemini-2.5-flash "your prompt"
llm -m gemini-2.5-pro --system "bash expert" "write a one-liner"
```
GitHub: https://github.com/simonw/llm | Plugin: https://github.com/simonw/llm-gemini

#### tgpt
```bash
curl -sSL https://raw.githubusercontent.com/aandrew-me/tgpt/main/install | bash -s /data/data/com.termux/files/usr/bin
tgpt --provider gemini --key $GEMINI_API_KEY "your prompt"
```
GitHub: https://github.com/aandrew-me/tgpt

#### shell-gpt via LiteLLM bridge
```bash
pip install shell-gpt litellm
# ~/.config/shell_gpt/.sgptrc:
# USE_LITELLM=true
# DEFAULT_MODEL=gemini/gemini-2.5-flash
export GEMINI_API_KEY=your_key
sgpt "explain this code"
```

#### Direct Python (google-genai)
```bash
pkg install python
python -m venv ~/gemini-env
source ~/gemini-env/bin/activate
pip install google-genai
```

#### Direct curl from Termux
```bash
export GEMINI_API_KEY="your_key"

# Text
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' | python -m json.tool

# Vision (camera photo → Gemini)
IMG_B64=$(base64 -w 0 /sdcard/photo.jpg)
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"Describe this image\"},{\"inline_data\":{\"mime_type\":\"image/jpeg\",\"data\":\"${IMG_B64}\"}}]}]}"
```

### gemini-cli in Termux

The upstream `@google/gemini-cli` has native module build issues on Android ARM64.

**Option A — Termux fork (recommended):**
```bash
pkg install nodejs-lts termux-api
npm install -g @mmmbuto/gemini-cli-termux@latest
gemini
```
- npm: https://www.npmjs.com/package/@mmmbuto/gemini-cli-termux
- GitHub: https://github.com/DioNanos/gemini-cli-termux

**Option B — Upstream with --ignore-scripts:**
```bash
pkg install nodejs-lts
npm install -g @google/gemini-cli --ignore-scripts
```

**Auth on Android (no popup browser):**
```bash
export GEMINI_API_KEY="your_key"   # simplest — no browser needed
gemini --api-key $GEMINI_API_KEY
# OR: gemini → Google Login → copy URL → termux-open-url <url>
```

**Known issues:** https://github.com/google-gemini/gemini-cli/issues/7895

---

## 7. Termux:API ↔ Gemini Automation

**Install:**
```bash
pkg install termux-api
# + install Termux:API app from F-Droid: https://f-droid.org/packages/com.termux.api/
```

### Camera → Gemini Vision
```bash
termux-camera-photo -c 0 ~/photo.jpg
IMG_B64=$(base64 -w 0 ~/photo.jpg)
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"Describe this\"},{\"inline_data\":{\"mime_type\":\"image/jpeg\",\"data\":\"${IMG_B64}\"}}]}]}" \
  | python -c "import sys,json; print(json.load(sys.stdin)['candidates'][0]['content']['parts'][0]['text'])"
```

### Mic → Gemini Transcription
```bash
termux-microphone-record -l 10 -o ~/recording.m4a
sleep 11
AUDIO_B64=$(base64 -w 0 ~/recording.m4a)
curl -s "...gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"Transcribe this\"},{\"inline_data\":{\"mime_type\":\"audio/mp4\",\"data\":\"${AUDIO_B64}\"}}]}]}"
```

### Clipboard → Gemini → Notification
```bash
CONTENT=$(termux-clipboard-get)
RESULT=$(curl -s "...generateContent?key=${GEMINI_API_KEY}" \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"Summarize: ${CONTENT}\"}]}]}" \
  | python -c "import sys,json; print(json.load(sys.stdin)['candidates'][0]['content']['parts'][0]['text'])")
termux-notification --title "Gemini" --content "$RESULT"
termux-tts-speak "$RESULT"
```

### Interactive Dialog
```bash
PROMPT=$(termux-dialog text -t "Ask Gemini" -i "Type your question" | python -c "import sys,json; print(json.load(sys.stdin)['text'])")
RESULT=$(curl -s "...generateContent?key=${GEMINI_API_KEY}" -d "{\"contents\":[{\"parts\":[{\"text\":\"${PROMPT}\"}]}]}" | python -c "...")
termux-dialog confirm -t "Gemini" -i "$RESULT"
```

### Homescreen Widget → Gemini
```bash
# Install Termux:Widget from F-Droid: https://f-droid.org/packages/com.termux.widget/
mkdir -p ~/.shortcuts
cat > ~/.shortcuts/ask-gemini.sh << 'EOF'
#!/bin/bash
source ~/.profile
PROMPT=$(termux-dialog text -t "Gemini Query" | python -c "import sys,json; d=json.load(sys.stdin); exit(1) if d['code']==-1 else print(d['text'])")
RESULT=$(curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"${PROMPT}\"}]}]}" \
  | python -c "import sys,json; print(json.load(sys.stdin)['candidates'][0]['content']['parts'][0]['text'])")
termux-notification --title "Gemini" --content "${RESULT:0:200}"
termux-tts-speak "$RESULT"
EOF
chmod +x ~/.shortcuts/ask-gemini.sh
```
Long-press homescreen → Widgets → Termux:Widget → select `ask-gemini`

### termux-boot Auto-Start
```bash
# Install Termux:Boot from F-Droid: https://f-droid.org/en/packages/com.termux.boot/
mkdir -p ~/.termux/boot/
cat > ~/.termux/boot/start-gemini.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
sleep 10
export GEMINI_API_KEY="your_key"
nohup python ~/gemini-server/server.py >> ~/logs/gemini.log 2>&1 &
EOF
chmod +x ~/.termux/boot/start-gemini.sh
# Open Termux:Boot app once to register the boot receiver
```

### Tasker + termux-tasker + Gemini
```bash
# Install Termux:Tasker from F-Droid: https://f-droid.org/packages/com.termux.tasker/
mkdir -p ~/.termux/tasker
cat > ~/.termux/tasker/gemini-query.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
RESULT=$(curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"$1\"}]}]}" \
  | python -c "import sys,json; print(json.load(sys.stdin)['candidates'][0]['content']['parts'][0]['text'])")
echo "$RESULT"
EOF
chmod +x ~/.termux/tasker/gemini-query.sh
```
In Tasker: Plugin → Termux:Tasker → `gemini-query.sh` → pass `%par1`. Result in `%stdout`.

**Dedicated Tasker-Gemini plugin (no Termux needed):**
- GitHub: https://github.com/meinside/android-tasker-gemini-plugin

### Clipboard Monitor (Background)
```bash
cat > ~/clipboard-monitor.sh << 'EOF'
#!/bin/bash
LAST=""
while true; do
  CURRENT=$(termux-clipboard-get)
  if [ "$CURRENT" != "$LAST" ] && [ -n "$CURRENT" ] && [ ${#CURRENT} -gt 50 ]; then
    LAST="$CURRENT"
    RESULT=$(curl -s "...generateContent?key=${GEMINI_API_KEY}" \
      -d "{\"contents\":[{\"parts\":[{\"text\":\"Summarize: ${CURRENT}\"}]}]}" \
      | python -c "...")
    termux-notification --title "Gemini Summary" --content "$RESULT"
  fi
  sleep 2
done
EOF
nohup bash ~/clipboard-monitor.sh &
```

### Automate (F-Droid, free automation app)
- F-Droid: https://f-droid.org/packages/com.llamalab.automate/
- Build flow: HTTP Request block → POST to Gemini REST → JSON Path parse → Notification/TTS

---

## 8. F-Droid + FOSS Android Apps

### Direct Gemini API Support

| App | F-Droid Link | Notes |
|-----|-------------|-------|
| **Maid** | [f-droid.org/packages/com.danemadsen.maid](https://f-droid.org/packages/com.danemadsen.maid/) | Gemini as remote provider + local llama.cpp |
| **GPTMobile** | [f-droid.org/en/packages/dev.chungjungsoo.gptmobile](https://f-droid.org/en/packages/dev.chungjungsoo.gptmobile/) | Multi-LLM simultaneous, Material3, Android 12+ |
| **Kai 9000** | [f-droid.org/en/packages/com.inspiredandroid.kai](https://f-droid.org/en/packages/com.inspiredandroid.kai/) | 17+ providers incl. Gemini, FOSS, no ads |
| **geminiAssist** | [f-droid.org/packages/io.github.acidefluorhydrique.geminiassist](https://f-droid.org/packages/io.github.acidefluorhydrique.geminiassist/) | Simple WebView wrapper |

**Maid APK (direct sideload):** https://github.com/Mobile-Artificial-Intelligence/maid/releases

### OpenAI-Compat Endpoint → Any App

Any app supporting custom OpenAI API base URL can use Gemini:
```
Base URL: https://generativelanguage.googleapis.com/v1beta/openai/
API Key: your Gemini API key
Model: gemini-2.5-flash
```

Apps: ChatterUI, Maid, GPTMobile, Open WebUI Android, Jan, etc.

### Better F-Droid Clients
- **Droid-ify:** https://f-droid.org/packages/com.looker.droidify/
- **Neo Store:** https://f-droid.org/packages/com.machiav3lli.fdroid/
- **Add IzzyOnDroid repo:** `https://apt.izzysoft.de/fdroid/repo`

### GitHub APK Sideload Sources
- Maid: https://github.com/Mobile-Artificial-Intelligence/maid/releases
- ChatterUI: https://github.com/Vali-98/ChatterUI/releases
- PocketPal AI: https://github.com/a-ghorbani/pocketpal-ai/releases (local models only, no Gemini remote)

---

## 9. Background + Push Workarounds (Android 13)

### Phantom Process Killer Fix (Android 12/13 — CRITICAL)
```bash
# Via ADB (from PC)
adb shell "/system/bin/device_config put activity_manager max_phantom_processes 2147483647"

# Via Shizuku rish (no PC needed)
rish -c "device_config put activity_manager max_phantom_processes 2147483647"
```
This is the #1 cause of Termux background session death.

### Battery Optimization
```bash
# Via ADB
adb shell dumpsys deviceidle whitelist +com.termux
adb shell dumpsys deviceidle whitelist +com.termux.api
adb shell dumpsys deviceidle whitelist +com.termux.boot

# Or: Settings → Battery → Battery Optimization → All Apps → Termux → Don't optimize
```

### Wake Lock
```bash
termux-wake-lock   # keep CPU awake
# ... long Gemini task ...
termux-wake-unlock
```

### Persistent Sessions
```bash
pkg install tmux
tmux new -s gemini
# Ctrl+B, D to detach
tmux attach -t gemini   # reattach

pkg install screen   # alternative
nohup python ~/server.py > ~/server.log 2>&1 &   # simple bg job
```

### Shizuku (No-Root Elevated Permissions)
- Download APK: https://shizuku.en.downlody.com/
- Setup: Developer Options → Wireless Debugging → Start Shizuku
- `rish` shell gives ADB-level privilege from Termux without a PC
- Key use: fix Phantom Process Killer, send system notifications

### ADB WiFi (Persistent, No USB)
```bash
# Android 11+ Wireless Debugging:
# Device: Developer Options → Wireless Debugging → Pair device with pairing code
adb pair <ip>:<pair_port> <6-digit-code>
adb connect <ip>:5555

# Push notification via ADB
adb shell cmd notification post -S bigtext -t "Gemini" "tag1" "$(cat result.txt)"
```

---

## 10. On-Device Edge Builds

### llama.cpp in Termux (Local Gemini Fallback)

**Snapdragon 778G (Moto G 5G) — OpenCL / Adreno 642L:**
```bash
pkg update && pkg upgrade
pkg install git cmake clang opencl-headers ocl-icd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp && mkdir build && cd build
cmake .. -DGGML_OPENCL=ON -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

**Exynos 990 (Note 20 Ultra) — Vulkan / Mali-G77:**
```bash
pkg install vulkan-headers vulkan-loader-android
cmake .. -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

**Run model as local API (OpenAI-compat):**
```bash
# Download Gemma 2B Q4
curl -L "https://huggingface.co/google/gemma-2b-GGUF/resolve/main/gemma-2b-q4_k_m.gguf" -o ~/models/gemma-2b.gguf
./llama-server -m ~/models/gemma-2b.gguf --port 8080 --ctx-size 2048
# → http://localhost:8080/v1 as local Gemini fallback
```

**Android docs:** https://github.com/ggml-org/llama.cpp/blob/master/docs/android.md

### Ollama in Termux

```bash
pkg install ollama   # official repo as of April 2025
ollama serve &
ollama pull gemma3:1b
ollama run gemma3:1b
# Exposes OpenAI-compat API at http://localhost:11434/v1
```

**Termux fork:** https://github.com/DioNanos/ollama-termux (ARM64-tuned)
**Simple installer:** https://github.com/Anon4You/ollama-in-termux

**Hardware guide:**
- Moto G 5G (6GB RAM): 1B–3B models, ~3–5 tok/sec on Gemma 2B Q4
- Note 20 Ultra (12GB RAM): up to 7B quantized

### KoboldCpp in Termux

```bash
# Auto-installer
curl -fsSL https://raw.githubusercontent.com/LostRuins/koboldcpp/main/android_install.sh | bash

# Manual with OpenCL
pkg install git python clang openssl blas-openblas clblast opencl-headers ocl-icd
git clone https://github.com/LostRuins/koboldcpp.git
cd koboldcpp && make LLAMA_CLBLAST=1
```

GitHub: https://github.com/LostRuins/koboldcpp

### MediaPipe LLM Inference (On-Device Gemma)

**Snapdragon 778G (Moto G 5G):** Gemma 2B Q4 supported, CPU+GPU backends
**Exynos 990 (Note 20 Ultra):** Not officially optimized — use llama.cpp Vulkan instead

```kotlin
// Android Kotlin
val options = LlmInference.LlmInferenceOptions.builder()
    .setModelPath("/sdcard/models/gemma-2b.bin")
    .setMaxTokens(1024)
    .build()
val llmInference = LlmInference.createFromOptions(context, options)
val response = llmInference.generateResponse("Hello from on-device Gemma!")
```

**Docs:** https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference/android
**Migration note:** Google recommends moving to LiteRT-LM for NPU acceleration.

### ADB + Gemini Vision (Screen Capture)

```bash
# Capture screen → send to Gemini Vision
SCREENSHOT="/tmp/screen.png"
adb exec-out screencap -p > "$SCREENSHOT"
IMG_B64=$(base64 -w 0 "$SCREENSHOT")
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"contents\":[{\"parts\":[{\"text\":\"What is on this Android screen?\"},{\"inline_data\":{\"mime_type\":\"image/png\",\"data\":\"${IMG_B64}\"}}]}]}"
```

**scrcpy-mcp:** MCP server exposing scrcpy as an AI tool interface — https://mcpmarket.com/server/scrcpy

### Android Studio + Gemini

- Built-in, no plugin install
- Features: AI code completion, next-edit prediction, test generation, error explanation
- Add custom API key: Settings → Tools → AI → Model Providers → Gemini
- Docs: https://developer.android.com/studio/gemini/features

---

## 11. Obsidian + Gemini Ecosystem

### Top Plugins (Ranked by Usefulness for Multi-Vault)

#### Gemini Scribe (`allenhutchison/obsidian-gemini`) ⭐ PRIMARY
- GitHub: https://github.com/allenhutchison/obsidian-gemini
- **Best for:** Agent-first workflows, scheduled tasks, lifecycle hooks, vault RAG
- **Key features:** Projects (scope agent to folder), semantic vault search, MCP support (HTTP transport works on Android), scheduled tasks (cron-like), lifecycle hooks (trigger on file events), stable prefix caching, custom API endpoint
- **Scheduled task frontmatter:**
```yaml
---
gemini-scribe/scheduled-task: true
schedule: daily@08:00
model: gemini-2.5-flash
---
Summarize all notes modified in the last 24 hours and write a briefing to daily/{{date}}.md
```

#### Copilot for Obsidian (`logancyang/obsidian-copilot`)
- GitHub: https://github.com/logancyang/obsidian-copilot
- **Best for:** Multi-provider chat + vault RAG
- Setup: Settings → Copilot → Basic → Set Keys → paste Google API key
- Config: `.obsidian/plugins/copilot/data.json`

#### Smart Connections (`brianpetro/obsidian-smart-connections`)
- GitHub: https://github.com/brianpetro/obsidian-smart-connections
- **Best for:** Semantic vault linking with Gemini embeddings
- Embedding model: `gemini-embedding-001` (3072d, MTEB multilingual #1)
- Cost estimate: $1–3 one-time for a 4M-word vault

#### Text Generator (`nhaouari/obsidian-textgenerator-plugin`)
- Gemini setup: Settings → Provider → Google Generative AI → API key

#### Agent Client (`RAIT-09/obsidian-agent-client`)
- GitHub: https://github.com/RAIT-09/obsidian-agent-client
- **Best for:** Embedding Gemini CLI, Claude Code, Codex inside an Obsidian pane
- `@notename` syntax to reference vault notes in prompts

#### VaultAI (`0xneobyte/VaultAI`)
- GitHub: https://github.com/0xneobyte/VaultAI
- Gemini-only chatbot with RAG + note citations

### Obsidian Local REST API (Vault as API)
- GitHub: https://github.com/coddingtonbear/obsidian-local-rest-api
- Endpoints: `GET/PUT/PATCH /vault/{filename}`, `POST /search/simple/`
- HTTP at `http://127.0.0.1:27123`, HTTPS at `https://127.0.0.1:27124`
- **MCP server built-in** — wire to gemini-cli via `~/.gemini/settings.json`

### gemini-obsidian CLI Extension
- GitHub: https://github.com/thoreinstein/gemini-obsidian
- Install into `~/.gemini/extensions/gemini-obsidian/` then `npm install`
- Tools: vault RAG indexing (LanceDB), semantic search, graph traversal, link repair

### Templater + Gemini (DIY)
```javascript
// scripts/gemini_generate.js
module.exports = async ({ prompt }) => {
  const response = await fetch(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=YOUR_KEY",
    { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] }) }
  );
  const data = await response.json();
  return data.candidates[0].content.parts[0].text;
};
```
Template usage: `<% await tp.user.gemini_generate({prompt: "Summarize: " + tp.file.content}) %>`

### n8n + Obsidian + Gemini
- n8n Google Gemini node: https://n8n.io/integrations/google-gemini/
- n8n Obsidian REST API node: https://github.com/j-shelfwood/n8n-nodes-obsidian-local-rest-api
- Pattern: Schedule → REST API read note → Gemini process → REST API write result

### Decision Matrix for Multi-Vault Setup

| Goal | Tool |
|------|------|
| Agent scoped to Claude_Vault | Gemini Scribe (Projects feature) |
| Semantic search across all vaults | Smart Connections + `gemini-embedding-001` |
| Scheduled briefing compilation | Gemini Scribe Scheduled Tasks |
| Trigger AI on file save | Gemini Scribe Lifecycle Hooks |
| n8n automation pipeline | Local REST API → n8n → Gemini Chat Model |
| Gemini CLI with vault access | `gemini-obsidian` CLI ext + REST API MCP |
| Mobile AI chat (Android) | BMO Chatbot or Gemini Scribe (HTTP MCP) |
| Embed Gemini CLI in Obsidian pane | Agent Client plugin |

---

## 12. Top GitHub Repos

### Official (Stars)

| Repo | Stars | Key Info |
|------|-------|----------|
| [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | ~76,300 | Official CLI, MCP support |
| [google/mediapipe](https://github.com/google-ai-edge/mediapipe) | ~28,000 | On-device AI, LLM inference |
| [google-gemini/cookbook](https://github.com/google-gemini/cookbook) | ~17,300 | Quickstarts + examples |
| [firebase/genkit](https://github.com/firebase/genkit) | ~7,000–8,000 | Multi-model AI framework |
| [googleapis/python-genai](https://github.com/googleapis/python-genai) | ~3,700 | Official Python SDK |
| [google-ai-edge/ai-edge-torch](https://github.com/google-ai-edge/ai-edge-torch) | ~1,500–2,000 | PyTorch → TFLite for edge |
| [googleapis/js-genai](https://github.com/googleapis/js-genai) | ~1,400 | Official JS/TS SDK |

### Community (Stars)

| Repo | Stars | Key Info |
|------|-------|----------|
| [open-webui/open-webui](https://github.com/open-webui/open-webui) | ~90,000+ | Self-hosted UI, Gemini backend |
| [langgenius/dify](https://github.com/langgenius/dify) | ~80,000+ | LLM app platform, Gemini plugin |
| [lobehub/lobe-chat](https://github.com/lobehub/lobe-chat) | ~65,300 | Chat UI, Docker one-liner |
| [openai/codex](https://github.com/openai/codex) | ~75,600 | Code agent CLI, Gemini compat |
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | ~44,700 | Unified LLM router, Gemini native |
| [huggingface/smolagents](https://github.com/huggingface/smolagents) | ~15,000 | Agent framework, Gemini via LiteLLM |
| [danny-avila/LibreChat](https://github.com/danny-avila/LibreChat) | ~37,300 | Self-hosted chat, Gemini support |
| [PublicAffairs/openai-gemini](https://github.com/PublicAffairs/openai-gemini) | ~3,000–4,000 | CF Workers OpenAI→Gemini proxy |

---

## 13. Multi-Provider Routing: Gemini → Codex → Ernie → Local

### OpenAI Codex CLI

**Install:**
```bash
npm install -g @openai/codex
```

**Route Codex to Gemini (drop-in):**
```bash
export OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
export OPENAI_API_KEY="your-gemini-key"
codex "refactor this function"
```

**Or config file (`~/.codex/config.toml`):**
```toml
[model_providers.gemini]
name = "Google Gemini"
base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
env_key = "GEMINI_API_KEY"
wire_api = "chat"

[model]
provider = "gemini"
name = "gemini-2.5-flash"
```

**Codex in Termux:** Upstream fails on native Termux. Use community fork:
```bash
npm install -g @mmmbuto/codex-cli-termux
# or: https://github.com/DioNanos/codex-termux
```

### Baidu Ernie Bot

```bash
pip install qianfan
```

**OpenAI-compat usage:**
```python
from openai import OpenAI
client = OpenAI(
    base_url="https://aistudio.baidu.com/llm/lmapi/v3",
    api_key=os.environ["QIANFAN_ACCESS_TOKEN"]
)
response = client.chat.completions.create(
    model="ernie-4.5",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Latest models (May 2026):** `ernie-5.1`, `ernie-4.5`, `ernie-x1.1` (reasoning), `ernie-4.5-turbo`

**Note:** Requires Baidu account (Chinese phone number for registration).

### Full Router Implementation

```python
import os, asyncio, subprocess
from google import genai
from google.api_core.exceptions import ResourceExhausted
from openai import OpenAI

GEMINI_KEY_POOL = [v for k, v in os.environ.items() if k.startswith("GEMINI_KEY_")]
_idx = 0

def _next_key():
    global _idx
    k = GEMINI_KEY_POOL[_idx % len(GEMINI_KEY_POOL)]
    _idx += 1
    return k

def _is_code_task(prompt):
    return any(kw in prompt.lower() for kw in ["write code","implement","function","class","script","debug","refactor","fix the"])

async def _gemini_flash(prompt):
    for key in GEMINI_KEY_POOL:
        try:
            client = genai.Client(api_key=key)
            return client.models.generate_content(model="gemini-2.5-flash", contents=prompt).text
        except ResourceExhausted:
            continue
    return None

async def _gemini_pro(prompt):
    try:
        client = genai.Client(api_key=_next_key())
        return client.models.generate_content(model="gemini-2.5-pro", contents=prompt).text
    except ResourceExhausted:
        return None

def _codex(prompt):
    try:
        env = {**os.environ, "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY","")}
        r = subprocess.run(["codex","--approval-mode","full-auto",prompt],
                           capture_output=True, text=True, env=env, timeout=120)
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None

def _ernie(prompt):
    try:
        c = OpenAI(base_url="https://aistudio.baidu.com/llm/lmapi/v3",
                   api_key=os.environ.get("QIANFAN_ACCESS_TOKEN",""))
        r = c.chat.completions.create(model="ernie-4.5",
            messages=[{"role":"user","content":prompt}], timeout=30)
        return r.choices[0].message.content
    except Exception:
        return None

def _local(prompt):
    try:
        c = OpenAI(base_url="http://localhost:8080/v1", api_key="none")
        r = c.chat.completions.create(model="local",
            messages=[{"role":"user","content":prompt}], timeout=60)
        return r.choices[0].message.content
    except Exception:
        return None

async def route(prompt: str, force_pro=False):
    if _is_code_task(prompt):
        if r := _codex(prompt): return {"response": r, "provider": "codex"}
    if not force_pro:
        if r := await _gemini_flash(prompt): return {"response": r, "provider": "gemini-flash"}
    if r := await _gemini_pro(prompt): return {"response": r, "provider": "gemini-pro"}
    if r := _ernie(prompt): return {"response": r, "provider": "ernie-4.5"}
    if r := _local(prompt): return {"response": r, "provider": "llama-local"}
    raise RuntimeError("All providers exhausted")
```

### LiteLLM Router (Simpler, Production-Grade)

```python
from litellm import Router

router = Router(
    model_list=[
        {"model_name": "primary", "litellm_params": {"model": "gemini/gemini-2.5-flash", "api_key": os.environ["GEMINI_API_KEY"]}},
        {"model_name": "primary", "litellm_params": {"model": "gemini/gemini-2.5-flash", "api_key": os.environ.get("GEMINI_KEY_2")}},
        {"model_name": "fallback", "litellm_params": {"model": "qianfan/ernie-4.5", "api_key": os.environ["QIANFAN_ACCESS_TOKEN"]}},
        {"model_name": "local", "litellm_params": {"model": "openai/local", "api_base": "http://localhost:8080/v1", "api_key": "none"}},
    ],
    fallbacks=[{"primary": ["fallback"]}, {"fallback": ["local"]}],
    allowed_fails=2,
    cooldown_time=60,
)
response = router.completion(model="primary", messages=[{"role": "user", "content": "Hello"}])
```

---

## 14. smolagents + qwen-agent + Gemini

### smolagents

```python
from smolagents import CodeAgent, LiteLLMModel
import os

os.environ["GEMINI_API_KEY"] = "your-key"
model = LiteLLMModel(model_id="gemini/gemini-2.5-flash", temperature=0.1)
agent = CodeAgent(tools=[], model=model)
result = agent.run("Calculate the first 20 Fibonacci numbers")
```

**CodeAgent** (recommended) vs ToolCallingAgent: CodeAgent uses ~30% fewer LLM steps, better for compute/file tasks. Use ToolCallingAgent for structured API workflows.

**Termux install:**
```bash
pip install smolagents[litellm]
export GEMINI_API_KEY=your-key
```
No known ARM64 issues.

### qwen-agent

```python
from qwen_agent.llm import get_chat_model

# Method 1: Native Gemini
llm = get_chat_model({'model': 'gemini-2.5-flash', 'api_key': 'key', 'model_type': 'gemini'})

# Method 2: OpenAI-compat (better for tool use)
llm = get_chat_model({'model': 'gemini-2.5-flash',
    'model_server': 'https://generativelanguage.googleapis.com/v1beta/openai/',
    'api_key': 'key', 'model_type': 'openai'})
```

Use Method 2 for function calling and MCP integration.

---

## 15. Advanced Patterns

### Context Caching

```python
import datetime
cache = client.caches.create(
    model="gemini-2.5-flash",
    config=types.CreateCachedContentConfig(
        contents=[types.Content(parts=[types.Part(text="...large doc...")], role="user")],
        system_instruction="You are an expert analyst.",
        ttl=datetime.timedelta(hours=1),
    )
)
response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Summarize key findings.",
    config=types.GenerateContentConfig(cached_content=cache.name)
)
```

Implicit caching (Gemini 2.5+): 90% discount on repeated prefix tokens automatically.
Minimum for explicit cache: 32,768 tokens (2.5 Flash), 1,024 tokens (2.5 Flash-Lite).

### Structured Output

```python
from pydantic import BaseModel
from typing import Literal

class Product(BaseModel):
    name: str; price: float; in_stock: bool
    category: Literal["electronics", "clothing", "food"]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Extract: Blue denim jeans, $49.99, available",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Product,
    )
)
product = Product.model_validate_json(response.text)
```

### Function Calling + Parallel Tool Execution

```python
async def run_parallel_tools():
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents="Weather in London and stock price of GOOG?",
        config=types.GenerateContentConfig(tools=[weather_tool, stock_tool])
    )
    fn_calls = [p.function_call for p in response.candidates[0].content.parts if p.function_call]
    results = await asyncio.gather(*[execute_tool(fc.name, dict(fc.args)) for fc in fn_calls])
    fn_response_parts = [types.Part.from_function_response(name=fc.name, response=r)
                         for fc, r in zip(fn_calls, results)]
    final = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Content(parts=fn_response_parts, role="function")]
    )
    return final.text
```

### Batch Processing (50% cheaper)

```python
batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src=types.CreateBatchJobRequest(
        inline_requests=[{"key": f"req_{i}", "request": {"contents": [{"parts": [{"text": f"Prompt {i}"}]}]}} for i in range(100)]
    )
)
while batch_job.state not in ("JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED"):
    time.sleep(30)
    batch_job = client.batches.get(name=batch_job.name)
```

Max 2GB input JSONL, 24h turnaround. Accepts OpenAI-format JSONL.

### Gemini Multimodal — File API

```python
# Upload once, reference for 48h
file_ref = client.files.upload(path=pathlib.Path("doc.pdf"))
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[types.Part.from_uri(file_uri=file_ref.uri, mime_type="application/pdf"),
              "Summarize key findings."]
)
```

Formats: JPEG/PNG/WebP images (5GB), MP4/MOV video (5GB), MP3/WAV audio (8.4h), PDF, text.

### Token Counting (Free)

```python
count = client.models.count_tokens(model="gemini-2.5-flash", contents="your content")
print(count.total_tokens)   # never billed
```

### Safety Filters (Legitimate Config)

```python
config = types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
    ]
)
```

Valid thresholds: `BLOCK_NONE`, `BLOCK_ONLY_HIGH`, `BLOCK_MEDIUM_AND_ABOVE`, `BLOCK_LOW_AND_ABOVE`.

---

## Quick Reference: Key URLs

| Resource | URL |
|----------|-----|
| AI Studio | https://aistudio.google.com |
| API Keys | https://aistudio.google.com/app/apikey |
| Rate Limits | https://ai.google.dev/gemini-api/docs/rate-limits |
| Models | https://ai.google.dev/gemini-api/docs/models |
| Pricing | https://ai.google.dev/gemini-api/docs/pricing |
| OpenAI Compat | https://ai.google.dev/gemini-api/docs/openai |
| Batch API | https://ai.google.dev/gemini-api/docs/batch-api |
| Live API | https://ai.google.dev/gemini-api/docs/live-api |
| Context Caching | https://ai.google.dev/gemini-api/docs/caching |
| Function Calling | https://ai.google.dev/gemini-api/docs/function-calling |
| Python SDK | https://github.com/googleapis/python-genai |
| JS SDK | https://github.com/googleapis/js-genai |
| gemini-cli | https://github.com/google-gemini/gemini-cli |
| Cookbook | https://github.com/google-gemini/cookbook |
| MediaPipe LLM (Android) | https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference/android |
| Firebase AI Logic | https://firebase.google.com/products/firebase-ai-logic |
| LiteLLM Gemini | https://docs.litellm.ai/docs/providers/gemini |

---

*Token estimate: ~18,000 tokens. Compiled from 4 parallel research agents, 2026-05-25.*
