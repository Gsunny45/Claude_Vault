---
type: session
id: SES-2026-05-30-002
date: 2026-05-30
agent: claude
status: handoff
title: CTE audit telemetry shipped + verified on device; accessibility service fixed
tokens: 1500
---

# Next Session — CTE Intelligence & Audit (post-verification)

Supersedes the prior `NEXT-SESSION-cte-audit-handoff.md` (SES-2026-05-30-NEXT).
Everything below is verified against live code AND the running app on Moto
(ZY22G7NFLK) on 2026-05-30. Commit: **`1b5434bc`** on `main`
(`android-ai-keyboard-harness`), 6 files, 583+/38-.

## Shipped + verified this session

1. **Audit wired into skill + chain pipelines** — `CteEngine.executeSkillPipeline`
   and `executeChainPipeline` now call `recordResult` at **all 8** exit points
   (4 each), mirroring the standard path. Telemetry is no longer incomplete.

2. **Accessibility service registration FIXED (real root cause).** The prior
   handoff said the UI was missing — wrong. `CteSettingsActivity` already had the
   full UI (intent, live `Settings.Secure` status read, `onResume` recheck,
   "Accessibility Service" section), committed in an earlier session. The actual
   bug was in `AndroidManifest.xml`: the `<service>` intent-filter action was
   misspelled `android.accessibility.AccessibilityService` instead of
   `android.accessibilityservice.AccessibilityService`, so Android never listed
   the service and it could never be enabled. Fixed. **Verified** via
   `pm query-services` + `dumpsys package` — the service is now registered with
   the correct action. This is what unblocks `{{file.path}}`/`{{file.tags}}`
   (still needs the user to toggle it on in Settings → Accessibility).

3. **`/fix` fired end-to-end on device.** After `pm clear` (see below), typed
   `teh cat /fix ` into the test field. Logs: `Trigger detected: '/fix'` →
   provider empty (no keys) → recorded. `cte_audit_prefs.xml` now holds
   `audit_stat_/fix = {attempts:1, failures:1, lastIntent:"Route",
   confidenceSum:0.68, elapsedSumMs:56}`. AnalyticsActivity renders it:
   "1 Trigger · 1 Run · 68% Avg conf", `/fix` row with Route badge, 0% success,
   avg 56 ms. Empty state cleared.

4. **AnalyticsActivity registration** (deep link `ui://hermetica-z-analytics`)
   and the HomeScreen entry were uncommitted from last session — now committed.

## Important device note

The app **hung on the Hermetic splash** at session start. Root cause:
`FlorisAppActivity.onCreate` keeps the splash until `prefs.datastoreReadyStatus`
is true (lines 88/117); a **corrupted Jetpref datastore** from a prior install
left it never-ready (activity went ANR). **`adb shell pm clear
dev.patrickgold.florisboard.vault.debug` fixed it** — cold start then advanced
through setup ("Initialize Interface" → "Complete Setup") to a clean HomeScreen.
This is the same blocker that defeated last session's ADB taps; it was a
*hang*, not a wizard awaiting input. Cost of the clear: wiped provider keys,
vault URI, IME/theme selection, setup state.

## ADB testing gotcha (so next session doesn't lose time)

`detectTrigger` matches the trigger as a whitespace-split **complete word**, and
`onSelectionChanged` has a **200ms debounce**. To fire via ADB:
`input text "body%s/fix"` (use `%s` for spaces, NOT `+`), then **wait >200ms**,
then a real `input keyevent KEYCODE_SPACE`. Chars sent faster than 200ms apart
get debounced away; `+` is a literal plus and breaks word-matching.

## Provider routing — investigated 2026-05-30 (commit `1ec4592c`)

Keys were re-added (Gemini + Groq). Verified on device via the API Keys screen:
`GROQ_KEY` and `GEMINI_KEY_1` **both set**; `gemini_2`/`groq2`/others unset.
Key-mismatch theory ruled out.

Chased why `/fix` still returns empty, found + fixed one bug, one still open:

- **FIXED (`1ec4592c`):** `ProviderRouter.selectProviderId` step 1 returned the
  trigger's `preferredProvider` (`/fix` → `local`) without honoring
  `standaloneMode`. With `standaloneMode=true` (routing.json; llama-server down)
  it dead-ended on the unreachable local server. Now skips local in the
  explicit-preference path so it falls through to budget rules (gemini_1/groq).
- **Pipeline staleness (by design, not a bug):** `buildPipeline()` only
  instantiates a provider if its key exists **at build time**, and is guarded by
  `pipelineInitAttempted`. Keys added after warmUp don't take effect until
  `reloadConfig()` (CTE Settings → Reload) or an IME restart. After restart the
  log correctly shows `Built 3 provider instances` (local, groq, gemini_1).
- **STILL OPEN:** even with providers built + keys present, `/fix` fast-fails in
  **~76ms with ZERO ProviderRouter/CostLogger/Gemini logging** — too fast for a
  network call. Suspected: the streaming/inline-render path, or an artifact of
  **synthetic `adb input`** (saw `endBatchEdit on inactive InputConnection` right
  before the empty result — the IC tears down between adb keystrokes).
  **Next: test `/fix` with a real finger in a real text field.** If it still
  fails, trace `ProviderRouter.tryProviderWithFallback` + the Gemini provider's
  `route()` Flow + `OutputModeRouter`/`InlineRenderer`. The audit layer is fine —
  it faithfully records every attempt as failure=1.

## Next steps (priority order)

1. **Hand-test `/fix`** (real finger, real field) now that keys + router fix are
   in. Confirm a **success=true** telemetry row in AnalyticsActivity. If it fails,
   pull full unfiltered app-pid logcat at the moment of the trigger (provider
   error is not surfacing under tag filters).
2. **Enable the accessibility service on-device** (now that it's registerable):
   Settings → Accessibility → FlorisBoard/HermeticA-Z. Confirm `{{file.path}}`
   resolves in an Obsidian template.
3. **Resolve orphaned `HermesAttachSystem.kt`** — still `Legacy*`-renamed and
   unreferenced. Committed as-is this session (deletion needs explicit user OK
   per vault rules). Decide: delete, or fold `parsePlanDelegateVerify` /
   `DelegateBlock` into the live `HermesCteAttachSystem.kt`.
4. **Keyboard surface still stock light-grey** — the Hermetic Night Snygg theme
   is registered but not auto-selected (harness CLAUDE.md gap #4). Wire setup
   wizard FINISH → `ThemeManager.activeTheme`.
5. **Two `CLAUDE.md` files still disagree** on the canonical visual-authority path
   (harness path vs `Pictures\Hermetic_A-Z_Vault`). Unresolved; reconcile.

## Caveats / honesty log

- No `gradlew test`/`lint` this session — only `assembleDebug` (passed) + on-device.
- Only a **failure** telemetry row exists; success path unproven until keys return.
- `pm clear` reset device state — anything that depended on prior on-device prefs
  (keys, vault URI, enabled accessibility) must be re-set up.
