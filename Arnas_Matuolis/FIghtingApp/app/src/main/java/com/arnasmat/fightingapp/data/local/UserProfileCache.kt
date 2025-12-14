package com.arnasmat.fightingapp.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.arnasmat.fightingapp.domain.model.Belt
import com.arnasmat.fightingapp.domain.model.UserProfile
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/**
 * DataStore cache for user profile data
 * Provides persistent storage with type safety
 * Modern replacement for SharedPreferences
 */

private val Context.userProfileDataStore: DataStore<Preferences> by preferencesDataStore(
    name = "user_profile_cache"
)

@Singleton
class UserProfileCache @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val dataStore = context.userProfileDataStore

    companion object {
        private val KEY_USER_ID = stringPreferencesKey("user_id")
        private val KEY_USERNAME = stringPreferencesKey("username")
        private val KEY_PROFILE_IMAGE_URL = stringPreferencesKey("profile_image_url")
        private val KEY_BELT = stringPreferencesKey("belt")
        private val KEY_STREAK_DAYS = intPreferencesKey("streak_days")
        private val KEY_CACHE_TIMESTAMP = stringPreferencesKey("cache_timestamp")
    }

    /**
     * Get cached user profile as a Flow
     */
    fun getUserProfile(): Flow<UserProfile?> = dataStore.data.map { preferences ->
        val userId = preferences[KEY_USER_ID]
        val username = preferences[KEY_USERNAME]
        val belt = preferences[KEY_BELT]

        // Return null if essential data is missing
        if (userId == null || username == null || belt == null) {
            return@map null
        }

        UserProfile(
            id = userId,
            username = username,
            profileImageUrl = preferences[KEY_PROFILE_IMAGE_URL],
            belt = Belt.fromString(belt),
            streakDays = preferences[KEY_STREAK_DAYS] ?: 0,
        )
    }

    /**
     * Save user profile to cache
     */
    suspend fun saveUserProfile(userProfile: UserProfile) {
        dataStore.edit { preferences ->
            preferences[KEY_USER_ID] = userProfile.id
            preferences[KEY_USERNAME] = userProfile.username
            preferences[KEY_PROFILE_IMAGE_URL] = userProfile.profileImageUrl ?: ""
            preferences[KEY_BELT] = userProfile.belt.name
            preferences[KEY_STREAK_DAYS] = userProfile.streakDays
            preferences[KEY_CACHE_TIMESTAMP] = System.currentTimeMillis().toString()
        }
    }

}

