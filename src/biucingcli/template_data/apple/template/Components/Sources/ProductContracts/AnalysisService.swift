public protocol AnalysisService: Sendable {
    func analyze(_ values: [Int64]) async throws -> Int64
    func close() async
}

public enum HomeOutput: Sendable, Equatable {
    case showAbout
}

public struct PreviewAnalysisService: AnalysisService {
    public init() {}
    public func analyze(_ values: [Int64]) async throws -> Int64 {
        42
    }

    public func close() async {}
}
