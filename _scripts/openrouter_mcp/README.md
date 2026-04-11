# OpenRouter MCP Server

Multi-model AI gateway for Claude Vault orchestration stack.

## What This Does

Gives Claude (Desktop, Code, Cowork) direct access to 300+ AI models through one API key.
Includes automatic fallback chains — if one model fails, it tries the next.

## Tools

| Tool | Purpose |
|------|---------|
| `openrouter_chat` | Single-turn chat completion to any model |
| `openrouter_chat_multi` | Multi-turn conversation with history |
| `openrouter_chat_fallback` | Resilient chat — auto-tries next model on failure |
| `openrouter_list_models` | Browse/search available models with pricing |
| `openrouter_model_info` | Detailed specs for a specific model |
| `openrouter_check_credits` | Check account balance and usage |

## Setup

### 1. Install dependencies

```powershell
pip install mcp httpx pydantic
```

### 2. Set your API key

```powershell
# PowerShell (add to $PROFILE for persistence)
$env:OPENROUTER_API_KEY = "sk-or-v1-your-key-here"

# Or WSL/bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

### 3. Add to Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openrouter": {
      "command": "python",
      "args": ["C:\\Users\\MarsBase\\Documents\\Claude_Vault\\_scripts\\openrouter_mcp\\openrouter_mcp.py"],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-your-key-here"
      }
    }
  }
}
```

### 4. Add to Claude Code

```bash
claude mcp add openrouter -- python /path/to/openrouter_mcp.py
```

### 5. Test

```bash
python openrouter_mcp.py
```

## Default Fallback Chain

1. google/gemini-flash-1.5 (fast + cheap)
2. google/gemini-pro-1.5 (deep reasoning)
3. anthropic/claude-3.5-sonnet (balanced)
4. meta-llama/llama-3.1-70b-instruct (open-source)

Override with the `models` parameter on `openrouter_chat_fallback`.

## Architecture Reference

See KNW-0010 in Claude Vault for full system map.
This server is Integration #12 (OpenRouter API gateway) in KNW-0011.
