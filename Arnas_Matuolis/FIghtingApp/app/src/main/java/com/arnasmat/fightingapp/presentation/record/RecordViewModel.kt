package com.arnasmat.fightingapp.presentation.record

import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.arnasmat.fightingapp.domain.model.RecordedVideo
import com.arnasmat.fightingapp.domain.model.VideoAnalysis
import com.arnasmat.fightingapp.domain.repository.MoveRepository
import com.arnasmat.fightingapp.domain.repository.VideoRepository
import com.arnasmat.fightingapp.domain.util.NetworkConnectivityChecker
import com.arnasmat.fightingapp.domain.util.Resource
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for Record Screen
 * Handles video recording and upload
 */
@HiltViewModel
class RecordViewModel @Inject constructor(
    private val videoRepository: VideoRepository,
    private val moveRepository: MoveRepository,
    private val networkChecker: NetworkConnectivityChecker
) : ViewModel() {

    private val _state = MutableStateFlow(RecordState())
    val state = _state.asStateFlow()

    /**
     * Set exercise ID for learning context and load exercise name
     */
    fun setExerciseId(exerciseId: Int?) {
        _state.update { it.copy(exerciseId = exerciseId) }

        // Load exercise name for display
        if (exerciseId != null) {
            loadExerciseName(exerciseId)
        }
    }

    /**
     * Load exercise name from repository
     */
    private fun loadExerciseName(exerciseId: Int) {
        viewModelScope.launch {
            moveRepository.getMoveDetail(exerciseId).onEach { result ->
                when (result) {
                    is Resource.Success -> {
                        _state.update { it.copy(exerciseName = result.data?.title) }
                    }
                    is Resource.Error -> {
                        // Silently fail - exercise name is optional for display
                    }
                    is Resource.Loading -> {
                        // No loading state needed
                    }
                }
            }.launchIn(this)
        }
    }

    /**
     * Update recording state
     */
    fun setRecording(isRecording: Boolean) {
        _state.update { it.copy(isRecording = isRecording) }
    }

    /**
     * Toggle sound-activated recording mode
     */
    fun toggleSoundActivatedMode() {
        _state.update { it.copy(soundActivatedMode = !it.soundActivatedMode) }
    }

    /**
     * Update sound listening state
     */
    fun setListeningForSound(isListening: Boolean) {
        _state.update { it.copy(isListeningForSound = isListening) }
    }

    /**
     * Update current sound level
     */
    fun updateSoundLevel(level: Double) {
        _state.update { it.copy(currentSoundLevel = level) }
    }

    /**
     * Handle video recorded
     */
    fun onVideoRecorded(videoUri: Uri, filePath: String, durationMs: Long, sizeBytes: Long) {
        // Ensure filename has .mp4 extension
        val rawFileName = videoUri.lastPathSegment ?: "video"
        val fileName = if (rawFileName.endsWith(".mp4", ignoreCase = true)) {
            rawFileName
        } else {
            "$rawFileName.mp4"
        }

        val recordedVideo = RecordedVideo(
            uri = videoUri,
            fileName = fileName,
            filePath = filePath,
            durationMs = durationMs,
            sizeBytes = sizeBytes,
            exerciseId = _state.value.exerciseId,
            exerciseName = _state.value.exerciseName
        )

        viewModelScope.launch {
            videoRepository.saveVideoToHistory(recordedVideo)
        }

        _state.update {
            it.copy(
                recordedVideo = recordedVideo,
                isRecording = false,
                error = null
            )
        }
    }

    /**
     * Handle video selected from gallery
     */
    fun onVideoSelectedFromGallery(videoUri: Uri) {
        // Create a RecordedVideo object from selected video
        val rawFileName = videoUri.lastPathSegment ?: "selected_video"
        val fileName = if (rawFileName.endsWith(".mp4", ignoreCase = true)) {
            rawFileName
        } else {
            "$rawFileName.mp4"
        }

        val recordedVideo = RecordedVideo(
            uri = videoUri,
            fileName = fileName,
            filePath = videoUri.toString(),
            durationMs = 0L, // Will be calculated by repository if needed
            sizeBytes = 0L, // Will be calculated by repository if needed
            exerciseId = _state.value.exerciseId,
            exerciseName = _state.value.exerciseName
        )

        viewModelScope.launch {
            videoRepository.saveVideoToHistory(recordedVideo)
        }

        _state.update {
            it.copy(
                recordedVideo = recordedVideo,
                isRecording = false,
                error = null
            )
        }
    }

    /**
     * Upload recorded video to backend
     */
    fun uploadVideo(title: String = "Fighting Training Video") {
        val video = _state.value.recordedVideo
        if (video == null) {
            _state.update { it.copy(error = "No video to upload") }
            return
        }

        val exerciseId = _state.value.exerciseId

        // Check network connectivity
        if (!networkChecker.isNetworkAvailable()) {
            _state.update { it.copy(error = "No internet connection. Please check your network.") }
            return
        }

        viewModelScope.launch {
            // Use different upload method based on whether we have exercise context
            val uploadFlow = if (exerciseId != null) {
                videoRepository.uploadVideoWithExercise(video, exerciseId, title)
            } else {
                videoRepository.uploadVideo(video, title)
            }

            uploadFlow.onEach { result ->
                when (result) {
                    is Resource.Loading -> {
                        _state.update { it.copy(isUploading = true, error = null) }
                    }
                    is Resource.Success -> {
                        val analysis = result.data
                        _state.update {
                            it.copy(
                                isUploading = false,
                                uploadSuccess = true,
                                videoAnalysis = analysis,
                                analyzedVideoUrl = analysis?.streamVideoUrl,
                                analyzedChartUrl = analysis?.chartUrl,
                                error = null
                            )
                        }
                    }
                    is Resource.Error -> {
                        _state.update {
                            it.copy(
                                isUploading = false,
                                uploadSuccess = false,
                                error = result.message ?: "Upload failed"
                            )
                        }
                    }
                }
            }.launchIn(this)
        }
    }

    /**
     * Delete recorded video and reset state
     */
    fun deleteVideo() {
        _state.update {
            it.copy(
                recordedVideo = null,
                uploadSuccess = false,
                videoAnalysis = null,
                analyzedVideoUrl = null,
                analyzedChartUrl = null,
                error = null
            )
        }
    }

    /**
     * Rename the recorded video
     */
    fun renameVideo(newFileName: String) {
        val video = _state.value.recordedVideo
        if (video == null) {
            _state.update { it.copy(error = "No video to rename") }
            return
        }

        viewModelScope.launch {
            videoRepository.renameVideo(video, newFileName)
            // Update local state with renamed video
            val updatedVideo = video.copy(
                fileName = if (newFileName.endsWith(".mp4", ignoreCase = true)) {
                    newFileName
                } else {
                    "$newFileName.mp4"
                }
            )
            _state.update { it.copy(recordedVideo = updatedVideo) }
        }
    }

    /**
     * Clear error message
     */
    fun clearError() {
        _state.update { it.copy(error = null) }
    }

    /**
     * Handle recording error
     */
    fun onRecordingError(error: String) {
        _state.update {
            it.copy(
                isRecording = false,
                error = error
            )
        }
    }
}

/**
 * UI State for Record Screen
 */
data class RecordState(
    val isRecording: Boolean = false,
    val recordedVideo: RecordedVideo? = null,
    val isUploading: Boolean = false,
    val uploadSuccess: Boolean = false,
    val videoAnalysis: VideoAnalysis? = null,  // Full analysis results from backend
    val analyzedVideoUrl: String? = null,  // URL to stream analyzed video
    val analyzedChartUrl: String? = null,  // URL to download chart image
    val error: String? = null,
    val exerciseId: Int? = null,  // ID of the exercise being practiced (for learning context)
    val exerciseName: String? = null,  // Name of the exercise for display
    val soundActivatedMode: Boolean = false,  // Sound-activated recording mode
    val isListeningForSound: Boolean = false,  // Currently listening for loud sound
    val currentSoundLevel: Double = 0.0  // Current sound level in dB
)

