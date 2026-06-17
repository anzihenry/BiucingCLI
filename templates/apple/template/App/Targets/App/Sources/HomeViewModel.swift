import Foundation

struct HomeFact: Equatable {
    let label: String
    let systemImage: String
    let value: String
}

protocol ReleaseChecklistProviding {
    func releaseChecklistItems() -> [String]
}

struct DefaultReleaseChecklistProvider: ReleaseChecklistProviding {
    let bundleIdentifier: String
    let developmentTeam: String

    func releaseChecklistItems() -> [String] {
        [
            "Confirm signing for \(developmentTeam).",
            "Verify bundle identifier \(bundleIdentifier).",
            "Run make test before the next beta build.",
        ]
    }
}

struct HomeViewModel {
    let title: String
    let subtitle: String
    let facts: [HomeFact]
    private let checklistProvider: ReleaseChecklistProviding

    init(
        displayName: String,
        bundleIdentifier: String,
        platformName: String,
        minimumOSVersion: String,
        developmentTeam: String,
        checklistProvider: ReleaseChecklistProviding? = nil
    ) {
        title = displayName
        subtitle = "Tuist-generated starter for Apple platform teams."
        facts = [
            HomeFact(label: "Bundle ID", systemImage: "shippingbox", value: bundleIdentifier),
            HomeFact(label: "Platform", systemImage: "app", value: platformName),
            HomeFact(label: "Minimum OS", systemImage: "gear", value: minimumOSVersion),
            HomeFact(label: "Team", systemImage: "person.3", value: developmentTeam),
        ]
        self.checklistProvider = checklistProvider
            ?? DefaultReleaseChecklistProvider(
                bundleIdentifier: bundleIdentifier,
                developmentTeam: developmentTeam
            )
    }

    func releaseChecklist() -> [String] {
        checklistProvider.releaseChecklistItems()
    }
}
