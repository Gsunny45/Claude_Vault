# Gemini Prompt Packet #1 — Restyle the 3 AI Settings Screens

**Relay this whole block to Gemini 3.5 Flash (AI Studio). Attach the 4 files listed under INPUT FILES.**

---

## ROLE
You are a Kotlin/Jetpack Compose refactoring engine for an Android keyboard app (FlorisBoard fork, "HermeticA-Z"). You apply mechanical, low-risk style alignment edits. You do NOT change behavior, logic, navigation, or any preference keys.

## INPUT FILES (attach all 4)
1. `HermeticTokens.kt` — the design-token single source of truth. READ ONLY. Do not edit.
2. `CteSettingsActivity.kt` — edit target.
3. `CteKeysActivity.kt` — edit target.
4. `VoiceSettingsActivity.kt` — edit target.

## DESIGN AUTHORITY
Palette (already correct app-wide, do not re-introduce others):
- Violet `#A855F7` (HmViolet) — primary
- Sky-Blue `#38BDF8` (HmSkyBlue) — secondary
- Amber `#F59E0B` (HmAmber) — accent
- Void Black `#080808` (HmBackground)
LEGACY = FORBIDDEN: never use cyan/magenta or any "cyberpunk/CyberDeck" neon. If you find such hardcoded colors, replace with the nearest Hm* token.

## RULES (apply to the 3 edit targets only)

1. **Tokenize spacing.** Replace hardcoded `.dp` padding/spacing literals with the matching `Hm*` spacing token from HermeticTokens.kt (HmSpaceKeyH, HmSpaceSmartbarPad, HmSpaceKeyV, HmSpaceCardPadV, HmSpaceCardPadH, HmSpaceScreenH, HmSpaceScreenTop). Match by intent: screen-edge horizontal padding → HmSpaceScreenH; top-of-screen → HmSpaceScreenTop; inside-card vertical/horizontal → HmSpaceCardPadV / HmSpaceCardPadH. If no token fits a value, leave the literal and add `// TODO(token): no matching Hm space` beside it.

2. **Standardize card elevation.** Any Card/Surface elevation literal (e.g. `2.dp`, `4.dp`) → `HmElevationCard`.

3. **Standardize corner shapes.** Card corners → `HmShapeCard`; popups/dialogs → `HmShapePopup`; small chips/keys → `HmShapeKey`; bottom bars → `HmShapeSmartbar`. Replace hardcoded RoundedCornerShape values only where one of these clearly applies.

4. **Purge cyberpunk copy.** Replace any user-facing string like "Neon cyberpunk palette (dark only)" or similar with Hermetic language, e.g. "Hermetic theme — Violet · Sky · Amber on Void Black". Do not touch resource keys/IDs, only the human-readable text.

5. **Colors → tokens.** Any hardcoded `Color(0xFF...)` that matches (or approximates) the palette → the Hm* token. Container/on-container structural colors that Material3 requires may stay as locals.

## HARD CONSTRAINTS (do not violate)
- Do NOT rename or alter any preference key, datastore identifier, function name, class name, route, or intent.
- Do NOT change logic, conditionals, coroutines, or navigation.
- Do NOT edit HermeticTokens.kt.
- Do NOT add new dependencies or imports beyond the Hm* token imports already used in the file's package.
- Keep imports valid — add `import ...theme.HmSpaceCardPadV` etc. as needed.

## OUTPUT FORMAT
For EACH of the 3 edited files, return:
1. A one-line summary of what changed.
2. The COMPLETE updated file (full contents, not a diff), in its own code block, ready to paste over the original.
Then a final "RISK NOTES" section listing anything you left as a TODO or were unsure about.
