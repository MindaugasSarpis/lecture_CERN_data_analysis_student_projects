package com.arnasmat.fightingapp.presentation.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
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
 * DESIGN SYSTEM - BUTTON COMPONENTS
 * Modern, edgy button styles for the fighting app
 */

// ============================================================
// PRIMARY BUTTONS
// ============================================================

@Composable
fun FightPrimaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    icon: ImageVector? = null,
    isLoading: Boolean = false
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1f,
        animationSpec = tween(100),
        label = "button_scale"
    )

    Button(
        onClick = onClick,
        modifier = modifier
            .heightIn(min = Dimensions.buttonHeightMedium)
            .scale(scale),
        enabled = enabled && !isLoading,
        colors = ButtonDefaults.buttonColors(
            containerColor = FightPrimary,
            contentColor = FightDarkBg,
            disabledContainerColor = FightDarkElevated,
            disabledContentColor = TextDisabled
        ),
        shape = FightingShapes.medium,
        elevation = ButtonDefaults.buttonElevation(
            defaultElevation = Elevation.small,
            pressedElevation = Elevation.none,
            disabledElevation = Elevation.none
        ),
        interactionSource = interactionSource,
        contentPadding = PaddingValues(
            horizontal = Spacing.large,
            vertical = Spacing.medium
        )
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(Dimensions.iconSizeMedium),
                color = TextPrimary,
                strokeWidth = 2.dp
            )
        } else {
            Row(
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth()
            ) {
                icon?.let {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        modifier = Modifier.size(Dimensions.iconSizeMedium)
                    )
                    Spacer(modifier = Modifier.width(Spacing.small))
                }
                Text(
                    text = text,
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
fun FightSecondaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    icon: ImageVector? = null,
    isLoading: Boolean = false
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1f,
        animationSpec = tween(100),
        label = "button_scale"
    )

    Button(
        onClick = onClick,
        modifier = modifier
            .heightIn(min = Dimensions.buttonHeightMedium)
            .scale(scale),
        enabled = enabled && !isLoading,
        colors = ButtonDefaults.buttonColors(
            containerColor = ElectricBlue,
            contentColor = FightDarkBg,
            disabledContainerColor = FightDarkElevated,
            disabledContentColor = TextDisabled
        ),
        shape = FightingShapes.medium,
        elevation = ButtonDefaults.buttonElevation(
            defaultElevation = Elevation.small,
            pressedElevation = Elevation.none
        ),
        interactionSource = interactionSource,
        contentPadding = PaddingValues(
            horizontal = Spacing.large,
            vertical = Spacing.medium
        )
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(Dimensions.iconSizeMedium),
                color = FightDarkBg,
                strokeWidth = 2.dp
            )
        } else {
            Row(
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth()
            ) {
                icon?.let {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        modifier = Modifier.size(Dimensions.iconSizeMedium)
                    )
                    Spacer(modifier = Modifier.width(Spacing.small))
                }
                Text(
                    text = text,
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

// ============================================================
// RECORD BUTTON - Red for recording actions
// ============================================================

@Composable
fun FightRecordButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    icon: ImageVector? = null,
    isLoading: Boolean = false
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1f,
        animationSpec = tween(100),
        label = "button_scale"
    )

    Button(
        onClick = onClick,
        modifier = modifier
            .heightIn(min = Dimensions.buttonHeightMedium)
            .scale(scale),
        enabled = enabled && !isLoading,
        colors = ButtonDefaults.buttonColors(
            containerColor = FightRed,
            contentColor = TextPrimary,
            disabledContainerColor = FightDarkElevated,
            disabledContentColor = TextDisabled
        ),
        shape = FightingShapes.medium,
        elevation = ButtonDefaults.buttonElevation(
            defaultElevation = Elevation.small,
            pressedElevation = Elevation.none,
            disabledElevation = Elevation.none
        ),
        interactionSource = interactionSource,
        contentPadding = PaddingValues(
            horizontal = Spacing.large,
            vertical = Spacing.medium
        )
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(Dimensions.iconSizeMedium),
                color = TextPrimary,
                strokeWidth = 2.dp
            )
        } else {
            Row(
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth()
            ) {
                icon?.let {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        modifier = Modifier.size(Dimensions.iconSizeMedium)
                    )
                    Spacer(modifier = Modifier.width(Spacing.small))
                }
                Text(
                    text = text,
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

// ============================================================
// OUTLINED BUTTONS
// ============================================================

@Composable
fun FightOutlinedButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    icon: ImageVector? = null,
    borderColor: Color = FightPrimary
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1f,
        animationSpec = tween(100),
        label = "button_scale"
    )

    OutlinedButton(
        onClick = onClick,
        modifier = modifier
            .heightIn(min = Dimensions.buttonHeightMedium)
            .scale(scale),
        enabled = enabled,
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = Color.Transparent,
            contentColor = borderColor,
            disabledContainerColor = Color.Transparent,
            disabledContentColor = TextDisabled
        ),
        border = BorderStroke(
            width = Dimensions.borderMedium,
            color = if (enabled) borderColor else BorderLight
        ),
        shape = FightingShapes.medium,
        interactionSource = interactionSource,
        contentPadding = PaddingValues(
            horizontal = Spacing.large,
            vertical = Spacing.medium
        )
    ) {
        Row(
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            icon?.let {
                Icon(
                    imageVector = it,
                    contentDescription = null,
                    modifier = Modifier.size(Dimensions.iconSizeMedium)
                )
                Spacer(modifier = Modifier.width(Spacing.small))
            }
            Text(
                text = text,
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

// ============================================================
// TEXT BUTTONS
// ============================================================

@Composable
fun FightTextButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    icon: ImageVector? = null,
    color: Color = FightRed
) {
    TextButton(
        onClick = onClick,
        modifier = modifier,
        enabled = enabled,
        colors = ButtonDefaults.textButtonColors(
            contentColor = color,
            disabledContentColor = TextDisabled
        )
    ) {
        Row(
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            icon?.let {
                Icon(
                    imageVector = it,
                    contentDescription = null,
                    modifier = Modifier.size(Dimensions.iconSizeMedium)
                )
                Spacer(modifier = Modifier.width(Spacing.small))
            }
            Text(
                text = text,
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

// ============================================================
// ICON BUTTONS
// ============================================================

@Composable
fun FightIconButton(
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    contentDescription: String? = null,
    backgroundColor: Color = FightDarkElevated,
    iconTint: Color = TextPrimary,
    size: Dp = 48.dp
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.9f else 1f,
        animationSpec = tween(100),
        label = "icon_scale"
    )

    FilledIconButton(
        onClick = onClick,
        modifier = modifier
            .size(size)
            .scale(scale),
        enabled = enabled,
        colors = IconButtonDefaults.filledIconButtonColors(
            containerColor = backgroundColor,
            contentColor = iconTint,
            disabledContainerColor = FightDarkSurface,
            disabledContentColor = TextDisabled
        ),
        interactionSource = interactionSource
    ) {
        Icon(
            imageVector = icon,
            contentDescription = contentDescription,
            modifier = Modifier.size(Dimensions.iconSizeMedium)
        )
    }
}

@Composable
fun FightCircleIconButton(
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    contentDescription: String? = null,
    backgroundColor: Color = FightRed,
    iconTint: Color = TextPrimary,
    size: Dp = 56.dp
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.9f else 1f,
        animationSpec = tween(100),
        label = "icon_scale"
    )

    FilledIconButton(
        onClick = onClick,
        modifier = modifier
            .size(size)
            .scale(scale),
        enabled = enabled,
        colors = IconButtonDefaults.filledIconButtonColors(
            containerColor = backgroundColor,
            contentColor = iconTint,
            disabledContainerColor = FightDarkSurface,
            disabledContentColor = TextDisabled
        ),
        shape = CircleShape,
        interactionSource = interactionSource
    ) {
        Icon(
            imageVector = icon,
            contentDescription = contentDescription,
            modifier = Modifier.size(size * 0.5f)
        )
    }
}

// ============================================================
// SMALL BUTTONS
// ============================================================

@Composable
fun FightSmallButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    containerColor: Color = FightRed,
    contentColor: Color = TextPrimary
) {
    Button(
        onClick = onClick,
        modifier = modifier.height(Dimensions.buttonHeightSmall),
        enabled = enabled,
        colors = ButtonDefaults.buttonColors(
            containerColor = containerColor,
            contentColor = contentColor,
            disabledContainerColor = FightDarkElevated,
            disabledContentColor = TextDisabled
        ),
        shape = FightingShapes.small,
        contentPadding = PaddingValues(
            horizontal = Spacing.medium,
            vertical = Spacing.extraSmall
        )
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Bold
        )
    }
}
