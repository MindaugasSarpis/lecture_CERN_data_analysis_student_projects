package com.arnasmat.fightingapp.presentation.learn

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.arnasmat.fightingapp.domain.model.Move
import com.arnasmat.fightingapp.domain.repository.MoveRepository
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
 * ViewModel for Move Detail Screen
 * Manages detailed view of a single move
 */
@HiltViewModel
class MoveDetailViewModel @Inject constructor(
    private val repository: MoveRepository,
    private val networkChecker: NetworkConnectivityChecker,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _state = MutableStateFlow(MoveDetailState())
    val state = _state.asStateFlow()

    private val moveId: Int? = savedStateHandle.get<String>("moveId")?.toIntOrNull()

    init {
        moveId?.let { loadMoveDetail(it) }
    }

    /**
     * Load detailed information about the move
     */
    private fun loadMoveDetail(id: Int) {
        // Check network connectivity before making request
        if (!networkChecker.isNetworkAvailable()) {
            _state.update { it.copy(error = "No internet connection. Please check your network.") }
            return
        }

        viewModelScope.launch {
            repository.getMoveDetail(id).onEach { result ->
                when (result) {
                    is Resource.Loading -> {
                        _state.update { it.copy(isLoading = true, error = null) }
                    }
                    is Resource.Success -> {
                        _state.update {
                            it.copy(
                                isLoading = false,
                                move = result.data,
                                error = null
                            )
                        }
                    }
                    is Resource.Error -> {
                        _state.update {
                            it.copy(
                                isLoading = false,
                                error = result.message ?: "Unknown error occurred"
                            )
                        }
                    }
                }
            }.launchIn(this)
        }
    }

    /**
     * Toggle marked status of the move
     */
    fun toggleMarked() {
        val currentMove = _state.value.move ?: return

        // Check network connectivity before making request
        if (!networkChecker.isNetworkAvailable()) {
            _state.update { it.copy(error = "No internet connection. Please check your network.") }
            return
        }

        viewModelScope.launch {
            repository.toggleMoveMarked(currentMove.id, !currentMove.isMarked).onEach { result ->
                when (result) {
                    is Resource.Loading -> {
                        _state.update { it.copy(isMarkingInProgress = true, error = null) }
                    }
                    is Resource.Success -> {
                        _state.update {
                            it.copy(
                                isMarkingInProgress = false,
                                move = result.data,
                                error = null
                            )
                        }
                    }
                    is Resource.Error -> {
                        _state.update {
                            it.copy(
                                isMarkingInProgress = false,
                                error = result.message ?: "Failed to update move"
                            )
                        }
                    }
                }
            }.launchIn(this)
        }
    }

    /**
     * Start learning the move
     */
    fun startLearning() {
        val currentMove = _state.value.move ?: return

        // Check network connectivity before making request
        if (!networkChecker.isNetworkAvailable()) {
            _state.update { it.copy(error = "No internet connection. Please check your network.") }
            return
        }

        viewModelScope.launch {
            repository.startLearningMove(currentMove.id).onEach { result ->
                when (result) {
                    is Resource.Loading -> {
                        _state.update { it.copy(isStartingLearning = true, error = null) }
                    }
                    is Resource.Success -> {
                        _state.update {
                            it.copy(
                                isStartingLearning = false,
                                hasStartedLearning = true,
                                error = null
                            )
                        }
                    }
                    is Resource.Error -> {
                        _state.update {
                            it.copy(
                                isStartingLearning = false,
                                error = result.message ?: "Failed to start learning"
                            )
                        }
                    }
                }
            }.launchIn(this)
        }
    }

    fun clearError() {
        _state.update { it.copy(error = null) }
    }
}

/**
 * UI State for Move Detail Screen
 */
data class MoveDetailState(
    val isLoading: Boolean = false,
    val move: Move? = null,
    val isMarkingInProgress: Boolean = false,
    val isStartingLearning: Boolean = false,
    val hasStartedLearning: Boolean = false,
    val error: String? = null
)

