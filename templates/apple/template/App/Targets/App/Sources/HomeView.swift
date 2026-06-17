import DesignSystem
import SwiftUI

struct HomeView: View {
    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 16) {
                Text("{{DISPLAY_NAME}}")
                    .font(BiucingTheme.titleFont)

                Text("Tuist-generated starter for Apple platform teams.")
                    .font(BiucingTheme.bodyFont)
                    .foregroundStyle(.secondary)

                VStack(alignment: .leading, spacing: 8) {
                    Label("Bundle ID: {{BUNDLE_IDENTIFIER}}", systemImage: "shippingbox")
                    Label("Platform: {{APPLE_PLATFORM_NAME}}", systemImage: "app")
                    Label("Minimum OS: {{MINIMUM_OS_VERSION}}", systemImage: "gear")
                    Label("Team: {{DEVELOPMENT_TEAM}}", systemImage: "person.3")
                }
                .font(BiucingTheme.captionFont)
            }
            .padding(24)
            .navigationTitle("Overview")
        }
    }
}

#Preview {
    HomeView()
}
