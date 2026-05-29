# Hermetic Keyboard — Facelift Handoff Map

**Last updated:** 2026-05-28
**Project:** `C:\Users\MarsBase\Documents\android-ai-keyboard-harness` (FlorisBoard fork, app "HermeticA-Z")
**Installed build:** `dev.patrickgold.florisboard.vault.debug` on Moto g 5G (ZY22G7NFLK). Build verified `BUILD SUCCESSFUL`, installed.

## Visual authority (do not drift)
> ✅ 2026-05-29 (ratified [[decisions/DEC-0006]]): canonical visual authority is `C:\Users\MarsBase\Documents\android-ai-keyboard-harness\Hermetic_A-Z_Vault`. The old Pictures path does NOT exist and is retired.

Palette authority (canonical: `...\android-ai-keyboard-harness\Hermetic_A-Z_Vault\`; old Pictures path retired):
Violet `#A855F7` · Sky-Blue `#38BDF8` · Amber `#F59E0B` on Void Black `#080808`.
Legacy CyberDeck cyan/magenta = **forbidden**.

---

## DONE & on-device (this session)
1. **Palette in source** — `res/values/colors.xml` aligned (primaryDark→#8644C6, warning→#F59E0B, card→#14130F, nav/window→#080808, toolbar fg→#FFFFFF).
2. **Night background** — Void Black `#080808` in `values-night/colors.xml`.
3. **Theme unconditional** — `HermeticTheme.kt`: removed the bare-Material fallback; Hermetic palette/shapes/type now always applied (audit H2).
4. **Logo wired** — splash (`themes.xml` → `windowSplashScreenAnimatedIcon=@drawable/hermetic_logo`) + Home/welcome header (`HomeScreen.kt`). Asset: `res/drawable-nodpi/hermetic_logo.png`.
5. **Launcher app icon** — generated `ic_hermetic_fg` foregrounds (mdpi→xxxhdpi) and repointed all 6 adaptive-icon XMLs (`mipmap-anydpi-v26/ic_app_icon_{debug,stable,beta}{,_round}.xml`) to `@mipmap/ic_hermetic_fg` on void-black background. Compiles + installed. *(Mars: confirm look in your app drawer.)*

## BLOCKED
- **On-device screenshot verify** — Moto is locked behind a secure PIN; I can't bypass it. Unlock the phone and open the app → I'll capture Home + an AI screen to confirm rendering. (stay-awake on, screen timeout 10 min already set.)

---

## REMAINING WORK — direct steps (no Gemini relay; do it in-session)
> The earlier `gemini_packet_01_ai_screens.md` is **deprecated** — ignore/delete it. Mars: this is the simpler path. These are mechanical edits I can do directly next session.

**A. Themed (monochrome) icon** — the 6 adaptive XMLs still point `monochrome` at the old Floris glyph (`ic_app_icon_*_monochrome`). Low priority; only affects Android-13 "themed icons" mode. To finish: make a single-color silhouette of the Hermetic mark and repoint `monochrome` like we did `foreground`.

**B. Tokenize the 3 AI screens** (`ime/ai/CteSettingsActivity.kt`, `ime/ai/CteKeysActivity.kt`, `ime/ai/settings/VoiceSettingsActivity.kt`):
  - Replace hardcoded `.dp` spacing with `Hm*` tokens from `ime/ai/theme/HermeticTokens.kt` (HmSpaceScreenH/ScreenTop/CardPadV/CardPadH/KeyH/KeyV).
  - Card elevation literals → `HmElevationCard`. Corners → `HmShapeCard`/`HmShapePopup`/`HmShapeKey`.
  - Replace any "Neon cyberpunk palette (dark only)" copy with Hermetic wording.
  - **Do not** touch preference keys, IDs, logic, or navigation. (audit M4)

**C. M1 — unify theme engines** — there are duplicated container hex values across the two theme paths. Consolidate so `HermeticTokens.kt` is the only source. Audit detail in `Hermetic_Companion_UI_Audit.md`.

**D. M3 — rename legacy identifiers** (deferred, higher risk): `cp_*`, `isCyberpunk`, `cyberdeck` SharedPref keys/strings. Rename carefully with migration for the existing `cyberdeck_prefs` pref so users' theme toggle survives. Touch points incl. `HermeticTheme.kt` (`isCyberpunkEnabled`/`setCyberpunkEnabled`, `cyberdeck_prefs`, `settingsTheme="cyberdeck"`).

**E. colorError token** — `colors.xml` still has `colorError #B00020` with a TODO. Define a Hermetic error token (HmRed = `#FF3860`) and point to it.

---

## Cleanup pending YOUR confirmation (I don't delete without it)
- `_res_bak/` — 6 backup files I moved out of `res/` (they broke the build when inside res). Safe to delete once you're happy with the new icon/palette.
- `Claude_Vault/inbox/gemini_packet_01_ai_screens.md` — deprecated, deletable.
- `Claude_Vault/inbox/hm_home.png` — lockscreen screenshot, deletable.

## Build/deploy crib
```
JAVA_HOME = C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot
cd C:\Users\MarsBase\Documents\android-ai-keyboard-harness
.\gradlew.bat :app:installDebug          # build type debug → ...vault.debug
```
Rules learned: every file under `res/` must end `.xml`/`.png` (a `.bak` there breaks `mergeDebugResources`). In the PowerShell bridge avoid `[IO.File]::*` writes (they wiped a file once) — use Set-Content / Copy-Item.
