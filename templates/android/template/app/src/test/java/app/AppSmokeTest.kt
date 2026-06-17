package {{PACKAGE_NAME}}

import {{PACKAGE_NAME}}.core.testing.FakeAppEnvironmentProvider
import org.junit.Assert.assertEquals
import org.junit.Test

class AppSmokeTest {
    @Test
    fun projectNameIsStable() {
        assertEquals("{{PROJECT_NAME}}", "{{PROJECT_NAME}}")
    }

    @Test
    fun fakeEnvironmentProviderExposesPredictableReleaseChannel() {
        val environment = FakeAppEnvironmentProvider().environment()

        assertEquals("beta", environment.releaseChannel)
    }
}
