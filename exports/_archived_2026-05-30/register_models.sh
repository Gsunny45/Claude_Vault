#!/bin/bash
# Mad Max model registration — runs in background, logs to ~/ai/register.log
LOG=~/ai/register.log
echo "=== Model Registration Started: $(date) ===" > "$LOG"

# Pull nomic-embed-text (needed for RAG/AnythingLLM)
echo "[1/4] Pulling nomic-embed-text..." >> "$LOG"
ollama pull nomic-embed-text >> "$LOG" 2>&1
echo "[1/4] Done: $(date)" >> "$LOG"

# Register DeepSeek-R1 7B
echo "[2/4] Creating deepseek-r1-7b..." >> "$LOG"
ollama create deepseek-r1-7b -f ~/ai/Configs/Modelfile.deepseek-r1-7b >> "$LOG" 2>&1
echo "[2/4] Done: $(date)" >> "$LOG"

# Register LFM2 2.6B
echo "[3/4] Creating lfm2-2b..." >> "$LOG"
ollama create lfm2-2b -f ~/ai/Configs/Modelfile.lfm2-2b >> "$LOG" 2>&1
echo "[3/4] Done: $(date)" >> "$LOG"

# Register Qwen2.5-Coder 1.5B
echo "[4/4] Creating coder-1.5b..." >> "$LOG"
ollama create coder-1.5b -f ~/ai/Configs/Modelfile.coder-1.5b >> "$LOG" 2>&1
echo "[4/4] Done: $(date)" >> "$LOG"

echo "=== All Done: $(date) ===" >> "$LOG"
echo "COMPLETE" >> "$LOG"
