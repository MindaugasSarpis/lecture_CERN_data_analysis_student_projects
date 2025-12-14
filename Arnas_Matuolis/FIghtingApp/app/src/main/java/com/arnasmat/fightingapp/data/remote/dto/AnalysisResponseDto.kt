package com.arnasmat.fightingapp.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Response DTO for video pose analysis
 * Based on OpenAPI spec for /analyze endpoint
 */
data class AnalysisResponseDto(
    @SerializedName("overall_score")
    val overallScore: Double,

    @SerializedName("frames_analyzed")
    val framesAnalyzed: Int,

    @SerializedName("reference_frames")
    val referenceFrames: Int,

    @SerializedName("per_landmark_accuracy")
    val perLandmarkAccuracy: Map<String, LandmarkAccuracyDto>,

    @SerializedName("analyzed_video")
    val analyzedVideo: String,

    @SerializedName("stream_video")
    val streamVideo: String,

    @SerializedName("chart")
    val chart: String
)

/**
 * Landmark accuracy statistics
 */
data class LandmarkAccuracyDto(
    @SerializedName("correct_frames")
    val correctFrames: Int,

    @SerializedName("total_frames")
    val totalFrames: Int,

    @SerializedName("accuracy_percentage")
    val accuracyPercentage: Double
)

