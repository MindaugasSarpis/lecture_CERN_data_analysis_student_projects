package com.arnasmat.fightingapp.data.repository

import android.content.Context
import android.provider.MediaStore
import android.util.Log
import com.arnasmat.fightingapp.data.local.VideoHistoryDataSource
import com.arnasmat.fightingapp.data.remote.api.FightingApi
import com.arnasmat.fightingapp.domain.model.LandmarkAccuracy
import com.arnasmat.fightingapp.domain.model.RecordedVideo
import com.arnasmat.fightingapp.domain.model.VideoAnalysis
import com.arnasmat.fightingapp.domain.repository.VideoRepository
import com.arnasmat.fightingapp.domain.util.Resource
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.HttpException
import java.io.File
import java.io.IOException
import javax.inject.Inject

/**
 * Implementation of VideoRepository
 * Handles video upload to backend and local history management
 */
class VideoRepositoryImpl @Inject constructor(
    private val api: FightingApi,
    @param:ApplicationContext private val context: Context,
    private val videoHistoryDataSource: VideoHistoryDataSource
) : VideoRepository {

    companion object {
        private const val TAG = "VideoRepository"
    }

    override suspend fun uploadVideo(
        video: RecordedVideo,
        title: String
    ): Flow<Resource<VideoAnalysis>> = flow {
        emit(Resource.Loading())

        try {
            Log.d(TAG, "Starting video analysis - Title: $title")

            // Get file from URI using ContentResolver
            val videoFile = getFileFromUri(video)

            if (videoFile == null || !videoFile.exists()) {
                Log.e(TAG, "Video file not found or could not be accessed")
                emit(Resource.Error("Video file not found or could not be accessed"))
                return@flow
            }

            if (!videoFile.canRead()) {
                Log.e(TAG, "Video file cannot be read - permission denied")
                emit(Resource.Error("Cannot read video file - permission denied"))
                return@flow
            }

            Log.d(TAG, "Video file found: ${videoFile.absolutePath}, size: ${videoFile.length()} bytes")

            // Ensure filename has .mp4 extension
            val fileName = if (video.fileName.endsWith(".mp4", ignoreCase = true)) {
                video.fileName
            } else {
                "${video.fileName}.mp4"
            }

            Log.d(TAG, "Preparing analysis - Original filename: ${video.fileName}, Final filename: $fileName")

            // Create request body for file with video/mp4 content type
            val requestFile = videoFile.asRequestBody("video/mp4".toMediaTypeOrNull())
            val videoPart = MultipartBody.Part.createFormData(
                "file",
                fileName,
                requestFile
            )

            Log.d(TAG, "Analyzing video - FileName: $fileName, ContentType: video/mp4, FileSize: ${videoFile.length()} bytes")

            Log.d(TAG, "Sending video to API for analysis...")
            // Analyze video - this will wait for complete analysis
            val response = api.analyzeVideo(videoPart)

            // Clean up temporary file
            if (videoFile.absolutePath.contains("cache")) {
                videoFile.delete()
            }

            if (response.isSuccessful && response.body() != null) {
                val result = response.body()!!
                Log.d(TAG, "Analysis successful - Score: ${result.overallScore}%")

                // Convert API response to domain model
                val analysis = VideoAnalysis(
                    moveId = video.exerciseId ?: 0,
                    moveName = video.exerciseName ?: "Unknown Move",
                    correctAspects = emptyList(), // Will be populated from landmark data
                    incorrectAspects = emptyList(), // Will be populated from landmark data
                    overallScore = result.overallScore.toInt(),
                    streamVideoUrl = result.streamVideo,
                    chartUrl = result.chart,
                    perLandmarkAccuracy = result.perLandmarkAccuracy.mapValues { (_, dto) ->
                        LandmarkAccuracy(
                            correctFrames = dto.correctFrames,
                            totalFrames = dto.totalFrames,
                            accuracyPercentage = dto.accuracyPercentage
                        )
                    }
                )

                emit(Resource.Success(analysis))
            } else {
                val errorBody = response.errorBody()?.string()
                Log.e(TAG, "Analysis failed - Code: ${response.code()}, Error: $errorBody")
                emit(Resource.Error("Analysis failed: ${response.code()} - $errorBody"))
            }
        } catch (e: HttpException) {
            Log.e(TAG, "HTTP exception during analysis", e)
            emit(Resource.Error("Network error: ${e.code()} - ${e.message()}"))
        } catch (e: IOException) {
            Log.e(TAG, "IO exception during analysis", e)
            emit(Resource.Error("Network connection failed: ${e.message}. Please check your internet connection."))
        } catch (e: Exception) {
            Log.e(TAG, "Unexpected exception during analysis", e)
            emit(Resource.Error("Analysis failed: ${e.message}"))
        }
    }

    override suspend fun uploadVideoWithExercise(
        video: RecordedVideo,
        exerciseId: Int,
        title: String
    ): Flow<Resource<VideoAnalysis>> = flow {
        emit(Resource.Loading())

        try {
            Log.d(TAG, "Starting video analysis with exercise - ExerciseId: $exerciseId, Title: $title")

            // Get file from URI using ContentResolver
            val videoFile = getFileFromUri(video)

            if (videoFile == null || !videoFile.exists()) {
                Log.e(TAG, "Video file not found or could not be accessed")
                emit(Resource.Error("Video file not found or could not be accessed"))
                return@flow
            }

            if (!videoFile.canRead()) {
                Log.e(TAG, "Video file cannot be read - permission denied")
                emit(Resource.Error("Cannot read video file - permission denied"))
                return@flow
            }

            Log.d(TAG, "Video file found: ${videoFile.absolutePath}, size: ${videoFile.length()} bytes")

            // Ensure filename has .mp4 extension
            val fileName = if (video.fileName.endsWith(".mp4", ignoreCase = true)) {
                video.fileName
            } else {
                "${video.fileName}.mp4"
            }

            Log.d(TAG, "Preparing analysis with exercise - Original filename: ${video.fileName}, Final filename: $fileName, ExerciseId: $exerciseId")

            // Create request body for file with video/mp4 content type
            val requestFile = videoFile.asRequestBody("video/mp4".toMediaTypeOrNull())
            val videoPart = MultipartBody.Part.createFormData(
                "file",
                fileName,
                requestFile
            )

            Log.d(TAG, "Analyzing video with exercise - FileName: $fileName, ContentType: video/mp4, ExerciseId: $exerciseId, FileSize: ${videoFile.length()} bytes")

            Log.d(TAG, "Sending video to API for analysis with exercise ID: $exerciseId")
            // Analyze video - this will wait for complete analysis
            val response = api.analyzeVideo(videoPart)

            // Clean up temporary file
            if (videoFile.absolutePath.contains("cache")) {
                videoFile.delete()
            }

            if (response.isSuccessful && response.body() != null) {
                val result = response.body()!!
                Log.d(TAG, "Analysis successful - Score: ${result.overallScore}%")

                // Convert API response to domain model
                val analysis = VideoAnalysis(
                    moveId = exerciseId,
                    moveName = video.exerciseName ?: "Unknown Move",
                    correctAspects = emptyList(), // Will be populated from landmark data
                    incorrectAspects = emptyList(), // Will be populated from landmark data
                    overallScore = result.overallScore.toInt(),
                    streamVideoUrl = result.streamVideo,
                    chartUrl = result.chart,
                    perLandmarkAccuracy = result.perLandmarkAccuracy.mapValues { (_, dto) ->
                        LandmarkAccuracy(
                            correctFrames = dto.correctFrames,
                            totalFrames = dto.totalFrames,
                            accuracyPercentage = dto.accuracyPercentage
                        )
                    }
                )

                emit(Resource.Success(analysis))
            } else {
                val errorBody = response.errorBody()?.string()
                Log.e(TAG, "Analysis failed - Code: ${response.code()}, Error: $errorBody")
                emit(Resource.Error("Analysis failed: ${response.code()} - $errorBody"))
            }
        } catch (e: HttpException) {
            Log.e(TAG, "HTTP exception during analysis with exercise", e)
            emit(Resource.Error("Network error: ${e.code()} - ${e.message()}"))
        } catch (e: IOException) {
            Log.e(TAG, "IO exception during analysis with exercise", e)
            emit(Resource.Error("Network connection failed: ${e.message}. Please check your internet connection."))
        } catch (e: Exception) {
            Log.e(TAG, "Unexpected exception during analysis with exercise", e)
            emit(Resource.Error("Analysis failed: ${e.message}"))
        }
    }

    override suspend fun saveVideoToHistory(video: RecordedVideo) {
        videoHistoryDataSource.saveVideo(video)
    }

    override fun getVideoHistory(): Flow<List<RecordedVideo>> {
        return videoHistoryDataSource.videos
    }


    override suspend fun deleteVideoFromHistory(video: RecordedVideo) {
        videoHistoryDataSource.deleteVideo(video)
    }

    override suspend fun renameVideo(video: RecordedVideo, newFileName: String) {
        // Ensure the new filename has .mp4 extension
        val sanitizedFileName = if (newFileName.endsWith(".mp4", ignoreCase = true)) {
            newFileName
        } else {
            "$newFileName.mp4"
        }

        val updatedVideo = video.copy(fileName = sanitizedFileName)
        videoHistoryDataSource.updateVideo(video, updatedVideo)
    }

    override suspend fun getVideoAnalysis(moveId: Int): Flow<Resource<VideoAnalysis>> = flow {
        emit(Resource.Loading())

        try {
            // Simulate network delay
            kotlinx.coroutines.delay(500)

            // Return mock analysis data based on moveId
            val analysis = getMockVideoAnalysis(moveId)
            emit(Resource.Success(analysis))
        } catch (e: Exception) {
            Log.e(TAG, "Error getting video analysis", e)
            emit(Resource.Error("Failed to get video analysis: ${e.localizedMessage}"))
        }
    }

    /**
     * Mock video analysis data
     * This simulates the backend analysis results
     */
    private fun getMockVideoAnalysis(moveId: Int): VideoAnalysis {
        return when (moveId) {
            2 -> { // Chūdan Tsuki
                VideoAnalysis(
                    moveId = 2,
                    moveName = "Chūdan Tsuki (中段突き)",
                    correctAspects = listOf(
                        "Proper hikite (pulling hand) positioning maintained throughout execution",
                        "Correct seiken (fore-fist) formation with thumb placement",
                        "Good koshi no kaiten (hip rotation) initiated from the core"
                    ),
                    incorrectAspects = listOf(
                        "Tsuki height inconsistent - maintain chudan (middle level) targeting solar plexus",
                        "Seiken rotation (kime) incomplete - fist should finish palm down at full extension",
                        "Elbow trajectory too wide - keep elbow closer to body for proper centerline striking"
                    ),
                    overallScore = 54
                )
            }
            1 -> { // Zenkutsu-Dachi
                VideoAnalysis(
                    moveId = 1,
                    moveName = "Zenkutsu-Dachi (前屈立ち)",
                    correctAspects = listOf(
                        "60/40 weight distribution correctly maintained",
                        "Front knee aligned over toes preventing inward collapse",
                        "Back leg demonstrating proper tension (koshi)"
                    ),
                    incorrectAspects = listOf(
                        "Stance width too narrow - shoulder-width separation required",
                        "Back foot angle exceeds 45 degrees - adjust for stability"
                    ),
                    overallScore = 54
                )
            }
            else -> {
                VideoAnalysis(
                    moveId = moveId,
                    moveName = "Unknown Move",
                    correctAspects = listOf(
                        "Good effort",
                        "Proper form maintained"
                    ),
                    incorrectAspects = listOf(
                        "Needs more practice",
                        "Focus on technique"
                    ),
                    overallScore = 54
                )
            }
        }
    }

    /**
     * Converts URI to File for upload
     * Creates a temporary file from the MediaStore URI
     */
    private fun getFileFromUri(video: RecordedVideo): File? {
        return try {
            // Try to query MediaStore for the actual file path
            val projection = arrayOf(MediaStore.Video.Media.DATA)
            context.contentResolver.query(
                video.uri,
                projection,
                null,
                null,
                null
            )?.use { cursor ->
                val columnIndex = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DATA)
                cursor.moveToFirst()
                val filePath = cursor.getString(columnIndex)
                if (filePath != null) {
                    val file = File(filePath)
                    if (file.exists()) {
                        return file
                    }
                }
            }

            // If MediaStore query doesn't work, copy to cache
            val inputStream = context.contentResolver.openInputStream(video.uri)
            inputStream?.use { input ->
                // Ensure filename has .mp4 extension for temp file
                val tempFileName = if (video.fileName.endsWith(".mp4", ignoreCase = true)) {
                    video.fileName
                } else {
                    "${video.fileName}.mp4"
                }
                val tempFile = File(context.cacheDir, tempFileName)
                tempFile.outputStream().use { output ->
                    input.copyTo(output)
                }
                tempFile
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
