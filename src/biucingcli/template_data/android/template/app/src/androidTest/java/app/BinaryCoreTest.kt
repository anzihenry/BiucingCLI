package {{PACKAGE_NAME}}

import androidx.lifecycle.ViewModelStore
import androidx.test.ext.junit.runners.AndroidJUnit4
import {{PACKAGE_NAME}}.composition.SessionOwner
import {{PACKAGE_NAME}}.composition.ShellAssembly
import {{PACKAGE_NAME}}.core.sharedcore.CoreSession
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertSame
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class BinaryCoreTest {
    @Test fun ownerClearSignalsNativeCompletionAndKeepsOtherSessionAlive() =
        runBlocking {
            val store = ViewModelStore()
            val first = SessionOwner()
            val second = SessionOwner()
            store.put("business", first)
            val retained = first.home
            first.home.run()
            assertSame(retained, first.home)
            assertEquals(42L, retained.state.value.result)
            assertFalse(first.home === second.home)
            store.clear()
            first.close()
            first.close()
            first.home.run()
            assertEquals(42L, first.home.state.value.result)
            second.home.run()
            assertEquals(42L, second.home.state.value.result)
            second.close()
        }

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
