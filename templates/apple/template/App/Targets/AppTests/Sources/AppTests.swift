import AppServices
@testable import {{SWIFT_MODULE_NAME}}
import XCTest

final class AppTests: XCTestCase {
    func testHomeViewModelBuildsOverviewFacts() {
        let viewModel = HomeViewModel(
            displayName: "Pulse Mac",
            bundleIdentifier: "com.example.pulsemac",
            platformName: "macOS",
            minimumOSVersion: "26.0",
            developmentTeam: "ABCDE12345"
        )

        XCTAssertEqual(viewModel.title, "Pulse Mac")
        XCTAssertEqual(viewModel.subtitle, "Tuist-generated starter for Apple platform teams.")
        XCTAssertEqual(
            viewModel.facts,
            [
                StarterFact(label: "Bundle ID", systemImage: "shippingbox", value: "com.example.pulsemac"),
                StarterFact(label: "Platform", systemImage: "app", value: "macOS"),
                StarterFact(label: "Minimum OS", systemImage: "gear", value: "26.0"),
                StarterFact(label: "Team", systemImage: "person.3", value: "ABCDE12345"),
            ]
        )
    }

    func testHomeViewModelUsesMockChecklistProvider() {
        let viewModel = HomeViewModel(
            displayName: "Pulse Mac",
            bundleIdentifier: "com.example.pulsemac",
            platformName: "macOS",
            minimumOSVersion: "26.0",
            developmentTeam: "ABCDE12345",
            checklistProvider: MockReleaseChecklistProvider(
                items: [
                    "Check beta notes.",
                    "Share build with QA.",
                ]
            )
        )

        XCTAssertEqual(
            viewModel.releaseChecklist(),
            [
                "Check beta notes.",
                "Share build with QA.",
            ]
        )
    }
}

private struct MockReleaseChecklistProvider: ReleaseChecklistProviding {
    let items: [String]

    func releaseChecklistItems() -> [String] {
        items
    }
}
