import HomeFeature
import SwiftUI

/// A business session survives temporary visibility changes. Each scene owns one instance.
@MainActor
final class SessionOwner: ObservableObject {
    let composition: AppComposition
    let model: HomeModel
    @Published private(set) var isClosed = false
    private var closing: Task<Void, Never>?
    private let release: @Sendable () async -> Void

    init(sessions: SessionFactory) {
        let composition = sessions.make()
        self.composition = composition
        let model = composition.home.makeModel()
        self.model = model
        release = { await model.close() }
    }

    /// Explicit business exit can await completion. Repeated exits join the same task.
    func close() async {
        if closing == nil {
            isClosed = true
            let model = model
            closing = Task { await model.close() }
        }
        await closing?.value
    }

    deinit {
        // Scene removal releases the owner; merely covering a view does not.
        // Capture the resource, never self, so in-flight native work is kept alive until close finishes.
        let release = release
        Task { await release() }
    }
}
