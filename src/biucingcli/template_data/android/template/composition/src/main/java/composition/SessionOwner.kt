package {{PACKAGE_NAME}}.composition

import androidx.lifecycle.ViewModel

// ViewModel retains the business session through configuration changes, never through process death.
class SessionOwner : ViewModel() {
    private val graph = ShellAssembly.session()
    val home = graph.home().makeModel()
    val environment = graph.environment()

    override fun onCleared() {
        graph.service().requestClose()
    }
}
