package com.arnasmat.fightingapp.presentation.learn

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
 * ViewModel for Learn Screen
 * Manages learning suggestions list
 */
@HiltViewModel
class LearnViewModel @Inject constructor(
    private val repository: MoveRepository,
    private val networkChecker: NetworkConnectivityChecker
) : ViewModel() {

    private val _state = MutableStateFlow(LearnState())
    val state = _state.asStateFlow()

    init {
        loadLearningSuggestions()
    }

    /**
     * Load list of suggested moves for learning
     */
    fun loadLearningSuggestions() {
        // Check network connectivity before making request
        if (!networkChecker.isNetworkAvailable()) {
            _state.update { it.copy(error = "No internet connection. Please check your network.") }
            return
        }

        viewModelScope.launch {
            repository.getLearningSuggestions().onEach { result ->
                when (result) {
                    is Resource.Loading -> {
                        _state.update { it.copy(isLoading = true, error = null) }
                    }
                    is Resource.Success -> {
                        _state.update {
                            it.copy(
                                isLoading = false,
                                moves = result.data ?: emptyList(),
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

    fun clearError() {
        _state.update { it.copy(error = null) }
    }
}

/**
 * UI State for Learn Screen
 */
data class LearnState(
    val isLoading: Boolean = false,
    val moves: List<Move> = emptyList(),
    val error: String? = null
)

