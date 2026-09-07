package {{PACKAGE_NAME}}.core.testing

import {{PACKAGE_NAME}}.core.network.AppEnvironment
import {{PACKAGE_NAME}}.core.network.AppEnvironmentProvider

class FakeAppEnvironmentProvider(
    private val environment: AppEnvironment = AppEnvironment(
        apiBaseUrl = "https://staging.example.internal",
        releaseChannel = "beta",
    ),
) : AppEnvironmentProvider {
    override fun environment(): AppEnvironment = environment
}
