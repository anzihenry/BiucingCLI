package {{PACKAGE_NAME}}.core.model

interface AnalysisService {
    suspend fun analyze(values: LongArray): Long
}

sealed interface HomeOutput {
    data object ShowSettings : HomeOutput
}
