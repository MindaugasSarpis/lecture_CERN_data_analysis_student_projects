package com.arnasmat.fightingapp.presentation.learn.steps

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.arnasmat.fightingapp.presentation.components.*
import com.arnasmat.fightingapp.presentation.learn.MoveDetailViewModel
import com.arnasmat.fightingapp.ui.theme.*

/**
 * Recording Positioning Screen
 * Provides instructions on how to position for recording
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecordingPositioningScreen(
    onBackClick: () -> Unit,
    onContinueToRecording: () -> Unit,
    viewModel: MoveDetailViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(FightDarkBg)
    ) {
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

                    Text(
                        text = "Camera Setup",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                }
            }

            // Content
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(Spacing.medium),
                verticalArrangement = Arrangement.spacedBy(Spacing.large),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(modifier = Modifier.weight(1f))

                // Title
                Icon(
                    imageVector = Icons.Default.Videocam,
                    contentDescription = null,
                    tint = FightRed,
                    modifier = Modifier.size(64.dp)
                )

                Text(
                    text = "Ready to Record",
                    style = MaterialTheme.typography.headlineLarge,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    textAlign = TextAlign.Center
                )

                // Quick Instructions - Clean list without card wrapper
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(Spacing.medium)
                ) {
                    QuickTip(
                        icon = Icons.Default.CropPortrait,
                        text = "Full body visible",
                        color = ElectricBlue
                    )
                    QuickTip(
                        icon = Icons.Default.CameraAlt,
                        text = "Front view, centered",
                        color = FightOrange
                    )
                    QuickTip(
                        icon = Icons.Default.WbSunny,
                        text = "Good lighting",
                        color = WarningYellow
                    )
                    QuickTip(
                        icon = Icons.Default.Straighten,
                        text = "Clear space around you",
                        color = SuccessGreen
                    )
                }

                Spacer(modifier = Modifier.weight(1f))

                // Action Button - Red for recording
                FightRecordButton(
                    text = "Start Recording",
                    onClick = onContinueToRecording,
                    modifier = Modifier.fillMaxWidth(),
                    icon = Icons.Default.Videocam
                )

                MediumSpacer()
            }
        }
    }
}

@Composable
private fun QuickTip(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    text: String,
    color: androidx.compose.ui.graphics.Color
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(Spacing.medium)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = color,
            modifier = Modifier.size(24.dp)
        )
        Text(
            text = text,
            style = MaterialTheme.typography.bodyLarge,
            color = TextPrimary,
            fontWeight = FontWeight.Medium
        )
    }
}

