package com.arnasmat.fightingapp.presentation.navigation

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import androidx.navigation.compose.currentBackStackEntryAsState
import com.arnasmat.fightingapp.ui.theme.*

/**
 * Custom Bottom Navigation Bar with Design System
 * Vinted-style: Clean design with filled pill for selected item
 */
@Composable
fun BottomNavigationBar(navController: NavController) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = FightDarkSurface,
        tonalElevation = Elevation.medium,
        shadowElevation = Elevation.large
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .navigationBarsPadding()
        ) {
            // Subtle top gradient for depth
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(80.dp) // Increased from 70dp for more text space
                    .background(
                        brush = Brush.verticalGradient(
                            colors = listOf(
                                BorderLight.copy(alpha = 0.05f),
                                Color.Transparent
                            )
                        )
                    )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(
                            horizontal = Spacing.small,
                            vertical = Spacing.small
                        ),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Screen.bottomNavScreens.forEach { screen ->
                        BottomNavItem(
                            screen = screen,
                            isSelected = currentRoute == screen.route,
                            onClick = {
                                navController.navigate(screen.route) {
                                    popUpTo(navController.graph.startDestinationId) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun RowScope.BottomNavItem(
    screen: Screen,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    val interactionSource = remember { MutableInteractionSource() }

    // Smooth color animations - only for icon and text, not background
    val iconColor by animateColorAsState(
        targetValue = if (isSelected) FightPrimary else TextSecondary,
        animationSpec = tween(300),
        label = "nav_icon"
    )

    val textColor by animateColorAsState(
        targetValue = if (isSelected) FightPrimary else TextSecondary,
        animationSpec = tween(300),
        label = "nav_text"
    )

    // Clean nav item: only icon and text change color, no background
    Column(
        modifier = Modifier
            .weight(1f)
            .clickable(
                interactionSource = interactionSource,
                indication = null,
                onClick = onClick
            )
            .padding(
                horizontal = Spacing.extraSmall,
                vertical = Spacing.small
            ),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = screen.icon,
            contentDescription = stringResource(screen.titleRes),
            tint = iconColor,
            modifier = Modifier.size(
                if (isSelected) 28.dp else 24.dp // Larger icons
            )
        )

        Spacer(modifier = Modifier.height(Spacing.extraSmall))

        Text(
            text = stringResource(screen.titleRes),
            style = MaterialTheme.typography.labelMedium, // Changed from labelSmall to labelMedium
            color = textColor,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
            maxLines = 1
        )
    }
}
