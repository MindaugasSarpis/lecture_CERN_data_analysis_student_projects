package com.arnasmat.fightingapp.presentation.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.arnasmat.fightingapp.ui.theme.*

/**
 * DESIGN SYSTEM - CARD COMPONENTS
 * Modern, edgy card styles for the fighting app
 */

// ============================================================
// STANDARD CARDS
// ============================================================

@Composable
fun FightCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    enabled: Boolean = true,
    backgroundColor: Color = FightDarkCard,
    borderColor: Color? = null,
    elevation: Dp = Elevation.small,
    content: @Composable ColumnScope.() -> Unit
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed && onClick != null) 0.98f else 1f,
        animationSpec = tween(100),
        label = "card_scale"
    )

    Card(
        modifier = modifier
            .scale(scale)
            .then(
                if (onClick != null) {
                    Modifier.clickable(
                        enabled = enabled,
                        interactionSource = interactionSource,
                        indication = null,
                        onClick = onClick
                    )
                } else Modifier
            )
            .then(
                borderColor?.let {
                    Modifier.border(
                        width = Dimensions.borderMedium,
                        color = it,
                        shape = FightingShapes.medium
                    )
                } ?: Modifier
            ),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor,
            contentColor = TextPrimary
        ),
        shape = FightingShapes.medium,
        elevation = CardDefaults.cardElevation(defaultElevation = elevation)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.medium),
            content = content
        )
    }
}

@Composable
fun FightInfoCard(
    title: String,
    description: String,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
    backgroundColor: Color = FightDarkCard,
    accentColor: Color = FightRed
) {
    FightCard(
        modifier = modifier,
        backgroundColor = backgroundColor,
        borderColor = accentColor.copy(alpha = 0.3f)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            icon?.let {
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .background(
                            color = accentColor.copy(alpha = 0.2f),
                            shape = FightingShapes.medium
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        tint = accentColor,
                        modifier = Modifier.size(Dimensions.iconSizeMedium)
                    )
                }
                Spacer(modifier = Modifier.width(Spacing.medium))
            }

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                Spacer(modifier = Modifier.height(Spacing.extraSmall))
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
            }
        }
    }
}

// ============================================================
// GRADIENT CARDS
// ============================================================

@Composable
fun FightGradientCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    gradientColors: List<Color> = listOf(
        FightRed.copy(alpha = 0.8f),
        FightOrange.copy(alpha = 0.6f)
    ),
    content: @Composable ColumnScope.() -> Unit
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed && onClick != null) 0.98f else 1f,
        animationSpec = tween(100),
        label = "card_scale"
    )

    Card(
        modifier = modifier
            .scale(scale)
            .then(
                if (onClick != null) {
                    Modifier.clickable(
                        interactionSource = interactionSource,
                        indication = null,
                        onClick = onClick
                    )
                } else Modifier
            ),
        shape = FightingShapes.medium,
        elevation = CardDefaults.cardElevation(defaultElevation = Elevation.medium)
    ) {
        Box(
            modifier = Modifier
                .background(
                    brush = Brush.linearGradient(colors = gradientColors)
                )
                .fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(Spacing.medium),
                content = content
            )
        }
    }
}

// ============================================================
// STATUS CARDS
// ============================================================

@Composable
fun FightSuccessCard(
    message: String,
    modifier: Modifier = Modifier,
    onDismiss: (() -> Unit)? = null
) {
    FightCard(
        modifier = modifier,
        backgroundColor = SuccessGreen.copy(alpha = 0.15f),
        borderColor = SuccessGreen
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = SuccessGreen,
                modifier = Modifier.weight(1f)
            )
            onDismiss?.let {
                FightTextButton(
                    text = "Dismiss",
                    onClick = it,
                    color = SuccessGreen
                )
            }
        }
    }
}

@Composable
fun FightErrorCard(
    message: String,
    modifier: Modifier = Modifier,
    onDismiss: (() -> Unit)? = null,
    onRetry: (() -> Unit)? = null
) {
    FightCard(
        modifier = modifier,
        backgroundColor = ErrorRed.copy(alpha = 0.15f),
        borderColor = ErrorRed
    ) {
        Column {
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = ErrorRed
            )

            if (onDismiss != null || onRetry != null) {
                Spacer(modifier = Modifier.height(Spacing.small))
                Row(
                    horizontalArrangement = Arrangement.End,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    onDismiss?.let {
                        FightTextButton(
                            text = "Dismiss",
                            onClick = it,
                            color = ErrorRed
                        )
                    }
                    onRetry?.let {
                        Spacer(modifier = Modifier.width(Spacing.small))
                        FightTextButton(
                            text = "Retry",
                            onClick = it,
                            color = ErrorRed
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun FightWarningCard(
    message: String,
    modifier: Modifier = Modifier,
    onDismiss: (() -> Unit)? = null
) {
    FightCard(
        modifier = modifier,
        backgroundColor = WarningYellow.copy(alpha = 0.15f),
        borderColor = WarningYellow
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = WarningYellow,
                modifier = Modifier.weight(1f)
            )
            onDismiss?.let {
                FightTextButton(
                    text = "Dismiss",
                    onClick = it,
                    color = WarningYellow
                )
            }
        }
    }
}

// ============================================================
// LIST ITEM CARDS
// ============================================================

@Composable
fun FightListItemCard(
    title: String,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    leadingIcon: ImageVector? = null,
    trailingContent: @Composable (() -> Unit)? = null,
    onClick: (() -> Unit)? = null,
    backgroundColor: Color = FightDarkCard
) {
    FightCard(
        modifier = modifier,
        onClick = onClick,
        backgroundColor = backgroundColor
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            leadingIcon?.let {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(
                            color = FightRed.copy(alpha = 0.2f),
                            shape = FightingShapes.small
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        tint = FightRed,
                        modifier = Modifier.size(Dimensions.iconSizeMedium)
                    )
                }
                Spacer(modifier = Modifier.width(Spacing.medium))
            }

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary
                )
                subtitle?.let {
                    Spacer(modifier = Modifier.height(Spacing.extraSmall))
                    Text(
                        text = it,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }
            }

            trailingContent?.let {
                Spacer(modifier = Modifier.width(Spacing.small))
                it()
            }
        }
    }
}

// ============================================================
// COMPACT CARDS
// ============================================================

@Composable
fun FightCompactCard(
    text: String,
    modifier: Modifier = Modifier,
    backgroundColor: Color = FightDarkElevated,
    textColor: Color = TextPrimary,
    borderColor: Color? = null
) {
    Surface(
        modifier = modifier
            .then(
                borderColor?.let {
                    Modifier.border(
                        width = Dimensions.borderThin,
                        color = it,
                        shape = FightingShapes.small
                    )
                } ?: Modifier
            ),
        color = backgroundColor,
        shape = FightingShapes.small
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            color = textColor,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(
                horizontal = Spacing.small,
                vertical = Spacing.extraSmall
            )
        )
    }
}

