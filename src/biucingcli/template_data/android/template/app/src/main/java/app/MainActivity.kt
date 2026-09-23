package {{PACKAGE_NAME}}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Column
import androidx.compose.material3.Button
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import {{PACKAGE_NAME}}.core.designsystem.BiucingTheme
import {{PACKAGE_NAME}}.core.model.HomeOutput
import {{PACKAGE_NAME}}.feature.home.HomeRoute
import {{PACKAGE_NAME}}.feature.settings.SettingsRoute

// ViewModel retains the business session through configuration changes, never through process death.
class SessionOwner : ViewModel() {
    private val graph = ShellAssembly.session()
    val home = graph.home().makeModel()
    val environment = graph.environment()

    override fun onCleared() {
        graph.service().requestClose()
    }
}

class MainActivity : ComponentActivity() {
    private val session: SessionOwner by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            var settings by rememberSaveable { mutableStateOf(false) }
            BiucingTheme {
                Surface {
                    if (settings) {
                        Column {
                            SettingsRoute(session.environment)
                            Button(onClick = { settings = false }) { Text("返回") }
                        }
                    } else {
                        HomeRoute(session.home) { output ->
                            when (output) {
                                HomeOutput.ShowSettings -> settings = true
                            }
                        }
                    }
                }
            }
        }
    }
}
