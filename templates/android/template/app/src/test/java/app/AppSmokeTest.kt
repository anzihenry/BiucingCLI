package {{PACKAGE_NAME}}

import org.junit.Assert.assertEquals
import org.junit.Test

class AppSmokeTest {
    @Test
    fun projectNameIsStable() {
        assertEquals("{{PROJECT_NAME}}", "{{PROJECT_NAME}}")
    }
}
