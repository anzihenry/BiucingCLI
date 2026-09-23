import HomeFeature
import SwiftUI

struct ShellRoot: View {
    let application: ApplicationComposition

    @State private var composition: AppComposition?
    @State private var aboutPresented = false

    var body: some View {
        NavigationStack {
            Group {
                if let composition {
                    composition.home.makeView { output in
                        switch output {
                        case .showAbout: aboutPresented = true
                        @unknown default: break
                        }
                    }
                } else {
                    ProgressView()
                }
            }
            .navigationTitle("{{DISPLAY_NAME_SWIFT}}")
            .navigationDestination(isPresented: $aboutPresented) {
                Text("{{DISPLAY_NAME_SWIFT}}")
            }
        }
        .onAppear {
            if composition == nil {
                composition = application.sessions.make()
            }
        }
        .onDisappear {
            let departingSession = composition
            composition = nil
            Task { await departingSession?.close() }
        }
    }
}
