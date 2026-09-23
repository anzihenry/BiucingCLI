package {{PACKAGE_NAME}}.wear

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import {{PACKAGE_NAME}}.composition.SessionOwner
import {{PACKAGE_NAME}}.core.model.HomeOutput
import {{PACKAGE_NAME}}.feature.wearhome.WearHomeRoute
import {{PACKAGE_NAME}}.feature.wearhome.WearAboutRoute

class MainActivity : ComponentActivity() {
    private val session: SessionOwner by viewModels()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            var about by rememberSaveable { mutableStateOf(false) }
            BackHandler(enabled = about) { about = false }
            if (about) {
                WearAboutRoute(session.environment) { about = false }
            } else {
                WearHomeRoute(session.home, title = "{{DISPLAY_NAME_KOTLIN}}") { output ->
                    when (output) { HomeOutput.ShowSettings -> about = true }
                }
            }
        }
    }
}
