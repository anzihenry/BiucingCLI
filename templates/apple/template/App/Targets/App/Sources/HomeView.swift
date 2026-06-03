import SwiftUI
import DesignSystem

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
                    Label("Minimum iOS: {{IOS_MINIMUM_VERSION}}", systemImage: "iphone")
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
