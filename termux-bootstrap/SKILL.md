---
name: termux-bootstrap
description: "Full Termux environment bootstrap on Android — from first install through vaults, dotfiles, SSH, proot-distro, Hermes agent, and ADB hardening. Use this skill whenever the user wants to set up Termux on a new phone, replicate an existing Termux environment to another device, bootstrap a hacking/pentesting lab on Android, configure Hermes agent on-device, or troubleshoot a broken Termux setup. Also trigger when the user mentions 'termux setup', 'phone dev environment', 'proot-distro install', 'termux from scratch', 'replicate my termux', or any combination of Android + terminal + agent setup."
---

# Termux Bootstrap — Full Environment Setup

This skill walks through bootstrapping a complete Termux environment on an Android device. It covers hardware prerequisites, package installation, proot-distro containers, SSH, Hermes agent, Obsidian vaults, dotfiles, and ADB hardening. Every step is verified against real devices (Samsung Note20 Ultra, Moto G 5G) running Android 13.

## Before You Start

### Gather device info

Before running any commands, identify the target device:

```bash
adb devices -l
```

Note the serial, model, and transport_id. You'll need these for multi-device setups.

Check the device specs that matter:

```bash
adb -s <SERIAL> shell getprop ro.product.model
adb -s <SERIAL> shell getprop ro.build.version.release
adb -s <SERIAL> shell cat /proc/cpuinfo | head -5
adb -s <SERIAL> shell cat /proc/meminfo | head -3
```

### Hard constraints (Android 13, no root)

These cannot be worked around — design around them:

| Constraint | Impact | Workaround |
|-----------|--------|------------|
| No Docker | No containers | proot-distro for Linux distros |
| No systemd | No service manager | tmux sessions, termux-services |
| No root | No privileged ops | SELinux enforcing, scoped storage |
| Ports <1024 blocked | No port 22/80/443 | Use 8022 (SSH), 8080 (llama), 3001 (hudui), 9119 (hermes) |
| Background process kills | Phantom process monitor (Android 12+) kills bg tasks ~3-5 min after screen off | Wake-lock + ADB phantom process disable |
| Scoped storage | Limited filesystem access | `termux-setup-storage` for /sdcard symlinks |
| ADB input limitations | `input text` fails on special chars (`>`, `&`, `$`, `-`) | Only alphanumeric + `/` + `.` + space are safe |
| scrcpy keyboard | SendKeys doesn't work when soft keyboard is visible in Termux | Use ADB shell or SSH instead |
| Locked bootloader (carrier) | No custom ROM, no Magisk | Accept stock Android constraints |

### Required app source

Termux MUST be installed from **F-Droid**, not the Play Store. The Play Store version is abandoned and incompatible with current packages. Direct APK from GitHub releases also works.

---

## Phase 1: Core Termux Setup

### 1.1 First boot

After installing Termux from F-Droid, run:

```bash
pkg update && pkg upgrade -y
termux-setup-storage    # Grants ~/storage/shared → /sdcard access. Prompts once.
```

### 1.2 Essential packages

Install in this order (dependencies matter):

```bash
# Core tools
pkg install -y git python nodejs openssh tmux wget curl jq nano

# System monitoring and search
pkg install -y btop ripgrep fd tree bat lsd

# Hardware/API access
pkg install -y termux-api

# Container support
pkg install -y proot-distro

# Build tools (needed for llama.cpp, native modules)
pkg install -y clang make cmake

# Audio pipeline (optional — for whisper/transcription)
pkg install -y sox ffmpeg
```

### 1.3 Storage layout

After `termux-setup-storage`, these symlinks exist:

| Symlink | Target |
|---------|--------|
| `~/storage/shared/` | `/sdcard/` |
| `~/storage/downloads/` | `/sdcard/Download/` |
| `~/storage/dcim/` | `/sdcard/DCIM/` |
| `~/storage/audiobooks/` | `/sdcard/Audiobooks/` |

The Termux home is at `/data/data/com.termux/files/home`.
The usr tree is at `/data/data/com.termux/files/usr`.

If storage access is denied, force it via ADB from desktop:

```bash
adb shell appops set com.termux MANAGE_EXTERNAL_STORAGE allow
```

---

## Phase 2: proot-distro (Linux Containers)

proot-distro provides unprivileged Linux distro containers. No kernel-level isolation — it's a userspace translation layer.

### 2.1 Install a distro

```bash
# Kali (pentesting)
proot-distro install kali
proot-distro login kali

# Ubuntu (general purpose, needed for Claude Code / glibc binaries)
proot-distro install ubuntu
proot-distro login ubuntu
```

### 2.2 Inside the distro

```bash
# Kali: install tools
apt update && apt full-upgrade -y
apt install -y nmap metasploit-framework hydra sqlmap wireshark-cli netcat-traditional

# Ubuntu: install dev tools
apt update && apt upgrade -y
apt install -y python3-pip python3-venv build-essential git curl
```

### 2.3 Known proot issues

- `--cpu` and `--mem` flags DO NOT exist for proot-distro. Resource limiting is via Android cgroups, not user-facing.
- DNS may fail inside proot. Fix: `echo "nameserver 8.8.8.8" > /etc/resolv.conf`
- **npm on proot always fails** with ENOTEMPTY/ENOENT on rename ops. Always use yarn: `npm install -g yarn && yarn install`
- Ubuntu 25.10 has no pip/ensurepip by default — `apt install python3-pip` first. Use venv to avoid system typing-extensions conflict.
- `process.platform` returns `'android'` on Termux native, not `'linux'`. glibc ELF binaries (linux-arm64) cannot run on Termux's Bionic — they must run inside proot.

---

## Phase 3: SSH & Remote Access

### 3.1 SSH server on device

```bash
# Start SSH server (Termux, port 8022)
sshd -p 8022

# Auto-start: add to ~/.bashrc or use termux-services
```

### 3.2 Connect from desktop

```bash
ssh -p 8022 <termux-user>@<phone-ip>
# Example: ssh -p 8022 u0_a396@192.168.1.170
```

### 3.3 Port forwarding via ADB

When USB-connected, ADB forwarding is more reliable than WiFi SSH:

```bash
adb -s <SERIAL> forward tcp:8022 tcp:8022    # SSH
adb -s <SERIAL> forward tcp:8080 tcp:8080    # llama-server
adb -s <SERIAL> forward tcp:3001 tcp:3001    # hermes-hudui
adb -s <SERIAL> forward tcp:9119 tcp:9119    # hermes dashboard
```

### 3.4 WiFi ADB (optional)

```bash
# From USB connection, enable wireless:
adb tcpip 5555
adb connect <phone-ip>:5555

# Android 11+: use Developer Options → Wireless Debugging → Pair device
```

---

## Phase 4: Hermes Agent

### 4.1 Install Hermes CLI

```bash
# Option A: pip install (Termux native)
pip install hermes-agent

# Option B: git install into proot venv (more reliable for full features)
proot-distro login ubuntu
python3 -m venv /root/henv
source /root/henv/bin/activate
pip install hermes-agent
# Create wrapper: echo '#!/bin/bash\nproot-distro login ubuntu -- /root/henv/bin/hermes "$@"' > /usr/local/bin/hermes && chmod +x /usr/local/bin/hermes
```

### 4.2 Configure

```bash
hermes login --provider <provider>     # deepseek, nous, openai, etc.
hermes config set model <model-name>
hermes config set provider <provider>
hermes status
hermes doctor
```

### 4.3 API keys

**Critical:** Never `cat >> ~/.hermes/.env` with multi-line blocks — it corrupts keys. Always:

```bash
echo "GEMINI_API_KEY=your-key" >> ~/.hermes/.env
echo "GROQ_API_KEY=your-key" >> ~/.hermes/.env
```

Or use `hermes config set`.

### 4.4 Hermes config locations

| Location | Path |
|----------|------|
| Config | `~/.hermes/config.yaml` |
| Secrets | `~/.hermes/.env` |
| Skills | `~/.hermes/skills/` |
| Sessions DB | `~/.hermes/state.db` |
| Logs | `~/.hermes/logs/` |
| Auth | `~/.hermes/auth.json` |

### 4.5 Known bugs

- `hermes dashboard` fails — `dashboard_auth` module missing from PyPI wheel. Use hermes-hudui instead.
- hermes-hudui: `cd /root/hermes-hudui && source venv/bin/activate && hermes-hudui --host 0.0.0.0 --port 3001`

---

## Phase 5: Dotfiles & Aliases

### 5.1 .bashrc essentials

```bash
cat << 'EOF' >> ~/.bashrc
# Hermes
export PATH="$HOME/.local/bin:$PATH"

# Source aliases
[ -f ~/.bash_aliases ] && . ~/.bash_aliases
EOF
```

### 5.2 .bash_aliases

```bash
cat << 'EOF' >> ~/.bash_aliases
# Quick nav
alias hermv='cd ~/storage/shared/Documents/Hermes_Phone_Vault && ls'
alias qr='cd ~/storage/audiobooks/QuickRef_Vault && ls'

# Distros
alias kali='proot-distro login kali'
alias ubuntu='proot-distro login ubuntu'

# Tools
alias dash='tmux new-session -d -s dash "btop" \; split-window -h "hermes insights" \; attach'
alias status='hermes status'

# Session
alias lock='termux-wake-lock'
alias unlock='termux-wake-unlock'
EOF
source ~/.bashrc
```

### 5.3 tmux config

```bash
cat << 'EOF' > ~/.tmux.conf
set -g mouse on
set -g history-limit 10000
set -g base-index 1
setw -g pane-base-index 1
set -g status-style 'bg=#333333 fg=#aaaaaa'
EOF
```

---

## Phase 6: Obsidian Vaults

Two vaults are standard for the phone environment:

### 6.1 Hermes_Phone_Vault (AI ops)

Location: `/sdcard/Documents/Hermes_Phone_Vault/`

Structure:
```
CLAUDE.md          # Agent guide (adapt per device)
AGENTS.md          # Agent roster
Dashboard.md       # Dataview dashboard
_system/           # Schemas, briefings, drift reports
_templates/        # Templater templates
decisions/         # DEC-NNNN
knowledge/         # KNW-NNNN
sessions/          # SYN-YYYY-MM-DD-NNN
capabilities/      # CAP-SKL-NNNN
devices/           # DP-NNNN device profiles
skills/            # SKL-NNNN
inbox/             # Quick capture
archive/           # Never delete, move here
```

Create the CLAUDE.md with device-specific specs (model, RAM, CPU, installed tools, proot distros, port assignments).

### 6.2 QuickRef_Vault (cheat sheets)

Location: `/sdcard/Audiobooks/QuickRef_Vault/`

The Audiobooks path is deliberate — it avoids Document-folder permission issues and is accessible via `~/storage/audiobooks/`.

Structure:
```
CLAUDE.md          # Agent guide
AGENTS.md          # Mirrored from Hermes_Phone_Vault
Home.md            # Dataview dashboard
ADB/               # ADB cheat sheets
Git/               # Git commands
Kali/              # Security tools
Terminal/          # Linux/bash commands
Termux/            # Termux-specific
Phone/             # Phone Linux environments
Hermes/            # Hermes agent reference
Hotkeys/           # Keyboard shortcuts
Paths/             # Directory maps, config locations
Recipes/           # Multi-step how-to guides
_Maps/             # Mermaid architecture diagrams
_archive/          # Desktop-only content (PowerShell, WSL)
_templates/        # Note templates (cmd, hotkey-sheet, recipe, path-map)
```

Keep AGENTS.md and CLAUDE.md mirrored between both vaults.

---

## Phase 7: ADB Hardening & Persistence

### 7.1 Disable phantom process monitor

Run once from desktop (survives reboot):

```bash
adb -s <SERIAL> shell settings put global settings_enable_monitor_phantom_procs 0
```

### 7.2 Battery optimization

Exempt Termux from battery optimization:

```bash
adb -s <SERIAL> shell cmd appops set com.termux RUN_IN_BACKGROUND allow
```

Also manually: Settings → Apps → Termux → Battery → Set to **Unrestricted**.

### 7.3 Wake-lock pattern

For any long-running service:

```bash
termux-wake-lock
termux-notification -i my-service -t "Service" -c "Running" --ongoing

# Start your service here
hermes gateway   # or llama-server, or sshd

# Cleanup later
termux-wake-unlock
termux-notification-remove my-service
```

### 7.4 scrcpy mirror from desktop

```bash
# Basic mirror
scrcpy -s <SERIAL> --window-title "<DeviceName> Mirror"

# With recording
scrcpy -s <SERIAL> --record file.mp4
```

---

## Phase 8: Verification Checklist

After completing all phases, verify:

```bash
# Termux basics
pkg list-installed | wc -l           # Should be 30+
ls ~/storage/shared/                  # Should show /sdcard contents

# proot-distro
proot-distro list                     # Shows installed distros

# SSH
sshd -p 8022                          # Should start without error

# Hermes
hermes status                          # Should show provider + model
hermes doctor                          # Should pass

# Vaults
ls ~/storage/shared/Documents/Hermes_Phone_Vault/CLAUDE.md
ls ~/storage/audiobooks/QuickRef_Vault/CLAUDE.md

# Aliases
type kali hermv qr dash               # All should resolve

# Wake-lock
termux-wake-lock                       # Should acquire lock
```

---

## Replicating Between Devices

To clone a Termux environment from device A to device B:

1. **Package list:** `adb -s <A> shell "su -c 'cat /data/data/com.termux/files/usr/var/lib/dpkg/status'" | grep "^Package:" | cut -d' ' -f2 > pkg-list.txt` (or if no root: manually list with `pkg list-installed`)
2. **Dotfiles:** `adb -s <A> pull /sdcard/.termux-dotfiles/` (if you've backed them up) or pull ~/.bashrc, ~/.bash_aliases, ~/.tmux.conf individually
3. **Vaults:** `adb -s <A> pull /sdcard/Documents/Hermes_Phone_Vault/ ./hpv/` then `adb -s <B> push ./hpv/ /sdcard/Documents/Hermes_Phone_Vault/`
4. **QuickRef:** Same pattern with `/sdcard/Audiobooks/QuickRef_Vault/`
5. **Hermes config:** Pull `~/.hermes/config.yaml` (NOT `.env` — re-enter keys manually on target)
6. **proot distros:** Must be reinstalled on target — no portable export

Adapt CLAUDE.md files for the target device's specs before pushing.
