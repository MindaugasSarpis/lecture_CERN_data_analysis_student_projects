package com.arnasmat.fightingapp.domain.repository

import com.arnasmat.fightingapp.domain.model.RecordedVideo
import com.arnasmat.fightingapp.domain.model.VideoAnalysis
import com.arnasmat.fightingapp.domain.util.Resource
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for video operations
 */
interface VideoRepository {

    /**
     * Upload recorded video to backend for analysis
     * @param video The recorded video to upload
     * @param title Optional title/description
     * @return Flow with analysis results
     */
    suspend fun uploadVideo(video: RecordedVideo, title: String): Flow<Resource<VideoAnalysis>>

    /**
     * Upload recorded video with exercise ID for learning flow
     * @param video The recorded video to upload
     * @param exerciseId The ID of the exercise/move being practiced
     * @param title Optional title/description
     * @return Flow with analysis results
     */
    suspend fun uploadVideoWithExercise(
        video: RecordedVideo,
        exerciseId: Int,
        title: String
    ): Flow<Resource<VideoAnalysis>>

    /**
     * Save video to local history
     * @param video The recorded video to save
     */
    suspend fun saveVideoToHistory(video: RecordedVideo)

    /**
     * Get all saved videos from history
     * @return Flow of list of recorded videos
     */
    fun getVideoHistory(): Flow<List<RecordedVideo>>

    /**
     * Delete video from history
     * @param video The video to delete
     */
    suspend fun deleteVideoFromHistory(video: RecordedVideo)

    /**
     * Rename a video in history
     * @param video The video to rename
     * @param newFileName The new file name
     */
    suspend fun renameVideo(video: RecordedVideo, newFileName: String)

    /**
     * Get video analysis results for a specific move
     * @param moveId The ID of the move that was practiced
     * @return Flow with analysis results
     */
    suspend fun getVideoAnalysis(moveId: Int): Flow<Resource<VideoAnalysis>>
}

