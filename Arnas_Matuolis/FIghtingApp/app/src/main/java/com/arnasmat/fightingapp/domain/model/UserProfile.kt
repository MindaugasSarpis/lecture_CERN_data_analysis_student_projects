package com.arnasmat.fightingapp.domain.model

/**
 * Domain model representing a user profile
 * This is the business logic representation of the user data
 */
data class UserProfile(
    val id: String,
    val username: String,
    val profileImageUrl: String?,
    val belt: Belt,
    val streakDays: Int,
)

/**
 * Represents the user's belt/rank in the martial arts system
 */
enum class Belt(
    val displayName: String,
    val colorHex: String
) {
    WHITE("White Belt", "#FFFFFF"),
    YELLOW("Yellow Belt", "#FFD700"),
    ORANGE("Orange Belt", "#FF8C00"),
    GREEN("Green Belt", "#32CD32"),
    BLUE("Blue Belt", "#4169E1"),
    PURPLE("Purple Belt", "#9370DB"),
    BROWN("Brown Belt", "#8B4513"),
    BLACK("Black Belt", "#000000");

    companion object {
        fun fromString(value: String): Belt {
            return entries.find { it.name.equals(value, ignoreCase = true) } ?: WHITE
        }
    }
}

