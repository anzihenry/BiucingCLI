package {{PACKAGE_NAME}}.feature.home

import {{PACKAGE_NAME}}.core.model.AnalysisService
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
