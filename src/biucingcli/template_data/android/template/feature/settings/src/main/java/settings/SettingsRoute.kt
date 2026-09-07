package {{PACKAGE_NAME}}.feature.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import {{PACKAGE_NAME}}.core.designsystem.AppSectionCard
import {{PACKAGE_NAME}}.core.designsystem.BiucingSpacing
import {{PACKAGE_NAME}}.core.designsystem.StatusBadge
import {{PACKAGE_NAME}}.core.network.DefaultAppEnvironmentProvider

@Composable
@Suppress("ktlint:standard:function-naming")
fun SettingsRoute() {
    val environment = DefaultAppEnvironmentProvider().environment()

    AppSectionCard(
        title = "Environment",
        eyebrow = "Shared Config",
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(BiucingSpacing.small)) {
            StatusBadge(text = "Release channel: ${environment.releaseChannel}")
            Text(
                text = "API base URL: ${environment.apiBaseUrl}",
                style = MaterialTheme.typography.bodyMedium,
            )
            Text(
                text = "Dark theme colors and reusable section cards live in core/designsystem.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}
