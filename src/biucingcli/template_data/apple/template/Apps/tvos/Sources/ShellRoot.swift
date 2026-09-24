import HomeFeature
import SwiftUI

struct ShellRoot: View {
    @StateObject private var owner: SessionOwner
    @State private var aboutPresented = false

    init(application: ApplicationComposition) {
        _owner = StateObject(wrappedValue: SessionOwner(sessions: application.sessions))
    }

    var body: some View {
        NavigationStack {
            owner.composition.home.makeView(model: owner.model) { output in
                switch output {
                case .showAbout: aboutPresented = true
                @unknown default: break
                }
            }
            .navigationTitle("{{DISPLAY_NAME_SWIFT}}")
            .navigationDestination(isPresented: $aboutPresented) {
                Text("{{DISPLAY_NAME_SWIFT}}")
            }
        }
        // No visibility-triggered teardown: the scene's state storage owns the session.
    }
}
