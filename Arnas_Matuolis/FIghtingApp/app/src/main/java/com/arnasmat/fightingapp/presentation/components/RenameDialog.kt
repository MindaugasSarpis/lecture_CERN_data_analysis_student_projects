package com.arnasmat.fightingapp.presentation.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.arnasmat.fightingapp.R

/**
 * Reusable Rename Dialog Component
 * Used for renaming videos in both Record and History screens
 *
 * @param currentName The current file name to display
 * @param onDismiss Callback when dialog is dismissed
 * @param onConfirm Callback with new name when confirmed
 */
@Composable
fun RenameDialog(
    currentName: String,
    onDismiss: () -> Unit,
    onConfirm: (String) -> Unit
) {
    // Remove .mp4 extension from current name for editing
    val nameWithoutExtension = currentName.removeSuffix(".mp4")
    var newName by remember { mutableStateOf(nameWithoutExtension) }
    var isError by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.history_rename_title)) },
        text = {
            Column {
                Text(
                    text = stringResource(R.string.history_rename_hint),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = newName,
                    onValueChange = {
                        newName = it
                        isError = it.isBlank()
                    },
                    label = { Text("Video name") },
                    singleLine = true,
                    isError = isError,
                    supportingText = if (isError) {
                        { Text("Name cannot be empty") }
                    } else null,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    if (newName.isNotBlank()) {
                        onConfirm(newName.trim())
                        onDismiss()
                    } else {
                        isError = true
                    }
                },
                enabled = newName.isNotBlank()
            ) {
                Text(stringResource(R.string.history_rename_confirm))
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.history_rename_cancel))
            }
        }
    )
}

