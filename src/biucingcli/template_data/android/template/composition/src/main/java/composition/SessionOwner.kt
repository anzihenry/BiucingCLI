package {{PACKAGE_NAME}}.composition

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

// The Activity's ViewModelStore owns the business session, including work while a route is covered.
class SessionOwner : ViewModel() {
    private val graph = ShellAssembly.session()
    val home = graph.home().makeModel()
    val environment = graph.environment()
    private var ending = false

    init {
        graph.service().invokeOnClose { error ->
            if (error != null) Log.e("SessionOwner", "Session close failed", error)
        }
    }

    fun run() {
        if (!ending) viewModelScope.launch { home.run() }
    }

    // Cancelling a caller's wait never cancels the shared native completion signal.
    suspend fun close() {
        requestClose()
        graph.service().close()
    }

    private fun requestClose() {
        if (ending) return
        ending = true
        home.stop()
        graph.service().requestClose()
    }

    override fun onCleared() {
        requestClose()
    }
}
