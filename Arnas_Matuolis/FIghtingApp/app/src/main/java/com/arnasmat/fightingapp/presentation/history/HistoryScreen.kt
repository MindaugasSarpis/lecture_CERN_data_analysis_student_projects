package com.arnasmat.fightingapp.presentation.history

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import com.arnasmat.fightingapp.R
import com.arnasmat.fightingapp.domain.model.RecordedVideo
import com.arnasmat.fightingapp.presentation.components.*
import com.arnasmat.fightingapp.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

/**
 * History Screen - Shows list of recorded videos
 * Updated with Design System components
 */
@Composable
fun HistoryScreen(
    viewModel: HistoryViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    // Main content - UserTopBar is now at MainActivity level
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(FightDarkBg)
    ) {
        when {
            state.selectedVideo != null -> {
                // Video playback view
                VideoPlaybackView(
                    video = state.selectedVideo!!,
                    onClose = { viewModel.clearSelectedVideo() },
                    onDelete = { video ->
                        viewModel.deleteVideo(video)
                    },
                    onRename = { video, newName ->
                        viewModel.renameVideo(video, newName)
                    }
                )
            }
            state.videos.isEmpty() -> {
                // Empty state with design system
                FightEmptyState(
                    message = stringResource(R.string.history_empty_message),
                    icon = Icons.Default.VideoLibrary
                )
            }
            else -> {
                // Video list
                VideoListView(
                    videos = state.videos,
                    onVideoClick = { video -> viewModel.selectVideo(video) },
                    onDeleteClick = { video -> viewModel.deleteVideo(video) }
                )
            }
        }
    }
}

@Composable
private fun VideoListView(
    videos: List<RecordedVideo>,
    onVideoClick: (RecordedVideo) -> Unit,
    onDeleteClick: (RecordedVideo) -> Unit
) {
    FightContainer(backgroundColor = FightDarkBg) {
        // Header with design system
        Text(
            text = stringResource(R.string.history_screen_title),
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold,
            color = TextPrimary
        )
        Spacer(modifier = Modifier.height(Spacing.extraSmall))
        Text(
            text = stringResource(R.string.history_subtitle, videos.size),
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary
        )

        MediumSpacer()

        // Video list
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(Spacing.small)
        ) {
            items(videos, key = { it.uri.toString() }) { video ->
                VideoListItem(
                    video = video,
                    onClick = { onVideoClick(video) },
                    onDeleteClick = { onDeleteClick(video) }
                )
            }
        }
    }
}

@Composable
private fun VideoListItem(
    video: RecordedVideo,
    onClick: () -> Unit,
    onDeleteClick: () -> Unit
) {
    var showDeleteDialog by remember { mutableStateOf(false) }

    FightCard(
        onClick = onClick,
        backgroundColor = FightDarkCard,
        borderColor = if (video.exerciseId != null) ElectricBlue.copy(alpha = 0.3f) else BorderLight
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(Spacing.medium)
        ) {
            // Leading icon
            Icon(
                imageVector = Icons.Default.PlayArrow,
                contentDescription = null,
                tint = ElectricBlue,
                modifier = Modifier.size(40.dp)
            )

            // Content
            Column(
                modifier = Modifier.weight(1f)
            ) {
                // Title
                Text(
                    text = video.fileName,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary
                )

                SmallSpacer()

                // Subtitle with duration and date
                Text(
                    text = buildString {
                        append(formatDuration(video.durationMs))
                        append(" • ")
                        append(formatDate(video.timestamp))
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )

                // Exercise badge (if available)
                if (video.exerciseId != null) {
                    SmallSpacer()
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(Spacing.extraSmall)
                    ) {
                        Icon(
                            imageVector = Icons.Default.FitnessCenter,
                            contentDescription = null,
                            tint = ElectricBlue,
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            text = video.exerciseName ?: "Exercise ID: ${video.exerciseId}",
                            style = MaterialTheme.typography.labelMedium,
                            color = ElectricBlue,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }

            // Delete button
            FightIconButton(
                icon = Icons.Default.Delete,
                onClick = { showDeleteDialog = true },
                contentDescription = stringResource(R.string.history_delete_video),
                backgroundColor = ErrorRed.copy(alpha = 0.2f),
                iconTint = ErrorRed,
                size = 40.dp
            )
        }
    }

    // Delete confirmation dialog with design system
    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            containerColor = FightDarkCard,
            titleContentColor = TextPrimary,
            textContentColor = TextSecondary,
            title = {
                Text(
                    text = stringResource(R.string.history_delete_title),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
            },
            text = { Text(stringResource(R.string.history_delete_message)) },
            confirmButton = {
                FightPrimaryButton(
                    text = stringResource(R.string.history_delete_confirm),
                    onClick = {
                        onDeleteClick()
                        showDeleteDialog = false
                    }
                )
            },
            dismissButton = {
                FightTextButton(
                    text = stringResource(R.string.history_delete_cancel),
                    onClick = { showDeleteDialog = false },
                    color = TextSecondary
                )
            }
        )
    }
}

@Composable
private fun VideoPlaybackView(
    video: RecordedVideo,
    onClose: () -> Unit,
    onDelete: (RecordedVideo) -> Unit,
    onRename: (RecordedVideo, String) -> Unit
) {
    var showDeleteDialog by remember { mutableStateOf(false) }
    var isEditing by remember { mutableStateOf(false) }
    var editedName by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(FightDarkBg)
    ) {
        // Video player
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
        ) {
            VideoPlayer(
                videoUri = video.uri,
                modifier = Modifier.fillMaxSize(),
                autoPlay = true
            )

            // Close button overlay with design system
            Box(
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .padding(Spacing.medium)
            ) {
                FightCircleIconButton(
                    icon = Icons.Default.Close,
                    onClick = onClose,
                    contentDescription = stringResource(R.string.history_close_video),
                    backgroundColor = FightDarkElevated.copy(alpha = 0.9f),
                    iconTint = TextPrimary,
                    size = 48.dp
                )
            }
        }

        // Video details card with design system
        FightCard(
            modifier = Modifier.fillMaxWidth(),
            backgroundColor = FightDarkCard,
            borderColor = ElectricBlue.copy(alpha = 0.3f)
        ) {
            // Inline editable filename
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                if (isEditing) {
                    FightTextField(
                        value = editedName,
                        onValueChange = { editedName = it },
                        modifier = Modifier.weight(1f),
                        singleLine = true,
                        leadingIcon = Icons.Default.Edit
                    )
                    Spacer(modifier = Modifier.width(Spacing.small))
                    FightIconButton(
                        icon = Icons.Default.Check,
                        onClick = {
                            if (editedName.isNotBlank()) {
                                onRename(video, editedName.trim())
                                isEditing = false
                            }
                        },
                        backgroundColor = SuccessGreen,
                        iconTint = TextPrimary
                    )
                    FightIconButton(
                        icon = Icons.Default.Close,
                        onClick = { isEditing = false },
                        backgroundColor = FightDarkElevated,
                        iconTint = TextSecondary
                    )
                } else {
                    Text(
                        text = video.fileName,
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                        modifier = Modifier.weight(1f)
                    )
                    FightIconButton(
                        icon = Icons.Default.Edit,
                        onClick = {
                            editedName = video.fileName.removeSuffix(".mp4")
                            isEditing = true
                        },
                        backgroundColor = ElectricBlue.copy(alpha = 0.2f),
                        iconTint = ElectricBlue
                    )
                }
            }

            SmallSpacer()

            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.small)
            ) {
                FightCompactCard(
                    text = formatDuration(video.durationMs),
                    backgroundColor = FightDarkElevated,
                    borderColor = ElectricBlue.copy(alpha = 0.3f)
                )
                FightCompactCard(
                    text = formatDate(video.timestamp),
                    backgroundColor = FightDarkElevated,
                    borderColor = ElectricBlue.copy(alpha = 0.3f)
                )
            }

            // Exercise context info (if available)
            if (video.exerciseId != null) {
                MediumSpacer()

                FightCard(
                    backgroundColor = FightDarkElevated,
                    borderColor = ElectricBlue.copy(alpha = 0.5f)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(Spacing.small)
                    ) {
                        Icon(
                            imageVector = Icons.Default.FitnessCenter,
                            contentDescription = null,
                            tint = ElectricBlue,
                            modifier = Modifier.size(24.dp)
                        )
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "🥋 Learning Context",
                                style = MaterialTheme.typography.labelSmall,
                                color = ElectricBlue,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = video.exerciseName ?: "Exercise ID: ${video.exerciseId}",
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextPrimary,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }

            MediumSpacer()

            // Delete button with design system
            FightOutlinedButton(
                text = stringResource(R.string.history_delete_video),
                onClick = { showDeleteDialog = true },
                modifier = Modifier.fillMaxWidth(),
                icon = Icons.Default.Delete,
                borderColor = ErrorRed
            )
        }
    }

    // Delete confirmation dialog with design system
    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            containerColor = FightDarkCard,
            titleContentColor = TextPrimary,
            textContentColor = TextSecondary,
            title = {
                Text(
                    text = stringResource(R.string.history_delete_title),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
            },
            text = { Text(stringResource(R.string.history_delete_message)) },
            confirmButton = {
                FightPrimaryButton(
                    text = stringResource(R.string.history_delete_confirm),
                    onClick = {
                        onDelete(video)
                        showDeleteDialog = false
                    }
                )
            },
            dismissButton = {
                FightTextButton(
                    text = stringResource(R.string.history_delete_cancel),
                    onClick = { showDeleteDialog = false },
                    color = TextSecondary
                )
            }
        )
    }
}

private fun formatDuration(milliseconds: Long): String {
    val seconds = milliseconds / 1000
    val minutes = seconds / 60
    val remainingSeconds = seconds % 60
    return String.format(Locale.getDefault(), "%02d:%02d", minutes, remainingSeconds)
}

private fun formatDate(timestamp: Long): String {
    val sdf = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
    return sdf.format(Date(timestamp))
}
