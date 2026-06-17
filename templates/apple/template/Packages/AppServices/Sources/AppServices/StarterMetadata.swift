import Foundation

public struct StarterFact: Equatable {
    public let label: String
    public let systemImage: String
    public let value: String

    public init(label: String, systemImage: String, value: String) {
        self.label = label
        self.systemImage = systemImage
        self.value = value
    }
}

public protocol ReleaseChecklistProviding {
    func releaseChecklistItems() -> [String]
}

public struct DefaultReleaseChecklistProvider: ReleaseChecklistProviding {
    public let bundleIdentifier: String
    public let developmentTeam: String

    public init(bundleIdentifier: String, developmentTeam: String) {
        self.bundleIdentifier = bundleIdentifier
        self.developmentTeam = developmentTeam
    }

    public func releaseChecklistItems() -> [String] {
        [
            "Confirm signing for \(developmentTeam).",
            "Verify bundle identifier \(bundleIdentifier).",
            "Run make test before the next beta build.",
        ]
    }
}

public enum StarterFactBuilder {
    public static func overviewFacts(
        bundleIdentifier: String,
        platformName: String,
        minimumOSVersion: String,
        developmentTeam: String
    ) -> [StarterFact] {
        [
            StarterFact(label: "Bundle ID", systemImage: "shippingbox", value: bundleIdentifier),
            StarterFact(label: "Platform", systemImage: "app", value: platformName),
            StarterFact(label: "Minimum OS", systemImage: "gear", value: minimumOSVersion),
            StarterFact(label: "Team", systemImage: "person.3", value: developmentTeam),
        ]
    }
}
