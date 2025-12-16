package com.arnasmat.fightingapp.ui.theme

import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import com.arnasmat.fightingapp.domain.model.MoveDifficulty

/**
 * DESIGN SYSTEM - DIFFICULTY COLORS
 * Centralized color definitions for belt-based move difficulty levels
 */

object DifficultyColors {
    @Composable
    fun getColor(difficulty: MoveDifficulty): Color {
        return when (difficulty) {
            MoveDifficulty.WHITE_BELT -> Color(0xFFFFFFFF)      // Pure white
            MoveDifficulty.YELLOW_BELT -> Color(0xFFFFD700)     // Gold/Yellow
            MoveDifficulty.ORANGE_BELT -> FightOrange            // Orange
            MoveDifficulty.GREEN_BELT -> SuccessGreen            // Green
            MoveDifficulty.BLUE_BELT -> ElectricBlue             // Electric Blue
            MoveDifficulty.PURPLE_BELT -> Color(0xFF9370DB)      // Medium Purple
            MoveDifficulty.BROWN_BELT -> Color(0xFFA0826D)       // Lighter Brown (visible)
            MoveDifficulty.BLACK_BELT -> Color(0xFFE8E8E8)       // Light Gray (for visibility on dark bg)
        }
    }

    @Composable
    fun getBackgroundColor(difficulty: MoveDifficulty): Color {
        return getColor(difficulty).copy(alpha = 0.15f)
    }

    @Composable
    fun getBorderColor(difficulty: MoveDifficulty): Color {
        return getColor(difficulty).copy(alpha = 0.5f)
    }

    @Composable
    fun getTextColor(difficulty: MoveDifficulty): Color {
        // White and Black belts need dark text for visibility on light backgrounds
        return when (difficulty) {
            MoveDifficulty.WHITE_BELT -> Color(0xFF1A1A1A)      // Dark gray/black
            MoveDifficulty.BLACK_BELT -> Color(0xFF1A1A1A)      // Dark gray/black
            else -> getColor(difficulty)                        // Use main color for other belts
        }
    }
}

