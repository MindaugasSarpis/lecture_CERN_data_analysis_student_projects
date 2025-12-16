package com.arnasmat.fightingapp.domain.model

import android.net.Uri

/**
 * Domain model for recorded video
 */
data class RecordedVideo(
    val uri: Uri,
    val fileName: String,
    val filePath: String,
    val durationMs: Long,
    val sizeBytes: Long,
    val timestamp: Long = System.currentTimeMillis(),
    val exerciseId: Int? = null,  // ID of the exercise practiced (for learning context)
    val exerciseName: String? = null  // Name of the exercise for display
)

