package {{PACKAGE_NAME}}.core.sharedcore

import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.cancel
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CoreSessionTest {
    @Test fun valueOverflowAndIsolation() =
        runBlocking {
            val first = CoreSession()
            val second = CoreSession()
            try {
                assertEquals(42L, first.analyze(longArrayOf(10, 20, 12)))
                val error = runCatching { first.analyze(longArrayOf(Long.MAX_VALUE, 1)) }.exceptionOrNull()
                assertTrue(error is CoreException && error.code == 2)
                assertEquals(1L, first.completedOperations())
                assertEquals(0L, second.completedOperations())
                assertEquals(0L, second.analyze(longArrayOf()))
            } finally {
                first.close()
                second.close()
            }
        }

    @Test fun concurrentWorkAndRepeatedClose() =
        runBlocking {
            val session = CoreSession()
            val results = (1..32).map { async { session.analyze(longArrayOf(it.toLong())) } }.awaitAll()
            assertEquals((1L..32L).toList(), results)
            assertEquals(32L, session.completedOperations())
            (1..8).map { async { session.close() } }.awaitAll()
            val error = runCatching { session.analyze(longArrayOf(1)) }.exceptionOrNull()
            assertTrue(error is CoreException && error.code == 4)
        }

    @Test fun cancellationAndCloseRaceDoNotReleaseLiveHandles() =
        runBlocking {
            repeat(20) {
                val session = CoreSession()
                val jobs =
                    (1..12).map {
                        launch(start = CoroutineStart.UNDISPATCHED) {
                            runCatching { session.analyze(LongArray(100_000) { 1 }) }
                        }
                    }
                jobs.forEach { it.cancel() }
                session.close()
                jobs.forEach { it.join() }
                session.close()
            }
        }

    @Test fun preCancelledOperationDoesNotCommit() =
        runBlocking {
            val session = CoreSession()
            try {
                val job =
                    launch(start = CoroutineStart.UNDISPATCHED) {
                        coroutineContext.cancel()
                        session.analyze(longArrayOf(7))
                    }
                job.cancelAndJoin()
                assertEquals(0L, session.completedOperations())
            } finally {
                session.close()
            }
        }
}
