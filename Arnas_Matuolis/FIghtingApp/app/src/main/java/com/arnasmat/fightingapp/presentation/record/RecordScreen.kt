package com.arnasmat.fightingapp.presentation.record

import android.Manifest
import android.content.ContentValues
import android.content.Context
import android.os.Build
import android.provider.MediaStore
import android.view.ViewGroup
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.RequiresPermission
import androidx.camera.core.Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.*
import androidx.camera.view.PreviewView
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.VolumeOff
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.core.util.Consumer
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import com.arnasmat.fightingapp.R
import com.arnasmat.fightingapp.presentation.components.*
import com.arnasmat.fightingapp.ui.theme.*
import com.arnasmat.fightingapp.util.SoundDetector
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberMultiplePermissionsState
import java.text.SimpleDateFormat
import java.util.*
import kotlinx.coroutines.flow.collectLatest

/**
 * Record Screen with CameraX video recording
 * Best practice: Proper permission handling and lifecycle management
 *
 * @param exerciseId Optional exercise ID for learning context
 * @param onNavigateToAnalyzedVideo Callback to navigate to analyzed video playback screen
 * @param viewModel ViewModel for managing recording state
 */
@androidx.annotation.OptIn(ExperimentalGetImage::class)
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun RecordScreen(
    exerciseId: Int? = null,  // Optional exercise ID for learning context
    onNavigateToAnalyzedVideo: ((com.arnasmat.fightingapp.domain.model.VideoAnalysis) -> Unit)? = null,  // Navigation callback for analyzed video
    viewModel: RecordViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val state by viewModel.state.collectAsState()

    // Set exercise ID when provided (for learning flow)
    LaunchedEffect(exerciseId) {
        if (exerciseId != null) {
            viewModel.setExerciseId(exerciseId)
        }
    }

    // Navigate to analyzed video playback when analysis is available
    LaunchedEffect(state.videoAnalysis) {
        state.videoAnalysis?.let { analysis ->
            onNavigateToAnalyzedVideo?.invoke(analysis)
        }
    }

    // Request camera and audio permissions
    val permissionsState = rememberMultiplePermissionsState(
        permissions = listOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO
        )
    )

    // Camera and recording state
    var cameraProvider by remember { mutableStateOf<ProcessCameraProvider?>(null) }
    var recording by remember { mutableStateOf<Recording?>(null) }
    var recordingDuration by remember { mutableLongStateOf(0L) }

    // Video picker launcher
    val videoPickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.PickVisualMedia()
    ) { uri ->
        uri?.let {
            viewModel.onVideoSelectedFromGallery(it)
        }
    }

    LaunchedEffect(Unit) {
        if (!permissionsState.allPermissionsGranted) {
            permissionsState.launchMultiplePermissionRequest()
        }
    }

    // Main recording content - fullscreen
    Box(modifier = Modifier.fillMaxSize()) {
        when {
            !permissionsState.allPermissionsGranted -> {
            // Permission request UI
            PermissionRequestContent(
                onRequestPermissions = { permissionsState.launchMultiplePermissionRequest() }
            )
        }
            state.recordedVideo != null -> {
                // Video preview and upload UI
                VideoPreviewContent(
                    state = state,
                    onUpload = { viewModel.uploadVideo() },
                    onDelete = { viewModel.deleteVideo() },
                    onRename = { newName -> viewModel.renameVideo(newName) },
                    onClearError = { viewModel.clearError() }
                )
            }
            else -> {
                // Camera preview and recording UI
                CameraContent(
                    state = state,
                    lifecycleOwner = lifecycleOwner,
                    viewModel = viewModel,
                    onCameraProviderReady = { provider -> cameraProvider = provider },
                    onStartRecording = @RequiresPermission(Manifest.permission.RECORD_AUDIO) { videoCapture ->
                        // Safety check: Don't start if already recording
                        if (recording == null) {
                            try {
                                // Set recording state IMMEDIATELY to prevent race condition
                                viewModel.setRecording(true)

                                recording = startRecording(
                                    context = context,
                                    videoCapture = videoCapture,
                                    onEvent = { event ->
                                        when (event) {
                                            is VideoRecordEvent.Start -> {
                                                // Already set above, but keep for consistency
                                                viewModel.setRecording(true)
                                            }
                                            is VideoRecordEvent.Finalize -> {
                                                if (event.hasError()) {
                                                    viewModel.onRecordingError("Recording error: ${event.cause?.message}")
                                                } else {
                                                    event.outputResults.outputUri.let { uri ->
                                                        viewModel.onVideoRecorded(
                                                            videoUri = uri,
                                                            filePath = uri.toString(), // Use URI string instead of path
                                                            durationMs = recordingDuration,
                                                            sizeBytes = 0L // Will be calculated by repository
                                                        )
                                                    }
                                                }
                                                recording = null
                                            }
                                            is VideoRecordEvent.Status -> {
                                                recordingDuration = event.recordingStats.recordedDurationNanos / 1_000_000
                                            }
                                        }
                                    }
                                )
                            } catch (e: SecurityException) {
                                viewModel.onRecordingError("Permission denied for recording audio")
                                viewModel.setRecording(false) // Reset state on error
                            } catch (e: IllegalStateException) {
                                // Recording already in progress - should not happen but catch it
                                viewModel.onRecordingError("Recording error: ${e.message}")
                                viewModel.setRecording(false) // Reset state on error
                            }
                        }
                    },
                    onStopRecording = {
                        recording?.stop()
                        recording = null
                        viewModel.setRecording(false)
                    },
                    recordingDuration = recordingDuration,
                    onSelectVideoFromGallery = {
                        videoPickerLauncher.launch(
                            PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.VideoOnly)
                        )
                    }
                )
            }
        }

        // Error display
        state.error?.let { error ->
            ErrorBanner(
                error = error,
                onDismiss = { viewModel.clearError() },
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(16.dp)
            )
        }

        // Upload loading overlay - full screen
        if (state.isUploading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.95f)),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(Spacing.large)
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(64.dp),
                        color = ElectricBlue,
                        strokeWidth = 6.dp
                    )
                    Text(
                        text = "Analyzing your technique...",
                        style = MaterialTheme.typography.titleLarge,
                        color = TextPrimary,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "This may take a few minutes",
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextSecondary,
                        textAlign = TextAlign.Center
                    )
                    SmallSpacer()
                    LinearProgressIndicator(
                        modifier = Modifier
                            .width(200.dp)
                            .height(4.dp),
                        color = ElectricBlue,
                        trackColor = FightDarkCard
                    )
                }
            }
        }
    }
}

@Composable
private fun PermissionRequestContent(
    onRequestPermissions: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = stringResource(R.string.record_permission_title),
            style = MaterialTheme.typography.headlineSmall,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = stringResource(R.string.record_permission_message),
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(32.dp))
        Button(onClick = onRequestPermissions) {
            Text(stringResource(R.string.record_permission_grant))
        }
    }
}

@Composable
private fun CameraContent(
    state: RecordState,
    lifecycleOwner: androidx.lifecycle.LifecycleOwner,
    viewModel: RecordViewModel,
    onCameraProviderReady: (ProcessCameraProvider) -> Unit,
    onStartRecording: (VideoCapture<Recorder>) -> Unit,
    onStopRecording: () -> Unit,
    recordingDuration: Long,
    onSelectVideoFromGallery: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    var videoCapture by remember { mutableStateOf<VideoCapture<Recorder>?>(null) }
    var camera by remember { mutableStateOf<Camera?>(null) }
    var isFrontCamera by remember { mutableStateOf(false) }
    var zoomRatio by remember { mutableFloatStateOf(1f) }
    var cameraProvider by remember { mutableStateOf<ProcessCameraProvider?>(null) }
    var previewView by remember { mutableStateOf<PreviewView?>(null) }
    val recordButtonScale = remember { Animatable(1f) }

    // Capture latest values for callback
    val currentState by rememberUpdatedState(state)
    val currentOnStopRecording by rememberUpdatedState(onStopRecording)
    val currentOnStartRecording by rememberUpdatedState(onStartRecording)
    val currentVideoCapture by rememberUpdatedState(videoCapture)

    // Sound detector for auto-start recording
    val soundDetector = remember {
        SoundDetector(
            scope = coroutineScope,
            onLoudSoundDetected = {
                // Toggle recording on loud sound detection
                // Use currentState to get latest value
                if (currentState.isRecording) {
                    currentOnStopRecording()
                } else {
                    currentVideoCapture?.let { currentOnStartRecording(it) }
                }
            }
        )
    }

    // Monitor sound level
    LaunchedEffect(state.soundActivatedMode) {
        if (state.soundActivatedMode) {
            soundDetector.currentVolume.collectLatest { volume ->
                viewModel.updateSoundLevel(volume)
            }
        }
    }

    // Monitor sound detection state
    LaunchedEffect(state.soundActivatedMode) {
        if (state.soundActivatedMode) {
            soundDetector.isDetecting.collectLatest { isDetecting ->
                viewModel.setListeningForSound(isDetecting)
            }
        }
    }

    // Start/stop sound detection based on mode
    LaunchedEffect(state.soundActivatedMode) {
        if (state.soundActivatedMode) {
            try {
                soundDetector.startListening()
            } catch (e: SecurityException) {
                // Permission not granted, ignore
                viewModel.toggleSoundActivatedMode() // Turn off the mode
            }
        } else {
            soundDetector.stopListening()
        }
    }

    // Cleanup sound detector on disposal
    DisposableEffect(Unit) {
        onDispose {
            soundDetector.release()
        }
    }

    // Sync recording state with sound detector
    LaunchedEffect(state.isRecording) {
        soundDetector.setRecordingState(state.isRecording)
    }

    // Edge glow animation for recording
    val infiniteTransition = rememberInfiniteTransition(label = "recording_glow")
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow_alpha"
    )

    // Function to bind camera with selected lens
    fun bindCamera(preview: PreviewView, provider: ProcessCameraProvider) {
        val previewUseCase = Preview.Builder().build().also {
            it.setSurfaceProvider(preview.surfaceProvider)
        }

        val recorder = Recorder.Builder()
            .setQualitySelector(QualitySelector.from(Quality.HD))
            .build()

        videoCapture = VideoCapture.withOutput(recorder)

        val cameraSelector = if (isFrontCamera) {
            CameraSelector.DEFAULT_FRONT_CAMERA
        } else {
            CameraSelector.DEFAULT_BACK_CAMERA
        }

        try {
            provider.unbindAll()
            camera = provider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                previewUseCase,
                videoCapture
            )

            // Set initial zoom
            camera?.cameraControl?.setZoomRatio(zoomRatio)
        } catch (_: Exception) {
            // Handle error silently
        }
    }

    // Rebind camera when camera selector changes
    LaunchedEffect(isFrontCamera) {
        previewView?.let { preview ->
            cameraProvider?.let { provider ->
                bindCamera(preview, provider)
            }
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        // Camera Preview with pinch-to-zoom
        AndroidView(
            factory = { ctx ->
                PreviewView(ctx).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT
                    )
                    implementationMode = PreviewView.ImplementationMode.COMPATIBLE
                    scaleType = PreviewView.ScaleType.FILL_CENTER

                    // Store reference for camera switching
                    previewView = this

                    val cameraProviderFuture = ProcessCameraProvider.getInstance(ctx)
                    cameraProviderFuture.addListener({
                        val provider = cameraProviderFuture.get()
                        cameraProvider = provider
                        onCameraProviderReady(provider)
                        bindCamera(this, provider)
                    }, ContextCompat.getMainExecutor(ctx))
                }
            },
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(Unit) {
                    detectTransformGestures { _, _, zoom, _ ->
                        camera?.let { cam ->
                            val currentZoom = cam.cameraInfo.zoomState.value?.zoomRatio ?: 1f
                            val maxZoom = cam.cameraInfo.zoomState.value?.maxZoomRatio ?: 8f
                            val minZoom = cam.cameraInfo.zoomState.value?.minZoomRatio ?: 1f

                            val newZoom = (currentZoom * zoom).coerceIn(minZoom, maxZoom)
                            zoomRatio = newZoom
                            cam.cameraControl.setZoomRatio(newZoom)
                        }
                    }
                }
        )

        // Recording indicator overlay with design system
        if (state.isRecording) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .border(
                        width = Dimensions.borderThick,
                        color = FightRed.copy(alpha = glowAlpha),
                        shape = FightingShapes.sharp
                    )
            )
        }

        // Top control bar - Camera switch and zoom indicator
        Row(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .fillMaxWidth()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(
                            OverlayBlack,
                            Color.Transparent
                        )
                    )
                )
                .padding(Spacing.medium),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.small),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Zoom indicator
                Surface(
                    shape = FightingShapes.pill,
                    color = FightDarkElevated.copy(alpha = 0.9f),
                    modifier = Modifier.padding(Spacing.small)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = Spacing.medium, vertical = Spacing.small),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.ZoomIn,
                            contentDescription = "Zoom",
                            tint = TextPrimary,
                            modifier = Modifier.size(Dimensions.iconSizeMedium)
                        )
                        Spacer(modifier = Modifier.width(Spacing.small))
                        Text(
                            text = String.format(Locale.getDefault(), "%.1fx", zoomRatio),
                            color = TextPrimary,
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                // Sound-activated mode toggle
                FilledIconButton(
                    onClick = {
                        viewModel.toggleSoundActivatedMode()
                    },
                    modifier = Modifier
                        .padding(Spacing.small)
                        .size(Dimensions.minTouchTarget),
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = if (state.soundActivatedMode)
                            ElectricBlue.copy(alpha = 0.9f)
                        else
                            FightDarkElevated.copy(alpha = 0.9f),
                        contentColor = TextPrimary,
                        disabledContainerColor = FightDarkSurface,
                        disabledContentColor = TextDisabled
                    ),
                    enabled = !state.isRecording
                ) {
                    Icon(
                        imageVector = if (state.soundActivatedMode) Icons.AutoMirrored.Filled.VolumeUp else Icons.AutoMirrored.Filled.VolumeOff,
                        contentDescription = "Sound-Activated Mode",
                        modifier = Modifier.size(Dimensions.iconSizeMedium)
                    )
                }
            }

            // Camera switch button with design system
            FilledIconButton(
                onClick = {
                    isFrontCamera = !isFrontCamera
                },
                modifier = Modifier
                    .padding(Spacing.small)
                    .size(Dimensions.minTouchTarget),
                colors = IconButtonDefaults.filledIconButtonColors(
                    containerColor = FightDarkElevated.copy(alpha = 0.9f),
                    contentColor = TextPrimary,
                    disabledContainerColor = FightDarkSurface,
                    disabledContentColor = TextDisabled
                ),
                enabled = !state.isRecording
            ) {
                Icon(
                    imageVector = Icons.Default.Cameraswitch,
                    contentDescription = "Switch Camera",
                    modifier = Modifier.size(Dimensions.iconSizeMedium)
                )
            }
        }


        // Recording duration with design system
        AnimatedVisibility(
            visible = state.isRecording,
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 80.dp),
            enter = fadeIn() + slideInVertically(),
            exit = fadeOut() + slideOutVertically()
        ) {
            Surface(
                shape = FightingShapes.large,
                color = FightDarkElevated.copy(alpha = 0.95f),
                modifier = Modifier.border(
                    width = Dimensions.borderMedium,
                    color = FightRed.copy(alpha = glowAlpha),
                    shape = FightingShapes.large
                )
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = Spacing.large, vertical = Spacing.small),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Pulsing red dot
                    Box(
                        modifier = Modifier
                            .size(12.dp)
                            .scale(if (glowAlpha > 0.5f) 1.1f else 0.9f)
                            .background(FightRed, CircleShape)
                    )
                    Spacer(modifier = Modifier.width(Spacing.small))
                    Text(
                        text = formatDuration(recordingDuration),
                        style = MaterialTheme.typography.headlineSmall,
                        color = TextPrimary,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        // Sound level indicator (when sound-activated mode is enabled)
        AnimatedVisibility(
            visible = state.soundActivatedMode && !state.isRecording,
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 80.dp),
            enter = fadeIn() + slideInVertically(),
            exit = fadeOut() + slideOutVertically()
        ) {
            Surface(
                shape = FightingShapes.large,
                color = FightDarkElevated.copy(alpha = 0.95f),
                modifier = Modifier.border(
                    width = Dimensions.borderMedium,
                    color = ElectricBlue.copy(alpha = 0.5f),
                    shape = FightingShapes.large
                )
            ) {
                Column(
                    modifier = Modifier.padding(horizontal = Spacing.large, vertical = Spacing.small),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(Spacing.small)
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.VolumeUp,
                            contentDescription = "Sound Level",
                            tint = ElectricBlue,
                            modifier = Modifier.size(20.dp)
                        )
                        Text(
                            text = "Sound-Activated",
                            style = MaterialTheme.typography.labelMedium,
                            color = TextPrimary,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Spacer(modifier = Modifier.height(Spacing.small))
                    // Sound level bar
                    Row(
                        modifier = Modifier.width(200.dp),
                        horizontalArrangement = Arrangement.spacedBy(2.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        val barCount = 20
                        val activeBarCount = (state.currentSoundLevel / 100.0 * barCount).toInt()
                        repeat(barCount) { index ->
                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .height(if (index < activeBarCount) 16.dp else 8.dp)
                                    .background(
                                        color = if (index < activeBarCount) {
                                            when {
                                                state.currentSoundLevel >= 70 -> FightRed
                                                state.currentSoundLevel >= 50 -> FightOrange
                                                else -> SuccessGreen
                                            }
                                        } else {
                                            FightDarkSurface
                                        },
                                        shape = FightingShapes.small
                                    )
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(Spacing.extraSmall))
                    Text(
                        text = "Scream to start/stop recording",
                        style = MaterialTheme.typography.labelSmall,
                        color = TextSecondary
                    )
                }
            }
        }

        // Bottom control panel with design system
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(
                            Color.Transparent,
                            OverlayBlack
                        )
                    )
                )
                .padding(bottom = Spacing.extraLarge, top = Spacing.huge),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Record button and gallery button row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Gallery button (select video from device)
                FilledIconButton(
                    onClick = onSelectVideoFromGallery,
                    modifier = Modifier.size(60.dp),
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = FightDarkElevated.copy(alpha = 0.9f),
                        contentColor = TextPrimary,
                        disabledContainerColor = FightDarkSurface,
                        disabledContentColor = TextDisabled
                    ),
                    enabled = !state.isRecording
                ) {
                    Icon(
                        imageVector = Icons.Default.VideoLibrary,
                        contentDescription = "Select Video from Gallery",
                        modifier = Modifier.size(28.dp)
                    )
                }

                // Record button with design system
                Box(
                    contentAlignment = Alignment.Center
                ) {
                    // Outer glow ring
                    if (state.isRecording) {
                        Box(
                            modifier = Modifier
                                .size(100.dp)
                                .background(
                                    brush = Brush.radialGradient(
                                        colors = listOf(
                                            FightRed.copy(alpha = glowAlpha * 0.5f),
                                            Color.Transparent
                                        )
                                    ),
                                    shape = CircleShape
                                )
                        )
                    }

                    // Main button
                    FilledIconButton(
                        onClick = {
                            if (state.isRecording) {
                                onStopRecording()
                            } else {
                                videoCapture?.let { onStartRecording(it) }
                            }
                        },
                        modifier = Modifier
                            .size(80.dp)
                            .scale(recordButtonScale.value)
                            .border(
                                width = Dimensions.borderThick,
                                color = if (state.isRecording) FightRed else TextPrimary,
                                shape = CircleShape
                            ),
                        colors = IconButtonDefaults.filledIconButtonColors(
                            containerColor = if (state.isRecording)
                                FightRed.copy(alpha = 0.9f)
                            else
                                FightRed,
                            contentColor = TextPrimary
                        )
                    ) {
                        Icon(
                            imageVector = if (state.isRecording) Icons.Default.Stop else Icons.Default.FiberManualRecord,
                            contentDescription = if (state.isRecording) "Stop Recording" else "Start Recording",
                            modifier = Modifier.size(40.dp)
                        )
                    }
                }

                // Placeholder for visual balance (same width as gallery button)
                Spacer(modifier = Modifier.size(60.dp))
            }

            Spacer(modifier = Modifier.height(Spacing.small))

            // Status text with design system
            if (state.soundActivatedMode && !state.isRecording) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(Spacing.extraSmall)
                ) {
                    Text(
                        text = "🔊 SOUND-ACTIVATED",
                        style = MaterialTheme.typography.labelLarge,
                        color = ElectricBlue,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 2.sp
                    )
                    Text(
                        text = "Scream to start",
                        style = MaterialTheme.typography.labelSmall,
                        color = TextSecondary,
                        letterSpacing = 1.sp
                    )
                }
            } else {
                Text(
                    text = if (state.isRecording) "TAP TO STOP" else "TAP TO RECORD",
                    style = MaterialTheme.typography.labelLarge,
                    color = TextPrimary,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 2.sp
                )
            }
        }
    }

    // Animate record button on state change
    LaunchedEffect(state.isRecording) {
        recordButtonScale.animateTo(
            targetValue = if (state.isRecording) 0.9f else 1f,
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessLow
            )
        )
    }
}

@Composable
private fun VideoPreviewContent(
    state: RecordState,
    onUpload: () -> Unit,
    onDelete: () -> Unit,
    onRename: (String) -> Unit,
    onClearError: () -> Unit
) {
    // Note: onRename kept in signature for compatibility but UI removed
    // Renaming is available in History screen

    FightContainer(backgroundColor = FightDarkBg) {
        // Video Player Card with design system
        FightCard(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
            backgroundColor = FightDarkCard,
            elevation = Elevation.medium
        ) {
            state.recordedVideo?.let { video ->
                VideoPlayer(
                    videoUri = video.uri,
                    modifier = Modifier.fillMaxSize(),
                    autoPlay = false
                )
            }
        }

        MediumSpacer()

        // Upload success indicator (if applicable)
        if (state.uploadSuccess) {
            FightSuccessCard(
                message = "Analysis complete! Results are ready."
            )
            MediumSpacer()
        }

        // Exercise Context Info Card (shown when recording from learning flow)
        if (state.exerciseId != null) {
            FightCard(
                modifier = Modifier.fillMaxWidth(),
                backgroundColor = FightDarkCard,
                borderColor = ElectricBlue.copy(alpha = 0.5f)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(Spacing.medium)
                ) {
                    Icon(
                        imageVector = Icons.Default.FitnessCenter,
                        contentDescription = null,
                        tint = ElectricBlue,
                        modifier = Modifier.size(32.dp)
                    )
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "🥋 Learning Context",
                            style = MaterialTheme.typography.labelMedium,
                            color = ElectricBlue,
                            fontWeight = FontWeight.SemiBold
                        )
                        SmallSpacer()
                        Text(
                            text = state.exerciseName ?: "Exercise ID: ${state.exerciseId}",
                            style = MaterialTheme.typography.titleMedium,
                            color = TextPrimary,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Exercise ID: ${state.exerciseId}",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary
                        )
                    }
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = "Will be sent to backend",
                        tint = SuccessGreen,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }

            MediumSpacer()
        }

        // Upload button with design system - Red for recording-related action
        FightRecordButton(
            text = if (state.uploadSuccess)
                stringResource(R.string.record_btn_uploaded)
            else
                stringResource(R.string.record_btn_upload),
            onClick = onUpload,
            modifier = Modifier.fillMaxWidth(),
            enabled = !state.isUploading && !state.uploadSuccess,
            isLoading = state.isUploading,
            icon = if (state.uploadSuccess) Icons.Default.Check else Icons.Default.CloudUpload
        )

        SmallSpacer()

        // Delete/Record again button with design system
        FightOutlinedButton(
            text = stringResource(R.string.record_btn_record_another),
            onClick = onDelete,
            modifier = Modifier.fillMaxWidth(),
            borderColor = FightRed
        )
    }
}

@Composable
private fun ErrorBanner(
    error: String,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = error,
                color = MaterialTheme.colorScheme.onErrorContainer,
                modifier = Modifier.weight(1f)
            )
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.record_btn_dismiss))
            }
        }
    }
}

private fun formatDuration(milliseconds: Long): String {
    val seconds = milliseconds / 1000
    val minutes = seconds / 60
    val remainingSeconds = seconds % 60
    return String.format(Locale.getDefault(), "%02d:%02d", minutes, remainingSeconds)
}

@RequiresPermission(Manifest.permission.RECORD_AUDIO)
@ExperimentalGetImage
private fun startRecording(
    context: Context,
    videoCapture: VideoCapture<Recorder>,
    onEvent: (VideoRecordEvent) -> Unit
): Recording {
    val name = SimpleDateFormat("yyyy-MM-dd-HH-mm-ss-SSS", Locale.US)
        .format(System.currentTimeMillis())

    val contentValues = ContentValues().apply {
        put(MediaStore.MediaColumns.DISPLAY_NAME, name)
        put(MediaStore.MediaColumns.MIME_TYPE, "video/mp4")
        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.P) {
            put(MediaStore.Video.Media.RELATIVE_PATH, "Movies/FightingApp")
        }
    }

    val mediaStoreOutputOptions = MediaStoreOutputOptions
        .Builder(context.contentResolver, MediaStore.Video.Media.EXTERNAL_CONTENT_URI)
        .setContentValues(contentValues)
        .build()

    return videoCapture.output
        .prepareRecording(context, mediaStoreOutputOptions)
        .withAudioEnabled()
        .start(ContextCompat.getMainExecutor(context), Consumer(onEvent))
}

