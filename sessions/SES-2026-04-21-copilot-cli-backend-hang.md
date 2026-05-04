---
type: session
id: SES-2026-04-21-copilot-cli-backend-hang
date: 2026-04-21
agent: claude-haiku-4-5
status: archived
tokens: 2400
---

# Copilot CLI Backend Hang Investigation

## Summary
Tested GitHub Copilot CLI v1.0.34 in PowerShell 7. Identified root cause of indefinite hangs: **MCP client connects successfully to GitHub's Copilot API, but model inference requests never complete.** Auth is working (logs show "Welcome Gsunny45!"), but actual command execution hangs waiting for AI model response.

## Key Findings

### What Works
- Authentication: Logged in as Gsunny45 via keyring (correct token scopes: gist, read:org, repo, workflow)
- GitHub config: Properly set (git_protocol=https)
- MCP client connection: Succeeds in 527–2130ms (logs show "MCP client for github-mcp-server connected")
- Version check: Up-to-date (v1.0.34)

### What Hangs
- **Model inference requests never return.** Logs show:
  ```
  [INFO] Using default model: gpt-5-mini
  [INFO] --- Start of group: Sending request to the AI model ---
  [INFO] --- End of group ---
  ```
  But the time between start and end is 9–45 seconds with no response, causing the CLI binary to hang indefinitely waiting for completion.

### Diagnostics Performed
- Ran `copilot_diagnostics.ps1` with 5-second timeouts (previous session)
- Executed actual Copilot logs from `C:\Users\MarsBase\.copilot\logs\`
- Analyzed 5 most recent process logs (timestamps 08:56–09:06 on 2026-04-21)

## Root Cause
Not a network connectivity or auth issue — the MCP client connects and authenticates successfully. The hang occurs **during AI model inference**, specifically when the CLI sends a completion request to GitHub's backend and waits for the model (gpt-5-mini) to respond.

Possible causes:
1. **Model service timeout** — GitHub's inference backend is slow or timing out
2. **Token quota exceeded** — Copilot account may have API rate limits or quota exhaustion
3. **Regional/service degradation** — API endpoint may be experiencing issues
4. **CLI bug** — Binary may have a read timeout bug preventing graceful failure

## Next Steps (for future session)
1. Check GitHub Copilot account status (free vs. paid, API access enabled)
2. Review GitHub system status page for Copilot API availability
3. Test with explicit timeout: `timeout 10s gh copilot explain "code"`
4. Try with different model if CLI supports it: `gh copilot explain --model gpt-4`
5. Check for rate-limiting headers in network trace (tcpdump or Fiddler)

## Files Generated
- `C:\Users\MarsBase\Desktop\copilot_diagnostics.ps1` — diagnostic script with timeout protection
- `C:\Users\MarsBase\Desktop\copilot_gh_test.ps1` — original test script (hangs indefinitely)
- Full logs in `C:\Users\MarsBase\.copilot\logs\process-*.log`

## Work Paused
User requested deletion of this chat and archival of findings to Claude_Vault.
