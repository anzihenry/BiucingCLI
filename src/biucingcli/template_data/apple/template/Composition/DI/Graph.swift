import HomeFeature
import ProductContracts

@Instantiable(isRoot: true)
public struct AppComposition {
    @Instantiated let service: NativeAnalysisService
    @Instantiated let home: HomeFactory
    public init(service: NativeAnalysisService, home: HomeFactory) {}
}

@Instantiable
public struct NativeAnalysisService {
    public init() {}
}

@Instantiable
public extension HomeFactory {
    static func instantiate(service: NativeAnalysisService) -> HomeFactory {
        HomeFactory(service: service)
    }
}

@Instantiable(isRoot: true)
public struct ApplicationComposition {
    @Instantiated let sessions: SessionFactory
    public init(sessions: SessionFactory) {}
}

@Instantiable
public struct SessionFactory {
    public init() {}
}
