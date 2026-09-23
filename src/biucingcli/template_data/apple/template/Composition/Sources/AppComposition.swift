import HomeFeature
import ProductContracts
import SharedCore

/// App scope owns a service factory; each feature session owns a CoreSession.
public actor NativeAnalysisService: AnalysisService {
    private var session: CoreSession?
    private var closed = false

    public init() {}

    public func analyze(_ values: [Int64]) async throws -> Int64 {
        guard !closed else { throw SharedCoreError.closed }
        if session == nil {
            session = try CoreSession()
        }
        guard let session else { throw SharedCoreError.closed }
        return try await session.analyze(values)
    }

    public func close() async {
        closed = true
        if let session {
            await session.close()
        }
        session = nil
    }
}

/// Generated construction uses only public SDK APIs, never component sources.
@MainActor
public struct AppComposition {
    let service: NativeAnalysisService
    let home: HomeFactory
    public init(service: NativeAnalysisService, home: HomeFactory) {
        self.service = service
        self.home = home
    }

    public func close() async {
        await service.close()
    }
}

/// App scope shares a factory, not a mutable feature session.
@MainActor
public struct ApplicationComposition {
    let sessions: SessionFactory
    public init(sessions: SessionFactory) { self.sessions = sessions }
}

@MainActor
public struct SessionFactory {
    public init() {}
    public func make() -> AppComposition { AppComposition() }
}
