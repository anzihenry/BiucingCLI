import SwiftUI

public struct FeatureStyle: Sendable {
    public let title: String
    public init(title: String = "共享计算") {
        self.title = title
    }
}

public struct ResultLabel: View {
    private let value: String
    public init(value: String) {
        self.value = value
    }

    public var body: some View {
        Text(value).font(.title2.monospacedDigit()).accessibilityLabel("计算结果：\(value)")
    }
}
