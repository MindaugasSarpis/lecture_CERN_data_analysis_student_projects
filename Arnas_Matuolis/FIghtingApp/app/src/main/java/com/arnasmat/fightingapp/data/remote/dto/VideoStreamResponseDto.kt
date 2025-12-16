package com.arnasmat.fightingapp.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Response DTO for video streaming
 */
data class VideoStreamResponseDto(
    @SerializedName("success")
    val success: Boolean,
    @SerializedName("data")
    val data: VideoStreamData?
)

data class VideoStreamData(
    @SerializedName("streamingUrl")
    val streamingUrl: String,
    @SerializedName("expiresAt")
    val expiresAt: String,
    @SerializedName("fileName")
    val fileName: String
)

