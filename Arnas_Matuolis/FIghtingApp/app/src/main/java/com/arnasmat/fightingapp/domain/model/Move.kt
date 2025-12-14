package com.arnasmat.fightingapp.domain.model

/**
 * Domain model for a fighting move
 * Represents a move suggestion for learning
 */
data class Move(
    val id: Int,
    val title: String,
    val description: String,
    val imageUrl: String,
    val difficulty: MoveDifficulty,
    val videoUrl: String,
    val isMarked: Boolean = false,
    val category: String? = null,
    val steps: List<MoveStep> = emptyList(),
    val isAvailable: Boolean = false,
)

/**
 * Belt-based difficulty levels for karate moves
 * Each move is categorized by the belt level at which it should be learned
 */
enum class MoveDifficulty(val displayName: String, val belt: Belt) {
    WHITE_BELT("White Belt", Belt.WHITE),
    YELLOW_BELT("Yellow Belt", Belt.YELLOW),
    ORANGE_BELT("Orange Belt", Belt.ORANGE),
    GREEN_BELT("Green Belt", Belt.GREEN),
    BLUE_BELT("Blue Belt", Belt.BLUE),
    PURPLE_BELT("Purple Belt", Belt.PURPLE),
    BROWN_BELT("Brown Belt", Belt.BROWN),
    BLACK_BELT("Black Belt", Belt.BLACK);

    companion object {
        fun fromBelt(belt: Belt): MoveDifficulty {
            return when (belt) {
                Belt.WHITE -> WHITE_BELT
                Belt.YELLOW -> YELLOW_BELT
                Belt.ORANGE -> ORANGE_BELT
                Belt.GREEN -> GREEN_BELT
                Belt.BLUE -> BLUE_BELT
                Belt.PURPLE -> PURPLE_BELT
                Belt.BROWN -> BROWN_BELT
                Belt.BLACK -> BLACK_BELT
            }
        }
    }
}


