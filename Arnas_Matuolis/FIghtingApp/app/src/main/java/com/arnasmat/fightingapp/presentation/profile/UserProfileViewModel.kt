package com.arnasmat.fightingapp.presentation.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.arnasmat.fightingapp.domain.model.UserProfile
import com.arnasmat.fightingapp.domain.repository.UserRepository
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
 * ViewModel for user profile management
 * Handles user profile data with DataStore caching
 * Singleton scoped - shared across all screens to prevent reloading
 */
@HiltViewModel
class UserProfileViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _state = MutableStateFlow(UserProfileState())
    val state = _state.asStateFlow()

    private var hasLoadedProfile = false

    init {
        // Load user profile when ViewModel is first created
        // Will use cache for instant display, then update from network
        loadUserProfile()
    }

    /**
     * Load current user profile from repository
     * Uses cache-first strategy: shows cached data immediately,
     * then updates from network in background
     */
    fun loadUserProfile() {
        // Prevent unnecessary reloads if we already have data
        if (hasLoadedProfile && _state.value.userProfile != null) {
            return
        }

        viewModelScope.launch {
            userRepository.getCurrentUserProfile().onEach { result ->
                when (result) {
                    is Resource.Loading -> {
                        // Only show loading if we don't have cached data
                        if (_state.value.userProfile == null) {
                            _state.update { it.copy(isLoading = true, error = null) }
                        }
                    }
                    is Resource.Success -> {
                        hasLoadedProfile = true
                        _state.update {
                            it.copy(
                                isLoading = false,
                                userProfile = result.data,
                                error = null
                            )
                        }
                    }
                    is Resource.Error -> {
                        _state.update {
                            it.copy(
                                isLoading = false,
                                error = result.message
                            )
                        }
                    }
                }
            }.launchIn(this)
        }
    }

    /**
     * Force refresh profile data from network
     * Bypasses cache and fetches fresh data
     */
    fun refreshProfile() {
        hasLoadedProfile = false
        loadUserProfile()
    }

    /**
     * Clear error message
     */
    fun clearError() {
        _state.update { it.copy(error = null) }
    }
}

/**
 * UI State for user profile
 */
data class UserProfileState(
    val isLoading: Boolean = false,
    val userProfile: UserProfile? = null,
    val error: String? = null
)

