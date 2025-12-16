package com.arnasmat.fightingapp.presentation.learn.steps

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.arnasmat.fightingapp.domain.model.Move
import com.arnasmat.fightingapp.domain.repository.MoveRepository
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
 * ViewModel for Learning Record Screen
 * Handles move context for recording
 */
@HiltViewModel
class LearningRecordViewModel @Inject constructor(
    private val moveRepository: MoveRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _state = MutableStateFlow(LearningRecordState())
    val state = _state.asStateFlow()

    private val moveId: Int? = savedStateHandle.get<String>("moveId")?.toIntOrNull()

    init {
        moveId?.let { loadMoveDetails(it) }
    }

    /**
     * Set the move ID for this recording session
     */
    fun setMoveId(id: Int) {
        if (_state.value.moveId != id) {
            _state.update { it.copy(moveId = id) }
            loadMoveDetails(id)
        }
    }

    /**
     * Load move details to display context
     */
    private fun loadMoveDetails(id: Int) {
        viewModelScope.launch {
            moveRepository.getMoveDetail(id).onEach { result ->
                when (result) {
                    is Resource.Success -> {
                        _state.update { it.copy(move = result.data) }
                    }
                    is Resource.Error -> {
                        // Silently fail - move details are optional for context
                    }
                    is Resource.Loading -> {
                        // Loading state not needed
                    }
                }
            }.launchIn(this)
        }
    }
}

/**
 * UI State for Learning Record Screen
 */
data class LearningRecordState(
    val moveId: Int? = null,
    val move: Move? = null
)

