package com.arnasmat.fightingapp.presentation.learn

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.BookmarkBorder
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import coil3.compose.AsyncImage
import com.arnasmat.fightingapp.R
import com.arnasmat.fightingapp.domain.model.Move
import com.arnasmat.fightingapp.presentation.components.*
import com.arnasmat.fightingapp.ui.theme.*

/**
 * Move Detail Screen - Shows detailed information about a move
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MoveDetailScreen(
    onBackClick: () -> Unit,
    onStartLearning: (Int) -> Unit, // Navigate to first step with moveId
    viewModel: MoveDetailViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    // Cleaner design without heavy Scaffold - matches LearnScreen style
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(FightDarkBg)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Compact top bar with back button and bookmark
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(FightDarkSurface)
                    .padding(horizontal = Spacing.small, vertical = Spacing.small),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.weight(1f)
                ) {
                    // Back button
                    FightIconButton(
                        icon = Icons.Default.ArrowBack,
                        onClick = onBackClick,
                        contentDescription = "Back",
                        backgroundColor = FightDarkElevated,
                        size = 40.dp
                    )

                    Spacer(modifier = Modifier.width(Spacing.small))

                    // Title
                    Text(
                        text = state.move?.title ?: stringResource(R.string.learn_move_detail_title),
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                // Bookmark button
                if (state.move != null) {
                    FightIconButton(
                        icon = if (state.move!!.isMarked) {
                            Icons.Default.Bookmark
                        } else {
                            Icons.Default.BookmarkBorder
                        },
                        onClick = { viewModel.toggleMarked() },
                        contentDescription = stringResource(R.string.learn_toggle_mark),
                        backgroundColor = if (state.move!!.isMarked) {
                            FightRed.copy(alpha = 0.2f)
                        } else {
                            FightDarkElevated
                        },
                        iconTint = if (state.move!!.isMarked) FightRed else TextSecondary,
                        enabled = !state.isMarkingInProgress,
                        size = 40.dp
                    )
                }
            }

            // Content
            when {
                state.isLoading -> {
                    FightLoadingIndicator(
                        text = "Loading move details...",
                        modifier = Modifier.fillMaxSize()
                    )
                }
                state.error != null -> {
                    Box(modifier = Modifier.padding(Spacing.medium)) {
                        FightErrorCard(
                            message = state.error!!,
                            onDismiss = { viewModel.clearError() }
                        )
                    }
                }
                state.move != null -> {
                    MoveDetailContent(
                        move = state.move!!,
                        isStartingLearning = state.isStartingLearning,
                        hasStartedLearning = state.hasStartedLearning,
                        onStartLearning = { onStartLearning(state.move!!.id) }
                    )
                }
            }
        }
    }
}

@Composable
private fun MoveDetailContent(
    move: Move,
    isStartingLearning: Boolean,
    hasStartedLearning: Boolean,
    onStartLearning: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
    ) {
        // Video Player - First thing user sees (replaces image)
        if (move.videoUrl.isNotEmpty()) {
            VideoPlayerWithNativeFullscreen(videoUrl = move.videoUrl)
        }

        // Content with modern sections
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.medium),
            verticalArrangement = Arrangement.spacedBy(Spacing.large)
        ) {
            // Description Section - No card, just clean text
            Column(
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = move.description,
                    style = MaterialTheme.typography.bodyLarge,
                    color = TextSecondary,
                    maxLines = 3,
                    overflow = TextOverflow.Ellipsis
                )
            }

            // Action Button - Immediately visible without scrolling
            FightPrimaryButton(
                text = if (hasStartedLearning) {
                    stringResource(R.string.learn_started)
                } else {
                    stringResource(R.string.learn_start_learning)
                },
                onClick = onStartLearning,
                modifier = Modifier.fillMaxWidth(),
                enabled = !isStartingLearning && !hasStartedLearning,
                isLoading = isStartingLearning,
                icon = Icons.Default.PlayArrow
            )

            if (hasStartedLearning) {
                FightSuccessCard(
                    message = stringResource(R.string.learn_started_message)
                )
            }
        }
    }
}

@Composable
private fun VideoPlayerWithNativeFullscreen(videoUrl: String) {
    val context = LocalContext.current
    val activity = context.findActivity()

    // Create ExoPlayer
    val exoPlayer = remember(videoUrl) {
        ExoPlayer.Builder(context).build().apply {
            setMediaItem(MediaItem.fromUri(videoUrl))
            prepare()
        }
    }

    // Dispose player when composable leaves composition
    DisposableEffect(videoUrl) {
        onDispose {
            exoPlayer.release()
        }
    }

    // Original working video player with border
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .border(
                width = Dimensions.borderMedium,
                color = ElectricBlue.copy(alpha = 0.5f),
                shape = FightingShapes.medium
            )
            .clip(FightingShapes.medium)
            .background(FightDarkBg)
    ) {
        AndroidView(
            factory = { ctx ->
                PlayerView(ctx).apply {
                    player = exoPlayer
                    useController = true

                    // Use ExoPlayer's native fullscreen handling
                    setFullscreenButtonClickListener { isFullscreen ->
                        activity?.let { act ->
                            if (isFullscreen) {
                                // Enter fullscreen
//                                act.requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
                                act.window.decorView.systemUiVisibility = (
                                    android.view.View.SYSTEM_UI_FLAG_FULLSCREEN or
                                    android.view.View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
                                    android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                                )
                            } else {
//                                act.requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
                                act.window.decorView.systemUiVisibility = android.view.View.SYSTEM_UI_FLAG_VISIBLE
                            }
                        }
                    }
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(250.dp)
        )
    }
}

// Extension function to get activity from context
private fun android.content.Context.findActivity(): android.app.Activity? {
    var context = this
    while (context is android.content.ContextWrapper) {
        if (context is android.app.Activity) return context
        context = context.baseContext
    }
    return null
}

