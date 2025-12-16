package com.arnasmat.fightingapp.presentation.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import com.arnasmat.fightingapp.ui.theme.*

/**
 * DESIGN SYSTEM - DIALOG COMPONENTS
 * Standardized dialog components for the fighting app
 */

enum class DialogType {
    Default, Success, Error, Warning, Info
}

@Composable
fun FightDialog(
    title: String,
    message: String,
    onDismiss: () -> Unit,
    confirmButton: @Composable () -> Unit,
    dismissButton: @Composable (() -> Unit)? = null,
    icon: ImageVector? = null,
    type: DialogType = DialogType.Default
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = FightDarkCard,
        titleContentColor = TextPrimary,
        textContentColor = TextSecondary,
        shape = FightingShapes.large,
        icon = icon?.let {
            {
                Icon(
                    imageVector = it,
                    contentDescription = null,
                    tint = when(type) {
                        DialogType.Error -> ErrorRed
                        DialogType.Warning -> WarningYellow
                        DialogType.Success -> SuccessGreen
                        DialogType.Info -> InfoBlue
                        else -> ElectricBlue
                    },
                    modifier = Modifier.size(Dimensions.iconSizeLarge)
                )
            }
        },
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        },
        text = {
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
        },
        confirmButton = confirmButton,
        dismissButton = dismissButton
    )
}

@Composable
fun FightConfirmDialog(
    title: String,
    message: String,
    confirmText: String,
    dismissText: String,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
    type: DialogType = DialogType.Warning,
    icon: ImageVector? = null
) {
    FightDialog(
        title = title,
        message = message,
        onDismiss = onDismiss,
        type = type,
        icon = icon,
        confirmButton = {
            FightPrimaryButton(
                text = confirmText,
                onClick = onConfirm
            )
        },
        dismissButton = {
            FightTextButton(
                text = dismissText,
                onClick = onDismiss,
                color = TextSecondary
            )
        }
    )
}

@Composable
fun FightInputDialog(
    title: String,
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    confirmText: String,
    dismissText: String,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
    placeholder: String? = null,
    isError: Boolean = false,
    errorMessage: String? = null,
    leadingIcon: ImageVector? = null
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = FightDarkCard,
        titleContentColor = TextPrimary,
        textContentColor = TextSecondary,
        shape = FightingShapes.large,
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        },
        text = {
            Column {
                FightTextField(
                    value = value,
                    onValueChange = onValueChange,
                    label = label,
                    placeholder = placeholder,
                    leadingIcon = leadingIcon,
                    isError = isError,
                    errorMessage = errorMessage,
                    singleLine = true
                )
            }
        },
        confirmButton = {
            FightPrimaryButton(
                text = confirmText,
                onClick = onConfirm,
                enabled = value.isNotBlank() && !isError
            )
        },
        dismissButton = {
            FightTextButton(
                text = dismissText,
                onClick = onDismiss,
                color = TextSecondary
            )
        }
    )
}

