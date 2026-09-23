package {{PACKAGE_NAME}}.feature.tvhome

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusProperties
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.tv.material3.Button
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import {{PACKAGE_NAME}}.core.model.HomeOutput
import {{PACKAGE_NAME}}.core.network.AppEnvironmentProvider
import {{PACKAGE_NAME}}.feature.home.HomeModel
import kotlinx.coroutines.launch

@Composable
@Suppress("ktlint:standard:function-naming")
fun TvHomeRoute(model: HomeModel, title: String, onOutput: (HomeOutput) -> Unit) {
    val state by model.state.collectAsState()
    val scope = rememberCoroutineScope()
    val calculate = remember { FocusRequester() }
    val about = remember { FocusRequester() }
    LaunchedEffect(Unit) { calculate.requestFocus() }
    MaterialTheme {
        Column(
            Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(48.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp),
        ) {
            Text(title, style = MaterialTheme.typography.headlineLarge)
            Text(state.result?.toString() ?: "—", style = MaterialTheme.typography.displayLarge)
            if (state.failed) Text(stringResource(R.string.device_error))
            Row(horizontalArrangement = Arrangement.spacedBy(24.dp)) {
                // Keep focus stable while work runs; the shared model rejects duplicate submissions.
                Button(onClick = { scope.launch { model.run() } }, modifier = Modifier.focusRequester(calculate).focusProperties { right = about }) {
                    Text(stringResource(R.string.device_calculate))
                }
                Button(onClick = { onOutput(HomeOutput.ShowSettings) }, modifier = Modifier.focusRequester(about).focusProperties { left = calculate }) {
                    Text(stringResource(R.string.device_about))
                }
            }
        }
    }
}

@Composable
@Suppress("ktlint:standard:function-naming")
fun TvAboutRoute(provider: AppEnvironmentProvider, onBack: () -> Unit) {
    val back = remember { FocusRequester() }
    LaunchedEffect(Unit) { back.requestFocus() }
    MaterialTheme {
        Column(
            Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(48.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp),
        ) {
            Text("Android TV", style = MaterialTheme.typography.headlineLarge)
            Text(provider.environment().releaseChannel)
            Button(onClick = onBack, modifier = Modifier.focusRequester(back)) { Text(stringResource(R.string.device_back)) }
        }
    }
}
