package com.arnasmat.fightingapp.domain.model

/**
 * Represents the analysis results from a recorded karate technique video
 */
data class VideoAnalysis(
    val moveId: Int,
    val moveName: String,
    val correctAspects: List<String>,
    val incorrectAspects: List<String>,
    val overallScore: Int? = null, // Optional overall score (0-100)
    val streamVideoUrl: String? = null, // URL to stream analyzed video
    val chartUrl: String? = null, // URL to download analysis chart
    val perLandmarkAccuracy: Map<String, LandmarkAccuracy>? = null // Per-landmark accuracy stats
)

/**
 * Accuracy statistics for individual body landmarks
 */
data class LandmarkAccuracy(
    val correctFrames: Int,
    val totalFrames: Int,
    val accuracyPercentage: Double
)


