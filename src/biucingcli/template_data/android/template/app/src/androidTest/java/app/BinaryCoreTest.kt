package {{PACKAGE_NAME}}

import androidx.test.ext.junit.runners.AndroidJUnit4
import {{PACKAGE_NAME}}.composition.ShellAssembly
import {{PACKAGE_NAME}}.core.sharedcore.CoreSession
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class BinaryCoreTest {
    @Test fun publishedNativeCoreAndShellFactoriesWork() =
        runBlocking {
            val first = ShellAssembly.session()
            val second = ShellAssembly.session()
            try {
                assertEquals(42L, first.service().analyze(longArrayOf(10, 20, 12)))
                first.service().close()
                assertEquals(7L, second.service().analyze(longArrayOf(7)))
            } finally {
                first.service().close()
                second.service().close()
            }
            val core = CoreSession()
            core.close()
            core.close()
        }
}
