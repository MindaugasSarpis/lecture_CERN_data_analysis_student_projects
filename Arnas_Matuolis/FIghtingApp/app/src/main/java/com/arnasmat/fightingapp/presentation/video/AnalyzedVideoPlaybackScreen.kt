package com.arnasmat.fightingapp.presentation.video

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.common.util.UnstableApi
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import coil3.compose.AsyncImage
import com.arnasmat.fightingapp.domain.model.VideoAnalysis

/**
 * Full-screen video playback screen for analyzed videos
 * Displays the analyzed video stream and chart image from the backend
 */
@androidx.annotation.OptIn(UnstableApi::class)
@Composable
fun AnalyzedVideoPlaybackScreen(
    analysis: VideoAnalysis,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val baseUrl = "https://web-production-a59ad.up.railway.app/"

    // Create and remember ExoPlayer
    val exoPlayer = remember(analysis.streamVideoUrl) {
        ExoPlayer.Builder(context).build().apply {
            analysis.streamVideoUrl?.let { videoPath ->
                val fullUrl = if (videoPath.startsWith("http")) {
                    videoPath
                } else {
                    baseUrl + videoPath.removePrefix("/")
                }
                val mediaItem = MediaItem.fromUri(fullUrl)
                setMediaItem(mediaItem)
                prepare()
                playWhenReady = true
                repeatMode = Player.REPEAT_MODE_OFF
            }
        }
    }

    // Clean up player when composable leaves composition
    DisposableEffect(Unit) {
        onDispose {
            exoPlayer.release()
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
    ) {
        // Video Player
        if (analysis.streamVideoUrl != null) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(16f / 9f)
                    .background(Color.Black)
            ) {
                AndroidView(
                    factory = { ctx ->
                        PlayerView(ctx).apply {
                            player = exoPlayer
                            useController = true
                            controllerAutoShow = true
                            controllerShowTimeoutMs = 3000
                        }
                    },
                    modifier = Modifier.fillMaxSize()
                )
            }
        }

        // Chart Image
        if (analysis.chartUrl != null) {
            val chartFullUrl = if (analysis.chartUrl.startsWith("http")) {
                analysis.chartUrl
            } else {
                baseUrl + analysis.chartUrl.removePrefix("/")
            }

            AsyncImage(
                model = chartFullUrl,
                contentDescription = "Analysis Chart",
                modifier = Modifier
                    .fillMaxWidth()
                    .wrapContentHeight(),
                contentScale = ContentScale.FillWidth
            )
        }

        // Add some bottom padding for scrolling
        Spacer(modifier = Modifier.height(24.dp))
    }
}

