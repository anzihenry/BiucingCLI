package {{PACKAGE_NAME}}.core.network

data class AppEnvironment(
    val apiBaseUrl: String,
    val releaseChannel: String,
)

interface AppEnvironmentProvider {
    fun environment(): AppEnvironment
}

class DefaultAppEnvironmentProvider : AppEnvironmentProvider {
    override fun environment(): AppEnvironment = AppEnvironment(
        apiBaseUrl = "https://api.example.internal",
        releaseChannel = "beta",
    )
}
