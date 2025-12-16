package com.arnasmat.fightingapp.presentation.profile

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.graphics.toColorInt
import androidx.hilt.navigation.compose.hiltViewModel
import coil3.compose.AsyncImage
import com.arnasmat.fightingapp.R
import com.arnasmat.fightingapp.domain.model.Belt
import com.arnasmat.fightingapp.domain.model.UserProfile
import com.arnasmat.fightingapp.presentation.components.*
import com.arnasmat.fightingapp.ui.theme.*

/**
 * Profile Screen showing detailed user information including move ratings
 */
@Composable
fun ProfileScreen(
    viewModel: UserProfileViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    // Detailed profile content - no need for UserTopBar as profile shows same data
    when {
        state.isLoading -> {
            LoadingState()
        }

        state.error != null -> {
            ErrorState(
                errorMessage = state.error!!,
                onRetry = { viewModel.loadUserProfile() }
            )
        }

        state.userProfile != null -> {
            ProfileContent(userProfile = state.userProfile!!)
        }
    }
}

/**
 * Loading state indicator
 */
@Composable
private fun LoadingState() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator()
    }
}

/**
 * Error state with retry button
 */
@Composable
private fun ErrorState(
    errorMessage: String,
    onRetry: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = errorMessage,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.error
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onRetry) {
            Text(stringResource(R.string.common_retry))
        }
    }
}

/**
 * Main profile content with detailed information
 */
@Composable
private fun ProfileContent(userProfile: UserProfile) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(32.dp))

        // Large profile picture
        LargeProfilePicture(
            imageUrl = userProfile.profileImageUrl,
            username = userProfile.username
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Username
        Text(
            text = userProfile.username,
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Profile details cards
        ProfileDetailCard(
            label = stringResource(R.string.profile_belt_label),
            content = {
                BeltDisplay(belt = userProfile.belt)
            }
        )

        Spacer(modifier = Modifier.height(16.dp))

        ProfileDetailCard(
            label = stringResource(R.string.profile_streak_label),
            content = {
                StreakDisplay(streakDays = userProfile.streakDays)
            }
        )
    }
}

/**
 * Large profile picture for detail view
 */
@Composable
private fun LargeProfilePicture(
    imageUrl: String?,
    username: String
) {
    Box(
        modifier = Modifier
            .size(120.dp)
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.primaryContainer)
            .border(3.dp, MaterialTheme.colorScheme.primary, CircleShape),
        contentAlignment = Alignment.Center
    ) {
        if (imageUrl != null) {
            AsyncImage(
                model = imageUrl,
                contentDescription = stringResource(R.string.profile_picture_desc, username),
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop
            )
        } else {
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = stringResource(R.string.profile_picture_desc, username),
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.primary
            )
        }
    }
}

/**
 * Card for displaying profile details
 */
@Composable
private fun ProfileDetailCard(
    label: String,
    content: @Composable () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))
            content()
        }
    }
}

/**
 * Belt display with color indicator
 */
@Composable
private fun BeltDisplay(belt: Belt) {
    Row(
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(32.dp)
                .clip(CircleShape)
                .background(
                    try {
                        Color(belt.colorHex.toColorInt())
                    } catch (e: Exception) {
                        MaterialTheme.colorScheme.primary
                    }
                )
                .border(2.dp, MaterialTheme.colorScheme.outline, CircleShape)
        )
        Spacer(modifier = Modifier.width(16.dp))
        Text(
            text = belt.displayName,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.SemiBold
        )
    }
}

/**
 * Streak display with fire emoji
 */
@Composable
private fun StreakDisplay(streakDays: Int) {
    Row(
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "🔥",
            fontSize = 32.sp
        )
        Spacer(modifier = Modifier.width(16.dp))
        Text(
            text = stringResource(R.string.streak_count, streakDays),
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold
        )
    }
}
