package com.arnasmat.fightingapp.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

/**
 * DESIGN SYSTEM - THEME
 * Modern, edgy dark theme optimized for fighting app
 */

private val FightingDarkColorScheme = darkColorScheme(
    // Primary - Main action color (Electric Blue)
    primary = FightPrimary,
    onPrimary = FightDarkBg,
    primaryContainer = FightPrimaryDark,
    onPrimaryContainer = TextPrimary,

    // Secondary - Accent color (Orange)
    secondary = FightOrange,
    onSecondary = FightDarkBg,
    secondaryContainer = FightOrangeDark,
    onSecondaryContainer = TextPrimary,

    // Tertiary - Secondary accent (Neon Purple)
    tertiary = NeonPurple,
    onTertiary = TextPrimary,
    tertiaryContainer = NeonPurpleDark,
    onTertiaryContainer = TextPrimary,

    // Background & Surface
    background = FightDarkBg,
    onBackground = TextPrimary,
    surface = FightDarkSurface,
    onSurface = TextPrimary,
    surfaceVariant = FightDarkCard,
    onSurfaceVariant = TextSecondary,
    surfaceTint = FightPrimary,

    // Inverse
    inverseSurface = TextPrimary,
    inverseOnSurface = FightDarkBg,
    inversePrimary = FightPrimaryDark,

    // Error
    error = ErrorRed,
    onError = TextPrimary,
    errorContainer = FightDarkElevated,
    onErrorContainer = ErrorRed,

    // Outline & Borders
    outline = BorderMedium,
    outlineVariant = BorderLight,

    // Scrim
    scrim = OverlayBlack
)

private val FightingLightColorScheme = lightColorScheme(
    // Even in light theme, we maintain dark elements for consistency
    primary = FightPrimary,
    onPrimary = FightDarkBg,
    primaryContainer = FightPrimaryDark,
    onPrimaryContainer = TextPrimary,

    secondary = FightOrange,
    onSecondary = FightDarkBg,
    secondaryContainer = FightOrangeDark,
    onSecondaryContainer = TextPrimary,

    tertiary = NeonPurpleDark,
    onTertiary = TextPrimary,
    tertiaryContainer = NeonPurple,
    onTertiaryContainer = FightDarkBg,

    // Background & Surface - Keep it dark even in light mode
    background = FightDarkBg,
    onBackground = TextPrimary,
    surface = FightDarkSurface,
    onSurface = TextPrimary,
    surfaceVariant = FightDarkCard,
    onSurfaceVariant = TextSecondary,

    error = ErrorRed,
    onError = TextPrimary,

    outline = BorderMedium,
    outlineVariant = BorderLight
)

// Legacy schemes for compatibility
private val DarkColorScheme = darkColorScheme(
    primary = Purple80,
    secondary = PurpleGrey80,
    tertiary = Pink80
)

private val LightColorScheme = lightColorScheme(
    primary = Purple40,
    secondary = PurpleGrey40,
    tertiary = Pink40
)

@Composable
fun FIghtingAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color disabled by default for consistent branding
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> FightingDarkColorScheme
        else -> FightingLightColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = Shapes,
        content = content
    )
}