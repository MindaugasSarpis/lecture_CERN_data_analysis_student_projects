package com.arnasmat.fightingapp.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for Move GET response
 * Maps to backend JSON structure
 */
data class MoveDto(
    @SerializedName("id") val id: Int,
    @SerializedName("title") val title: String,
    @SerializedName("description") val description: String,
    @SerializedName("image_url") val imageUrl: String?,
    @SerializedName("difficulty") val difficulty: String?,
    @SerializedName("video_url") val videoUrl: String?,
    @SerializedName("is_marked") val isMarked: Boolean?,
    @SerializedName("category") val category: String?
)

/**
 * DTO for marking/unmarking a move
 */
data class MarkMoveRequestDto(
    @SerializedName("is_marked") val isMarked: Boolean
)

/**
 * DTO for starting to learn a move
 */
data class StartLearningRequestDto(
    @SerializedName("move_id") val moveId: Int,
    @SerializedName("started_at") val startedAt: Long = System.currentTimeMillis()
)

/**
 * DTO for generic success response
 */
data class SuccessResponseDto(
    @SerializedName("success") val success: Boolean,
    @SerializedName("message") val message: String?
)

