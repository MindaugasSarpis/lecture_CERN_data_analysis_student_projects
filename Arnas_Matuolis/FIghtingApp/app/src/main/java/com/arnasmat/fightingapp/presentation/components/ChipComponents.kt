package com.arnasmat.fightingapp.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import com.arnasmat.fightingapp.ui.theme.*

/**
 * DESIGN SYSTEM - CHIP COMPONENTS
 * Chip/tag components for selections, filters, and badges
 */

@Composable
fun FightChip(
    text: String,
    modifier: Modifier = Modifier,
    selected: Boolean = false,
    onClick: (() -> Unit)? = null,
    leadingIcon: ImageVector? = null,
    backgroundColor: Color = FightDarkElevated,
    selectedBackgroundColor: Color = FightRed,
    textColor: Color = TextPrimary,
    selectedTextColor: Color = TextPrimary,
    borderColor: Color? = null
) {
    val interactionSource = remember { MutableInteractionSource() }
    val finalBackgroundColor = if (selected) selectedBackgroundColor else backgroundColor
    val finalTextColor = if (selected) selectedTextColor else textColor

    Surface(
        modifier = modifier
            .then(
                borderColor?.let {
                    Modifier.border(
                        width = Dimensions.borderThin,
                        color = it,
                        shape = FightingShapes.pill
                    )
                } ?: Modifier
            ),
        onClick = onClick ?: {},
        enabled = onClick != null,
        shape = FightingShapes.pill,
        color = finalBackgroundColor,
        interactionSource = interactionSource
    ) {
        Row(
            modifier = Modifier.padding(
                horizontal = Spacing.small,
                vertical = Spacing.extraSmall
            ),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            leadingIcon?.let {
                Icon(
                    imageVector = it,
                    contentDescription = null,
                    tint = finalTextColor,
                    modifier = Modifier.size(Dimensions.iconSizeSmall)
                )
                Spacer(modifier = Modifier.width(Spacing.extraSmall))
            }

            Text(
                text = text,
                style = MaterialTheme.typography.labelMedium,
                color = finalTextColor,
                fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium
            )
        }
    }
}

@Composable
fun FightFilterChip(
    text: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    leadingIcon: ImageVector? = null
) {
    FightChip(
        text = text,
        modifier = modifier,
        selected = selected,
        onClick = onClick,
        leadingIcon = leadingIcon,
        backgroundColor = FightDarkElevated,
        selectedBackgroundColor = FightRed,
        textColor = TextSecondary,
        selectedTextColor = TextPrimary,
        borderColor = if (selected) null else BorderMedium
    )
}

@Composable
fun FightDifficultyChip(
    difficulty: String,
    color: Color,
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null
) {
    FightChip(
        text = difficulty.uppercase(),
        modifier = modifier,
        onClick = onClick,
        backgroundColor = color, // Full solid background color
        selectedBackgroundColor = color,
        textColor = TextPrimary, // White text for contrast
        selectedTextColor = TextPrimary,
        borderColor = null // No border - just solid background
    )
}

