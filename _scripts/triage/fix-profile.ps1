# ─────────────────────────────────────────────────────────────
# fix-profile.ps1 — Surgical profile repair + HUD upgrade
# Date: 2026-04-21
# Safe to run multiple times (idempotent).
#
# What it does:
#   1. Backs up your current profile (.bak-YYYYMMDD-HHMMSS)
#   2. Removes ONLY the orphaned antigravity block (the cause of
#      the startup error and broken `code` command)
#   3. Escapes the Gemini API-key echo (stops leaking your key)
#   4. Guards the VS Code PATH append (stops duplicating every shell)
#   5. Removes the duplicate `function gemini` (dead code)
#   6. Upgrades Show-HUD to include: RAM, disk free, battery,
#      session clock (keeps everything you already had)
#
# What it does NOT do:
#   - Does not remove: ll, oc, gemini, code, model dispatcher,
#     vault shortcuts, drift guard, anything else.
#   - Does not touch files outside the profile.
#
# Rollback: your backup is at the same path with .bak-<timestamp>
# ─────────────────────────────────────────────────────────────

$ErrorActionPreference = 'Stop'
$profilePath = "$env:USERPROFILE\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"

if (-not (Test-Path $profilePath)) {
    Write-Host "Profile not found at $profilePath" -ForegroundColor Red
    Write-Host "Check: `$PROFILE.CurrentUserAllHosts" -ForegroundColor DarkGray
    exit 1
}

# 1. Backup
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = "$profilePath.bak-$stamp"
Copy-Item $profilePath $backup -Force
Write-Host "Backed up: $backup" -ForegroundColor Green

$c = Get-Content $profilePath -Raw

# 2. Remove orphaned antigravity block.
#    Matches the dangling $paths = @("~/antigravity"...) through its
#    closing } — safe because the block has no `function` header,
#    so it can't be confused with a real function body.
$pattern = '(?s)\r?\n\s*\$paths = @\("~/antigravity".*?\n\}\r?\n'
if ($c -match $pattern) {
    $c = $c -replace $pattern, "`r`n"
    Write-Host "Removed: orphaned antigravity block" -ForegroundColor Green
} else {
    Write-Host "Skip: antigravity block already removed" -ForegroundColor DarkGray
}

# 3. Fix the API key echo — change double quotes to single so
#    $env:GEMINI_API_KEY is NOT interpolated to the terminal.
$keyBad  = 'Write-Host "✓ Gemini CLI loaded. Set API key: $env:GEMINI_API_KEY = ''your_key_here''" -ForegroundColor Green'
$keyGood = "Write-Host '✓ Gemini CLI loaded. Set API key via: `$env:GEMINI_API_KEY' -ForegroundColor Green"
if ($c.Contains($keyBad)) {
    $c = $c.Replace($keyBad, $keyGood)
    Write-Host "Fixed: Gemini API key echo (was printing your real key)" -ForegroundColor Green
} else {
    Write-Host "Skip: Gemini key echo already patched" -ForegroundColor DarkGray
}

# 4. Guard the VS Code PATH append so it doesn't duplicate every shell.
$pathBad = '$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft VS Code\bin"'
$pathGood = @'
$vscodeBin = "C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft VS Code\bin"
if ($env:PATH -notlike "*$vscodeBin*") { $env:PATH += ";$vscodeBin" }
'@
if ($c.Contains($pathBad)) {
    $c = $c.Replace($pathBad, $pathGood)
    Write-Host "Guarded: VS Code PATH append (no more duplicates)" -ForegroundColor Green
} else {
    Write-Host "Skip: PATH append already guarded" -ForegroundColor DarkGray
}

# 5. Remove the duplicate `function gemini` near the bottom.
#    The FIRST definition (one-liner) is kept; the SECOND (inside
#    the big comment-documented block) is identical and redundant.
#    We match the second one by its unique trailing context.
$dupPattern = '(?s)\# ═{70,}\s*\r?\nfunction gemini \{\s*\r?\n\s*& ''C:\\Users\\MarsBase\\AppData\\Roaming\\npm\\gemini-docker\.ps1'' @args\s*\r?\n\}\s*\r?\n'
if ($c -match $dupPattern) {
    $c = $c -replace $dupPattern, "`r`n"
    Write-Host "Removed: duplicate function gemini" -ForegroundColor Green
} else {
    Write-Host "Skip: no duplicate gemini function found" -ForegroundColor DarkGray
}

# 6. Upgrade Show-HUD — inject RAM / disk / battery lines.
#    We replace the old Show-HUD wholesale with a richer one.
$oldHud = @'
function Show-HUD {
    $t = Get-SessionTime
    $d = Get-Date -Format "ddd MMM dd  HH:mm:ss"
    Write-Host ""
    Write-Host "  pwsh 7.6.0  ·  .NET 10  ·  poweruser" -ForegroundColor Magenta
    Write-Host "  $d  ·  session $t"                     -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  WSL    ub · kali · sky"                -ForegroundColor Cyan
    Write-Host "  APPS   ob · gem · lm · rec · dk"       -ForegroundColor Cyan
    Write-Host "  DEV    vsc · ag · ll · oc"             -ForegroundColor Cyan
    Write-Host "  AI     AI [model]  →  deepseek·lfm·coder-small·coder-7b·qwen3·coder" -ForegroundColor Yellow
    Write-Host "  type ref for full help"                 -ForegroundColor DarkGray
    Write-Host ""
}
'@

$newHud = @'
function Get-SystemStats {
    # Fast — all CIM queries, no WMI, no external processes.
    try {
        $os  = Get-CimInstance Win32_OperatingSystem
        $ramTotalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
        $ramFreeGB  = [math]::Round($os.FreePhysicalMemory   / 1MB, 1)
        $ramUsedPct = [math]::Round((($ramTotalGB - $ramFreeGB) / $ramTotalGB) * 100)

        $c = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
        $diskFreeGB  = [math]::Round($c.FreeSpace / 1GB, 0)
        $diskTotalGB = [math]::Round($c.Size      / 1GB, 0)
        $diskUsedPct = [math]::Round((($diskTotalGB - $diskFreeGB) / $diskTotalGB) * 100)

        $batt = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
        $battPct = if ($batt) { $batt.EstimatedChargeRemaining } else { $null }
        $battState = if ($batt) {
            switch ($batt.BatteryStatus) {
                1 {'disch'} 2 {'AC'} 3 {'full'} 4 {'low'} 5 {'crit'} default {'?'}
            }
        } else { 'n/a' }

        [PSCustomObject]@{
            RamUsedPct  = $ramUsedPct
            RamFreeGB   = $ramFreeGB
            RamTotalGB  = $ramTotalGB
            DiskFreeGB  = $diskFreeGB
            DiskTotalGB = $diskTotalGB
            DiskUsedPct = $diskUsedPct
            BattPct     = $battPct
            BattState   = $battState
        }
    } catch {
        $null
    }
}

function Show-HUD {
    $t = Get-SessionTime
    $d = Get-Date -Format "ddd MMM dd  HH:mm:ss"
    $s = Get-SystemStats

    Write-Host ""
    Write-Host "  pwsh 7.6.0  ·  .NET 10  ·  poweruser" -ForegroundColor Magenta
    Write-Host "  $d  ·  session $t"                     -ForegroundColor DarkGray

    if ($s) {
        # Color-code thresholds
        $ramColor  = if ($s.RamUsedPct  -ge 85) {'Red'} elseif ($s.RamUsedPct  -ge 70) {'Yellow'} else {'Green'}
        $diskColor = if ($s.DiskUsedPct -ge 90) {'Red'} elseif ($s.DiskUsedPct -ge 80) {'Yellow'} else {'Green'}
        $battColor = if ($s.BattPct -and $s.BattPct -le 20) {'Red'} elseif ($s.BattPct -and $s.BattPct -le 40) {'Yellow'} else {'Green'}

        $ramLine  = "RAM  {0,3}% used  ·  {1} GB free of {2} GB" -f $s.RamUsedPct,  $s.RamFreeGB,  $s.RamTotalGB
        $diskLine = "DISK {0,3}% used  ·  {1} GB free of {2} GB" -f $s.DiskUsedPct, $s.DiskFreeGB, $s.DiskTotalGB
        $battLine = if ($s.BattPct) {
            "BATT {0,3}%  ·  {1}" -f $s.BattPct, $s.BattState
        } else {
            "BATT n/a"
        }

        Write-Host ""
        Write-Host "  $ramLine"  -ForegroundColor $ramColor
        Write-Host "  $diskLine" -ForegroundColor $diskColor
        Write-Host "  $battLine" -ForegroundColor $battColor
    }

    Write-Host ""
    Write-Host "  WSL    ub · kali · sky"                -ForegroundColor Cyan
    Write-Host "  APPS   ob · gem · lm · rec · dk"       -ForegroundColor Cyan
    Write-Host "  DEV    vsc · ag · ll · oc"             -ForegroundColor Cyan
    Write-Host "  AI     AI [model]  →  deepseek·lfm·coder-small·coder-7b·qwen3·coder" -ForegroundColor Yellow
    Write-Host "  type ref for full help  ·  stats for live stats" -ForegroundColor DarkGray
    Write-Host ""
}

function stats {
    $s = Get-SystemStats
    if (-not $s) { Write-Host "stats unavailable" -ForegroundColor Red; return }
    Write-Host ""
    Write-Host ("  RAM   {0,3}% used  ·  {1} GB free of {2} GB" -f $s.RamUsedPct,  $s.RamFreeGB,  $s.RamTotalGB)
    Write-Host ("  DISK  {0,3}% used  ·  {1} GB free of {2} GB" -f $s.DiskUsedPct, $s.DiskFreeGB, $s.DiskTotalGB)
    if ($s.BattPct) {
        Write-Host ("  BATT  {0,3}%  ·  {1}" -f $s.BattPct, $s.BattState)
    }
    Write-Host ("  SESS  {0}" -f (Get-SessionTime))
    Write-Host ""
}
'@

if ($c.Contains($oldHud)) {
    $c = $c.Replace($oldHud, $newHud)
    Write-Host "Upgraded: Show-HUD now shows RAM, disk, battery + added 'stats' command" -ForegroundColor Green
} else {
    Write-Host "Skip: Show-HUD already upgraded or signature changed" -ForegroundColor DarkGray
    Write-Host "      (your backup at $backup if you want to compare)" -ForegroundColor DarkGray
}

# Write back
Set-Content $profilePath $c -Encoding UTF8
Write-Host ""
Write-Host "Done. Close this window and open a fresh PowerShell." -ForegroundColor Cyan
Write-Host "  - Startup error should be gone" -ForegroundColor DarkGray
Write-Host "  - 'code' should open VS Code" -ForegroundColor DarkGray
Write-Host "  - HUD shows RAM / disk / battery" -ForegroundColor DarkGray
Write-Host "  - Type 'stats' anytime for a fresh read" -ForegroundColor DarkGray
Write-Host ""
Write-Host "If anything looks wrong, restore with:" -ForegroundColor Yellow
Write-Host "  Copy-Item '$backup' '$profilePath' -Force" -ForegroundColor DarkGray
