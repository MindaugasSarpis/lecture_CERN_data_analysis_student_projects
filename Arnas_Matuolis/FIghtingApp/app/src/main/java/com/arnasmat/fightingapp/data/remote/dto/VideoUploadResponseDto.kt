package com.arnasmat.fightingapp.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Response DTO for video upload
 */
data class VideoUploadResponseDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("url")
    val url: String,
    @SerializedName("analysis_status")
    val analysisStatus: String,
    @SerializedName("message")
    val message: String?,
    @SerializedName("uploaded_at")
    val uploadedAt: String?
)

