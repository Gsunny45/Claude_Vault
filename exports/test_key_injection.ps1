<#
.SYNOPSIS
  Keyboard <-> Vault key/config injection test harness.
  Verifies the ADB key-injection contract of CteKeysActivity against the live
  HermeticA-Z keyboard on the Moto. NON-DESTRUCTIVE by default: injects a
  throwaway keyRef and restores the encrypted prefs file at teardown.

.DESCRIPTION
  Contract verified from source 2026-05-29 (CteKeysActivity.kt / KeyVault.kt):
    am start -n <pkg>/...CteKeysActivity --ei inject 1 -e keyRef <R> -e keyValue <V>
  Success log:  "Key injected via ADB: <R> (<N> chars)"
  Reject log:   "ADB inject: missing keyRef or keyValue extras"
  Storage: EncryptedSharedPreferences florisboard_ai_keyvault.xml (names+values encrypted)
  -> verification is by logcat + prefs mtime/entry-count delta, not plaintext.

.PARAMETER IncludeRealKey
  Also run TC-7 (real provider keyRef roundtrip). Requires -RealKeyRef/-RealKeyValue.
  Real-key injects are intentionally NOT auto-restored.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\test_key_injection.ps1
#>
[CmdletBinding()]
param(
    [string]$Adb     = "C:\Users\MarsBase\Android\Sdk\platform-tools\adb.exe",
    [string]$Pkg     = "dev.patrickgold.florisboard.vault.debug",
    [string]$Activity= "dev.patrickgold.florisboard.ime.ai.CteKeysActivity",
    [string]$Serial  = "ZY22G7NFLK",
    [string]$PrefsFile = "shared_prefs/florisboard_ai_keyvault.xml",
    [switch]$IncludeRealKey,
    [string]$RealKeyRef,
    [string]$RealKeyValue
)

$ErrorActionPreference = "Stop"
$TestRef = "__TEST_INJECT_KEY__"
$Comp    = "$Pkg/$Activity"
$results = [System.Collections.Generic.List[object]]::new()
$ts      = Get-Date -Format "yyyyMMdd-HHmmss"
$report  = Join-Path $PSScriptRoot "injection_test_report_$ts.txt"

function A { param([Parameter(ValueFromRemainingArguments)]$Args)
    # Capture stdout+stderr without letting a native stderr warning abort the
    # script under ErrorActionPreference=Stop.
    $old = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    try { (& $Adb -s $Serial @Args 2>&1) } finally { $ErrorActionPreference = $old } }
function RunAs { param([string]$Cmd) (A shell "run-as $Pkg $Cmd") -join "`n" }
function Rec { param($id,$name,$pass,$detail)
    $results.Add([pscustomobject]@{ ID=$id; Name=$name; Pass=$pass; Detail=$detail })
    $tag = if ($pass) { "PASS" } else { "FAIL" }
    Write-Host ("[{0}] {1,-6} {2} - {3}" -f $tag, $id, $name, $detail) -ForegroundColor ($(if($pass){"Green"}else{"Red"})) }

# Count encrypted string entries in the prefs map (includes 2 Tink keyset entries).
function Get-EntryCount {
    $xml = RunAs "cat $PrefsFile"
    if ($xml -notmatch "<map") { return -1 }
    ([regex]::Matches($xml, '<string name=')).Count
}
function Get-Mtime { (RunAs "stat -c %Y $PrefsFile").Trim() }

# Inject helper. Returns logcat captured during the call.
# IMPORTANT (verified 2026-05-29): CteKeysActivity is a singleTask deep-link
# activity (action VIEW, data ui://hermetica-z/cte/keys). The inject logic lives
# only in onCreate (no onNewIntent override), so we force-stop before each launch
# to guarantee a fresh onCreate. Launching by -n alone fails ("does not exist")
# and launching by data alone hits the ResolverActivity chooser (ui:// scheme is
# not unique). The reliable contract is: explicit -n PLUS matching action+data.
function Invoke-Inject {
    param([hashtable]$Extras, [switch]$NoInjectExtras)
    A shell am force-stop $Pkg | Out-Null
    Start-Sleep -Milliseconds 500
    A logcat -c | Out-Null
    $argList = @("shell","am","start","-n",$Comp,"-a","android.intent.action.VIEW","-d","ui://hermetica-z/cte/keys")
    if (-not $NoInjectExtras) {
        foreach ($k in $Extras.Keys) {
            if ($k -eq "inject") { $argList += @("--ei","inject",[string]$Extras[$k]) }
            else                 { $argList += @("-e",$k,[string]$Extras[$k]) }
        }
    }
    A @argList | Out-Null
    Start-Sleep -Milliseconds 900
    (A logcat -d -s "CteKeysActivity:*" "KeyVault:*") -join "`n"
}

# Inject via a single shell-string so the device shell (not the local arg
# splitter) tokenizes the value. Needed for a whitespace-only keyValue: passed as
# separate adb args, the device shell strips it and `am` errors with
# "Argument expected after keyValue" before the activity runs. Wrapped in nested
# quotes the blank token survives and reaches the app's isNotBlank() guard.
function Invoke-InjectShell {
    param([string]$KeyRef, [string]$RawValue)
    A shell am force-stop $Pkg | Out-Null
    Start-Sleep -Milliseconds 500
    A logcat -c | Out-Null
    $cmd = "am start -n $Comp -a android.intent.action.VIEW -d 'ui://hermetica-z/cte/keys' --ei inject 1 -e keyRef $KeyRef -e keyValue '$RawValue'"
    A shell $cmd | Out-Null
    Start-Sleep -Milliseconds 900
    (A logcat -d -s "CteKeysActivity:*" "KeyVault:*") -join "`n"
}

Write-Host "`n=== Keyboard<->Vault Key Injection Tests ($ts) ===`n" -ForegroundColor Cyan

# ---------------- PRECONDITIONS ----------------
$abort = $false
$dev = (A devices) -join "`n"
$p1 = $dev -match "$([regex]::Escape($Serial))\s+device"
Rec "PRE-1" "Device present/authorized" $p1 ($(if($p1){"$Serial online"}else{"not found"}))
if (-not $p1) { $abort = $true }

if (-not $abort) {
    $path = (A shell pm path $Pkg) -join "`n"
    $p2 = $path -match "package:"
    Rec "PRE-2" "Package installed" $p2 ($path.Trim())
    if (-not $p2) { $abort = $true }
}
if (-not $abort) {
    $win = (A shell dumpsys window) -join "`n"
    $awake = $win -match "mAwake=true"
    $unlocked = $win -match "mDreamingLockscreen=false"
    $p3 = $awake -and $unlocked
    Rec "PRE-3" "Device unlocked/awake" $p3 ("mAwake=$awake unlocked=$unlocked")
    if (-not $p3) { Write-Host "  -> KeyVault is a no-op while locked. Unlock the phone and re-run." -ForegroundColor Yellow; $abort = $true }
}
if (-not $abort) {
    $ls = RunAs "ls $PrefsFile"
    $p4 = $ls -match "florisboard_ai_keyvault.xml"
    Rec "PRE-4" "run-as access" $p4 ($ls.Trim())
    if (-not $p4) { $abort = $true }
}
if (-not $abort) {
    $tj = RunAs "cat files/cte/configs/triggers.json"
    $p5 = $tj -match '"providers"'
    Rec "PRE-5" "triggers.json present" $p5 ($(if($p5){"providers block found"}else{"missing/unreadable"}))
    if (-not $p5) { $abort = $true }
}

if ($abort) {
    Write-Host "`nPreconditions failed - aborting before any mutation.`n" -ForegroundColor Red
    ($results | Format-Table -AutoSize | Out-String) | Tee-Object -FilePath $report
    exit 2
}

# Snapshot prefs for restore
$snapshot = Join-Path $env:TEMP "keyvault_snapshot_$ts.xml"
RunAs "cat $PrefsFile" | Set-Content -Path $snapshot -Encoding utf8
$baseCount = Get-EntryCount
Write-Host "`nBaseline entry count: $baseCount  (snapshot: $snapshot)`n" -ForegroundColor DarkGray

# ---------------- TEST CASES ----------------
# TC-1 happy path
$val = "sk-test-" + ([guid]::NewGuid().ToString("N").Substring(0,12))
$log = Invoke-Inject @{ inject=1; keyRef=$TestRef; keyValue=$val }
$expN = $val.Length
$okLog = $log -match "Key injected via ADB: $([regex]::Escape($TestRef)) \((\d+) chars\)"
$loggedN = if ($okLog) { [int]$Matches[1] } else { -1 }
$c1 = Get-EntryCount
Rec "TC-1" "Happy-path inject" ($okLog -and $loggedN -eq $expN -and $c1 -gt $baseCount) `
    "log=$okLog loggedChars=$loggedN expected=$expN entryCount $baseCount->$c1"

# TC-2 trim (shell variant so the padding survives the device tokenizer)
$log = Invoke-InjectShell -KeyRef $TestRef -RawValue "  sk-pad  "
$trimLen = "sk-pad".Length
$okTrim = $log -match "\((\d+) chars\)"
$tN = if ($okTrim) { [int]$Matches[1] } else { -1 }
Rec "TC-2" "Trim behaviour" ($okTrim -and $tN -eq $trimLen) "loggedChars=$tN expectedTrimmed=$trimLen"

# TC-3 blank value rejected (shell variant; whitespace-only reaches isNotBlank guard)
$cPre = Get-EntryCount
$log = Invoke-InjectShell -KeyRef $TestRef -RawValue "   "
$cPost = Get-EntryCount
$rej = $log -match "missing keyRef or keyValue extras"
Rec "TC-3" "Blank value rejected" ($rej -and $cPost -eq $cPre) "rejectLog=$rej count $cPre->$cPost"

# TC-4 missing keyValue
$cPre = Get-EntryCount
$log = Invoke-Inject @{ inject=1; keyRef=$TestRef }
$cPost = Get-EntryCount
$rej = $log -match "missing keyRef or keyValue extras"
Rec "TC-4" "Missing keyValue rejected" ($rej -and $cPost -eq $cPre) "rejectLog=$rej count $cPre->$cPost"

# TC-5 missing keyRef
$cPre = Get-EntryCount
$log = Invoke-Inject @{ inject=1; keyValue="sk-orphan" }
$cPost = Get-EntryCount
$rej = $log -match "missing keyRef or keyValue extras"
Rec "TC-5" "Missing keyRef rejected" ($rej -and $cPost -eq $cPre) "rejectLog=$rej count $cPre->$cPost"

# TC-6 inject flag off
$cPre = Get-EntryCount
$log = Invoke-Inject @{ inject=0; keyRef=$TestRef; keyValue="sk-noinject" }
$cPost = Get-EntryCount
$noInjectLog = ($log -notmatch "Key injected via ADB")
Rec "TC-6" "inject=0 opens UI, no write" ($noInjectLog -and $cPost -eq $cPre) "noInjectLog=$noInjectLog count $cPre->$cPost"
A shell am force-stop $Pkg | Out-Null

# TC-8 idempotent overwrite
$cPre = Get-EntryCount
Invoke-Inject @{ inject=1; keyRef=$TestRef; keyValue="first-value-aaaa" } | Out-Null
Invoke-Inject @{ inject=1; keyRef=$TestRef; keyValue="second-value-bbbb" } | Out-Null
$cPost = Get-EntryCount
Rec "TC-8" "Idempotent overwrite" ($cPost -le ($cPre + 1)) "count $cPre->$cPost (expected <= +1)"

# TC-7 real key (opt-in)
if ($IncludeRealKey) {
    if (-not $RealKeyRef -or -not $RealKeyValue) {
        Rec "TC-7" "Real-provider roundtrip" $false "missing -RealKeyRef/-RealKeyValue"
    } else {
        $log = Invoke-Inject @{ inject=1; keyRef=$RealKeyRef; keyValue=$RealKeyValue }
        $okR = $log -match "Key injected via ADB: $([regex]::Escape($RealKeyRef))"
        Rec "TC-7" "Real-provider roundtrip" $okR "ref=$RealKeyRef log=$okR (NOT auto-restored; confirm in UI)"
    }
}

# ---------------- TEARDOWN ----------------
Write-Host "`nRestoring KeyVault prefs from snapshot (removes throwaway test entries)..." -ForegroundColor DarkGray
$devTmp = "/data/local/tmp/keyvault_restore_$ts.xml"
A push $snapshot $devTmp | Out-Null
RunAs "cp $devTmp $PrefsFile" | Out-Null
A shell rm -f $devTmp | Out-Null
A shell am force-stop $Pkg | Out-Null
$finalCount = Get-EntryCount
$restored = ($finalCount -eq $baseCount)
Rec "TEARDOWN" "Restore baseline" $restored "entryCount now $finalCount (baseline $baseCount)"
if (-not $restored) {
    Write-Host "  -> WARNING: count differs. Snapshot kept at $snapshot for manual restore." -ForegroundColor Yellow
}

# ---------------- SUMMARY ----------------
$core = $results | Where-Object { $_.ID -like "TC-*" -and $_.ID -ne "TC-7" }
$pre  = $results | Where-Object { $_.ID -like "PRE-*" }
$allCorePass = ($core | Where-Object { -not $_.Pass }).Count -eq 0
$allPrePass  = ($pre  | Where-Object { -not $_.Pass }).Count -eq 0
$verdict = if ($allPrePass -and $allCorePass) { "PASS" } else { "FAIL" }

Write-Host ""
Write-Host "================ RESULT: $verdict ================" -ForegroundColor ($(if($verdict -eq "PASS"){"Green"}else{"Red"}))
$tbl = ($results | Format-Table ID,Name,Pass,Detail -AutoSize | Out-String)
Write-Host $tbl
"RESULT: $verdict`n$tbl" | Out-File -FilePath $report -Encoding utf8
Write-Host "Report written: $report" -ForegroundColor Cyan
exit $(if ($verdict -eq "PASS") { 0 } else { 1 })
