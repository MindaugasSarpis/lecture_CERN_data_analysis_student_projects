package com.arnasmat.fightingapp.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for user profile response from the API
 * This represents the JSON structure from the backend
 */
data class UserProfileDto(
    @SerializedName("id") val id: String,
    @SerializedName("username") val username: String,
    @SerializedName("profile_image_url") val profileImageUrl: String?,
    @SerializedName("belt") val belt: String,
    @SerializedName("streak_days") val streakDays: Int,
)

