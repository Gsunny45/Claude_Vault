---
name: note20-recovery
description: |
  Recovery, unlock, and maintenance for the Note20 Ultra (SM-N986U). Use this skill whenever the user mentions their phone being locked, disconnected, needing a mirror, ADB issues, scrcpy, USB drops, or any Note20 Ultra device management. Also trigger for "phone won't connect", "locked out", "screen mirror", "start scrcpy", "fix USB", "phone rebooted", or any Samsung device troubleshooting. This skill contains hard-won operational knowledge — coordinates, timing, Samsung quirks — that cannot be derived from general knowledge. Always load it before touching the phone.
---

# Note20 Ultra Recovery & Management

## Device Identity

| Fact | Value |
|------|-------|
| Model | SM-N986U (Verizon, Snapdragon 865+) |
| Serial | R5CN81CDXJV |
| Android | 13 / OneUI 5.1 |
| ADB path | `C:\Users\MarsBase\Android\Sdk\platform-tools\adb.exe` |
| scrcpy path | `C:\Users\MarsBase\AppData\Local\Microsoft\WinGet\Packages\Genymobile.scrcpy_Microsoft.Winget.Source_8wekyb3d8bbwe\scrcpy-win64-v3.3.4\` |
| WiFi ADB | Only works when PC and phone are on same subnet (currently PC=192.168.12.x, phone=192.168.1.x — different subnets, WiFi ADB WILL NOT WORK) |

## Critical Display Facts

**The phone runs at 720x1544 (HD+ override), NOT 1080 or 1440.**

```
Physical: 1440x3088
Override: 720x1544
```

ALL `input` coordinates must use the override resolution. Verify with `adb shell wm size` before trusting any coordinates. If `wm size` shows a different override, recalculate the grid.

## Lock Pattern

Pattern shape: **M** (dot sequence 7→4→1→5→3→6→9)

Bouncer grid bounds (at 720x1544): `[137,881][583,1327]`

| Dot | Grid Position | X | Y |
|-----|--------------|---|---|
| 7 (bottom-left) | C1,R3 | 211 | 1253 |
| 4 (middle-left) | C1,R2 | 211 | 1104 |
| 1 (top-left) | C1,R1 | 211 | 955 |
| 5 (center) | C2,R2 | 360 | 1104 |
| 3 (top-right) | C3,R1 | 509 | 955 |
| 6 (middle-right) | C3,R2 | 509 | 1104 |
| 9 (bottom-right) | C3,R3 | 509 | 1253 |

Grid formula from bounds `[L,T][R,B]`:
```
W = R - L, H = B - T
C1 = L + W/6, C2 = (L+R)/2, C3 = R - W/6
R1 = T + H/6, R2 = (T+B)/2, R3 = B - H/6
```

## Samsung KNOX USB Kill Behavior

**Samsung OneUI kills USB ADB when `input` commands are sent on the keyguard (lock screen).** This is a security feature, not a bug. It affects `input keyevent`, `input tap`, `input swipe`, and `input motionevent` — any input injection while the bouncer/keyguard is the focused window.

This does NOT happen when:
- The phone is unlocked (normal apps)
- Running commands in Settings, Termux, or any non-keyguard app
- Running `dumpsys`, `settings`, `wm`, `am`, or other non-input commands on the lock screen
- The command runs via `nohup` in a detached script (USB still dies, but the script continues on-device)

### Consequence
Never run ADB input commands directly from the PC while the lock screen is showing. Always push a shell script and run it via `nohup sh /data/local/tmp/script.sh >/dev/null 2>&1 &`. The script runs to completion on-device even if USB drops.

## USB Recovery (PnP Cycle)

When USB drops, this sequence recovers it **without unplugging**. It works about 60% of the time — if it fails, a physical replug or phone reboot (Power + Volume Down 10s) is needed.

```powershell
# 1. Kill ADB server
Get-Process adb -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2

# 2. Elevated PnP double-cycle
Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -Command "Disable-PnpDevice -InstanceId ''USB\VID_04E8&PID_6860\R5CN81CDXJV'' -Confirm:`$false; Start-Sleep 3; Enable-PnpDevice -InstanceId ''USB\VID_04E8&PID_6860\R5CN81CDXJV'' -Confirm:`$false; Start-Sleep 3; Disable-PnpDevice -InstanceId ''USB\VID_04E8&PID_6860\R5CN81CDXJV'' -Confirm:`$false; Start-Sleep 3; Enable-PnpDevice -InstanceId ''USB\VID_04E8&PID_6860\R5CN81CDXJV'' -Confirm:`$false"' -Verb RunAs -WindowStyle Hidden

# 3. Wait for PnP, restart ADB
Start-Sleep 15
adb start-server
Start-Sleep 8
adb devices
```

Key: the double-cycle (disable→enable→disable→enable) works more reliably than a single cycle. The elevated RunAs is required.

If `adb tcpip 5555` was run before USB died, adbd may be stuck in TCP mode and USB will not recover from PnP alone. The phone must be rebooted (Power + Volume Down 10s).

## Unlock Procedure (if lock is re-enabled)

The lock screen was disabled on 2026-06-03. If it ever gets re-enabled (factory reset, system update, manual change), here is the proven unlock sequence. It runs entirely on-device via nohup.

```sh
#!/system/bin/sh
# 1. Wake screen (224=WAKEUP only, never toggles off)
input keyevent 224
sleep 3

# 2. Swipe up to bouncer (twice — first may hit notification shade)
input swipe 360 1200 360 200 300
sleep 3
input swipe 360 1200 360 200 300
sleep 3

# 3. Dismiss biometric prompt (tap bottom-center area)
input tap 360 1350
sleep 2
input tap 360 1300
sleep 2
input tap 360 1250
sleep 2

# 4. Auto-detect pattern grid from uiautomator
uiautomator dump /data/local/tmp/ui.xml 2>/dev/null
sleep 1
BOUNDS=$(cat /data/local/tmp/ui.xml | grep -oE 'lockPatternView[^>]*bounds="\[[0-9,]+\]\[[0-9,]+\]"' | grep -oE '\[[0-9,]+\]' | head -2)

if [ -z "$BOUNDS" ]; then
    # Fallback: use known coords for 720x1544
    C1=211; C2=360; C3=509; R1=955; R2=1104; R3=1253
else
    L=$(echo "$BOUNDS" | head -1 | grep -oE '[0-9]+' | head -1)
    T=$(echo "$BOUNDS" | head -1 | grep -oE '[0-9]+' | tail -1)
    R=$(echo "$BOUNDS" | tail -1 | grep -oE '[0-9]+' | head -1)
    B=$(echo "$BOUNDS" | tail -1 | grep -oE '[0-9]+' | tail -1)
    W=$((R - L)); H=$((B - T))
    C1=$((L + W / 6)); C2=$(((L + R) / 2)); C3=$((R - W / 6))
    R1=$((T + H / 6)); R2=$(((T + B) / 2)); R3=$((B - H / 6))
fi

# 5. Draw M-pattern 7→4→1→5→3→6→9
sleep 1
input motionevent DOWN $C1 $R3
input motionevent MOVE $C1 $R2
input motionevent MOVE $C1 $R1
input motionevent MOVE $C2 $R2
input motionevent MOVE $C3 $R1
input motionevent MOVE $C3 $R2
input motionevent MOVE $C3 $R3
input motionevent UP $C3 $R3
sleep 3

# 6. Harden
settings put system screen_off_timeout 2147483647
settings put secure lock_screen_lock_after_timeout 2147483647
settings put global stay_on_while_plugged_in 3
svc power stayon true
```

### Deployment sequence
1. `adb push <script> /data/local/tmp/unlock.sh`
2. `adb shell "nohup sh /data/local/tmp/unlock.sh >/dev/null 2>&1 &"`
3. Wait 35 seconds
4. USB will likely die — use PnP recovery (above) to reconnect
5. Check result: `adb shell cat /data/local/tmp/unlock_log.txt`

### Disabling the lock via Settings UI (when phone is unlocked)
If the phone is unlocked and you want to remove the lock permanently:
1. `adb shell am start -a android.settings.SECURITY_SETTINGS`
2. Use uiautomator dump + `input tap` to navigate: Lock screen → Screen lock → draw pattern in ConfirmLockPattern → select None → tap "Remove data"
3. Input taps in Settings are safe — Samsung only kills USB on the keyguard

### locksettings CLI limitation
`locksettings clear --old <pattern>` cannot work for this pattern because dot 1 (top-left) maps to byte 0x00 (null), which truncates the shell string. Do not waste time trying to fix this — it's a fundamental POSIX limitation.

## scrcpy Mirror

Launch command:
```bat
C:\Users\MarsBase\AppData\Local\Microsoft\WinGet\Packages\Genymobile.scrcpy_Microsoft.Winget.Source_8wekyb3d8bbwe\scrcpy-win64-v3.3.4\scrcpy.exe --serial R5CN81CDXJV --no-audio --stay-awake --always-on-top --window-title "Note20 Mirror" --max-size 800
```

Notes:
- scrcpy ships its own `adb.exe` — can conflict with the SDK adb. Kill all adb instances before launching if connection fails.
- `--stay-awake` keeps phone awake while mirroring.
- `--max-size 800` reduces encoding load and helps with connection stability.
- scrcpy needs USB ADB alive to push its server jar. If USB is dead, scrcpy cannot launch.
- Window title may be "SM-N986U" if `--window-title` is not passed.

### Bring scrcpy to foreground (PowerShell)
```powershell
$hwnd = (Get-Process scrcpy).MainWindowHandle
Add-Type 'using System; using System.Runtime.InteropServices; public class W { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c); }'
[W]::ShowWindow($hwnd, 9); [W]::SetForegroundWindow($hwnd)
```

## Hardening Settings

These prevent the phone from locking/sleeping. Apply after every unlock or reboot:

```sh
settings put system screen_off_timeout 2147483647
settings put secure lock_screen_lock_after_timeout 2147483647
settings put global stay_on_while_plugged_in 3
svc power stayon true
```

These do NOT survive a factory reset. They DO survive normal reboots on most Samsung devices, but `svc power stayon true` resets on reboot.

## Diagnostic Commands (safe on lock screen — won't kill USB)

```sh
# Check if locked
adb shell "dumpsys window | grep mDreamingLockscreen"

# Check what's focused
adb shell "dumpsys window | grep mCurrentFocus"

# Check screen state
adb shell "dumpsys power | grep mWakefulness"

# Check display resolution
adb shell wm size

# Check lock type
adb shell "settings get secure lockscreen.password_type"

# Check if lock is disabled
adb shell "locksettings get-disabled"

# Check USB device status (Windows)
Get-PnpDevice -InstanceId 'USB\VID_04E8&PID_6860\R5CN81CDXJV' | Select FriendlyName, Status
```

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `adb devices` empty, PnP shows OK | adbd crashed from input on keyguard | PnP double-cycle, or replug, or reboot |
| `adb devices` empty after `tcpip 5555` | adbd stuck in TCP mode | Reboot phone (Power+VolDown 10s) |
| scrcpy won't start, "Could not find any ADB device" | ADB server conflict or USB dead | Kill all adb processes, restart server, retry |
| Pattern draws but doesn't unlock | Wrong coordinates (resolution changed?) | Check `wm size`, recalculate grid |
| Pattern draws but no haptic feedback | Coordinates are for wrong resolution | Same as above — verify 720x1544 |
| WiFi ADB times out | PC and phone on different subnets | Check with `ipconfig` and `ip addr show wlan0` |
