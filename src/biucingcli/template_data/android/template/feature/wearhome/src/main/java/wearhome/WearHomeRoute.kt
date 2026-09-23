package {{PACKAGE_NAME}}.feature.wearhome

import androidx.compose.foundation.focusable
import androidx.compose.foundation.gestures.scrollBy
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.input.rotary.onRotaryScrollEvent
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.wear.compose.foundation.lazy.ScalingLazyColumn
import androidx.wear.compose.foundation.lazy.rememberScalingLazyListState
import androidx.wear.compose.material.Chip
import androidx.wear.compose.material.MaterialTheme
import androidx.wear.compose.material.PositionIndicator
import androidx.wear.compose.material.Scaffold
import androidx.wear.compose.material.SwipeToDismissBox
import androidx.wear.compose.material.Text
import androidx.wear.compose.material.TimeText
import {{PACKAGE_NAME}}.core.model.HomeOutput
import {{PACKAGE_NAME}}.core.network.AppEnvironmentProvider
import {{PACKAGE_NAME}}.feature.home.HomeModel
import kotlinx.coroutines.launch

@Composable
@Suppress("ktlint:standard:function-naming")
fun WearHomeRoute(model: HomeModel, title: String, onOutput: (HomeOutput) -> Unit) {
    val state by model.state.collectAsState()
    val scope = rememberCoroutineScope()
    val list = rememberScalingLazyListState()
    val rotaryFocus = remember { FocusRequester() }
    LaunchedEffect(Unit) { rotaryFocus.requestFocus() }
    MaterialTheme {
        Scaffold(timeText = { TimeText() }, positionIndicator = { PositionIndicator(scalingLazyListState = list) }) {
            ScalingLazyColumn(
                state = list,
                modifier = Modifier.fillMaxSize()
                    .onRotaryScrollEvent { event ->
                        scope.launch { list.scrollBy(event.verticalScrollPixels) }
                        true
                    }
                    .focusRequester(rotaryFocus).focusable(),
            ) {
                item { Text(title, textAlign = TextAlign.Center) }
                item { Text(state.result?.toString() ?: "—", style = MaterialTheme.typography.display2) }
                if (state.failed) item { Text(stringResource(R.string.device_error)) }
                item {
                    Chip(
                        onClick = { scope.launch { model.run() } },
                        enabled = !state.running,
                        label = { Text(stringResource(R.string.device_calculate)) },
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
                item {
                    Chip(
                        onClick = { onOutput(HomeOutput.ShowSettings) },
                        label = { Text(stringResource(R.string.device_about)) },
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            }
        }
    }
}

@Composable
@Suppress("ktlint:standard:function-naming")
fun WearAboutRoute(provider: AppEnvironmentProvider, onBack: () -> Unit) {
    MaterialTheme {
        SwipeToDismissBox(onDismissed = onBack) { background ->
            if (!background) {
                ScalingLazyColumn {
                    item { Text("Wear OS", style = MaterialTheme.typography.title2) }
                    item { Text(provider.environment().releaseChannel) }
                    item { Chip(onClick = onBack, label = { Text(stringResource(R.string.device_back)) }) }
                }
            }
        }
    }
}
