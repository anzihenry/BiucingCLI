package {{PACKAGE_NAME}}.core.sharedcore

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.suspendCancellableCoroutine
import java.util.concurrent.Executors

class CoreException(
    val code: Int,
) : Exception("Shared core error: $code")

internal object NativeBridge {
    init {
        System.loadLibrary("biucing_shared")
    }

    external fun create(): Long

    external fun destroy(handle: Long)

    external fun tokenCreate(): Long

    external fun tokenCancel(token: Long)

    external fun tokenDestroy(token: Long)

    external fun analyze(
        handle: Long,
        token: Long,
        values: LongArray,
    ): Long

    external fun completed(handle: Long): Long
}

/** One session serializes its native calls; accepted work retains this owner until completion. */
class CoreSession {
    private val gate = Any()
    private val handle = NativeBridge.create()
    private val executor =
        Executors.newSingleThreadExecutor { work ->
            Thread(work, "SharedCore-session").apply { isDaemon = true }
        }
    private val tokens = mutableSetOf<Token>()
    private var accepting = true
    private val closed = CompletableDeferred<Unit>()

    private class Token {
        private var pointer = NativeBridge.tokenCreate()

        @Synchronized fun cancel() {
            if (pointer != 0L) NativeBridge.tokenCancel(pointer)
        }

        @Synchronized fun release() {
            if (pointer != 0L) NativeBridge.tokenDestroy(pointer)
            pointer = 0L
        }

        fun value(): Long = pointer // Only the queue releases; cancellation never changes it.
    }

    suspend fun analyze(values: LongArray): Long {
        require(values.size <= 1_000_000) { "At most 1,000,000 values" }
        val snapshot = values.copyOf()
        return suspendCancellableCoroutine { continuation ->
            synchronized(gate) {
                if (!accepting) {
                    continuation.resumeWith(Result.failure(CoreException(4)))
                    return@synchronized
                }
                val token = Token()
                tokens.add(token)
                continuation.invokeOnCancellation { token.cancel() }
                executor.execute {
                    val result =
                        runCatching { NativeBridge.analyze(handle, token.value(), snapshot) }
                            .recoverCatching { error ->
                                if (error is CoreException && error.code == 3) throw CancellationException("Core operation cancelled")
                                throw error
                            }
                    token.release()
                    synchronized(gate) { tokens.remove(token) }
                    continuation.resumeWith(result)
                }
            }
        }
    }

    suspend fun completedOperations(): Long =
        suspendCancellableCoroutine { continuation ->
            synchronized(gate) {
                if (!accepting) {
                    continuation.resumeWith(Result.failure(CoreException(4)))
                } else {
                    executor.execute { continuation.resumeWith(runCatching { NativeBridge.completed(handle) }) }
                }
            }
        }

    /** Initiates idempotent shutdown without blocking the UI or depending on a caller's coroutine. */
    fun requestClose() {
        synchronized(gate) {
            if (!accepting) return
            accepting = false
            tokens.forEach { it.cancel() }
            executor.execute {
                try {
                    NativeBridge.destroy(handle)
                    closed.complete(Unit)
                } catch (error: Throwable) {
                    closed.completeExceptionally(error)
                } finally {
                    executor.shutdown()
                }
            }
        }
    }

    suspend fun close() {
        requestClose()
        closed.await()
    }
}
