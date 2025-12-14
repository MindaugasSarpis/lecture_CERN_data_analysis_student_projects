package com.arnasmat.fightingapp.presentation.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import com.arnasmat.fightingapp.ui.theme.*

/**
 * DESIGN SYSTEM - TOP APP BAR COMPONENTS
 * Standardized top app bars for the fighting app
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FightTopAppBar(
    title: String,
    modifier: Modifier = Modifier,
    onNavigationClick: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {},
    backgroundColor: Color = FightDarkSurface,
    scrollBehavior: TopAppBarScrollBehavior? = null
) {
    TopAppBar(
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        },
        modifier = modifier,
        navigationIcon = {
            onNavigationClick?.let {
                FightIconButton(
                    icon = Icons.AutoMirrored.Filled.ArrowBack,
                    onClick = it,
                    contentDescription = "Back",
                    backgroundColor = Color.Transparent,
                    iconTint = TextPrimary
                )
            }
        },
        actions = actions,
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = backgroundColor,
            titleContentColor = TextPrimary,
            navigationIconContentColor = TextPrimary,
            actionIconContentColor = TextPrimary,
            scrolledContainerColor = backgroundColor
        ),
        scrollBehavior = scrollBehavior
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FightLargeTopAppBar(
    title: String,
    modifier: Modifier = Modifier,
    onNavigationClick: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {},
    backgroundColor: Color = FightDarkSurface,
    scrollBehavior: TopAppBarScrollBehavior? = null
) {
    LargeTopAppBar(
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.displaySmall,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        },
        modifier = modifier,
        navigationIcon = {
            onNavigationClick?.let {
                FightIconButton(
                    icon = Icons.AutoMirrored.Filled.ArrowBack,
                    onClick = it,
                    contentDescription = "Back",
                    backgroundColor = Color.Transparent,
                    iconTint = TextPrimary
                )
            }
        },
        actions = actions,
        colors = TopAppBarDefaults.largeTopAppBarColors(
            containerColor = backgroundColor,
            titleContentColor = TextPrimary,
            navigationIconContentColor = TextPrimary,
            actionIconContentColor = TextPrimary,
            scrolledContainerColor = backgroundColor
        ),
        scrollBehavior = scrollBehavior
    )
}

