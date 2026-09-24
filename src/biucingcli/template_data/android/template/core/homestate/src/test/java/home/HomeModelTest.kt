package {{PACKAGE_NAME}}.feature.home

import {{PACKAGE_NAME}}.core.model.AnalysisService
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class HomeModelTest {
    @Test fun factoryUsesInjectedService() =
        runBlocking {
            var observed = emptyList<Long>()
            val model =
                HomeFactory(
                    object : AnalysisService {
                        override suspend fun analyze(values: LongArray): Long {
                            observed = values.toList()
                            return 99
                        }
                    },
                ).makeModel()
            model.run()
            assertEquals(listOf(10L, 20L, 12L), observed)
            assertEquals(99L, model.state.value.result)
        }

    @Test fun stoppedModelRejectsNewWorkAndIgnoresLateResult() =
        runBlocking {
            val started = CompletableDeferred<Unit>()
            val finish = CompletableDeferred<Long>()
            var calls = 0
            val model =
                HomeFactory(
                    object : AnalysisService {
                        override suspend fun analyze(values: LongArray): Long {
                            calls++
                            started.complete(Unit)
                            return finish.await()
                        }
                    },
                ).makeModel()
            val work = launch { model.run() }
            started.await()
            model.stop()
            finish.complete(42)
            work.join()
            model.run()
            assertEquals(1, calls)
            assertEquals(null, model.state.value.result)
            assertEquals(false, model.state.value.running)
        }

    @Test fun failureBecomesPresentationState() =
        runBlocking {
            val model =
                HomeFactory(
                    object : AnalysisService {
                        override suspend fun analyze(values: LongArray): Long = error("fake failure")
                    },
                ).makeModel()
            model.run()
            assertTrue(model.state.value.failed)
            assertEquals(false, model.state.value.running)
        }
}
