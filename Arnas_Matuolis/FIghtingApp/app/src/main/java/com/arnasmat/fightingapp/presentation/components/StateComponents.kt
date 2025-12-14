package com.arnasmat.fightingapp.presentation.components

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.arnasmat.fightingapp.ui.theme.*

/**
 * DESIGN SYSTEM - LOADING & STATE COMPONENTS
 * Modern loading indicators and state views
 */

// ============================================================
// LOADING INDICATORS
// ============================================================

@Composable
fun FightLoadingIndicator(
    modifier: Modifier = Modifier,
    text: String? = null,
    color: Color = FightRed
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        CircularProgressIndicator(
            modifier = Modifier.size(48.dp),
            color = color,
            strokeWidth = 4.dp
        )

        text?.let {
            Spacer(modifier = Modifier.height(Spacing.medium))
            Text(
                text = it,
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
fun FightSmallLoadingIndicator(
    modifier: Modifier = Modifier,
    color: Color = FightRed
) {
    CircularProgressIndicator(
        modifier = modifier.size(24.dp),
        color = color,
        strokeWidth = 2.dp
    )
}

@Composable
fun FightPulsingDot(
    modifier: Modifier = Modifier,
    color: Color = FightRed,
    size: androidx.compose.ui.unit.Dp = 12.dp
) {
    val infiniteTransition = rememberInfiniteTransition(label = "pulsing_dot")
    val scale by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(600, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "dot_scale"
    )
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.5f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(600, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "dot_alpha"
    )

    Box(
        modifier = modifier
            .size(size)
            .scale(scale)
            .alpha(alpha)
            .background(color, CircleShape)
    )
}

@Composable
fun FightLoadingOverlay(
    isLoading: Boolean,
    modifier: Modifier = Modifier,
    text: String? = null,
    backgroundColor: Color = OverlayBlack
) {
    AnimatedVisibility(
        visible = isLoading,
        enter = fadeIn(),
        exit = fadeOut()
    ) {
        Box(
            modifier = modifier
                .fillMaxSize()
                .background(backgroundColor),
            contentAlignment = Alignment.Center
        ) {
            FightLoadingIndicator(text = text)
        }
    }
}

// ============================================================
// EMPTY STATES
// ============================================================

@Composable
fun FightEmptyState(
    message: String,
    modifier: Modifier = Modifier,
    icon: ImageVector = Icons.Default.SearchOff,
    actionButton: @Composable (() -> Unit)? = null
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(Spacing.extraLarge),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(120.dp)
                .background(
                    color = FightDarkElevated,
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = TextTertiary,
                modifier = Modifier.size(64.dp)
            )
        }

        Spacer(modifier = Modifier.height(Spacing.large))

        Text(
            text = message,
            style = MaterialTheme.typography.titleMedium,
            color = TextSecondary,
            textAlign = TextAlign.Center
        )

        actionButton?.let {
            Spacer(modifier = Modifier.height(Spacing.large))
            it()
        }
    }
}

@Composable
fun FightCompactEmptyState(
    message: String,
    modifier: Modifier = Modifier,
    icon: ImageVector = Icons.Default.Info
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(Spacing.medium),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = TextTertiary,
            modifier = Modifier.size(Dimensions.iconSizeMedium)
        )
        Spacer(modifier = Modifier.width(Spacing.small))
        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary
        )
    }
}

// ============================================================
// ERROR STATES
// ============================================================

@Composable
fun FightErrorState(
    message: String,
    modifier: Modifier = Modifier,
    icon: ImageVector = Icons.Default.ErrorOutline,
    onRetry: (() -> Unit)? = null,
    onDismiss: (() -> Unit)? = null
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(Spacing.extraLarge),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(120.dp)
                .background(
                    color = ErrorRed.copy(alpha = 0.2f),
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = ErrorRed,
                modifier = Modifier.size(64.dp)
            )
        }

        Spacer(modifier = Modifier.height(Spacing.large))

        Text(
            text = "Error",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = ErrorRed
        )

        Spacer(modifier = Modifier.height(Spacing.small))

        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary,
            textAlign = TextAlign.Center
        )

        if (onRetry != null || onDismiss != null) {
            Spacer(modifier = Modifier.height(Spacing.large))
            Row(
                horizontalArrangement = Arrangement.spacedBy(Spacing.small)
            ) {
                onDismiss?.let {
                    FightOutlinedButton(
                        text = "Dismiss",
                        onClick = it,
                        borderColor = TextSecondary
                    )
                }
                onRetry?.let {
                    FightPrimaryButton(
                        text = "Retry",
                        onClick = it,
                        icon = Icons.Default.Refresh
                    )
                }
            }
        }
    }
}

// ============================================================
// SUCCESS STATES
// ============================================================

@Composable
fun FightSuccessState(
    message: String,
    modifier: Modifier = Modifier,
    icon: ImageVector = Icons.Default.CheckCircle,
    onDismiss: (() -> Unit)? = null
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(Spacing.extraLarge),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(120.dp)
                .background(
                    color = SuccessGreen.copy(alpha = 0.2f),
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = SuccessGreen,
                modifier = Modifier.size(64.dp)
            )
        }

        Spacer(modifier = Modifier.height(Spacing.large))

        Text(
            text = "Success!",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = SuccessGreen
        )

        Spacer(modifier = Modifier.height(Spacing.small))

        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary,
            textAlign = TextAlign.Center
        )

        onDismiss?.let {
            Spacer(modifier = Modifier.height(Spacing.large))
            FightPrimaryButton(
                text = "Done",
                onClick = it
            )
        }
    }
}

// ============================================================
// BANNERS
// ============================================================

@Composable
fun FightBanner(
    message: String,
    modifier: Modifier = Modifier,
    type: BannerType = BannerType.Info,
    onDismiss: (() -> Unit)? = null
) {
    val (backgroundColor, borderColor, textColor, icon) = when (type) {
        BannerType.Success -> Tuple4(
            SuccessGreen.copy(alpha = 0.15f),
            SuccessGreen,
            SuccessGreen,
            Icons.Default.CheckCircle
        )
        BannerType.Error -> Tuple4(
            ErrorRed.copy(alpha = 0.15f),
            ErrorRed,
            ErrorRed,
            Icons.Default.Error
        )
        BannerType.Warning -> Tuple4(
            WarningYellow.copy(alpha = 0.15f),
            WarningYellow,
            WarningYellow,
            Icons.Default.Warning
        )
        BannerType.Info -> Tuple4(
            InfoBlue.copy(alpha = 0.15f),
            InfoBlue,
            InfoBlue,
            Icons.Default.Info
        )
    }

    FightCard(
        modifier = modifier,
        backgroundColor = backgroundColor,
        borderColor = borderColor
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = textColor,
                modifier = Modifier.size(Dimensions.iconSizeMedium)
            )
            Spacer(modifier = Modifier.width(Spacing.small))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = textColor,
                modifier = Modifier.weight(1f)
            )
            onDismiss?.let {
                IconButton(onClick = it) {
                    Icon(
                        imageVector = Icons.Default.Close,
                        contentDescription = "Dismiss",
                        tint = textColor,
                        modifier = Modifier.size(Dimensions.iconSizeMedium)
                    )
                }
            }
        }
    }
}

enum class BannerType {
    Success, Error, Warning, Info
}

// Helper data class for banner configuration
private data class Tuple4<A, B, C, D>(
    val first: A,
    val second: B,
    val third: C,
    val fourth: D
)

