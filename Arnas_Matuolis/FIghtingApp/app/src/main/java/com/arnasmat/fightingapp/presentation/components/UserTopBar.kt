package com.arnasmat.fightingapp.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Person
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
import com.arnasmat.fightingapp.presentation.profile.UserProfileViewModel
import com.arnasmat.fightingapp.ui.theme.*

/**
 * Reusable top bar component showing user profile information
 * Displays profile picture, belt/rank, and streak number
 *
 * @param modifier Modifier for customization
 * @param viewModel UserProfileViewModel for accessing user data
 */
@Composable
fun UserTopBar(
    modifier: Modifier = Modifier,
    viewModel: UserProfileViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    Surface(
        modifier = modifier
            .fillMaxWidth()
            .height(80.dp),
        shadowElevation = 4.dp,
        color = MaterialTheme.colorScheme.surface
    ) {
        when {
            state.isLoading -> {
                // Show loading state
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        strokeWidth = 2.dp
                    )
                }
            }
            state.userProfile != null -> {
                // Show user profile data
                UserTopBarContent(userProfile = state.userProfile!!)
            }
            else -> {
                // Show placeholder or error state
                UserTopBarPlaceholder()
            }
        }
    }
}

/**
 * Content of the top bar with user profile data
 */
@Composable
private fun UserTopBarContent(userProfile: UserProfile) {
    Row(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Profile Picture
        ProfilePicture(
            imageUrl = userProfile.profileImageUrl,
            username = userProfile.username
        )

        Spacer(modifier = Modifier.width(16.dp))

        // Belt/Rank Badge
        BeltBadge(
            belt = userProfile.belt,
            modifier = Modifier.weight(1f)
        )

        Spacer(modifier = Modifier.width(16.dp))

        // Streak Counter
        StreakCounter(streakDays = userProfile.streakDays)
    }
}

/**
 * Profile picture with fallback icon
 */
@Composable
private fun ProfilePicture(
    imageUrl: String?,
    username: String,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(44.dp)  // Reduced from 56dp
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.primaryContainer)
            .border(2.dp, MaterialTheme.colorScheme.primary, CircleShape),
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
            // Fallback icon if no profile picture
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = stringResource(R.string.profile_picture_desc, username),
                modifier = Modifier.size(24.dp),  // Reduced from 32dp
                tint = MaterialTheme.colorScheme.primary
            )
        }
    }
}

/**
 * Belt/rank badge with color indicator
 */
@Composable
private fun BeltBadge(
    belt: Belt,
    modifier: Modifier = Modifier
) {
    // Use actual belt color for background, white background for White Belt
    val beltColor = try {
        Color(belt.colorHex.toColorInt())
    } catch (e: Exception) {
        Color.White
    }

    val backgroundColor = when (belt) {
        Belt.WHITE -> Color.White
        else -> beltColor.copy(alpha = 0.2f)
    }

    val textColor = when (belt) {
        Belt.WHITE -> Color(0xFF1A1A1A) // Dark gray/black for white background
        else -> TextPrimary
    }

    val borderColor = when (belt) {
        Belt.WHITE -> Color(0xFFE0E0E0) // Light gray border for white background
        else -> beltColor.copy(alpha = 0.5f)
    }

    Surface(
        modifier = modifier,
        shape = MaterialTheme.shapes.small,
        color = backgroundColor,
        tonalElevation = 2.dp
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            // Belt color indicator
            Box(
                modifier = Modifier
                    .size(20.dp)
                    .clip(CircleShape)
                    .background(beltColor)
                    .border(1.dp, borderColor, CircleShape)
            )

            Spacer(modifier = Modifier.width(8.dp))

            // Belt name
            Text(
                text = belt.displayName,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold,
                color = textColor
            )
        }
    }
}

/**
 * Streak counter with fire emoji
 */
@Composable
private fun StreakCounter(
    streakDays: Int,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier,
        shape = MaterialTheme.shapes.small,
        color = FightRed.copy(alpha = 0.2f),
        tonalElevation = 2.dp
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Fire emoji for streak - universal indicator
            Text(
                text = "🔥",
                fontSize = 20.sp
            )

            Spacer(modifier = Modifier.width(6.dp))

            // Streak number
            Text(
                text = stringResource(R.string.streak_count, streakDays),
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        }
    }
}

/**
 * Placeholder shown while loading or on error
 */
@Composable
private fun UserTopBarPlaceholder() {
    Row(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = Spacing.medium, vertical = Spacing.small),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Placeholder profile picture
        Box(
            modifier = Modifier
                .size(56.dp)
                .clip(CircleShape)
                .background(FightDarkElevated)
                .border(2.dp, BorderMedium, CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = null,
                modifier = Modifier.size(32.dp),
                tint = TextTertiary
            )
        }

        Spacer(modifier = Modifier.width(Spacing.medium))

        // Placeholder belt
        Box(
            modifier = Modifier
                .weight(1f)
                .background(FightDarkElevated, FightingShapes.small)
                .border(1.dp, BorderMedium, FightingShapes.small)
                .padding(horizontal = Spacing.small, vertical = Spacing.extraSmall)
        ) {
            Text(
                text = stringResource(R.string.loading),
                style = MaterialTheme.typography.bodyMedium,
                color = TextTertiary
            )
        }

        Spacer(modifier = Modifier.width(Spacing.medium))

        // Placeholder streak
        Box(
            modifier = Modifier
                .background(FightDarkElevated, FightingShapes.small)
                .border(1.dp, BorderMedium, FightingShapes.small)
                .padding(horizontal = Spacing.small, vertical = Spacing.extraSmall)
        ) {
            Text(
                text = "🔥 -",
                style = MaterialTheme.typography.bodyMedium,
                color = TextTertiary
            )
        }
    }
}

