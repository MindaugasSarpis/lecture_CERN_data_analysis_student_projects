package com.arnasmat.fightingapp.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Example DTO for POST request body
 * Replace with actual API request structure when backend is ready
 */
data class ExamplePostRequestDto(
    @SerializedName("title")
    val title: String,
    @SerializedName("description")
    val description: String
)

