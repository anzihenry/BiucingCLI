import AppServices
import Foundation

typealias HomeFact = StarterFact

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
        facts = StarterFactBuilder.overviewFacts(
            bundleIdentifier: bundleIdentifier,
            platformName: platformName,
            minimumOSVersion: minimumOSVersion,
            developmentTeam: developmentTeam
        )
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
