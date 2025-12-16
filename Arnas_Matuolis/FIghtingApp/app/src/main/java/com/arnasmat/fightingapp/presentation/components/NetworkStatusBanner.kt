package com.arnasmat.fightingapp.presentation.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.runtime.*
import androidx.compose.ui.res.stringResource
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import com.arnasmat.fightingapp.R
import com.arnasmat.fightingapp.presentation.util.NetworkStatusViewModel

/**
 * Generic network connectivity banner that shows across all screens
 * Automatically appears when network is disconnected
 * Best practice: Centralized UI for network status
 * Updated to use Design System components
 */
@Composable
fun NetworkStatusBanner(
    viewModel: NetworkStatusViewModel = hiltViewModel()
) {
    val isConnected by viewModel.isConnected.collectAsState()

    AnimatedVisibility(
        visible = !isConnected,
        enter = expandVertically(),
        exit = shrinkVertically()
    ) {
        FightBanner(
            message = stringResource(R.string.network_status_no_internet),
            type = BannerType.Error,
            onDismiss = null // No dismiss for network status - it disappears when connected
        )
    }
}

