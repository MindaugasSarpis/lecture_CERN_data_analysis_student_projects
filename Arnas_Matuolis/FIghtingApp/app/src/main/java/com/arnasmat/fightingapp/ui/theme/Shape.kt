package com.arnasmat.fightingapp.ui.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes
import androidx.compose.ui.unit.dp

/**
 * DESIGN SYSTEM - SHAPES
 * Consistent corner radius definitions for the fighting app
 * Using sharp corners and moderate rounding for an edgy, modern look
 */

val Shapes = Shapes(
    // Extra Small - Chips, tags
    extraSmall = RoundedCornerShape(4.dp),

    // Small - Buttons, small cards
    small = RoundedCornerShape(8.dp),

    // Medium - Standard cards, inputs
    medium = RoundedCornerShape(12.dp),

    // Large - Large cards, bottom sheets
    large = RoundedCornerShape(16.dp),

    // Extra Large - Modal dialogs, full screen overlays
    extraLarge = RoundedCornerShape(24.dp)
)

// Additional custom shapes for specific use cases
object FightingShapes {
    val sharp = RoundedCornerShape(0.dp)
    val subtle = RoundedCornerShape(4.dp)
    val small = RoundedCornerShape(8.dp)
    val medium = RoundedCornerShape(12.dp)
    val large = RoundedCornerShape(16.dp)
    val extraLarge = RoundedCornerShape(24.dp)
    val pill = RoundedCornerShape(50)

    // Asymmetric shapes for edgy design
    val topRounded = RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp)
    val bottomRounded = RoundedCornerShape(bottomStart = 16.dp, bottomEnd = 16.dp)
    val leftRounded = RoundedCornerShape(topStart = 16.dp, bottomStart = 16.dp)
    val rightRounded = RoundedCornerShape(topEnd = 16.dp, bottomEnd = 16.dp)
}

