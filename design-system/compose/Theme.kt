// ═══════════════════════════════════════════════════════════════════════════════
// HERMETIC OS — Compose Theme Configuration
// ═══════════════════════════════════════════════════════════════════════════════
// Auto-generated from tokens.yaml by sync-tokens.py
// DO NOT EDIT MANUALLY — changes will be overwritten on next sync.
//
// Package: com.hermetic.designsystem.theme
// ═══════════════════════════════════════════════════════════════════════════════

package com.hermetic.designsystem.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.Typography
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.view.WindowCompat

// ─────────────────────────────────────────────────────────────────────────────
// §1  Material3 Dark Color Scheme
// ─────────────────────────────────────────────────────────────────────────────

private val HermeticDarkColorScheme = darkColorScheme(
    // Primary (Violet)
    primary                = PrimaryDefault,       // #8C7BFF
    onPrimary              = OnPrimary,            // #080808
    primaryContainer       = PrimarySubtle,        // #2D2466
    onPrimaryContainer     = Violet100,            // #E4E1FF

    // Secondary (Sky)
    secondary              = SecondaryDefault,     // #52C7FF
    onSecondary            = OnSecondary,          // #080808
    secondaryContainer     = SecondarySubtle,      // #0F3752
    onSecondaryContainer   = Sky100,               // #DAF5FF

    // Tertiary (Amber)
    tertiary               = AccentDefault,        // #D2B35E
    onTertiary             = OnAccent,             // #080808
    tertiaryContainer      = AccentSubtle,         // #3E3115
    onTertiaryContainer    = Amber100,             // #F6F2DE

    // Error
    error                  = StatusError,          // #F87171
    onError                = Void950,              // #080808
    errorContainer         = StatusErrorDim,       // #7F1D1D
    onErrorContainer       = Color(0xFFFFDAD6),

    // Background & Surface
    background             = SurfaceBase,          // #080808
    onBackground           = TextPrimary,          // #DCDCE6
    surface                = SurfaceBase,          // #080808
    onSurface              = TextPrimary,          // #DCDCE6
    surfaceVariant         = SurfaceRaised,        // #0D0D0F
    onSurfaceVariant       = TextSecondary,        // #8E8E9E

    // Surface containers (Material3 tonal elevation)
    surfaceContainerLowest  = Void950,             // #080808
    surfaceContainerLow     = Void900,             // #0D0D0F
    surfaceContainer        = Void850,             // #111114
    surfaceContainerHigh    = Void800,             // #16161A
    surfaceContainerHighest = Void750,             // #1C1C22

    // Outline
    outline                = BorderDefault,        // #22222A
    outlineVariant         = BorderSubtle,         // #16161A

    // Inverse
    inverseSurface         = Void50,               // #DCDCE6
    inverseOnSurface       = Void950,              // #080808
    inversePrimary         = Violet700,            // #5A4CB3

    // Scrim
    scrim                  = Color(0xFF080808),

    // Surface tint
    surfaceTint            = PrimaryDefault,       // #8C7BFF
)


// ─────────────────────────────────────────────────────────────────────────────
// §2  Extended Color System (beyond Material3)
// ─────────────────────────────────────────────────────────────────────────────

@Immutable
data class HermeticExtendedColors(
    // Glow colors (for box-shadow equivalents in Compose)
    val glowViolet: Color,
    val glowSky: Color,
    val glowAmber: Color,

    // Status
    val success: Color,
    val successDim: Color,
    val warning: Color,
    val warningDim: Color,
    val info: Color,
    val infoDim: Color,

    // Surface extensions
    val surfaceElevated: Color,
    val surfaceOverlay: Color,
    val surfaceScrim: Color,

    // Text extensions
    val textMuted: Color,
    val textDisabled: Color,
    val textLink: Color,
    val textLinkHover: Color,

    // Border extensions
    val borderStrong: Color,
    val borderFocus: Color,

    // Interactive states
    val hoverOverlay: Color,
    val pressedOverlay: Color,
    val focusRing: Color,
    val selectedBg: Color,

    // Accent (Amber) — since Material3 maps it to tertiary
    val accent: Color,
    val accentHover: Color,
    val accentPressed: Color,
    val accentDisabled: Color,
    val accentSubtle: Color,
    val onAccent: Color,
)

val HermeticDarkExtendedColors = HermeticExtendedColors(
    glowViolet      = Violet500,
    glowSky         = Sky500,
    glowAmber       = Amber500,

    success         = StatusSuccess,
    successDim      = StatusSuccessDim,
    warning         = StatusWarning,
    warningDim      = StatusWarningDim,
    info            = StatusInfo,
    infoDim         = StatusInfoDim,

    surfaceElevated = SurfaceElevated,
    surfaceOverlay  = SurfaceOverlay,
    surfaceScrim    = Scrim,

    textMuted       = TextMuted,
    textDisabled    = TextDisabled,
    textLink        = TextLink,
    textLinkHover   = TextLinkHover,

    borderStrong    = BorderStrong,
    borderFocus     = BorderFocus,

    hoverOverlay    = HoverOverlay,
    pressedOverlay  = PressedOverlay,
    focusRing       = FocusRing,
    selectedBg      = SelectedBg,

    accent          = AccentDefault,
    accentHover     = AccentHover,
    accentPressed   = AccentPressed,
    accentDisabled  = AccentDisabled,
    accentSubtle    = AccentSubtle,
    onAccent        = OnAccent,
)

val LocalHermeticExtendedColors = staticCompositionLocalOf {
    HermeticDarkExtendedColors
}


// ─────────────────────────────────────────────────────────────────────────────
// §3  Typography
// ─────────────────────────────────────────────────────────────────────────────

// Font families — replace R.font references with your actual font resources
val JetBrainsMonoFamily = FontFamily(
    Font(/* R.font.jetbrains_mono_regular, */ weight = FontWeight.Normal),
    Font(/* R.font.jetbrains_mono_medium,  */ weight = FontWeight.Medium),
    Font(/* R.font.jetbrains_mono_semibold,*/ weight = FontWeight.SemiBold),
    Font(/* R.font.jetbrains_mono_bold,    */ weight = FontWeight.Bold),
)

val InterFamily = FontFamily(
    Font(/* R.font.inter_regular,  */ weight = FontWeight.Normal),
    Font(/* R.font.inter_medium,   */ weight = FontWeight.Medium),
    Font(/* R.font.inter_semibold, */ weight = FontWeight.SemiBold),
    Font(/* R.font.inter_bold,     */ weight = FontWeight.Bold),
)

val HermeticTypography = Typography(
    // Display
    displayLarge = TextStyle(
        fontFamily = JetBrainsMonoFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 48.sp,
        lineHeight = 56.sp,
        letterSpacing = (-0.035).sp,
        color = Color.Unspecified,
    ),
    displayMedium = TextStyle(
        fontFamily = JetBrainsMonoFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 36.sp,
        lineHeight = 44.sp,
        letterSpacing = (-0.03).sp,
    ),
    displaySmall = TextStyle(
        fontFamily = JetBrainsMonoFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        lineHeight = 36.sp,
        letterSpacing = (-0.025).sp,
    ),

    // Headline
    headlineLarge = TextStyle(
        fontFamily = JetBrainsMonoFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp,
        lineHeight = 36.sp,
        letterSpacing = (-0.025).sp,
    ),
    headlineMedium = TextStyle(
        fontFamily = JetBrainsMonoFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp,
        lineHeight = 32.sp,
        letterSpacing = (-0.02).sp,
    ),
    headlineSmall = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 18.sp,
        lineHeight = 28.sp,
        letterSpacing = (-0.015).sp,
    ),

    // Title
    titleLarge = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 18.sp,
        lineHeight = 28.sp,
        letterSpacing = (-0.015).sp,
    ),
    titleMedium = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = (-0.01).sp,
    ),
    titleSmall = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.sp,
    ),

    // Body
    bodyLarge = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = (-0.01).sp,
    ),
    bodyMedium = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.sp,
    ),
    bodySmall = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 18.sp,
        letterSpacing = 0.01.sp,
    ),

    // Label
    labelLarge = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 14.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.sp,
    ),
    labelMedium = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 18.sp,
        letterSpacing = 0.01.sp,
    ),
    labelSmall = TextStyle(
        fontFamily = JetBrainsMonoFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 10.sp,
        lineHeight = 14.sp,
        letterSpacing = 0.1.sp,
    ),
)


// ─────────────────────────────────────────────────────────────────────────────
// §4  Spacing & Dimensions
// ─────────────────────────────────────────────────────────────────────────────

object HermeticSpacing {
    val None     = 0.dp
    val Xxs      = 2.dp
    val Xs       = 4.dp
    val Sm       = 6.dp
    val Md       = 8.dp
    val MdPlus   = 10.dp
    val Base     = 12.dp
    val Lg       = 16.dp
    val Xl       = 20.dp
    val Xxl      = 24.dp
    val Section  = 24.dp
    val Huge     = 32.dp
    val Mega     = 40.dp
    val Giga     = 48.dp
    val Ultra    = 64.dp
    val Page     = 80.dp
}

object HermeticRadius {
    val None  = 0.dp
    val Xs    = 2.dp
    val Sm    = 4.dp
    val Md    = 8.dp
    val Lg    = 12.dp
    val Xl    = 16.dp
    val Xxl   = 24.dp
    val Full  = 999.dp

    // Semantic
    val Button  = Md
    val Card    = Lg
    val Panel   = Lg
    val Input   = Md
    val Badge   = Full
    val Tooltip = Md
    val Modal   = Xl
    val Key     = Md
}

object HermeticElevation {
    val Level0 = 0.dp
    val Level1 = 1.dp
    val Level2 = 3.dp
    val Level3 = 6.dp
    val Level4 = 8.dp
    val Level5 = 12.dp
}


// ─────────────────────────────────────────────────────────────────────────────
// §5  Theme Composable
// ─────────────────────────────────────────────────────────────────────────────

@Composable
fun HermeticTheme(
    content: @Composable () -> Unit
) {
    val colorScheme = HermeticDarkColorScheme
    val extendedColors = HermeticDarkExtendedColors

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.surface.toArgb()
            window.navigationBarColor = colorScheme.surface.toArgb()
            WindowCompat.getInsetsController(window, view).apply {
                isAppearanceLightStatusBars = false
                isAppearanceLightNavigationBars = false
            }
        }
    }

    CompositionLocalProvider(
        LocalHermeticExtendedColors provides extendedColors,
    ) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = HermeticTypography,
            content = content,
        )
    }
}

// Convenience accessor
object HermeticTheme {
    val extendedColors: HermeticExtendedColors
        @Composable
        get() = LocalHermeticExtendedColors.current
}
