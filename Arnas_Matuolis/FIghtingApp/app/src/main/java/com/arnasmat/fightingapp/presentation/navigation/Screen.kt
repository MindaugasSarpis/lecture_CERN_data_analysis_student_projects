package com.arnasmat.fightingapp.presentation.navigation

import androidx.annotation.StringRes
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.School
import androidx.compose.material.icons.filled.Star
import androidx.compose.ui.graphics.vector.ImageVector
import com.arnasmat.fightingapp.R

/**
 * Navigation screen definitions
 * Using regular objects instead of data objects for stability
 */
sealed class Screen(
    val route: String,
    @StringRes val titleRes: Int,
    val icon: ImageVector
) {

    // Bottom Navigation Screens
    object History : Screen(
        route = "history",
        titleRes = R.string.nav_history,
        icon = Icons.Default.Star
    )

    object Learn : Screen(
        route = "learn",
        titleRes = R.string.nav_learn,
        icon = Icons.Default.School
    )

    object Profile : Screen(
        route = "profile",
        titleRes = R.string.nav_profile,
        icon = Icons.Default.Person
    )

    object MoveDetail : Screen(
        route = "move_detail/{moveId}",
        titleRes = R.string.learn_move_detail_title,
        icon = Icons.Default.School
    ) {
        fun createRoute(moveId: Int) = "move_detail/$moveId"
    }

    // New screens for step-by-step learning flow
    object MoveSteps : Screen(
        route = "move_steps/{moveId}/{stepIndex}",
        titleRes = R.string.learn_move_detail_title,
        icon = Icons.Default.School
    ) {
        fun createRoute(moveId: Int, stepIndex: Int) = "move_steps/$moveId/$stepIndex"
    }

    object PracticeOverview : Screen(
        route = "practice_overview/{moveId}",
        titleRes = R.string.learn_move_detail_title,
        icon = Icons.Default.School
    ) {
        fun createRoute(moveId: Int) = "practice_overview/$moveId"
    }

    object RecordingPositioning : Screen(
        route = "recording_positioning/{moveId}",
        titleRes = R.string.learn_move_detail_title,
        icon = Icons.Default.PlayArrow
    ) {
        fun createRoute(moveId: Int) = "recording_positioning/$moveId"
    }

    object LearningRecording : Screen(
        route = "learning_recording/{moveId}",
        titleRes = R.string.nav_record,
        icon = Icons.Default.PlayArrow
    ) {
        fun createRoute(moveId: Int) = "learning_recording/$moveId"
    }

    object AnalyzedVideoPlayback : Screen(
        route = "analyzed_video_playback/{videoUrl}/{moveId}",
        titleRes = R.string.nav_record,
        icon = Icons.Default.PlayArrow
    ) {
        fun createRoute(videoUrl: String, moveId: Int): String {
            // URL encode the video URL to pass it as a route parameter
            return "analyzed_video_playback/${java.net.URLEncoder.encode(videoUrl, "UTF-8")}/$moveId"
        }
    }

    companion object {
        val bottomNavScreens: List<Screen> by lazy {
            listOf(Learn, History, Profile)
        }
    }
}
