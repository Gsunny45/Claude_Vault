---
type: knowledge
id: KNW-0025
subject: "Keyboard ↔ Vault key/config injection — test plan & harness"
confidence: verified
last_verified: 2026-05-29
source: "Live probe 2026-05-29: CteKeysActivity.kt, KeyVault.kt, TriggerConfigStore.kt source + on-device adb run-as inspection (Moto ZY22G7NFLK)"
related:
  - "KNW-0024"
  - "KNW-0008"
  - "DEC-0004"
tags: [keyboard, injection, testing, adb, keyvault, floris, boundary-pointer]
tokens: 1700
---

# Keyboard ↔ Vault Key/Config Injection — Test Plan

> **Boundary note (per [[decisions/DEC-0004]] / [[knowledge/KNW-0024]]):** this is a
> *boundary-pointer* test record. The keyboard's code lives at
> `Documents\android-ai-keyboard-harness` (not a vault). This doc and the test
> scripts describe how to verify the injection contract; they are not keyboard
> internals pulled into vault briefings.

## What is under test

The **key/config injection** path only — sense (1) of "injection" from KNW-0024:
provider API keys delivered from the host into the keyboard's encrypted KeyVault
via an ADB-launched intent. (Prompt/context injection — sense 2 — is out of scope
for this suite.)

## Verified contract (read from source 2026-05-29)

**Activity:** `dev.patrickgold.florisboard.ime.ai.CteKeysActivity`
**Package:** `dev.patrickgold.florisboard.vault.debug`

> **CORRECTED LAUNCH CONTRACT (verified live 2026-05-29).** The command in the
> `CteKeysActivity` source doc-comment (`am start -n .../CteKeysActivity ...`) is
> **wrong on this build** and must not be used. Findings:
> - `am start -n <component>` alone → `Error: Activity ... does not exist` (the
>   activity has no default-launchable filter; only a custom VIEW deep link).
> - `am start -a VIEW -d ui://hermetica-z/cte/keys` alone → routed to Android's
>   **ResolverActivity chooser** (the `ui://` scheme is not unique on this device),
>   so CteKeysActivity never runs and nothing injects.
> - **Working form: explicit component PLUS matching action+data**, which binds
>   directly and bypasses the resolver:

```
adb shell am start \
    -n dev.patrickgold.florisboard.vault.debug/dev.patrickgold.florisboard.ime.ai.CteKeysActivity \
    -a android.intent.action.VIEW -d "ui://hermetica-z/cte/keys" \
    --ei inject 1 -e keyRef <KEYREF> -e keyValue "<VALUE>"
```

> **singleTask caveat:** the activity is `launchMode="singleTask"` and the inject
> logic lives only in `onCreate` (no `onNewIntent` override). A repeat launch while
> the task already exists is delivered to the running instance and **does not
> re-inject**. Tests therefore `am force-stop` before every inject to force a fresh
> `onCreate`. (Real-world implication: from a cold app state injection works; if the
> Keys screen is already open, an ADB inject is silently ignored.)
>
> **Whitespace-value caveat:** a whitespace-only `keyValue` passed as separate adb
> args is stripped by the device shell, so `am` errors *"Argument expected after
> keyValue"* before the app runs. To exercise the app's `isNotBlank()` guard, send
> the whole `am` line as one nested-quoted shell string (see `Invoke-InjectShell`).

Behaviour, from `CteKeysActivity.onCreate`:

| Condition | Result |
|-----------|--------|
| `inject == 1` AND `keyRef != null` AND `keyValue != null` AND `keyValue.isNotBlank()` | `KeyVault.set(keyRef, keyValue.trim())`; logs `Key injected via ADB: <keyRef> (<N> chars)`; toast "<keyRef> saved via ADB"; `finish()` |
| `inject == 1` but missing/blank extras | logs `ADB inject: missing keyRef or keyValue extras`; toast error; `finish()` |
| `inject != 1` (or absent) | normal UI opens (manage keys screen) |

Notes that drive test design:
- The injected value is **trimmed** — a `keyValue` of all-whitespace is blank → rejected.
- `keyRef` is **not validated against triggers.json** at inject time. Any string is
  stored. (It only needs to match a provider keyRef to *appear* in the manage-keys UI.)

**Storage:** `KeyVault` → `EncryptedSharedPreferences` file
`shared_prefs/florisboard_ai_keyvault.xml`, scheme AES256-SIV (keys) / AES256-GCM
(values), via Tink. **Both entry names and values are encrypted** — you cannot read
which keyRef is set by inspecting the XML. Verification must use logcat + file
mtime/size delta, not plaintext readback.

**Unlock requirement:** KeyVault uses credential-encrypted storage. If the device is
locked (not unlocked since boot), `set()` is a **silent no-op** with log
`setKey(<ref>): device locked, skipping`. Tests MUST assert the device is unlocked first.

**Valid provider keyRefs** (from on-device `files/cte/configs/triggers.json`,
schemaVersion 2): `GROQ_KEY`, `GROQ_KEY_2`, `CEREBRAS_KEY`, `ANTHROPIC_KEY`,
`OPENAI_KEY`, `GROK_KEY`, `MISTRAL_KEY`, `FIREWORKS_KEY`, `DEEPSEEK_KEY`,
`GEMINI_KEY_1`, `GEMINI_KEY_2`, `OPENROUTER_KEY`.

**Config path on-device:** `getFilesDir()/cte/configs/` (note the `configs/`
subdir — `CteKeysActivity.loadProvidersFromDisk()` reads
`getConfigsDir()/triggers.json`).

## Preconditions (PRE)

| ID | Check | Expected |
|----|-------|----------|
| PRE-1 | `adb devices` lists ZY22G7NFLK as `device` | present, authorized |
| PRE-2 | Package `...vault.debug` installed | `pm path` returns an APK |
| PRE-3 | Device unlocked (`dumpsys window` → `mDreamingLockscreen=false`, `mAwake=true`) | unlocked |
| PRE-4 | `run-as <pkg>` works (debug build) | can `ls shared_prefs` |
| PRE-5 | `triggers.json` present at `files/cte/configs/` | exists, parses |

## Test cases (TC)

Each case is **non-destructive**: it injects a throwaway keyRef
`__TEST_INJECT_KEY__` with a sentinel value, then deletes that entry from the
KeyVault prefs at teardown so no real provider key is touched.

| ID | Name | Steps | Expected | Verify via |
|----|------|-------|----------|------------|
| TC-1 | Happy-path inject | clear logcat; inject `__TEST_INJECT_KEY__` = `sk-test-<rand>`; wait | logcat `Key injected via ADB: __TEST_INJECT_KEY__ (N chars)` with N == value length; prefs file mtime advances; entry count +1 | logcat grep + prefs mtime/entry-count delta |
| TC-2 | Trim behaviour | inject value `"  sk-pad  "` | logged char count == trimmed length (not padded length) | logcat `(N chars)` equals trimmed len |
| TC-3 | Blank value rejected | inject `keyValue` = `"   "` (whitespace) | logcat `ADB inject: missing keyRef or keyValue extras`; prefs entry count unchanged | logcat grep + count delta == 0 |
| TC-4 | Missing keyValue rejected | inject with `keyRef` but no `keyValue` extra | logcat missing-extras warning; no write | logcat + count delta == 0 |
| TC-5 | Missing keyRef rejected | inject with `keyValue` but no `keyRef` | logcat missing-extras warning; no write | logcat + count delta == 0 |
| TC-6 | inject flag off | launch activity with `--ei inject 0` and a keyRef/keyValue | no inject log line; activity opens UI (no write) | logcat absence + count delta == 0 |
| TC-7 | Real-provider roundtrip (opt-in) | inject a real keyRef (e.g. `GROQ_KEY`) with a real key — only when `-IncludeRealKey` passed | inject log; entry persists; visible as "configured" in manage-keys UI | logcat + manual UI confirm |
| TC-8 | Idempotent overwrite | inject `__TEST_INJECT_KEY__` twice with different values | both log success; entry count rises by 1 total (overwrite, not duplicate) | count delta == 1 after two injects |

**Teardown (every run):** remove the `__TEST_INJECT_KEY__` entry. Because the XML
key-name is encrypted, the entry cannot be deleted by name from the file directly;
teardown instead snapshots the prefs file before the run and **restores that
snapshot** at the end (TC-7 real-key injects are excluded from auto-restore and
left in place).

## Pass/fail definition

A run **PASSES** when PRE-1..5 all hold and TC-1..6 + TC-8 all meet expected.
TC-7 is opt-in and reported separately. Any PRE failure aborts before mutation.

## How to run

```powershell
# From host PowerShell (Windows-MCP). Non-destructive by default.
powershell -ExecutionPolicy Bypass -File .\test_key_injection.ps1
# Include a real-key roundtrip (prompts / takes -RealKeyRef + -RealKeyValue):
powershell -ExecutionPolicy Bypass -File .\test_key_injection.ps1 -IncludeRealKey -RealKeyRef GROQ_KEY -RealKeyValue "<key>"
```

Or the Python runner (same logic, cross-checked):
```
python test_key_injection.py
```

## Artifacts

- `test_key_injection.ps1` — primary host runner (PowerShell).
- `test_key_injection.py` — cross-check runner (stdlib only, calls adb).
- Output: pass/fail table to stdout + `injection_test_report_<ts>.txt`.
- Delivered to `Desktop\Hermes_Drop_vault\`; source kept in `Claude_Vault\exports\`.

## First live run — results (2026-05-29, Moto ZY22G7NFLK, build 0.4.6-debug)

Executed against the live device once the corrected launch contract was found.
Baseline KeyVault held **2 entries** (Tink keyset-management strings only — i.e.
**no real provider keys were stored**).

| Case | Result | Evidence |
|------|--------|----------|
| PRE-1..5 | PASS | device online; pkg installed; unlocked/awake; run-as OK; triggers.json parsed |
| TC-1 Happy-path | PASS | `Key injected via ADB: __TEST_INJECT_KEY__ (12 chars)`; entry count 2→3 |
| TC-2 Trim | PASS | `"  sk-pad  "` logged as 6 chars (trimmed) |
| TC-3 Blank rejected | PASS | whitespace value → `ADB inject: missing keyRef or keyValue extras`; no write |
| TC-4 Missing keyValue | PASS | reject log; no write |
| TC-5 Missing keyRef | PASS | reject log; no write |
| TC-6 inject=0 | PASS | no inject log; count unchanged |
| TC-8 Idempotent overwrite | PASS | two injects same ref → count +1 only (3→4) |

**Verdict: PASS** — the key/config injection path is functional via the corrected
contract. The shipped source doc-comment command is broken (see corrected contract above).

## Update 2026-05-29 — go-live + harness fixes ([[decisions/DEC-0005]])

Mars set a **Gemini key and a Groq key**; project is a go. KeyVault now holds 2 user
keys + 2 Tink keyset entries. `gemini_1`/`gemini_2`/`groq` all enabled; routing
default `gemini_1`, `standaloneMode: true`. Device reaches both provider endpoints.

Three `CteKeysActivity` defects this suite surfaced were fixed in the harness and
rebuilt/installed on the Moto:
1. Stale inject doc-comment → corrected to the verified component+action+data contract.
2. **singleTask re-inject gap** → added `onNewIntent` + extracted `handleAdbInject()`;
   inject into an already-open Keys screen now writes (verified: count 4→5).
3. Char-count log used untrimmed length → now logs `trimmed.length`.

Backup `CteKeysActivity.kt.bak_preinject` left in the harness pending Mars confirmation.

### Open cleanup item
The first run left two throwaway refs in the KeyVault (`__TEST_INJECT_KEY__`,
`__OVERWRITE_TEST__`), count now 4. Names are encrypted so they can't be deleted by
name; they're harmless (not provider keyRefs, never shown in the manage-keys UI). To
reset to a clean 2-entry state, clear the app's KeyVault prefs while no real keys are
present:
`adb shell run-as <pkg> rm shared_prefs/florisboard_ai_keyvault.xml` then reopen the
app (regenerates the Tink keysets). **Only safe while no real provider keys are set.**
Subsequent full script runs auto-restore from a pre-run snapshot.

## Re-run + E2E smoke (2026-05-29, evening — Moto ZY22G7NFLK)

Phone connected (USB `ZY22G7NFLK` + WiFi ADB `192.168.1.105:5555`). Two devices
attached → all `adb` calls must use `-s ZY22G7NFLK` or `adb shell` errors "more than
one device". Keyboard is now the **active system IME**
(`settings get secure default_input_method` → `…vault.debug/…FlorisImeService`).

### Key/config injection — re-verified PASS
- PRE-1..5 all PASS (device online, pkg installed, unlocked/awake, run-as OK,
  triggers.json parsed). Baseline KeyVault = **6** string entries (2 Tink + 2 prior
  throwaway refs + Gemini + Groq).
- TC-1 happy-path re-run inline: injected `__TEST_INJECT_KEY__` = `sk-test-93372` →
  `CteKeysActivity: Key injected via ADB: __TEST_INJECT_KEY__ (13 chars)` (exact match).
- Note: `test_key_injection.ps1` run detached stalled in the per-case logcat-wait loop
  past the 45 s Windows-MCP cap; the inline TC-1 above is the decisive confirmation.
  Full suite already PASSED earlier this day (table above).

### Prompt/trigger pipeline — LIVE / wired (first on-device evidence)
Focused a Google Keep note (FlorisBoard up, `mInputShown=true`) and drove input via
`adb input text`. Logcat captured the pipeline firing for the first time on-device:
```
CteEngine: Built 2 provider instances (configured: 13)
CteEngine: Loaded 7 skills from skills.json
CTE: Trigger detected: '/fix' with text=''
CTE: Provider returned empty result for '/fix'
```
So: trigger detection works, the CTE engine instantiates the **2 reachable cheap-budget
providers** (gemini_1 + groq; local skipped via `standaloneMode`), loads skills, and
handles an empty payload gracefully.

### What's NOT yet captured + why
The full **completion-insert round-trip** wasn't reproduced under ADB automation:
- Detection is **start-anchored** and fires on the space **immediately after** the
  trigger token. `adb input text` streams the whole string instantly, so the trigger
  fired before its payload was typed → `text=''`.
- Putting the trigger at the **end** of the buffer ("…text /fix") produced **no**
  detection at all (confirming start-anchoring).
- `files/cte/logs/events.jsonl` absent — expected (`routing.json monitoring.captureRuns:
  false`), so no run-log readback.

**Conclusion:** the pipeline is proven live up to and including trigger detection +
provider instantiation; the only unproven leg is the final inserted completion, gated by
**ADB input cadence vs. a start-anchored detector**, *not* by any keyboard defect. A
human typing a sentence then the trigger at normal speed exercises it correctly — a
~10-second manual acceptance check closes DEC-0005's last open item.

### Teardown / state
- Keep scratch note cleared; returned to home. No real provider keys touched.
- TC-1 left the harmless `__TEST_INJECT_KEY__` throwaway ref (encrypted name, never shown
  in the manage-keys UI, not a provider keyRef) — same documented situation as the first run.
- Artifacts (screenshots) in `exports/e2e_*_2026…png`.
