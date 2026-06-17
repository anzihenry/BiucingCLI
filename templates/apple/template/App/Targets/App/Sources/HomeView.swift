import DesignSystem
import SwiftUI

struct HomeView: View {
    private let viewModel = HomeViewModel(
        displayName: "{{DISPLAY_NAME}}",
        bundleIdentifier: "{{BUNDLE_IDENTIFIER}}",
        platformName: "{{APPLE_PLATFORM_NAME}}",
        minimumOSVersion: "{{MINIMUM_OS_VERSION}}",
        developmentTeam: "{{DEVELOPMENT_TEAM}}"
    )

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 16) {
                Text(viewModel.title)
                    .font(BiucingTheme.titleFont)

                Text(viewModel.subtitle)
                    .font(BiucingTheme.bodyFont)
                    .foregroundStyle(.secondary)

                VStack(alignment: .leading, spacing: 8) {
                    ForEach(viewModel.facts, id: \.label) { fact in
                        Label("\(fact.label): \(fact.value)", systemImage: fact.systemImage)
                    }
                }
                .font(BiucingTheme.captionFont)

                VStack(alignment: .leading, spacing: 8) {
                    Text("Release Checklist")
                        .font(BiucingTheme.sectionTitleFont)

                    ForEach(viewModel.releaseChecklist(), id: \.self) { item in
                        Label(item, systemImage: "checkmark.circle")
                    }
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
