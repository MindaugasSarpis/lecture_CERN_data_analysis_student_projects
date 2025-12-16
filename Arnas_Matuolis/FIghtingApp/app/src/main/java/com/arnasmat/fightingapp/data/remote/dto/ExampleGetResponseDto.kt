package com.arnasmat.fightingapp.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Example DTO for GET request response
 * Replace with actual API response structure when backend is ready
 */
data class ExampleGetResponseDto(
    @SerializedName("id")
    val id: Int,
    @SerializedName("title")
    val title: String,
    @SerializedName("description")
    val description: String?,
    @SerializedName("created_at")
    val createdAt: String?
)

