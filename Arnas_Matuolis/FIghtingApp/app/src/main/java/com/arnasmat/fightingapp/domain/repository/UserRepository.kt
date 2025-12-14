package com.arnasmat.fightingapp.domain.repository

import com.arnasmat.fightingapp.domain.model.UserProfile
import com.arnasmat.fightingapp.domain.util.Resource
import kotlinx.coroutines.flow.Flow

/**
 * Repository contract for user profile operations
 * Following Clean Architecture - this is a domain layer interface
 */
interface UserRepository {
    /**
     * Get the current user's profile
     * @return Flow emitting Resource states with UserProfile data
     */
    suspend fun getCurrentUserProfile(): Flow<Resource<UserProfile>>

    /**
     * Update user profile
     * @param userProfile Updated profile data
     * @return Flow emitting Resource states indicating success/failure
     */
    suspend fun updateUserProfile(userProfile: UserProfile): Flow<Resource<UserProfile>>
}

