package com.arnasmat.fightingapp.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import com.arnasmat.fightingapp.ui.theme.*

/**
 * DESIGN SYSTEM - INPUT COMPONENTS
 * Modern input fields for the fighting app
 */

// ============================================================
// TEXT FIELDS
// ============================================================

@Composable
fun FightTextField(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    label: String? = null,
    placeholder: String? = null,
    leadingIcon: ImageVector? = null,
    trailingIcon: @Composable (() -> Unit)? = null,
    isError: Boolean = false,
    errorMessage: String? = null,
    enabled: Boolean = true,
    singleLine: Boolean = true,
    maxLines: Int = 1,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default,
    keyboardActions: KeyboardActions = KeyboardActions.Default,
    visualTransformation: VisualTransformation = VisualTransformation.None
) {
    Column(modifier = modifier) {
        label?.let {
            Text(
                text = it,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.SemiBold,
                color = TextSecondary,
                modifier = Modifier.padding(bottom = Spacing.extraSmall)
            )
        }

        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier.fillMaxWidth(),
            placeholder = placeholder?.let {
                {
                    Text(
                        text = it,
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextTertiary
                    )
                }
            },
            leadingIcon = leadingIcon?.let {
                {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        tint = if (isError) ErrorRed else TextSecondary,
                        modifier = Modifier.size(Dimensions.iconSizeMedium)
                    )
                }
            },
            trailingIcon = trailingIcon,
            isError = isError,
            enabled = enabled,
            singleLine = singleLine,
            maxLines = maxLines,
            keyboardOptions = keyboardOptions,
            keyboardActions = keyboardActions,
            visualTransformation = visualTransformation,
            shape = FightingShapes.medium,
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = TextPrimary,
                unfocusedTextColor = TextPrimary,
                disabledTextColor = TextDisabled,
                errorTextColor = TextPrimary,
                focusedContainerColor = FightDarkElevated,
                unfocusedContainerColor = FightDarkElevated,
                disabledContainerColor = FightDarkSurface,
                errorContainerColor = FightDarkElevated,
                focusedBorderColor = FightRed,
                unfocusedBorderColor = BorderMedium,
                disabledBorderColor = BorderLight,
                errorBorderColor = ErrorRed,
                cursorColor = FightRed,
                errorCursorColor = ErrorRed
            ),
            textStyle = MaterialTheme.typography.bodyMedium
        )

        if (isError && errorMessage != null) {
            Spacer(modifier = Modifier.height(Spacing.extraSmall))
            Text(
                text = errorMessage,
                style = MaterialTheme.typography.bodySmall,
                color = ErrorRed,
                modifier = Modifier.padding(start = Spacing.medium)
            )
        }
    }
}

@Composable
fun FightSearchField(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    placeholder: String = "Search...",
    leadingIcon: ImageVector? = null,
    onClear: (() -> Unit)? = null
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier.fillMaxWidth(),
        placeholder = {
            Text(
                text = placeholder,
                style = MaterialTheme.typography.bodyMedium,
                color = TextTertiary
            )
        },
        leadingIcon = leadingIcon?.let {
            {
                Icon(
                    imageVector = it,
                    contentDescription = null,
                    tint = TextSecondary,
                    modifier = Modifier.size(Dimensions.iconSizeMedium)
                )
            }
        },
        trailingIcon = if (value.isNotEmpty() && onClear != null) {
            {
                IconButton(onClick = onClear) {
                    Icon(
                        imageVector = androidx.compose.material.icons.Icons.Default.Clear,
                        contentDescription = "Clear",
                        tint = TextSecondary,
                        modifier = Modifier.size(Dimensions.iconSizeMedium)
                    )
                }
            }
        } else null,
        singleLine = true,
        shape = FightingShapes.pill,
        colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = TextPrimary,
            unfocusedTextColor = TextPrimary,
            focusedContainerColor = FightDarkElevated,
            unfocusedContainerColor = FightDarkElevated,
            focusedBorderColor = BorderMedium,
            unfocusedBorderColor = BorderLight,
            cursorColor = FightRed
        ),
        textStyle = MaterialTheme.typography.bodyMedium
    )
}

// ============================================================
// SURFACE COMPONENTS
// ============================================================

@Composable
fun FightSurface(
    modifier: Modifier = Modifier,
    backgroundColor: Color = FightDarkSurface,
    borderColor: Color? = null,
    content: @Composable BoxScope.() -> Unit
) {
    Surface(
        modifier = modifier
            .then(
                borderColor?.let {
                    Modifier.border(
                        width = Dimensions.borderMedium,
                        color = it,
                        shape = FightingShapes.medium
                    )
                } ?: Modifier
            ),
        color = backgroundColor,
        shape = FightingShapes.medium
    ) {
        Box(
            modifier = Modifier.padding(Spacing.medium),
            content = content
        )
    }
}

@Composable
fun FightContainer(
    modifier: Modifier = Modifier,
    backgroundColor: Color = FightDarkBg,
    content: @Composable ColumnScope.() -> Unit
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .background(backgroundColor)
            .padding(Spacing.medium),
        content = content
    )
}

// ============================================================
// DIVIDERS
// ============================================================

@Composable
fun FightDivider(
    modifier: Modifier = Modifier,
    color: Color = DividerColor,
    thickness: androidx.compose.ui.unit.Dp = Dimensions.borderThin
) {
    HorizontalDivider(
        modifier = modifier,
        thickness = thickness,
        color = color
    )
}

@Composable
fun FightVerticalDivider(
    modifier: Modifier = Modifier,
    color: Color = DividerColor,
    thickness: androidx.compose.ui.unit.Dp = Dimensions.borderThin
) {
    VerticalDivider(
        modifier = modifier,
        thickness = thickness,
        color = color
    )
}

// ============================================================
// SPACERS
// ============================================================

@Composable
fun SmallSpacer() {
    Spacer(modifier = Modifier.height(Spacing.small))
}

@Composable
fun MediumSpacer() {
    Spacer(modifier = Modifier.height(Spacing.medium))
}

@Composable
fun LargeSpacer() {
    Spacer(modifier = Modifier.height(Spacing.large))
}

