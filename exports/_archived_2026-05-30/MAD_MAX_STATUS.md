---
type: knowledge
id: KNW-MAD-MAX-001
subject: Mad Max LLM Stack — Build Status
confidence: verified
last_verified: 2026-04-17
---

# Mad Max LLM Stack — Build Status
> Full offline, mesh-ready AI stack. Assumes internet is permanently gone.

---

## ✅ DONE

| Component | Status | Details |
|-----------|--------|---------|
| Kali MCP server | Live | `/home/biocyberswarwAI/mcp/kali_mcp.py` — shell, nmap, msf, file ops |
| Ubuntu symlinks | Done | ~/vault, ~/docs, ~/ai, ~/rag, ~/n8n, ~/force-mult all linked to Windows |
| Kali symlinks | Done | ~/vault, ~/docs, ~/ai, ~/rag all linked |
| n8n | Installed | localhost:5678, Docker inside Ubuntu WSL. Start: `docker start n8n_local` |
| Quick Capture workflow | Imported | POST /webhook/capture → writes .md to Local-Network-Hub/03-Inbox/ |
| nomic-embed-text | Registered | 274MB — needed for AnythingLLM RAG embeddings |
| OpenClaw gateway.mode | Fixed | Changed from "remote" to "local" in ~/.openclaw/openclaw.json |
| Obsidian REST API | Located | Port 27123, key: 6912a564d7fbbf5003c1f9f20c1eaf7b7e8de48abad8c491637e58669b4393b7 |
| AnythingLLM | Configured | LLM: Ollama qwen3:8b @ http://localhost:11435, Embed: nomic-embed-text |
| ollama_bridge.py | Written | 0.0.0.0:11435 → 127.0.0.1:11434. Start: `wsl -d Ubuntu -- bash -c "nohup python3 ~/vault/ollama_bridge.py &"` |
| daily-briefing-offline.json | Written | Uses Ollama qwen3:8b, saved to vault/n8n-workflows/ |
| All 7 Ollama models | Registered | See model registry below |
| .wslconfig memory cap | Fixed | Changed from 9GB → 4GB. WSL now capped. File: C:\Users\MarsBase\.wslconfig |
| Docker Desktop startup | Removed | No longer auto-starts on boot (was silently consuming 1.5GB Hyper-V VM) |

---

## ⚠️ NEEDS YOUR ACTION

### 1. CRITICAL — Bind Ollama to 0.0.0.0 (required for Windows apps + mesh)
ollama_bridge.py is the current workaround (port 11435). Proper fix requires sudo:

```bash
# In Ubuntu WSL terminal:
sudo mkdir -p /etc/systemd/system/ollama.service.d
echo -e '[Service]\nEnvironment="OLLAMA_HOST=0.0.0.0:11434"' | sudo tee /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

Verify: `ss -tlnp | grep 11434` → should show `0.0.0.0:11434`
After this: update AnythingLLM URL from 11435 → 11434, and ollama_bridge.py is no longer needed.

### 2. Make ollama_bridge.py persistent
Currently requires manual start each session. Add to Ubuntu WSL startup:

```bash
# In Ubuntu WSL — add to /etc/profile.d/ or systemd user service
# Quick fix (add to ~/.bashrc — runs when you open WSL):
echo 'pgrep -f ollama_bridge.py > /dev/null || nohup python3 ~/vault/ollama_bridge.py > /tmp/bridge.log 2>&1 &' >> ~/.bashrc
```

### 3. Import daily-briefing-offline.json into n8n
- Start n8n: `wsl -d Ubuntu -- docker start n8n_local`
- Open http://localhost:5678
- Menu → Workflows → Import from file
- File: `C:\Users\MarsBase\Documents\Claude_Vault\n8n-workflows\daily-briefing-offline.json`
- Activate the workflow

⚠️ n8n was caught pegging CPU at 99% — check logs before activating any workflows:
```bash
wsl -d Ubuntu -- docker logs n8n_local --tail 50
```

### 4. RAG — Ingest documents into AnythingLLM (NEXT PRIORITY)
AnythingLLM is configured (LLM + embeddings) but NO documents ingested yet.
Steps:
- Open AnythingLLM
- Create a new workspace (e.g. "Claude Vault", "Force Mult")
- Click Upload Documents → select folder → pick files from C:\Users\MarsBase\Documents\Claude_Vault
- Start with: knowledge/, decisions/, sessions/ folders
- For Force Multiplication v1 (1600+ files): ingest in batches by topic folder
- After ingestion, test with a question about vault content

### 5. OpenClaw — connect while internet still works
OpenClaw needs CLAUDE_AI_SESSION_KEY. Get it from browser devtools while logged into claude.ai:
- Open claude.ai in browser → F12 → Application → Cookies → find sessionKey
- Add to ~/.openclaw/openclaw.json: `"session_key": "YOUR_KEY_HERE"`
- gateway.mode is already set to "local" ✅

---

## 🔴 DEPRIORITIZED

| Item | Reason |
|------|--------|
| Gemma-4 Q8 (8.1GB) | Too large for 16GB RAM alongside Ollama. Skip unless running alone. |
| Obsidian REST API from WSL/Docker | Port 27123 is bound to 127.0.0.1 only. Workaround: filesystem access via /mnt/docs/ |

---

## Ollama Model Registry — All Registered ✅

| Model | Size | Use Case | RAM pressure |
|-------|------|----------|-------------|
| qwen3:8b | 5.2GB | General reasoning, daily briefing | HIGH — don't run with other apps open |
| qwen2.5-coder:7b | 5.4GB | Code generation | HIGH |
| deepseek-r1-7b | 4.5GB | Heavy reasoning, problem solving | HIGH |
| nu11secur1tyAIRedTeam | 2.5GB | Security/red team tasks | MEDIUM |
| lfm2-2b | 1.6GB | Fast responses | LOW |
| coder-1.5b | 1.3GB | Lightweight code completion | LOW |
| nomic-embed-text | 274MB | Embeddings/RAG (AnythingLLM) | MINIMAL |

**RAM budget for AnythingLLM RAG on 16GB:**
- Best combo: nomic-embed-text (always loaded for RAG) + lfm2-2b or coder-1.5b for chat = ~3GB model RAM total
- Close AnythingLLM + load qwen3:8b solo = up to 5.2GB model RAM
- NEVER: qwen3:8b + n8n + AnythingLLM simultaneously → OOM risk

---

## Memory — What vmmem/vmmemWSL Actually Are

**This comes up every session. Explanation:**

- `vmmemWSL` = the WSL2 Linux virtual machine. It exists whenever WSL is running. YOU CANNOT KILL IT. It holds memory for Ubuntu and Kali. It is not a problem — it's the engine.
- `vmmem` (non-WSL) = Docker Desktop's Hyper-V VM. This was auto-starting and wasting 1.5GB. FIXED: removed from Windows startup registry. Will not return after next reboot.
- Task Manager "End Task" on these = denied by design. They are hypervisor processes.
- **Baseline after next clean boot:** vmmemWSL ~800MB-1.2GB (WSL idle), vmmem GONE.

**WSL memory cap:** C:\Users\MarsBase\.wslconfig → memory=4GB (was 9GB, fixed 2026-04-17)

---

## Startup Bloat — Other Items Still Auto-Starting

These are NOT removed but eat RAM on every boot. Remove if not needed daily:
- Google Drive File Stream (~150MB)
- Chrome auto-launch
- Perplexity auto-launch
- Canva auto-launch
- Postman Agent
- Typeless
- OneDrive (if not used)

To remove any: `regedit → HKCU\Software\Microsoft\Windows\CurrentVersion\Run → delete key`

---

## n8n — Run On Demand, Not Always-On

n8n was consuming 99.8% CPU in WSL Docker. Stop/start as needed:

```bash
# Start n8n
wsl -d Ubuntu -- docker start n8n_local

# Stop n8n  
wsl -d Ubuntu -- docker stop n8n_local

# Check logs
wsl -d Ubuntu -- docker logs n8n_local --tail 50
```

n8n Docker is inside Ubuntu WSL (not Windows Docker Desktop). Restart policy: unless-stopped (won't auto-start after manual stop).

---

## Key Ports

| Port | Service | Bound To | Notes |
|------|---------|----------|-------|
| 11434 | Ollama | 127.0.0.1 | Fix pending (needs sudo) |
| 11435 | ollama_bridge.py | 0.0.0.0 | Workaround — must be running |
| 5678 | n8n | localhost (WSL Docker) | Start manually |
| 27123 | Obsidian REST API | 127.0.0.1 | Windows only |
| 27124 | Local-Network-Hub REST | localhost | |

---

## Mesh Networking (Phase 2 — TODO)

Requirements:
- Ollama bound to 0.0.0.0:11434 (pending sudo fix above)
- Hardware: at least 2 nodes with WiFi/Ethernet

Next steps when hardware ready:
1. Install tailscale: `curl -fsSL https://tailscale.com/install.sh | sh`
2. Or batman-adv for true mesh (no coordinator)
3. Expose Ollama, n8n webhooks across mesh

---

*Last updated: 2026-04-17*
