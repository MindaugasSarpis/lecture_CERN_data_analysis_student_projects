package com.arnasmat.fightingapp.presentation.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.arnasmat.fightingapp.presentation.history.HistoryScreen
import com.arnasmat.fightingapp.presentation.learn.LearnScreen
import com.arnasmat.fightingapp.presentation.learn.MoveDetailScreen
import com.arnasmat.fightingapp.presentation.learn.steps.MoveStepScreen
import com.arnasmat.fightingapp.presentation.learn.steps.PracticeOverviewScreen
import com.arnasmat.fightingapp.presentation.learn.steps.RecordingPositioningScreen
import com.arnasmat.fightingapp.presentation.profile.ProfileScreen
import com.arnasmat.fightingapp.presentation.record.RecordScreen
import com.arnasmat.fightingapp.presentation.record.RecordViewModel

@Composable
fun NavGraph(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Learn.route,
        modifier = modifier
    ) {

        // Bottom Navigation Screens
        composable(Screen.History.route) {
            HistoryScreen()
        }
        composable(Screen.Learn.route) {
            LearnScreen(
                onMoveClick = { moveId ->
                    navController.navigate(Screen.MoveDetail.createRoute(moveId))
                }
            )
        }
        composable(
            route = Screen.MoveDetail.route,
            arguments = listOf(
                navArgument("moveId") {
                    type = NavType.StringType
                }
            )
        ) {
            MoveDetailScreen(
                onBackClick = {
                    navController.navigateUp()
                },
                onStartLearning = { moveId ->
                    // Navigate to first step (index 0)
                    navController.navigate(Screen.MoveSteps.createRoute(moveId, 0))
                }
            )
        }

        // Step-by-step learning flow screens
        composable(
            route = Screen.MoveSteps.route,
            arguments = listOf(
                navArgument("moveId") {
                    type = NavType.StringType
                },
                navArgument("stepIndex") {
                    type = NavType.StringType
                }
            )
        ) { backStackEntry ->
            val moveId = backStackEntry.arguments?.getString("moveId")?.toIntOrNull() ?: 0
            val stepIndex = backStackEntry.arguments?.getString("stepIndex")?.toIntOrNull() ?: 0

            MoveStepScreen(
                stepIndex = stepIndex,
                onBackClick = {
                    navController.navigateUp()
                },
                onPreviousStep = {
                    if (stepIndex > 0) {
                        navController.navigate(Screen.MoveSteps.createRoute(moveId, stepIndex - 1)) {
                            popUpTo(Screen.MoveSteps.createRoute(moveId, stepIndex)) {
                                inclusive = true
                            }
                        }
                    }
                },
                onNextStep = {
                    navController.navigate(Screen.MoveSteps.createRoute(moveId, stepIndex + 1)) {
                        popUpTo(Screen.MoveSteps.createRoute(moveId, stepIndex)) {
                            inclusive = true
                        }
                    }
                },
                onCompleteSteps = {
                    // Navigate to practice overview
                    navController.navigate(Screen.PracticeOverview.createRoute(moveId)) {
                        // Clear the step stack
                        popUpTo(Screen.MoveDetail.createRoute(moveId)) {
                            inclusive = false
                        }
                    }
                }
            )
        }

        composable(
            route = Screen.PracticeOverview.route,
            arguments = listOf(
                navArgument("moveId") {
                    type = NavType.StringType
                }
            )
        ) { backStackEntry ->
            val moveId = backStackEntry.arguments?.getString("moveId")?.toIntOrNull() ?: 0

            PracticeOverviewScreen(
                onBackClick = {
                    navController.navigateUp()
                },
                onStartRecording = {
                    navController.navigate(Screen.RecordingPositioning.createRoute(moveId))
                }
            )
        }

        composable(
            route = Screen.RecordingPositioning.route,
            arguments = listOf(
                navArgument("moveId") {
                    type = NavType.StringType
                }
            )
        ) { backStackEntry ->
            val moveId = backStackEntry.arguments?.getString("moveId")?.toIntOrNull() ?: 0

            RecordingPositioningScreen(
                onBackClick = {
                    navController.navigateUp()
                },
                onContinueToRecording = {
                    navController.navigate(Screen.LearningRecording.createRoute(moveId))
                }
            )
        }

        composable(
            route = Screen.LearningRecording.route,
            arguments = listOf(
                navArgument("moveId") {
                    type = NavType.StringType
                }
            )
        ) { backStackEntry ->
            val moveId = backStackEntry.arguments?.getString("moveId")?.toIntOrNull() ?: 0

            // Use the regular RecordScreen but with exerciseId context
            RecordScreen(
                exerciseId = moveId,
                onNavigateToAnalyzedVideo = { analysis ->
                    // Navigate with just the moveId, the analysis will be fetched/displayed
                    navController.navigate(Screen.AnalyzedVideoPlayback.createRoute("analyzed", moveId))
                }
            )
        }

        composable(
            route = Screen.AnalyzedVideoPlayback.route,
            arguments = listOf(
                navArgument("videoUrl") {
                    type = NavType.StringType
                },
                navArgument("moveId") {
                    type = NavType.IntType
                }
            )
        ) { backStackEntry ->
            val moveId = backStackEntry.arguments?.getInt("moveId") ?: 2

            // Get the analysis from the RecordViewModel which should still be in memory
            val parentEntry = remember(backStackEntry) {
                navController.getBackStackEntry(Screen.LearningRecording.createRoute(moveId))
            }
            val recordViewModel: RecordViewModel = hiltViewModel(parentEntry)
            val recordState by recordViewModel.state.collectAsState()

            if (recordState.videoAnalysis != null) {
                com.arnasmat.fightingapp.presentation.video.AnalyzedVideoPlaybackScreen(
                    analysis = recordState.videoAnalysis!!
                )
            } else {
                // Fallback if analysis is not available
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
        }

        composable(Screen.Profile.route) {
            ProfileScreen()
        }
    }
}
