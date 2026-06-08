# Hermes_Phone_Vault — CLAUDE.md (Agent Guide)

## Purpose

Structured AI operations vault for phone-side Hermes Agent. Device profiles, knowledge entries, decisions, session syntheses, and capability tracking for Android/Termux operations. Machine-first structure — notes written for Hermes to parse.

## Environment

- **Phone**: Samsung SM-N986U (Note20 Ultra 5G), Snapdragon 865+, 10GB RAM, Android 13
- **Termux**: F-Droid (aarch64)
- **Hermes**: v0.15.2 CLI (Ubuntu proot venv)
- **Claude Code**: 2.1.128 (Ubuntu proot — `claude-proot`)
- **llama.cpp**: built in Ubuntu proot (`/root/llama.cpp/build/bin/`)
- **hermes-hudui**: port 3001 (`/root/hermes-hudui/`)
- **Primary vault**: `/sdcard/Documents/Hermes_Phone_Vault/`
- **QuickRef vault**: `~/storage/audiobooks/QuickRef_Vault/` (cheat sheets)
- **Ubuntu**: 25.10 via proot-distro
- **Desktop**: Windows 11 + WSL2 (secondary — always-on gateway host)
- **Mirror files**: AGENTS.md and CLAUDE.md kept in sync with QuickRef_Vault

## Vault Structure

| Folder | Purpose | Note Type | ID Format |
|--------|---------|-----------|-----------|
| devices/ | Phone device profiles | device-profile | DP-NNNN |
| devices/types/ | Device type taxonomy | device-type | DT-NNNN |
| knowledge/ | Android/phone discoveries | knowledge | KNW-NNNN |
| decisions/ | Decision rationale | decision | DEC-NNNN |
| sessions/ | Cross-session synthesis | session-synthesis | SYN-YYYY-MM-DD-NNN |
| capabilities/ | Skill x tool x provider inventory | capability | CAP-SKL-NNNN |
| skills/ | Phone skill tracker | skill | SKL-NNNN |
| gemini-scribe/ | Gemini CLI scribe sessions | — | — |
| notes/ | General notes | — | — |
| inbox/ | Quick captures | any | N/A |
| archive/ | Superseded content | any | N/A |

Schema source of truth: `_system/_schemas.yaml`.

## Android Constraints

- No Docker, no systemd, no root
- Bootloader **LOCKED** (Verizon — no custom ROM, permanent)
- Ports <1024 blocked (use 8022 SSH, 8080 llama-server, 3001 hermes-hudui)
- Background killed on screen-off — use termux-wake-lock + notification
- SELinux enforcing, scoped storage
- Proot-distro for Linux containers (Ubuntu 25.10 verified)
- `input text` via ADB: fails on special chars — plain alphanumeric + `/` + `.` + space only
- scrcpy SendKeys: DOES NOT WORK when soft keyboard visible in Termux
- npm on proot: ALWAYS use yarn (npm rename fails with ENOTEMPTY/ENOENT)

## Key Commands

```bash
hermes status          # Live provider/model check
dash                   # btop + hermes insights in tmux split
claude-proot           # Claude Code in Ubuntu proot
bash /sdcard/go.sh     # Start llama-server (port 8080)
```

## ADB Forwarding

```bash
adb forward tcp:8080 tcp:8080   # llama-server
adb forward tcp:3001 tcp:3001   # hermes-hudui
```

## Rules

1. Read `_system/_briefing.md` at session start
2. Log non-obvious decisions immediately (DEC)
3. Create KNW entries for durable discoveries
4. Maintain DP entries for managed devices
5. Archive aggressively — never delete
6. Machine-first means terse
7. Keep AGENTS.md and CLAUDE.md mirrors in sync across vaults
