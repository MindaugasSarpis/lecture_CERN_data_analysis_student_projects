package com.arnasmat.fightingapp.presentation.learn

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import coil3.compose.AsyncImage
import com.arnasmat.fightingapp.R
import com.arnasmat.fightingapp.domain.model.Belt
import com.arnasmat.fightingapp.domain.model.Move
import com.arnasmat.fightingapp.domain.model.MoveDifficulty
import com.arnasmat.fightingapp.presentation.components.*
import com.arnasmat.fightingapp.ui.theme.*

/**
 * Learn Screen - Shows list of suggested moves for learning
 * Updated with Design System components
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LearnScreen(
    onMoveClick: (Int) -> Unit,
    viewModel: LearnViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    // UserTopBar is now at MainActivity level - no need for separate TopAppBar
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(FightDarkBg)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Screen title
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(FightDarkSurface)
                    .padding(horizontal = Spacing.medium, vertical = Spacing.small),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Your Learning Path",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
            }

            // Content
            Box(
                modifier = Modifier
                    .fillMaxSize()
            ) {
                when {
                    state.isLoading && state.moves.isEmpty() -> {
                        FightLoadingIndicator(
                            text = "Loading moves...",
                            modifier = Modifier.fillMaxSize()
                        )
                    }

                    state.error != null -> {
                        FightErrorState(
                            message = state.error!!,
                            onDismiss = { viewModel.clearError() },
                            onRetry = { viewModel.loadLearningSuggestions() }
                        )
                    }

                    state.moves.isEmpty() -> {
                        FightEmptyState(
                            message = stringResource(R.string.learn_empty_state),
                            icon = Icons.Default.MenuBook,
                            actionButton = {
                                FightPrimaryButton(
                                    text = "Refresh",
                                    onClick = { viewModel.loadLearningSuggestions() },
                                    icon = Icons.Default.Refresh
                                )
                            }
                        )
                    }
                    else -> {
                        MovesList(
                            moves = state.moves,
                            onMoveClick = onMoveClick,
                            userBelt = Belt.WHITE, // TODO: Get from user profile
                            completedMoveIds = setOf(1) // Only first white belt move completed
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun MovesList(
    moves: List<Move>,
    onMoveClick: (Int) -> Unit,
    userBelt: Belt,
    completedMoveIds: Set<Int> = emptySet()
) {
    // Group moves by belt level
    val groupedMoves = moves.groupBy { it.difficulty }
        .toSortedMap(compareBy { it.ordinal })

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(FightDarkBg),
        contentPadding = PaddingValues(vertical = Spacing.small)
    ) {
        groupedMoves.forEach { (difficulty, beltMoves) ->
            val beltLevel = difficulty.belt
            val isCompleted = beltLevel.ordinal < userBelt.ordinal
            val isCurrent = beltLevel == userBelt
            val isLocked = beltLevel.ordinal > userBelt.ordinal

            // Belt header
            item(key = "header_${difficulty.name}") {
                BeltProgressionHeader(
                    difficulty = difficulty,
                    isCompleted = isCompleted,
                    isCurrent = isCurrent,
                    isLocked = isLocked,
                    moveCount = beltMoves.size
                )
            }

            // Moves for this belt
            items(
                items = beltMoves,
                key = { it.id }
            ) { move ->
                MoveListItem(
                    move = move,
                    onClick = {
                        if (!isLocked || !move.isAvailable) {
                            onMoveClick(move.id)
                        }
                    },
                    isLocked = isLocked || !move.isAvailable,
                    isCompleted = completedMoveIds.contains(move.id)
                )
            }
        }
    }
}

@Composable
private fun BeltProgressionHeader(
    difficulty: MoveDifficulty,
    isCompleted: Boolean,
    isCurrent: Boolean,
    isLocked: Boolean,
    moveCount: Int
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                if (isCurrent) FightDarkSurface else FightDarkBg
            )
            .padding(
                horizontal = Spacing.medium,
                vertical = Spacing.medium
            ),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(Spacing.medium)
    ) {
        // Status icon
        Box(
            modifier = Modifier
                .size(40.dp)
                .background(
                    color = when {
                        isCompleted -> SuccessGreen.copy(alpha = 0.2f)
                        isCurrent -> DifficultyColors.getColor(difficulty).copy(alpha = 0.2f)
                        else -> FightDarkElevated
                    },
                    shape = FightingShapes.medium
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = when {
                    isCompleted -> Icons.Default.CheckCircle
                    isCurrent -> Icons.Default.PlayArrow
                    else -> Icons.Default.Lock
                },
                contentDescription = null,
                tint = when {
                    isCompleted -> SuccessGreen
                    isCurrent -> DifficultyColors.getColor(difficulty)
                    else -> TextTertiary
                },
                modifier = Modifier.size(24.dp)
            )
        }

        // Belt info
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = difficulty.displayName,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = when {
                    isCompleted -> TextPrimary
                    isCurrent -> DifficultyColors.getColor(difficulty)
                    else -> TextTertiary
                }
            )

            Text(
                text = when {
                    isCompleted -> "$moveCount techniques learned ✓"
                    isCurrent -> "$moveCount techniques to learn"
                    else -> "Complete previous belts to unlock"
                },
                style = MaterialTheme.typography.bodyMedium,
                color = when {
                    isCompleted -> SuccessGreen
                    isCurrent -> TextSecondary
                    else -> TextTertiary
                }
            )
        }

        // Belt color indicator
        Box(
            modifier = Modifier
                .size(48.dp, 8.dp)
                .background(
                    color = DifficultyColors.getColor(difficulty).copy(
                        alpha = if (isLocked) 0.3f else 1f
                    ),
                    shape = FightingShapes.small
                )
        )
    }
}

@Composable
private fun MoveListItem(
    move: Move,
    onClick: () -> Unit,
    isLocked: Boolean = false,
    isCompleted: Boolean = false
) {
    // Modern list item - minimal card with subtle styling
    Card(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.medium, vertical = Spacing.extraSmall),
        colors = CardDefaults.cardColors(
            containerColor = when {
                isCompleted -> SuccessGreen.copy(alpha = 0.15f)
                isLocked -> FightDarkElevated
                else -> FightDarkCard
            },
            contentColor = if (isLocked) TextTertiary else TextPrimary
        ),
        shape = FightingShapes.medium,
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp), // Flat design
        enabled = !isLocked
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.medium),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(Spacing.medium)
        ) {
            // Move Image with optional overlays
            Box {
                AsyncImage(
                    model = move.imageUrl,
                    contentDescription = move.title,
                    modifier = Modifier
                        .size(72.dp)
                        .clip(FightingShapes.medium)
                        .background(FightDarkElevated),
                    contentScale = ContentScale.Crop,
                    alpha = if (isLocked) 0.4f else 1f
                )

                // Completed checkmark overlay
                if (isCompleted) {
                    Box(
                        modifier = Modifier
                            .size(72.dp)
                            .background(
                                color = SuccessGreen.copy(alpha = 0.7f),
                                shape = FightingShapes.medium
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = "Completed",
                            tint = Color.White,
                            modifier = Modifier.size(32.dp)
                        )
                    }
                }

                // Lock overlay for locked moves
                if (isLocked && !isCompleted || !move.isAvailable) {
                    Box(
                        modifier = Modifier
                            .size(72.dp)
                            .background(
                                color = FightDarkBg.copy(alpha = 0.7f),
                                shape = FightingShapes.medium
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Lock,
                            contentDescription = "Locked",
                            tint = TextTertiary,
                            modifier = Modifier.size(32.dp)
                        )
                    }
                }
            }

            // Move Info
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = move.title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = when {
                        isCompleted -> SuccessGreen
                        isLocked -> TextTertiary
                        else -> TextPrimary
                    },
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                Spacer(modifier = Modifier.height(Spacing.extraSmall))

                Text(
                    text = when {
                        isCompleted -> "✓ Learned"
                        isLocked -> "Complete previous belts to unlock"
                        else -> move.description
                    },
                    style = MaterialTheme.typography.bodyMedium,
                    color = when {
                        isCompleted -> SuccessGreen
                        isLocked -> TextTertiary
                        else -> TextSecondary
                    },
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )

                Spacer(modifier = Modifier.height(Spacing.small))

                DifficultyChip(
                    difficulty = move.difficulty,
                    alpha = if (isLocked) 0.5f else 1f
                )
            }

            // Status indicator icon
            Icon(
                imageVector = when {
                    isCompleted -> Icons.Default.CheckCircle
                    isLocked -> Icons.Default.Lock
                    else -> Icons.Default.ChevronRight
                },
                contentDescription = null,
                tint = when {
                    isCompleted -> SuccessGreen
                    isLocked -> TextTertiary
                    else -> TextTertiary
                },
                modifier = Modifier.size(24.dp)
            )
        }
    }
}

@Composable
private fun DifficultyChip(difficulty: MoveDifficulty, alpha: Float = 1f) {
    FightCompactCard(
        text = difficulty.displayName.uppercase(),
        backgroundColor = DifficultyColors.getBackgroundColor(difficulty).copy(alpha = alpha),
        textColor = DifficultyColors.getTextColor(difficulty).copy(alpha = alpha),
        borderColor = DifficultyColors.getBorderColor(difficulty).copy(alpha = alpha)
    )
}

