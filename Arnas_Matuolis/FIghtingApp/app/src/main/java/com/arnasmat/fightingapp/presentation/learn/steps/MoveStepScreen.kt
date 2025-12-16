package com.arnasmat.fightingapp.presentation.learn.steps

import android.content.Context
import androidx.activity.ComponentActivity
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import com.arnasmat.fightingapp.presentation.components.*
import com.arnasmat.fightingapp.presentation.learn.MoveDetailViewModel
import com.arnasmat.fightingapp.ui.theme.*

/**
 * Screen showing individual step of a move with detailed instructions and video
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MoveStepScreen(
    stepIndex: Int,
    onBackClick: () -> Unit,
    onPreviousStep: () -> Unit,
    onNextStep: () -> Unit,
    onCompleteSteps: () -> Unit,
    viewModel: MoveDetailViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()
    val move = state.move

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(FightDarkBg)
    ) {
        if (move == null || move.steps.isEmpty()) {
            FightLoadingIndicator(
                text = "Loading step...",
                modifier = Modifier.fillMaxSize()
            )
        } else {
            val currentStepIndex = stepIndex.coerceIn(0, move.steps.size - 1)
            val currentStep = move.steps[currentStepIndex]
            val totalSteps = move.steps.size

            Column(modifier = Modifier.fillMaxSize()) {
                // Top Bar
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
                        FightIconButton(
                            icon = Icons.Default.ArrowBack,
                            onClick = onBackClick,
                            contentDescription = "Back",
                            backgroundColor = FightDarkElevated,
                            size = 40.dp
                        )

                        Spacer(modifier = Modifier.width(Spacing.small))

                        Column {
                            Text(
                                text = move.title,
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = TextPrimary
                            )
                            Text(
                                text = "Step ${currentStepIndex + 1} of $totalSteps",
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary
                            )
                        }
                    }
                }

                // Content
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                ) {
                    // Video Player - First thing user sees
                    if (currentStep.videoUrl.isNotEmpty()) {
                        VideoPlayerWithNativeFullscreen(videoUrl = currentStep.videoUrl)
                    }

                    // Step Content
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(Spacing.medium),
                        verticalArrangement = Arrangement.spacedBy(Spacing.medium)
                    ) {
                        // Step Description - Clean surface without heavy card
                        FightSurfaceSection(
                            backgroundColor = FightDarkSurface,
                            borderColor = ElectricBlue.copy(alpha = 0.2f),
                            content = {
                                Text(
                                    text = "Step ${currentStepIndex + 1}: ${currentStep.title}",
                                    style = MaterialTheme.typography.headlineSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = TextPrimary
                                )

                                SmallSpacer()

                                Text(
                                    text = currentStep.description,
                                    style = MaterialTheme.typography.bodyLarge,
                                    color = TextSecondary,
                                    lineHeight = MaterialTheme.typography.bodyLarge.lineHeight
                                )
                            }
                        )


                        // Progress Indicator
                        LinearProgressIndicator(
                            progress = { (currentStepIndex + 1).toFloat() / totalSteps },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(8.dp)
                                .clip(FightingShapes.small),
                            color = ElectricBlue,
                            trackColor = FightDarkElevated,
                        )

                        // Navigation Buttons
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(Spacing.small)
                        ) {
                            // Previous Button
                            if (currentStepIndex > 0) {
                                FightSecondaryButton(
                                    text = "Previous",
                                    onClick = onPreviousStep,
                                    modifier = Modifier.weight(1f),
                                    icon = Icons.Default.ArrowBack
                                )
                            }

                            // Next/Complete Button
                            if (currentStepIndex < totalSteps - 1) {
                                FightPrimaryButton(
                                    text = "Next Step",
                                    onClick = onNextStep,
                                    modifier = Modifier.weight(1f),
                                    icon = Icons.Default.ArrowForward
                                )
                            } else {
                                FightPrimaryButton(
                                    text = "Complete Steps",
                                    onClick = onCompleteSteps,
                                    modifier = Modifier.weight(1f),
                                    icon = Icons.Default.Check
                                )
                            }
                        }

                        MediumSpacer()
                    }
                }
            }
        }
    }
}

@Composable
private fun VideoPlayerWithNativeFullscreen(videoUrl: String) {
    val context = LocalContext.current
    val activity = context.findActivity()

    val exoPlayer = remember(videoUrl) {
        ExoPlayer.Builder(context).build().apply {
            setMediaItem(MediaItem.fromUri(videoUrl))
            prepare()
        }
    }

    DisposableEffect(videoUrl) {
        onDispose {
            exoPlayer.release()
        }
    }

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

                    setFullscreenButtonClickListener { isFullscreen ->
                        activity?.let { act ->
                            if (isFullscreen) {
                                act.window.decorView.systemUiVisibility = (
                                    android.view.View.SYSTEM_UI_FLAG_FULLSCREEN or
                                    android.view.View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
                                    android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                                )
                            } else {
                                act.window.decorView.systemUiVisibility = android.view.View.SYSTEM_UI_FLAG_VISIBLE
                            }
                        }
                    }
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(16f / 9f)
        )
    }
}

/**
 * Helper function to find activity from context
 */
private fun Context.findActivity(): ComponentActivity? {
    var context = this
    while (context is android.content.ContextWrapper) {
        if (context is ComponentActivity) return context
        context = context.baseContext
    }
    return null
}

