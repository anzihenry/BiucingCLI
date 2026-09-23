import HomeFeature

extension HomeFactory {
    @MainActor
    static func instantiate(service: NativeAnalysisService) -> HomeFactory {
        HomeFactory(service: service)
    }
}
