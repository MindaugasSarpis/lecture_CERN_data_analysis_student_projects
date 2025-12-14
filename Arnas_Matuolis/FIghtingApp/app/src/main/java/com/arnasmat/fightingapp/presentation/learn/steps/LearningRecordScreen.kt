package com.arnasmat.fightingapp.presentation.learn.steps

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.arnasmat.fightingapp.presentation.components.*
import com.arnasmat.fightingapp.ui.theme.*

/**
 * Learning Record Screen - Simple wrapper that shows recording context
 * Note: Actual recording happens in RecordScreen
 */
@Composable
fun LearningRecordScreen(
    moveId: Int,
    onBackClick: () -> Unit,
    onRecordingComplete: () -> Unit,
    viewModel: LearningRecordViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    // Set the move ID when screen is first composed
    LaunchedEffect(moveId) {
        viewModel.setMoveId(moveId)
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(FightDarkBg)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar with context
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
                            text = "Record Your Practice",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary
                        )
                        if (state.move != null) {
                            Text(
                                text = state.move!!.title,
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary
                            )
                        }
                    }
                }
            }

            // Simple message - actual recording UI would be complex
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(Spacing.large),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                FightCard(
                    backgroundColor = FightDarkCard,
                    borderColor = ElectricBlue.copy(alpha = 0.3f)
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(Spacing.medium)
                    ) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = "Success",
                            tint = SuccessGreen,
                            modifier = Modifier.size(80.dp)
                        )

                        Text(
                            text = "Recording Feature",
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary,
                            textAlign = TextAlign.Center
                        )

                        Text(
                            text = "This screen would integrate with the RecordScreen to capture video with the move context (ID: $moveId).",
                            style = MaterialTheme.typography.bodyLarge,
                            color = TextSecondary,
                            textAlign = TextAlign.Center
                        )

                        if (state.move != null) {
                            Text(
                                text = "Move: ${state.move!!.title}",
                                style = MaterialTheme.typography.bodyMedium,
                                color = ElectricBlue,
                                textAlign = TextAlign.Center
                            )
                        }

                        FightPrimaryButton(
                            text = "Complete (Demo)",
                            onClick = onRecordingComplete,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }
            }
        }
    }
}

