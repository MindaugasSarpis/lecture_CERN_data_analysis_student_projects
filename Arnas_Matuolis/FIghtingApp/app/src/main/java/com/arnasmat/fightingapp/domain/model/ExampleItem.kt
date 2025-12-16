package com.arnasmat.fightingapp.domain.model

/**
 * Domain model for example data
 * Separate from DTO to maintain clean architecture
 * This is what the app will use internally
 */
data class ExampleItem(
    val id: Int,
    val title: String,
    val description: String
)

