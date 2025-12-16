package com.arnasmat.fightingapp.presentation.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.arnasmat.fightingapp.domain.model.RecordedVideo
import com.arnasmat.fightingapp.domain.repository.VideoRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for History Screen
 * Manages video history and playback
 */
@HiltViewModel
class HistoryViewModel @Inject constructor(
    private val videoRepository: VideoRepository
) : ViewModel() {

    private val _state = MutableStateFlow(HistoryState())
    val state = _state.asStateFlow()

    init {
        loadVideoHistory()
    }

    /**
     * Load all videos from history
     */
    private fun loadVideoHistory() {
        videoRepository.getVideoHistory().onEach { videos ->
            _state.update { it.copy(videos = videos) }
        }.launchIn(viewModelScope)
    }

    /**
     * Select a video for playback
     */
    fun selectVideo(video: RecordedVideo) {
        _state.update { it.copy(selectedVideo = video) }
    }

    /**
     * Clear selected video
     */
    fun clearSelectedVideo() {
        _state.update { it.copy(selectedVideo = null) }
    }

    /**
     * Delete video from history
     */
    fun deleteVideo(video: RecordedVideo) {
        viewModelScope.launch {
            videoRepository.deleteVideoFromHistory(video)
            // If the deleted video was selected, clear selection
            if (_state.value.selectedVideo == video) {
                clearSelectedVideo()
            }
        }
    }

    /**
     * Rename a video
     */
    fun renameVideo(video: RecordedVideo, newFileName: String) {
        viewModelScope.launch {
            videoRepository.renameVideo(video, newFileName)
            // Update selected video if it's the one being renamed
            if (_state.value.selectedVideo?.uri == video.uri) {
                val updatedVideo = video.copy(
                    fileName = if (newFileName.endsWith(".mp4", ignoreCase = true)) {
                        newFileName
                    } else {
                        "$newFileName.mp4"
                    }
                )
                _state.update { it.copy(selectedVideo = updatedVideo) }
            }
        }
    }
}

/**
 * UI State for History Screen
 */
data class HistoryState(
    val videos: List<RecordedVideo> = emptyList(),
    val selectedVideo: RecordedVideo? = null
)

