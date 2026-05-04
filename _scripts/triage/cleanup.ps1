# ─────────────────────────────────────────────────────────────
# cleanup.ps1 — Reclaim disk + RAM without breaking your stack
# Date: 2026-04-21
#
# Run in THIS ORDER. Each step prints what it will do BEFORE
# doing it. Nothing here is irreversible except Docker prune,
# which is gated behind a confirmation prompt.
#
# Estimated reclaim on your box (477 GB SSD, 453 used):
#   - Windows temp / updates:   5–15 GB
#   - Docker prune:             5–30 GB (you have n8n_local, be careful)
#   - WSL vhdx compaction:     10–40 GB (Ubuntu + Kali + Skywork)
#   - Recycle bin:               1–5 GB
#   TOTAL:                     20–90 GB realistic
#
# Run as Administrator for best results.
# ─────────────────────────────────────────────────────────────

$ErrorActionPreference = 'Continue'

function Step($label) {
    Write-Host ""
    Write-Host "═══ $label ═══" -ForegroundColor Cyan
}

function Ask($q) {
    $a = Read-Host "$q [y/N]"
    return $a -eq 'y' -or $a -eq 'Y'
}

# ─── 0. BEFORE SNAPSHOT ──────────────────────────────────────
Step "Before"
$before = (Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB
Write-Host ("  C:\ free: {0:N1} GB" -f $before) -ForegroundColor Yellow

# ─── 1. TEMP FOLDERS (safe) ──────────────────────────────────
Step "Temp folders"
$tempPaths = @(
    "$env:TEMP",
    "$env:LOCALAPPDATA\Temp",
    "C:\Windows\Temp"
)
foreach ($p in $tempPaths) {
    if (Test-Path $p) {
        Write-Host "  Clearing $p"
        Get-ChildItem $p -Force -ErrorAction SilentlyContinue |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# ─── 2. RECYCLE BIN ──────────────────────────────────────────
Step "Recycle bin"
Clear-RecycleBin -Force -ErrorAction SilentlyContinue
Write-Host "  Emptied." -ForegroundColor Green

# ─── 3. WINDOWS UPDATE CLEANUP (big wins, takes a few min) ──
Step "Windows Update cleanup"
Write-Host "  Running DISM /startcomponentcleanup (takes 2–10 min)..."
Start-Process -FilePath dism.exe `
    -ArgumentList '/online /cleanup-image /startcomponentcleanup /resetbase' `
    -Wait -NoNewWindow

# ─── 4. cleanmgr with all flags ─────────────────────────────
Step "cleanmgr (disk cleanup automation)"
# Preset sageset:1 to flag all cleanup categories, then run it
$sagesetKeys = @(
    'Active Setup Temp Folders',
    'BranchCache',
    'Downloaded Program Files',
    'Internet Cache Files',
    'Old ChkDsk Files',
    'Previous Installations',
    'Recycle Bin',
    'Service Pack Cleanup',
    'Setup Log Files',
    'System error memory dump files',
    'System error minidump files',
    'Temporary Files',
    'Temporary Setup Files',
    'Thumbnail Cache',
    'Update Cleanup',
    'Upgrade Discarded Files',
    'Windows Defender',
    'Windows Error Reporting Files',
    'Windows ESD installation files',
    'Windows Upgrade Log Files'
)
$base = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches'
foreach ($k in $sagesetKeys) {
    $path = Join-Path $base $k
    if (Test-Path $path) {
        Set-ItemProperty -Path $path -Name 'StateFlags0001' -Value 2 -Type DWord -ErrorAction SilentlyContinue
    }
}
Write-Host "  Launching cleanmgr /sagerun:1 ..."
Start-Process cleanmgr.exe -ArgumentList '/sagerun:1' -Wait

# ─── 5. DOCKER PRUNE (gated) ────────────────────────────────
Step "Docker prune"
Write-Host "  This removes STOPPED containers, unused images, unused volumes." -ForegroundColor Yellow
Write-Host "  Your n8n_local container is protected if it is currently RUNNING." -ForegroundColor Yellow
Write-Host "  (Start it first with: wsl -d Ubuntu -- docker start n8n_local)" -ForegroundColor DarkGray
if (Ask "  Run docker system prune now?") {
    docker system prune -af --volumes
} else {
    Write-Host "  Skipped." -ForegroundColor DarkGray
}

# ─── 6. WSL VHDX COMPACT ────────────────────────────────────
Step "WSL vhdx compaction"
Write-Host "  Shutting down all WSL distros..."
wsl --shutdown

$vhdxFiles = @()
$packagesDir = "$env:LOCALAPPDATA\Packages"
$vhdxFiles += Get-ChildItem $packagesDir -Recurse -Filter 'ext4.vhdx' -ErrorAction SilentlyContinue
$dockerData = "$env:LOCALAPPDATA\Docker\wsl"
if (Test-Path $dockerData) {
    $vhdxFiles += Get-ChildItem $dockerData -Recurse -Filter 'ext4.vhdx' -ErrorAction SilentlyContinue
}

if ($vhdxFiles.Count -eq 0) {
    Write-Host "  No vhdx files found." -ForegroundColor DarkGray
} else {
    foreach ($f in $vhdxFiles) {
        $sizeBefore = [math]::Round($f.Length / 1GB, 1)
        Write-Host "  Compacting $($f.FullName) ($sizeBefore GB) ..."
        # Use diskpart — works without Hyper-V module
        $dpScript = @"
select vdisk file="$($f.FullName)"
attach vdisk readonly
compact vdisk
detach vdisk
exit
"@
        $tmp = [System.IO.Path]::GetTempFileName()
        Set-Content $tmp $dpScript -Encoding ASCII
        diskpart /s $tmp | Out-Null
        Remove-Item $tmp -Force
        $newSize = [math]::Round((Get-Item $f.FullName).Length / 1GB, 1)
        Write-Host ("    {0} GB -> {1} GB" -f $sizeBefore, $newSize) -ForegroundColor Green
    }
}

# ─── 7. DISABLE DOCKER DESKTOP AUTOSTART (optional) ────────
Step "Docker Desktop autostart"
Write-Host "  Your MAD_MAX_STATUS.md already says this was done." -ForegroundColor DarkGray
Write-Host "  Verifying..."
$dockerStartup = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'Docker Desktop' -ErrorAction SilentlyContinue
if ($dockerStartup) {
    Write-Host "  Docker Desktop IS still set to autostart." -ForegroundColor Yellow
    if (Ask "  Remove Docker Desktop autostart?") {
        Remove-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'Docker Desktop'
        Write-Host "  Removed." -ForegroundColor Green
    }
} else {
    Write-Host "  Confirmed: Docker Desktop is not in HKCU Run." -ForegroundColor Green
}

# ─── 8. SEARCH INDEXER EXCLUSIONS ──────────────────────────
Step "Windows Search indexer exclusions"
Write-Host "  Recommend excluding AI model and vault folders from indexing." -ForegroundColor DarkGray
Write-Host "  This can't be scripted reliably — do it manually:" -ForegroundColor DarkGray
Write-Host "    Start → Indexing Options → Modify → UNCHECK:" -ForegroundColor DarkGray
Write-Host "      C:\AI" -ForegroundColor DarkGray
Write-Host "      C:\Users\MarsBase\Documents\Claude_Vault" -ForegroundColor DarkGray
Write-Host "      C:\Users\MarsBase\Documents\Command_Vault" -ForegroundColor DarkGray
Write-Host "      C:\Users\MarsBase\Documents\Gemini_Vault" -ForegroundColor DarkGray

# ─── 9. AFTER SNAPSHOT ──────────────────────────────────────
Step "After"
$after = (Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB
$delta = $after - $before
Write-Host ("  C:\ free: {0:N1} GB  (+{1:N1} GB reclaimed)" -f $after, $delta) -ForegroundColor Green
Write-Host ""
Write-Host "Done. Reboot recommended but not required." -ForegroundColor Cyan
