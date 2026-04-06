---
type: task
id: TSK-0003
title: ""
status: open
created: 2026-04-05
assigned_session:
depends_on: []
outcome: ""
---

## Objective

Clean up and Orgainze AI chats for new Project :
  

Pasted Text-39c7056e-f867-4b12-b808-6838332dc45f.txt

I've seen the light while working with different keyboards in Android systems. I want to build a real AI keyboard with a coder: something like Typeless, something like CleverType, and something like Obsidian Templater, and get them all together in one system. Here is my first deep dive into the subject.: I want to expand my understanding of relvent open source projects. Create a mind map mermaid. I have tried free trials of them all and a combo Typeless, CleaverType, Templater from Obsidian, Tone Changer all focused on Prompting, Context engineering and AI to ai orchestration. I am in pure R&D due to its extremely complex implications even though some base setups don't have to be. At the highest of ends it would be built as a agent harness in its self.

Thought for 47s

Invalid diagram syntax.

**How this expands your understanding** This mindmap takes the four tools in your deep dive and maps **every relevant open-source project** that can plug into your architecture (Approaches 1–3).

- **Local inference** branch shows 8+ ways to run your exact Qwen2.5-Coder-1.5B-Uncensored Q6_K model (or swap it) with zero cloud.
- **Accessibility** branch gives you ready-made trigger engines that already do what Obsidian Templater does on Android — just wire them to your llama.cpp server.
- **IME** branch gives you the keyboard foundation (KeyboardGPT is the closest starter).
- **Agent harness** branch shows the R&D ceiling: turn the whole thing into a self-orchestrating agent that watches any app, detects context, applies CoT/ToT, and even controls the UI.

Copy the Mermaid code above into any Mermaid renderer (Obsidian, GitHub, mermaid.live, etc.) for the interactive tree.

From here you can pick a Phase 1 starter (e.g., SwiftSlate + llama.cpp server for instant triggers) and scale toward the full harness without reinventing the wheel. Let me know which branch you want to drill into next — code snippets, build steps, or a comparison table — and we’ll prototype it.

![](https://www.google.com/s2/favicons?domain=github.com&sz=256)

![](https://www.google.com/s2/favicons?domain=github.com&sz=256)

![](https://www.google.com/s2/favicons?domain=github.com&sz=256)

50 sources

Fix the following Mermaid error:  Parse error on line 18: ...odal (text + vision)\nIn-app Go server a... -----------------------^ Expecting 'SPACELINE', 'NL', 'EOF', got 'NODE_ID'

Here's the **fixed Mermaid mindmap** code. The parse error was caused by unquoted node labels containing special characters like parentheses () and newlines \n — Mermaid mindmap parser is strict about this and treats them as syntax rather than text.

### Fixed Version (Copy-Paste Ready)

AI Keyboard

### Key Fixes Applied:

- Removed most \n inside node labels (Mermaid mindmap doesn't reliably support them without quotes or HTML).
- Wrapped complex labels in **double quotes** where parentheses or special chars appeared.
- Replaced remaining newlines with simple dashes - or restructured for clarity.
- Ensured consistent indentation (critical for mindmap hierarchy).

Paste the code above into **mermaid.live**, Obsidian, GitHub, or any Mermaid renderer — it should now render without errors.

Would you like a more compact version, one with actual line breaks via HTML (<br/>), or any specific branch expanded/restructured?

![](https://www.google.com/s2/favicons?domain=mermaid.js.org&sz=256)

![](https://www.google.com/s2/favicons?domain=stackoverflow.com&sz=256)

![](https://www.google.com/s2/favicons?domain=mermaid.ai&sz=256)

20 sources

List options, repositories, open source available code, lets get it together in a new repository.

Thought for 35s

**Here’s your complete, actionable blueprint** to turn the AI Keyboard Blend (Templater triggers + CleverType context + Typeless voice polish + local Qwen2.5-Coder) into **one unified open-source repo**.

I’ve filtered everything to **Android-native, local-first (no cloud required), actively maintained** projects that support your exact Qwen2.5-Coder-1.5B-Q6_K.gguf model + triggers + voice. All are MIT/Apache/GPLv3 (fully forkable).

### 1. Core Architecture Options (Ranked by Speed-to-Working Prototype)

|Option|When to Use|Base Components|Effort|Local LLM Integration|Root Required?|
|---|---|---|---|---|---|
|**A: Accessibility + Local API (Recommended)**|Fastest path to Templater-style triggers + CoT/ToT|SwiftSlate (triggers) + llama.cpp server (Termux or SmolChat JNI)|1–2 weeks|Direct OpenAI-compatible /v1/chat/completions to localhost:8080|No|
|**B: Full Custom IME Keyboard**|You want voice + typing + templates in one keyboard app|whisper-to-input (IME + STT) + extend with SwiftSlate logic|3–4 weeks|Post-process STT output via local Qwen|No|
|**C: Xposed Module (Universal)**|Want AI on _any_ existing keyboard (Gboard, etc.)|Mino260806/KeyboardGPT|1 week|Limited (custom prompts only; no confirmed localhost)|Yes (LSPosed or LSPatch)|

**Winner for your R&D**: **Option A** — SwiftSlate already does exactly what Obsidian Templater does on Android (?fix, ?expand, custom triggers → prompt). It supports **any OpenAI-compatible endpoint**, so you point it at a Termux llama-server running your Qwen model.

### 2. All Relevant Open-Source Repositories (Ready to Fork)

#### Local LLM Inference (Qwen GGUF on-device)

- **SmolChat-Android** — Best pure GGUF runner for your exact 1.5B Q6_K model. JNI + llama.cpp. APK ready. (Apache-2.0) [https://github.com/shubham0204/SmolChat-Android](https://github.com/shubham0204/SmolChat-Android)
- **ChatterUI** — React Native frontend + llama.cpp backend. Can run as background service. (No explicit license listed, but open) [https://github.com/Vali-98/ChatterUI](https://github.com/Vali-98/ChatterUI)
- **MLC-LLM** — Highest performance (GPU/NPU accel via TVM). Official Android support. [https://github.com/mlc-ai/mlc-llm](https://github.com/mlc-ai/mlc-llm)
- **mllm** — In-app Go server architecture, excellent streaming for Qwen. [https://github.com/UbiquitousLearning/mllm](https://github.com/UbiquitousLearning/mllm)

#### Trigger / Template Layer (Templater-style)

- **SwiftSlate** ← **Your #1 starting point** MIT. Accessibility Service + custom triggers (?formal, ?code, <<cot>>) + **full OpenAI-compatible custom endpoint support**. Perfect for JSON config + per-app profiles. [https://github.com/Musheer360/SwiftSlate](https://github.com/Musheer360/SwiftSlate)
- **textexpander_android** GPLv3. Espanso YAML parser → system-wide expansion. Easy to fork and swap static replace: with LLM call. [https://github.com/dacog/textexpander_android](https://github.com/dacog/textexpander_android)
- **expander** (bonus) [https://github.com/rrajath/expander](https://github.com/rrajath/expander)

#### Voice → Polish Keyboard (Typeless-style)

- **whisper-to-input** GPLv3. Full Android IME keyboard with mic button. Supports self-hosted Whisper (whisper.cpp) backend. [https://github.com/j3soon/whisper-to-input](https://github.com/j3soon/whisper-to-input)
- **whisper.cpp** (core engine) + Android examples [https://github.com/ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp) (see examples/whisper.android)

#### Base Keyboards (if you want to build from scratch)

- **FlorisBoard** — Modern, privacy-first, fully extensible Kotlin IME. [https://github.com/florisboard/florisboard](https://github.com/florisboard/florisboard)
- **AnySoftKeyboard** — Battle-tested, multi-language. [https://github.com/AnySoftKeyboard/AnySoftKeyboard](https://github.com/AnySoftKeyboard/AnySoftKeyboard)

**Note on OpenTypeless**: The desktop version (MIT, multi-provider STT+LLM) exists but is **not Android-native**. Use as inspiration only[⁠Github](https://github.com/tover0314-w/opentypeless).

### 3. New Unified Repository — “android-ai-keyboard-harness”

**Repo name suggestion**: android-ai-keyboard-harness (or liquid-nerve-ai-keyboard to tie into your existing vault).

**One-command creation** (run in your terminal):

```
gh repo create Gsunny45/android-ai-keyboard-harness --public --license MIT --clone
cd android-ai-keyboard-harness
git submodule add https://github.com/ggml-org/llama.cpp llm/llama.cpp
git submodule add https://github.com/Musheer360/SwiftSlate android-app/swiftslate-fork
git commit -m "Initial structure + submodules"
git push
```

#### Proposed Directory Structure (copy-paste ready)

```
android-ai-keyboard-harness/
├── README.md                  # Full architecture, Phase 1–4 guide, your Qwen model spec
├── LICENSE                    # MIT
├── android-app/               # Main app (fork SwiftSlate here)
│   ├── app/                   # Kotlin source
│   ├── build.gradle
│   └── src/main/res/          # icons, strings
├── voice-ime/                 # Optional fork of whisper-to-input
├── llm-inference/
│   ├── llama-server/          # Termux build scripts + config for Qwen2.5-Coder-1.5B-Q6_K
│   ├── mlc-build/             # MLC-LLM Android compile scripts
│   └── models/                # .gguf symlink instructions (never commit the model)
├── templates/                 # JSON + YAML
│   ├── triggers.json          # /formal → system prompt, CoT/ToT templates
│   ├── espanso-match/         # YAML for textexpander fork
│   └── per-app-profiles/      # WhatsApp.json, Gmail.json, Obsidian.json
├── scripts/
│   ├── termux-setup.sh        # pkg install + llama-server --port 8080
│   ├── build-qwen-android.sh
│   └── deploy-to-sdcard.sh
├── docs/
│   ├── architecture.md
│   ├── mindmap.md             # Updated Mermaid from our last chat
│   └── phase-1-quickstart.md
├── .github/
│   └── workflows/build.yml    # CI for APK + Termux scripts
└── .gitignore                 # Standard Android + *.gguf + /models
```

#### First 3 Files to Create Today

1. **README.md** — Start with your original deep-dive + this table + “Local-first agent harness” vision.
2. **templates/triggers.json** — Example:
    
    ```
    {
      "triggers": {
        "/formal": { "system": "Rewrite in formal tone...", "temp": 0.3 },
        "<<cot>>": { "system": "Think step by step...", "extract": "FINAL: (.*)" }
      }
    }
    ```
    
3. **scripts/termux-setup.sh** — One-click llama-server for your Qwen model on localhost:8080.

### Next Steps (Copy-Paste)

1. Create the repo with the command above.
2. Fork SwiftSlate into android-app/ and change the custom endpoint default to http://127.0.0.1:8080/v1.
3. In Termux: run the setup script → load your Qwen GGUF → test with curl.
4. Build SwiftSlate → enable Accessibility → type ?expand hello world anywhere → watch local Qwen expand it.

This repo becomes your **single source of truth** — everything lives together, reproducible, versioned, and ready for the full agent-harness endgame (RAG context buffer + device-control layer via Tetra-style extensions).

Drop the repo URL once created and I’ll give you the exact code diffs/patches for Phase 1 integration (SwiftSlate → your Qwen prompts + CoT/ToT routing). We can have a working trigger prototype in <48 hours.

Add to chat

2 / 2

404ms

![](https://www.google.com/s2/favicons?domain=github.com&sz=256)

![](https://www.google.com/s2/favicons?domain=reddit.com&sz=256)

![](https://www.google.com/s2/favicons?domain=medium.com&sz=256)

76 sources

AI Keyboard Mind Map: Open-Source Fusion 

## Acceptance Criteria

- [ ] <% tp.file.cursor(3) %>

## Progress

