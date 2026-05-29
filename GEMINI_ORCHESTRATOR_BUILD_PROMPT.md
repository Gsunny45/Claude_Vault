# Gemini Orchestrator — Build Prompt Package
*Drop this into AI Studio System Instructions. Current model IDs as of May 2026.*

---

## CORRECT MODEL IDs (May 2026)

| Use Case | Model ID | Tier |
|----------|----------|------|
| Daily orchestrator (free) | `gemini-3.5-flash` | Free tier GA |
| Heavy reasoning | `gemini-3.1-pro-preview` | Paid only ($2/$12 per 1M) |
| Fast/cheap bulk | `gemini-3.1-flash-lite` | GA |
| Local worker (on-device) | `gemma4:e4b` | Ollama, ~5GB RAM |
| Local worker (desktop) | `gemma4:26b` | Ollama, ~14-18GB RAM |

> **Note on your Gemma download:** Gemma 4 has no 9B or 12B variant.
> Sizes are: e2b / e4b / 26b (MoE) / 31b (Dense).
> If you pulled something labeled 12B, that is Gemma 3 — still excellent for local work.
> On your 16GB i5-1335U, `gemma4:e4b` runs clean. `gemma4:26b` will page and be slow.

---

## PART 1 — AI STUDIO SYSTEM PROMPT
*Paste this into AI Studio → System Instructions for Gemini 3.5 Flash or 3.1 Pro*

```
You are Gemini Orchestrator, the reasoning and routing core of Hermetic OS — a multi-agent AI stack running on Windows 11 with WSL2 Kali, Termux on Android (Moto G 5G + Note 20 Ultra), and a multi-vault Obsidian system.

## Your Role
You are the PLANNER and VERIFIER. You do not execute code directly.
You delegate execution to specialized agents:
- **Codex CLI** — code generation and file edits (routes via OpenAI Codex)
- **Ernie Bot** — fallback LLM when quota is exhausted
- **Gemma 4 local** — on-device inference via Ollama at localhost:11434
- **smolagents CodeAgent** — Python execution sandbox
- **qwen-agent** — tool-calling and MCP workflows

## Your Stack Context
- OS: Windows 11 + WSL2 Kali Linux
- Local model server: Ollama at http://localhost:11434 (running gemma4:e4b or gemma4:26b)
- Agent harness: C:\Users\MarsBase\Documents\Agents\claude_code_delegate.py
- Vault system: Claude_Vault (AI ops), Command_Vault (monitoring), Local-Network-Hub (orchestration), RAG_Vault (retrieval)
- Termux stack: aichat (gemini backend), llm+llm-gemini, Termux:API scripts
- Android devices: Moto G 5G (Snapdragon 778G), Note 20 Ultra (Exynos 990)

## Routing Rules
1. **Code tasks** → delegate to Codex CLI with exact file paths and requirements
2. **Obsidian vault ops** → delegate to Gemini Scribe (HTTP MCP) or Local REST API
3. **Long reasoning / research** → use your own context window, then summarize to vault
4. **On-device Android tasks** → route Termux aichat commands or Termux:API scripts
5. **Quota exhausted (429)** → route to Ernie Bot (ernie-4.5 via qianfan)
6. **Offline** → route to local Ollama (gemma4:e4b at localhost:11434)

## Response Format
Always structure your output as:

PLAN:
[numbered steps]

DELEGATE:
agent: [codex | ernie | gemma4-local | smolagents | qwen-agent | termux]
task: [exact instruction]
context: [file paths, constraints, expected output format]

VERIFY:
[how you will check the result]

## Constraints
- Token budget awareness: prefer gemini-3.5-flash for bulk; use gemini-3.1-pro-preview only for deep reasoning tasks
- Never duplicate work already in vault knowledge notes
- All outputs go to C:\Users\MarsBase\Desktop\Hermes_Drop_vault\ unless specified
- Log non-obvious decisions to Claude_Vault/decisions/
```

---

## PART 2 — aichat Config (Termux + Desktop)
*Drop at `~/.config/aichat/config.yaml`*

```yaml
# Updated May 2026 — correct Gemini 3.x model IDs
model: gemini:gemini-3.5-flash

clients:
  - type: gemini
    api_key: $GEMINI_API_KEY
    models:
      - name: gemini-3.5-flash
        max_input_tokens: 1000000
        supports_function_calling: true
        supports_vision: true
      - name: gemini-3.1-pro-preview
        max_input_tokens: 1000000
        supports_function_calling: true
        supports_vision: true
      - name: gemini-3.1-flash-lite
        max_input_tokens: 1000000
        supports_function_calling: true

  - type: ollama
    api_base: http://localhost:11434
    models:
      - name: gemma4:e4b
        max_input_tokens: 8192
      - name: gemma4:26b
        max_input_tokens: 16384

  - type: openai-compatible
    name: ernie
    api_base: https://aistudio.baidu.com/llm/lmapi/v3
    api_key: $QIANFAN_ACCESS_TOKEN
    models:
      - name: ernie-4.5
        max_input_tokens: 8192

role: |
  You are Gemini Orchestrator running inside Hermetic OS.
  Route tasks: code→Codex, vault ops→Obsidian REST API, offline→Ollama gemma4.
  Structure output as PLAN / DELEGATE / VERIFY.
```

---

## PART 3 — smolagents Script (Desktop WSL)

```python
#!/usr/bin/env python3
"""
hermetic_agent.py — Gemini 3.5 Flash orchestrator over smolagents
Drop at: C:\Users\MarsBase\Documents\Agents\hermetic_agent.py
Run from WSL2: python hermetic_agent.py "your task"
"""

import os, sys
from smolagents import CodeAgent, LiteLLMModel
from smolagents.tools import DuckDuckGoSearchTool, PythonInterpreterTool

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")

gemini_flash = LiteLLMModel(model_id="gemini/gemini-3.5-flash", api_key=GEMINI_KEY, temperature=0.2)
gemini_pro   = LiteLLMModel(model_id="gemini/gemini-3.1-pro-preview", api_key=GEMINI_KEY, temperature=0.1)

from smolagents import OpenAIServerModel
gemma4_local = OpenAIServerModel(model_id="gemma4:e4b", api_base=f"{OLLAMA_BASE}/v1", api_key="ollama")

def pick_model(prompt, force_local=False):
    if force_local: return gemma4_local
    if any(kw in prompt.lower() for kw in ["analyze","architecture","design","compare","evaluate"]):
        return gemini_pro
    return gemini_flash

if __name__ == "__main__":
    task = " ".join(a for a in sys.argv[1:] if a != "--local") or input("Task: ")
    offline = "--local" in sys.argv
    model = pick_model(task, offline)
    agent = CodeAgent(tools=[PythonInterpreterTool(), DuckDuckGoSearchTool()], model=model, max_steps=8)
    print(f"\n[Hermetic] Using: {model.model_id}")
    result = agent.run(task)
    print(f"\n[RESULT]\n{result}")
    with open("/mnt/c/Users/MarsBase/Desktop/Hermes_Drop_vault/last_agent_result.txt", "w") as f:
        f.write(f"Task: {task}\nModel: {model.model_id}\n\nResult:\n{result}\n")
```

```bash
# Usage from WSL2
python hermetic_agent.py "summarize notes modified today in Claude_Vault"
python hermetic_agent.py "write a bash script to sync vault to Android" --local
```

---

## PART 4 — llm CLI (Termux + Desktop)

```bash
pip install llm && llm install llm-gemini llm-ollama
llm keys set gemini
llm models default gemini-3.5-flash

llm "your prompt"                                        # free tier
llm -m gemini-3.1-pro-preview "deep analysis"           # paid
llm -m gemma4:e4b "offline task"                        # local
```

---

## PART 5 — Ollama Pull Commands

```bash
ollama pull gemma4:e4b       # 5GB, runs clean on 16GB RAM — USE THIS
ollama pull gemma4:26b       # 14-18GB — test carefully on 16GB
ollama list                  # see what you actually have

# Start API server
ollama serve                 # exposes localhost:11434/v1 (OpenAI compat)
ollama run gemma4:e4b "Hello from Hermetic OS"
```

---

## QUICK REFERENCE

```
gemini-3.5-flash          free tier GA — daily driver
gemini-3.1-flash-lite     cheapest GA
gemini-3.1-pro-preview    paid only — heavy reasoning
gemma4:e4b                local, 16GB safe
gemma4:26b                local, 16GB tight
gemma3:12b                if that's what you downloaded — still works
ernie-4.5                 Gemini quota fallback
```
