package {{PACKAGE_NAME}}.feature.home

import {{PACKAGE_NAME}}.core.model.AnalysisService
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

data class HomeState(
    val result: Long? = null,
    val running: Boolean = false,
    val failed: Boolean = false,
)

class HomeModel(
    private val service: AnalysisService,
) {
    private val mutableState = MutableStateFlow(HomeState())
    val state = mutableState.asStateFlow()

    suspend fun run() {
        if (mutableState.value.running) return
        mutableState.value = HomeState(running = true)
        try {
            mutableState.value = HomeState(result = service.analyze(longArrayOf(10, 20, 12)))
        } catch (cancelled: CancellationException) {
            mutableState.value = HomeState()
            throw cancelled
        } catch (_: Exception) {
            mutableState.value = HomeState(failed = true)
        }
    }
}

class HomeFactory(
    private val service: AnalysisService,
) {
    fun makeModel(): HomeModel = HomeAssembly.make(service)
}
