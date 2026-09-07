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

{{APPLE_HOME_BODY}}
}

#Preview {
    HomeView()
}
