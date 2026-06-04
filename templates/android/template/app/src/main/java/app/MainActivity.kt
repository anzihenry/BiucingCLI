package {{PACKAGE_NAME}}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.Surface
import {{PACKAGE_NAME}}.core.designsystem.BiucingTheme
import {{PACKAGE_NAME}}.feature.home.HomeRoute

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BiucingTheme {
                Surface {
                    HomeRoute()
                }
            }
        }
    }
}
