package com.arnasmat.fightingapp.presentation.learn.steps

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.FiberManualRecord
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.arnasmat.fightingapp.presentation.components.*
import com.arnasmat.fightingapp.presentation.learn.MoveDetailViewModel
import com.arnasmat.fightingapp.ui.theme.*

/**
 * Practice Overview Screen - Final review before recording
 * Shows broad overview with key reminders
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PracticeOverviewScreen(
    onBackClick: () -> Unit,
    onStartRecording: () -> Unit,
    viewModel: MoveDetailViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()
    val move = state.move

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(FightDarkBg)
    ) {
        if (move == null) {
            FightLoadingIndicator(
                text = "Loading...",
                modifier = Modifier.fillMaxSize()
            )
        } else {
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
                            text = "Show us what you got!",
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
                        .verticalScroll(rememberScrollState())
                        .padding(Spacing.medium),
                    verticalArrangement = Arrangement.spacedBy(Spacing.large)
                ) {
                    // Theory Completed - Clean section without card
                    FightSurfaceSection(
                        backgroundColor = FightDarkSurface,
                        borderColor = SuccessGreen.copy(alpha = 0.3f),
                        content = {
                            Text(
                                text = "✅ Theory Completed!",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = SuccessGreen
                            )

                            SmallSpacer()

                            Text(
                                text = move.title,
                                style = MaterialTheme.typography.headlineMedium,
                                fontWeight = FontWeight.Bold,
                                color = TextPrimary
                            )

                            SmallSpacer()

                            Text(
                                text = "You've learned all the steps. Now let's practice!",
                                style = MaterialTheme.typography.bodyLarge,
                                color = TextSecondary
                            )
                        }
                    )

                    // Action Button - Red for recording action (immediately visible)
                    FightRecordButton(
                        text = "Record My Practice",
                        onClick = onStartRecording,
                        modifier = Modifier.fillMaxWidth(),
                        icon = Icons.Default.FiberManualRecord
                    )

                    // Key Reminders - Keep as card since it's important pre-recording checklist
                    FightCard(
                        backgroundColor = FightDarkCard,
                        borderColor = FightRed.copy(alpha = 0.3f)
                    ) {
                        Column(
                            verticalArrangement = Arrangement.spacedBy(Spacing.medium)
                        ) {
                            Text(
                                text = "🎯 Key Tips to Remember",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                                color = FightRed
                            )

                            // Collect all tips from all steps
                            val allTips = move.steps.flatMap { it.tips }.distinct()

                            if (allTips.isNotEmpty()) {
                                Column(
                                    verticalArrangement = Arrangement.spacedBy(Spacing.small)
                                ) {
                                    allTips.take(8).forEach { tip ->
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            verticalAlignment = Alignment.Top
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.FiberManualRecord,
                                                contentDescription = null,
                                                tint = FightRed,
                                                modifier = Modifier
                                                    .size(8.dp)
                                                    .padding(top = 8.dp)
                                            )
                                            Spacer(modifier = Modifier.width(Spacing.small))
                                            Text(
                                                text = tip,
                                                style = MaterialTheme.typography.bodyMedium,
                                                color = TextSecondary,
                                                modifier = Modifier.weight(1f)
                                            )
                                        }
                                    }
                                }
                            } else {
                                // Fallback if no tips available
                                Column(
                                    verticalArrangement = Arrangement.spacedBy(Spacing.small)
                                ) {
                                    listOf(
                                        "Maintain proper stance and posture",
                                        "Execute each movement with control",
                                        "Focus on technique over speed",
                                        "Breathe naturally throughout",
                                        "Keep your guard up"
                                    ).forEach { tip ->
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            verticalAlignment = Alignment.Top
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.FiberManualRecord,
                                                contentDescription = null,
                                                tint = FightRed,
                                                modifier = Modifier
                                                    .size(8.dp)
                                                    .padding(top = 8.dp)
                                            )
                                            Spacer(modifier = Modifier.width(Spacing.small))
                                            Text(
                                                text = tip,
                                                style = MaterialTheme.typography.bodyMedium,
                                                color = TextSecondary,
                                                modifier = Modifier.weight(1f)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }


                    MediumSpacer()
                }
            }
        }
    }
}

