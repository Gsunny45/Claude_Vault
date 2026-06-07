---
type: knowledge
id: KNW-0029
subject: "Why CTE /fix produces no output on Note 20 — root-cause chain + 2026-06-03 stabilization"
confidence: verified
last_verified: 2026-06-03
source: "Live logcat diagnosis on Note 20 Ultra (R5CN81CDXJV) 2026-06-03 via Windows-MCP/adb; CteEngine.kt + FlorisImeService.kt + on-device files/cte/configs"
related:
  - "KNW-0024"
  - "KNW-0025-keyboard-vault-injection-tests"
  - "KNW-0008"
tags: [keyboard, cte, /fix, trigger, provider-routing, note20, debugging, harness]
tokens: 1500
---

# CTE `/fix` dead-end — full root-cause chain (verified on device)

Live-debugged on the Note 20 Ultra (`R5CN81CDXJV`) 2026-06-03. The "nothing happens"
on `/fix` was **four stacked bugs**, each confirmed by logcat. Detection itself works;
the failures are config + routing + a self-inflicted regression.

## The chain (in the order each was peeled back)

1. **Empty command list (primary user-facing cause).** The on-device runtime
   `files/cte/configs/triggers.json` had been rewritten to a **providers-only** file
   with **no `"triggers"` section** (2538 bytes, dated the same day keys/vault were
   saved). `detectTrigger` got an empty map → **0 trigger detections** despite input
   landing (104 / 63 `onUpdateSelection` events). The bundled asset (`app/src/main/
   assets/cte_defaults/configs/triggers.json`, 11396 bytes) has the full triggers.
   **Strong suspicion: the on-device config writer (CteKeys/CteSettings save path)
   rewrites triggers.json and drops every section except `providers`.** This is the
   real root cause and the #1 fix.

2. **Self-heal + visibility added this session (UNCOMMITTED working-tree edits).**
   `CteEngine.detectTrigger` now self-heals (`registeredTriggers ?: loadTriggersConfig()`),
   added a 15s `processing`-flag watchdog, a `CyberToast` "⚡ <trigger> — working…" on
   detection, and `FlorisImeService` init try/catch + null-diagnostic logs. The toast
   works (user confirmed ⚡). **BUG I introduced:** the self-heal calls
   `loadTriggersConfig()` → `awaitSeedComplete(2000)` **on the main thread** ("possible
   ANR" warning ×21) → contributed to the IME glitching / being dropped. **Must move
   off the main thread before this is committed.**

3. **Routing pins `/fix` to a dead local server.** With the full triggers.json in place,
   detection fired (`Trigger detected: '/fix'` ×6) but `ProviderRouter` logged
   **"No eligible providers — falling back to first instantiable: local (standaloneMode
   =false)"**. `/fix` is defined `provider: local`, `budget: cheap`; `local` =
   llama.cpp at `127.0.0.1:8080` which is **not installed on the Note 20** → connection
   hang = the "freeze." **4 of 13 providers built** (local + 3 cloud from loaded keys;
   6 keys loaded, `routing.json` `balanced: []` empty, `default: "local"`). The
   explicit-local skip (commit `1ec4592c`) only triggers when `standaloneMode=true`,
   which it isn't here.

4. **Cloud-routed config crashed the IME (reverted).** Pushed an edited triggers.json
   (local `enabled:false`, triggers repointed to `groq`) → keyboard crashed/glitched
   and the **Samsung BrailleIme took over as default**. Likely `buildPipeline` chokes
   with `local` disabled while `routing.json` `default` is still `"local"`, compounded
   by accumulated main-thread ANRs. **Reverted to bundled config.**

## Device reality (important)
Note 20 has **only two IMEs**: HermeticA-Z and `com.samsung.android.accessibility.
talkback/...BrailleIme`. **No normal fallback keyboard.** Whenever HermeticA-Z fails,
braille becomes default — that is the "braille coming on." User advised to install
Gboard/Samsung Keyboard as a safety net (needs Play Store; not adb-installable).

## Stabilization done 2026-06-03
Restored bundled `triggers.json` on device, `am force-stop`, set HermeticA-Z back as
default IME (braille had grabbed the default slot). Plain typing is stable; CTE/AI is
parked. No code committed.

## Concrete fixes for the next (controlled) round — priority order
1. **Config writer must not strip `triggers`.** Find the key/vault save path that
   rewrites `triggers.json` and make it round-trip every section (or write providers to
   a separate file). This is the actual root cause of "empty command list."
2. **Move `detectTrigger` self-heal off the main thread** — `awaitSeedComplete` must not
   block the IME UI thread.
3. **Routing for cloud-only devices** — `/fix` pinned to `local`; make `ProviderRouter`
   skip `local` when no local server is reachable regardless of `standaloneMode`, and/or
   repoint `routing.json` `default`/budgets off `local` for keyless-local devices.
4. **Uncommitted harness edits** (`CteEngine.kt`, `FlorisImeService.kt`) need the
   main-thread fix before commit. Decide keep/refine.

## Test venue
Do this on the **backup Moto (`ZY22G7NFLK`)** or as code + unit tests — **not live on
the primary Note 20.** Live-debugging the daily driver destabilized it on 2026-06-03.
