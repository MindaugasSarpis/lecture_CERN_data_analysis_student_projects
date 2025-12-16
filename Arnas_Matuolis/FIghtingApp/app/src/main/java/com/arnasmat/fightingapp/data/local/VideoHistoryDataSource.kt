package com.arnasmat.fightingapp.data.local

import android.content.Context
import android.net.Uri
import com.arnasmat.fightingapp.domain.model.RecordedVideo
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton
import androidx.core.net.toUri

/**
 * Local data source for video history
 * Uses SharedPreferences for simple persistence
 * TODO: Consider migrating to Room database for better scalability
 */
@Singleton
class VideoHistoryDataSource @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val gson = Gson()

    private val _videos = MutableStateFlow<List<RecordedVideo>>(emptyList())
    val videos: Flow<List<RecordedVideo>> = _videos.asStateFlow()

    init {
        loadVideos()
    }

    /**
     * Save video to history
     */
    fun saveVideo(video: RecordedVideo) {
        val currentVideos = _videos.value.toMutableList()
        // Add to beginning of list (most recent first)
        currentVideos.add(0, video)
        _videos.value = currentVideos
        persistVideos(currentVideos)
    }

    /**
     * Delete video from history
     */
    fun deleteVideo(video: RecordedVideo) {
        val currentVideos = _videos.value.toMutableList()
        currentVideos.removeAll { it.uri == video.uri }
        _videos.value = currentVideos
        persistVideos(currentVideos)
    }

    /**
     * Update video in history (e.g., for renaming)
     */
    fun updateVideo(oldVideo: RecordedVideo, newVideo: RecordedVideo) {
        val currentVideos = _videos.value.toMutableList()
        val index = currentVideos.indexOfFirst { it.uri == oldVideo.uri }
        if (index != -1) {
            currentVideos[index] = newVideo
            _videos.value = currentVideos
            persistVideos(currentVideos)
        }
    }

    /**
     * Load videos from SharedPreferences
     */
    private fun loadVideos() {
        val json = prefs.getString(KEY_VIDEOS, null)
        if (json != null) {
            try {
                val type = object : TypeToken<List<VideoDto>>() {}.type
                val dtos: List<VideoDto> = gson.fromJson(json, type)
                _videos.value = dtos.map { it.toDomain() }
            } catch (e: Exception) {
                e.printStackTrace()
                _videos.value = emptyList()
            }
        }
    }

    /**
     * Persist videos to SharedPreferences
     */
    private fun persistVideos(videos: List<RecordedVideo>) {
        val dtos = videos.map { VideoDto.fromDomain(it) }
        val json = gson.toJson(dtos)
        prefs.edit().putString(KEY_VIDEOS, json).apply()
    }

    /**
     * DTO for serialization (Uri can't be directly serialized)
     */
    private data class VideoDto(
        val uriString: String,
        val fileName: String,
        val filePath: String,
        val durationMs: Long,
        val sizeBytes: Long,
        val timestamp: Long
    ) {
        fun toDomain() = RecordedVideo(
            uri = uriString.toUri(),
            fileName = fileName,
            filePath = filePath,
            durationMs = durationMs,
            sizeBytes = sizeBytes,
            timestamp = timestamp
        )

        companion object {
            fun fromDomain(video: RecordedVideo) = VideoDto(
                uriString = video.uri.toString(),
                fileName = video.fileName,
                filePath = video.filePath,
                durationMs = video.durationMs,
                sizeBytes = video.sizeBytes,
                timestamp = video.timestamp
            )
        }
    }

    companion object {
        private const val PREFS_NAME = "video_history"
        private const val KEY_VIDEOS = "videos"
    }
}

