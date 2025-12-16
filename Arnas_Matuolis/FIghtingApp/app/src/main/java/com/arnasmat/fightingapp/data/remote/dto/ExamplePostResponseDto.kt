package com.arnasmat.fightingapp.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Example DTO for POST request response
 * Replace with actual API response structure when backend is ready
 */
data class ExamplePostResponseDto(
    @SerializedName("id")
    val id: Int,
    @SerializedName("title")
    val title: String,
    @SerializedName("description")
    val description: String,
    @SerializedName("success")
    val success: Boolean,
    @SerializedName("message")
    val message: String?
)

