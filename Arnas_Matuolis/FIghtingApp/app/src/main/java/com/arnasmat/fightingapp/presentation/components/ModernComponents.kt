package com.arnasmat.fightingapp.presentation.components
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.arnasmat.fightingapp.ui.theme.*
/**
 * MODERN DESIGN SYSTEM COMPONENTS
 * Whoop/Revolut-inspired minimal design
 * Less cards, more structure
 */
// List item without card
@Composable
fun FightListItem(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    leadingContent: (@Composable () -> Unit)? = null,
    trailingContent: (@Composable () -> Unit)? = null,
    showDivider: Boolean = true,
    backgroundColor: Color = Color.Transparent,
    content: @Composable RowScope.() -> Unit
) {
    val interactionSource = remember { MutableInteractionSource() }
    Column(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(backgroundColor)
                .then(
                    if (onClick != null) {
                        Modifier.clickable(
                            interactionSource = interactionSource,
                            indication = null,
                            onClick = onClick
                        )
                    } else Modifier
                )
                .padding(vertical = Spacing.medium),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(Spacing.medium)
        ) {
            leadingContent?.invoke()
            Row(
                modifier = Modifier.weight(1f),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(Spacing.medium),
                content = content
            )
            trailingContent?.invoke()
        }
        if (showDivider) {
            HorizontalDivider(
                modifier = Modifier.fillMaxWidth(),
                thickness = 1.dp,
                color = BorderLight
            )
        }
    }
}
// Surface section for grouped content
@Composable
fun FightSurfaceSection(
    modifier: Modifier = Modifier,
    backgroundColor: Color = FightDarkSurface,
    borderColor: Color? = null,
    content: @Composable ColumnScope.() -> Unit
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .background(backgroundColor, shape = FightingShapes.medium)
            .then(
                borderColor?.let {
                    Modifier.border(
                        width = 1.dp,
                        color = it,
                        shape = FightingShapes.medium
                    )
                } ?: Modifier
            )
            .padding(Spacing.medium),
        content = content
    )
}
