// ═══════════════════════════════════════════════════════════════════════════════
// HERMETIC OS — Dashboard Components for Android Compose
// ═══════════════════════════════════════════════════════════════════════════════
// Example implementation: glowing elevated metric card, status badge,
// panel container, and sparkline chart.
//
// Package: com.hermetic.designsystem.components
// ═══════════════════════════════════════════════════════════════════════════════

package com.hermetic.designsystem.components

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.hermetic.designsystem.theme.*


// ─────────────────────────────────────────────────────────────────────────────
// §1  Glowing Metric Card
// ─────────────────────────────────────────────────────────────────────────────

enum class GlowColor {
    VIOLET, SKY, AMBER
}

enum class DeltaDirection {
    UP, DOWN, NEUTRAL
}

/**
 * A dashboard metric card with animated glow border.
 *
 * Usage:
 * ```
 * GlowingMetricCard(
 *     label = "ACTIVE SESSIONS",
 *     value = "2,847",
 *     delta = "+12.4%",
 *     deltaDirection = DeltaDirection.UP,
 *     glowColor = GlowColor.VIOLET,
 * )
 * ```
 */
@Composable
fun GlowingMetricCard(
    label: String,
    value: String,
    delta: String? = null,
    deltaDirection: DeltaDirection = DeltaDirection.NEUTRAL,
    glowColor: GlowColor = GlowColor.VIOLET,
    modifier: Modifier = Modifier,
) {
    val extended = HermeticTheme.extendedColors

    // Glow color resolution
    val glowBaseColor = when (glowColor) {
        GlowColor.VIOLET -> extended.glowViolet
        GlowColor.SKY    -> extended.glowSky
        GlowColor.AMBER  -> extended.glowAmber
    }

    // Animated glow pulse
    val infiniteTransition = rememberInfiniteTransition(label = "glow")
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.15f,
        targetValue = 0.35f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "glowAlpha",
    )

    val glowAnimatedColor = glowBaseColor.copy(alpha = glowAlpha)

    // Gradient fade overlay per glow color
    val gradientBrush = Brush.linearGradient(
        colors = listOf(
            glowBaseColor.copy(alpha = 0.08f),
            Color.Transparent,
        ),
    )

    Box(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(HermeticRadius.Card))
            .background(SurfaceRaised)
            .border(
                width = 1.dp,
                color = glowAnimatedColor,
                shape = RoundedCornerShape(HermeticRadius.Card),
            )
            .drawBehind {
                // Outer glow effect
                drawRect(
                    color = glowBaseColor.copy(alpha = glowAlpha * 0.4f),
                    size = size,
                )
            }
    ) {
        // Gradient overlay
        Box(
            modifier = Modifier
                .matchParentSize()
                .background(gradientBrush)
        )

        Column(
            modifier = Modifier
                .padding(HermeticSpacing.Lg)
                .fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(HermeticSpacing.Xs),
        ) {
            // Overline label
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
                letterSpacing = 0.1.sp,
            )

            Spacer(modifier = Modifier.height(HermeticSpacing.Xs))

            // Main value
            Text(
                text = value,
                style = MaterialTheme.typography.displaySmall.copy(
                    fontSize = 28.sp,
                    lineHeight = 36.sp,
                ),
                color = TextPrimary,
                fontWeight = FontWeight.Bold,
            )

            // Delta indicator
            if (delta != null) {
                Spacer(modifier = Modifier.height(HermeticSpacing.Xxs))

                val deltaColor = when (deltaDirection) {
                    DeltaDirection.UP      -> extended.success
                    DeltaDirection.DOWN    -> StatusError
                    DeltaDirection.NEUTRAL -> TextMuted
                }

                val deltaPrefix = when (deltaDirection) {
                    DeltaDirection.UP   -> "↑ "   // ↑
                    DeltaDirection.DOWN -> "↓ "   // ↓
                    DeltaDirection.NEUTRAL -> ""
                }

                Text(
                    text = "$deltaPrefix$delta",
                    style = MaterialTheme.typography.bodySmall,
                    color = deltaColor,
                    fontWeight = FontWeight.Medium,
                )
            }
        }
    }
}


// ─────────────────────────────────────────────────────────────────────────────
// §2  Status Badge
// ─────────────────────────────────────────────────────────────────────────────

enum class BadgeVariant {
    SUCCESS, ERROR, WARNING, INFO, PRIMARY
}

@Composable
fun StatusBadge(
    text: String,
    variant: BadgeVariant = BadgeVariant.PRIMARY,
    modifier: Modifier = Modifier,
) {
    val extended = HermeticTheme.extendedColors

    val (bgColor, fgColor) = when (variant) {
        BadgeVariant.SUCCESS -> extended.successDim to extended.success
        BadgeVariant.ERROR   -> StatusErrorDim to StatusError
        BadgeVariant.WARNING -> extended.warningDim to extended.warning
        BadgeVariant.INFO    -> extended.infoDim to extended.info
        BadgeVariant.PRIMARY -> PrimarySubtle to PrimaryDefault
    }

    Box(
        modifier = modifier
            .height(20.dp)
            .clip(RoundedCornerShape(HermeticRadius.Badge))
            .background(bgColor)
            .padding(horizontal = HermeticSpacing.Md),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = text.uppercase(),
            style = MaterialTheme.typography.labelSmall.copy(
                fontSize = 10.sp,
                letterSpacing = 0.04.sp,
            ),
            color = fgColor,
            fontWeight = FontWeight.Bold,
        )
    }
}


// ─────────────────────────────────────────────────────────────────────────────
// §3  Panel Container
// ─────────────────────────────────────────────────────────────────────────────

enum class PanelAccent {
    NONE, VIOLET, SKY, AMBER
}

@Composable
fun HermeticPanel(
    title: String,
    accent: PanelAccent = PanelAccent.NONE,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    val accentColor = when (accent) {
        PanelAccent.NONE   -> null
        PanelAccent.VIOLET -> Violet500
        PanelAccent.SKY    -> Sky500
        PanelAccent.AMBER  -> Amber500
    }

    val borderModifier = if (accentColor != null) {
        Modifier.drawBehind {
            drawLine(
                color = accentColor,
                start = Offset(0f, 0f),
                end = Offset(0f, size.height),
                strokeWidth = 3.dp.toPx(),
                cap = StrokeCap.Round,
            )
        }
    } else {
        Modifier
    }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(HermeticRadius.Panel))
            .background(SurfaceRaised)
            .border(
                width = 1.dp,
                color = BorderDefault,
                shape = RoundedCornerShape(HermeticRadius.Panel),
            )
            .then(borderModifier)
            .padding(HermeticSpacing.Lg),
    ) {
        // Panel header
        Text(
            text = title.uppercase(),
            style = MaterialTheme.typography.labelSmall,
            color = TextSecondary,
            letterSpacing = 0.04.sp,
            fontWeight = FontWeight.SemiBold,
        )

        Spacer(modifier = Modifier.height(HermeticSpacing.Base))

        // Divider
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(1.dp)
                .background(BorderSubtle)
        )

        Spacer(modifier = Modifier.height(HermeticSpacing.Base))

        content()
    }
}


// ─────────────────────────────────────────────────────────────────────────────
// §4  Sparkline Chart
// ─────────────────────────────────────────────────────────────────────────────

@Composable
fun Sparkline(
    data: List<Float>,
    color: Color = Violet600,
    height: Dp = 40.dp,
    modifier: Modifier = Modifier,
) {
    if (data.isEmpty()) return

    val maxVal = data.max()
    val minVal = data.min()
    val range = (maxVal - minVal).coerceAtLeast(0.01f)

    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(height)
    ) {
        val stepX = size.width / (data.size - 1).coerceAtLeast(1)
        val path = Path()

        data.forEachIndexed { index, value ->
            val x = index * stepX
            val y = size.height - ((value - minVal) / range) * size.height

            if (index == 0) {
                path.moveTo(x, y)
            } else {
                path.lineTo(x, y)
            }
        }

        drawPath(
            path = path,
            color = color,
            style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round),
        )
    }
}


// ─────────────────────────────────────────────────────────────────────────────
// §5  Glow Dot Indicator
// ─────────────────────────────────────────────────────────────────────────────

@Composable
fun GlowDot(
    color: Color = StatusSuccess,
    size: Dp = 8.dp,
    modifier: Modifier = Modifier,
) {
    val infiniteTransition = rememberInfiniteTransition(label = "dot")
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.4f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "dotAlpha",
    )

    Box(
        modifier = modifier
            .size(size)
            .clip(CircleShape)
            .background(color.copy(alpha = alpha))
            .drawBehind {
                drawCircle(
                    color = color.copy(alpha = alpha * 0.3f),
                    radius = this.size.minDimension,
                )
            }
    )
}


// ─────────────────────────────────────────────────────────────────────────────
// §6  Example Dashboard Row
// ─────────────────────────────────────────────────────────────────────────────

@Composable
fun ExampleDashboardRow() {
    Column(
        verticalArrangement = Arrangement.spacedBy(HermeticSpacing.Lg),
        modifier = Modifier.padding(HermeticSpacing.Lg),
    ) {
        // Top metric row
        Row(
            horizontalArrangement = Arrangement.spacedBy(HermeticSpacing.Lg),
            modifier = Modifier.fillMaxWidth(),
        ) {
            GlowingMetricCard(
                label = "ACTIVE SESSIONS",
                value = "2,847",
                delta = "+12.4%",
                deltaDirection = DeltaDirection.UP,
                glowColor = GlowColor.VIOLET,
                modifier = Modifier.weight(1f),
            )
            GlowingMetricCard(
                label = "THROUGHPUT",
                value = "1.2K/s",
                delta = "-3.1%",
                deltaDirection = DeltaDirection.DOWN,
                glowColor = GlowColor.SKY,
                modifier = Modifier.weight(1f),
            )
            GlowingMetricCard(
                label = "ACCURACY",
                value = "99.7%",
                delta = "stable",
                deltaDirection = DeltaDirection.NEUTRAL,
                glowColor = GlowColor.AMBER,
                modifier = Modifier.weight(1f),
            )
        }

        // Panel with sparkline
        HermeticPanel(
            title = "Request Volume (24h)",
            accent = PanelAccent.VIOLET,
        ) {
            Sparkline(
                data = listOf(
                    12f, 19f, 15f, 22f, 28f, 25f, 31f, 35f, 29f, 38f,
                    42f, 36f, 45f, 48f, 44f, 52f, 55f, 49f, 58f, 62f,
                    56f, 65f, 68f, 71f,
                ),
                color = Violet500,
                height = 60.dp,
            )
        }

        // Status row
        Row(
            horizontalArrangement = Arrangement.spacedBy(HermeticSpacing.Md),
        ) {
            StatusBadge(text = "Online", variant = BadgeVariant.SUCCESS)
            StatusBadge(text = "3 Alerts", variant = BadgeVariant.WARNING)
            StatusBadge(text = "Synced", variant = BadgeVariant.INFO)
        }
    }
}
