package {{PACKAGE_NAME}}

import {{PACKAGE_NAME}}.core.model.AnalysisService
import {{PACKAGE_NAME}}.core.sharedcore.CoreSession

internal class NativeAnalysisService : AnalysisService {
    private val core = CoreSession()

    override suspend fun analyze(values: LongArray): Long = core.analyze(values)

    fun requestClose() = core.requestClose()

    suspend fun close() = core.close()
}
