package {{PACKAGE_NAME}}.feature.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.unit.dp
import {{PACKAGE_NAME}}.core.network.DefaultAppEnvironmentProvider

@Composable
@Suppress("ktlint:standard:function-naming")
fun SettingsRoute() {
    val environment = DefaultAppEnvironmentProvider().environment()

    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            text = "Release channel: ${environment.releaseChannel}",
            style = MaterialTheme.typography.titleMedium,
        )
        Text(
            text = "API base URL: ${environment.apiBaseUrl}",
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}
