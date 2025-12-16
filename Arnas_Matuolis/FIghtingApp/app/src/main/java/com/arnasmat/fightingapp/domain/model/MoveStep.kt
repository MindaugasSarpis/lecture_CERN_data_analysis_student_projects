package com.arnasmat.fightingapp.domain.model

/**
 * Domain model for a single step in learning a move
 * Represents individual instruction steps with video guidance
 */
data class MoveStep(
    val id: Int,
    val stepNumber: Int,
    val title: String,
    val description: String,
    val videoUrl: String,
    val tips: List<String> = emptyList(),
    val imageUrl: String = ""
)

/**
 * Extension function to get the next step number
 */
fun MoveStep.hasNextStep(totalSteps: Int): Boolean = stepNumber < totalSteps

/**
 * Extension function to check if this is the last step
 */
fun MoveStep.isLastStep(totalSteps: Int): Boolean = stepNumber == totalSteps

/**
 * Extension function to check if this is the first step
 */
fun MoveStep.isFirstStep(): Boolean = stepNumber == 1

