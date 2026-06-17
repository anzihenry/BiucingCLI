package {{PACKAGE_NAME}}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import {{PACKAGE_NAME}}.core.designsystem.BiucingSpacing
import {{PACKAGE_NAME}}.core.designsystem.BiucingTheme
import {{PACKAGE_NAME}}.feature.home.HomeRoute
import {{PACKAGE_NAME}}.feature.settings.SettingsRoute

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BiucingTheme {
                Surface {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(BiucingSpacing.large),
                        verticalArrangement = Arrangement.spacedBy(BiucingSpacing.large),
                    ) {
                        HomeRoute()
                        SettingsRoute()
                    }
                }
            }
        }
    }
}
