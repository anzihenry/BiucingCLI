import SwiftUI

@main
struct ProductApp: App {
    private let application = ApplicationComposition()

    var body: some Scene {
        WindowGroup { ShellRoot(application: application) }
    }
}
