package com.arnasmat.fightingapp.data.repository

import com.arnasmat.fightingapp.data.local.UserProfileCache
import com.arnasmat.fightingapp.data.remote.api.FightingApi
import com.arnasmat.fightingapp.data.remote.dto.UserProfileDto
import com.arnasmat.fightingapp.domain.model.Belt
import com.arnasmat.fightingapp.domain.model.UserProfile
import com.arnasmat.fightingapp.domain.repository.UserRepository
import com.arnasmat.fightingapp.domain.util.Resource
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flow
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of UserRepository
 * Handles user profile data from API with DataStore caching
 * Cache-first strategy: Returns cached data immediately, then updates from network
 */
@Singleton
class UserRepositoryImpl @Inject constructor(
    private val api: FightingApi,
    private val cache: UserProfileCache
) : UserRepository {

    companion object {
        /**
         * Toggle this flag to switch between mock data and real API calls
         * true = Use mock data (for debugging/testing)
         * false = Use real API calls (for production)
         */
        private const val USE_MOCK_DATA = true // TODO: Set to false when backend is ready
    }

    override suspend fun getCurrentUserProfile(): Flow<Resource<UserProfile>> = flow {
        emit(Resource.Loading())

        try {
            if (USE_MOCK_DATA) {
                // Simulate network delay
                delay(800)

                // Mock user profile data with move ratings
                val mockDto = UserProfileDto(
                    id = "user_12345",
                    username = "CERNlover",
                    profileImageUrl = "https://avatars.githubusercontent.com/u/114922420?v=4",
                    belt = "WHITE",
                    streakDays = 7,
                )

                val domainModel = mapDtoToDomain(mockDto)
                emit(Resource.Success(domainModel))
            } else {
                // Real API call
                val response = api.getUserProfile()

                if (response.isSuccessful && response.body() != null) {
                    val dto = response.body()!!
                    val domainModel = mapDtoToDomain(dto)
                    emit(Resource.Success(domainModel))
                } else {
                    emit(Resource.Error("Failed to load profile: ${response.code()}"))
                }
            }
        } catch (e: HttpException) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        } catch (e: IOException) {
            emit(Resource.Error("Connection failed. Check internet."))
        } catch (e: Exception) {
            emit(Resource.Error("Unexpected error: ${e.localizedMessage}"))
        }
    }

    override suspend fun updateUserProfile(userProfile: UserProfile): Flow<Resource<UserProfile>> = flow {
        emit(Resource.Loading())

        try {
            if (USE_MOCK_DATA) {
                // Simulate network delay
                delay(500)

                // Save to cache
                cache.saveUserProfile(userProfile)

                // Return the updated profile
                emit(Resource.Success(userProfile))
            } else {
                // TODO: Implement real API call when endpoint is ready
                emit(Resource.Error("Update profile endpoint not yet implemented"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        } catch (e: IOException) {
            emit(Resource.Error("Connection failed. Check internet."))
        } catch (e: Exception) {
            emit(Resource.Error("Unexpected error: ${e.localizedMessage}"))
        }
    }

    /**
     * Maps DTO to Domain Model
     * Separates data layer concerns from business logic layer
     */
    private fun mapDtoToDomain(dto: UserProfileDto): UserProfile {
        return UserProfile(
            id = dto.id,
            username = dto.username,
            profileImageUrl = dto.profileImageUrl,
            belt = Belt.fromString(dto.belt),
            streakDays = dto.streakDays,
        )
    }
}

