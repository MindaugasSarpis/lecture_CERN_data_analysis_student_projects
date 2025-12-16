package com.arnasmat.fightingapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.arnasmat.fightingapp.presentation.components.NetworkStatusBanner
import com.arnasmat.fightingapp.presentation.components.UserTopBar
import com.arnasmat.fightingapp.presentation.navigation.BottomNavigationBar
import com.arnasmat.fightingapp.presentation.navigation.NavGraph
import com.arnasmat.fightingapp.presentation.navigation.Screen
import com.arnasmat.fightingapp.presentation.profile.UserProfileViewModel
import com.arnasmat.fightingapp.ui.theme.FIghtingAppTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            FIghtingAppTheme {
                val navController = rememberNavController()

                // Shared UserProfileViewModel at activity level
                // This ensures it's only created once and survives navigation
                val userProfileViewModel: UserProfileViewModel = hiltViewModel()

                // Get current route to determine UserTopBar visibility
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentRoute = navBackStackEntry?.destination?.route

                // Define which screens should NOT show the UserTopBar
                // Profile has its own detailed profile view, so no top bar needed
                val hideUserTopBar = currentRoute in listOf(
                    Screen.Profile.route
                )

                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    bottomBar = {
                        BottomNavigationBar(navController = navController)
                    }
                ) { innerPadding ->
                    Column(modifier = Modifier.padding(innerPadding)) {
                        // Global network status banner
                        NetworkStatusBanner()

                        // Shared UserTopBar - conditionally shown based on current screen
                        if (!hideUserTopBar) {
                            UserTopBar(viewModel = userProfileViewModel)
                        }

                        // Main content
                        NavGraph(
                            navController = navController,
                            modifier = Modifier.fillMaxSize()
                        )
                    }
                }
            }
        }
    }
}
