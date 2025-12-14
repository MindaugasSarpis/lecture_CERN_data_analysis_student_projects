package com.arnasmat.fightingapp.presentation.video

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.arnasmat.fightingapp.domain.model.VideoAnalysis
import com.arnasmat.fightingapp.domain.repository.VideoRepository
import com.arnasmat.fightingapp.domain.util.Resource
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for analyzed video playback and statistics display
 */
@HiltViewModel
class AnalyzedVideoViewModel @Inject constructor(
    private val videoRepository: VideoRepository
) : ViewModel() {

    private val _state = MutableStateFlow(AnalyzedVideoState())
    val state: StateFlow<AnalyzedVideoState> = _state.asStateFlow()

    /**
     * Load video analysis results for a specific move
     */
    fun loadAnalysis(moveId: Int) {
        viewModelScope.launch {
            videoRepository.getVideoAnalysis(moveId).collect { result ->
                when (result) {
                    is Resource.Loading -> {
                        _state.value = _state.value.copy(
                            isLoading = true,
                            error = null
                        )
                    }
                    is Resource.Success -> {
                        _state.value = _state.value.copy(
                            isLoading = false,
                            analysis = result.data,
                            error = null
                        )
                    }
                    is Resource.Error -> {
                        _state.value = _state.value.copy(
                            isLoading = false,
                            error = result.message ?: "Unknown error occurred"
                        )
                    }
                }
            }
        }
    }
}

/**
 * State for analyzed video screen
 */
data class AnalyzedVideoState(
    val isLoading: Boolean = false,
    val analysis: VideoAnalysis? = null,
    val error: String? = null
)

