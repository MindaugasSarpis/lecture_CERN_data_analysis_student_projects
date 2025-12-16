package com.arnasmat.fightingapp.util

import android.Manifest
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import androidx.annotation.RequiresPermission
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlin.math.log10

/**
 * Sound detector for automatic recording activation
 * Listens for loud sounds (screams) to trigger recording start/stop
 */
class SoundDetector(
    private val scope: CoroutineScope,
    private val onLoudSoundDetected: () -> Unit
) {
    companion object {
        // Audio configuration
        private const val SAMPLE_RATE = 44100
        private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        private const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT

        // Detection thresholds
        private const val LOUD_SOUND_THRESHOLD_DB = 70.0 // Decibels threshold for loud sound
        private const val MIN_LOUD_DURATION_MS = 200L // Minimum duration of loud sound
        private const val DETECTION_COOLDOWN_MS = 1000L // Cooldown between detections
        private const val RECORDING_START_GRACE_PERIOD_MS = 3000L // 3 seconds before allowing stop
    }

    private var audioRecord: AudioRecord? = null
    private var detectionJob: Job? = null
    private var isListening = false
    private var lastDetectionTime = 0L
    private var recordingStartTime = 0L // Track when recording starts
    private var isRecording = false // Track recording state
    private var isProcessingDetection = false // Flag to prevent double-triggers

    private val _currentVolume = MutableStateFlow(0.0)
    val currentVolume = _currentVolume.asStateFlow()

    private val _isDetecting = MutableStateFlow(false)
    val isDetecting = _isDetecting.asStateFlow()

    /**
     * Start listening for loud sounds
     */
    @RequiresPermission(Manifest.permission.RECORD_AUDIO)
    fun startListening() {
        if (isListening) return

        val bufferSize = AudioRecord.getMinBufferSize(
            SAMPLE_RATE,
            CHANNEL_CONFIG,
            AUDIO_FORMAT
        )

        if (bufferSize == AudioRecord.ERROR || bufferSize == AudioRecord.ERROR_BAD_VALUE) {
            return
        }

        try {
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize
            )

            audioRecord?.startRecording()
            isListening = true
            _isDetecting.value = true

            detectionJob = scope.launch(Dispatchers.IO) {
                val buffer = ShortArray(bufferSize)
                var loudSoundStartTime = 0L
                var isCurrentlyLoud = false

                while (isActive && isListening) {
                    val readResult = audioRecord?.read(buffer, 0, bufferSize) ?: 0

                    if (readResult > 0) {
                        val amplitude = calculateAmplitude(buffer, readResult)
                        val decibels = amplitudeToDecibels(amplitude)

                        // Update current volume for UI
                        _currentVolume.value = decibels

                        // Check if sound is loud enough
                        if (decibels >= LOUD_SOUND_THRESHOLD_DB) {
                            if (!isCurrentlyLoud) {
                                // Start of loud sound
                                loudSoundStartTime = System.currentTimeMillis()
                                isCurrentlyLoud = true
                            } else {
                                // Check if loud sound duration is sufficient
                                val loudDuration = System.currentTimeMillis() - loudSoundStartTime
                                if (loudDuration >= MIN_LOUD_DURATION_MS) {
                                    // Check cooldown
                                    val timeSinceLastDetection = System.currentTimeMillis() - lastDetectionTime
                                    if (timeSinceLastDetection >= DETECTION_COOLDOWN_MS) {
                                        // Check if we're not already processing a detection
                                        if (!isProcessingDetection) {
                                            // If recording, check grace period before allowing stop
                                            val canStopRecording = !isRecording ||
                                                (System.currentTimeMillis() - recordingStartTime) >= RECORDING_START_GRACE_PERIOD_MS

                                            if (canStopRecording) {
                                                // Set processing flag to prevent any double-triggers
                                                isProcessingDetection = true

                                                // Trigger detection
                                                lastDetectionTime = System.currentTimeMillis()

                                                // Trigger callback - state will be updated via setRecordingState
                                                scope.launch(Dispatchers.Main) {
                                                    onLoudSoundDetected()
                                                }

                                                // Reset to prevent immediate re-trigger
                                                isCurrentlyLoud = false

                                                // Reset processing flag after a delay
                                                scope.launch {
                                                    delay(300) // Wait 300ms before allowing next detection
                                                    isProcessingDetection = false
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        } else {
                            // Sound is not loud enough, reset
                            isCurrentlyLoud = false
                        }
                    }

                    // Small delay to prevent excessive CPU usage
                    delay(50)
                }
            }
        } catch (e: SecurityException) {
            // Permission not granted
            stopListening()
        } catch (e: Exception) {
            // Other error
            stopListening()
        }
    }

    /**
     * Stop listening for loud sounds
     */
    fun stopListening() {
        isListening = false
        _isDetecting.value = false

        detectionJob?.cancel()
        detectionJob = null

        audioRecord?.apply {
            try {
                stop()
                release()
            } catch (e: Exception) {
                // Ignore errors on cleanup
            }
        }
        audioRecord = null

        _currentVolume.value = 0.0
    }

    /**
     * Calculate RMS amplitude from audio buffer
     */
    private fun calculateAmplitude(buffer: ShortArray, readSize: Int): Double {
        var sum = 0.0
        for (i in 0 until readSize) {
            val sample = buffer[i].toDouble()
            sum += sample * sample
        }
        return kotlin.math.sqrt(sum / readSize)
    }

    /**
     * Convert amplitude to decibels
     */
    private fun amplitudeToDecibels(amplitude: Double): Double {
        if (amplitude <= 0) return 0.0

        // Reference amplitude (maximum for 16-bit audio)
        val reference = 32768.0

        // Calculate dB = 20 * log10(amplitude / reference)
        val db = 20 * log10(amplitude / reference)

        // Normalize to positive range (0-100 dB)
        return (db + 100).coerceIn(0.0, 100.0)
    }

    /**
     * Check if detector is currently active
     */
    fun isActive(): Boolean = isListening

    /**
     * Manually set recording state (for synchronization with actual recording)
     */
    fun setRecordingState(recording: Boolean) {
        isRecording = recording
        if (recording) {
            recordingStartTime = System.currentTimeMillis()
        }
    }

    /**
     * Cleanup resources
     */
    fun release() {
        stopListening()
    }
}

