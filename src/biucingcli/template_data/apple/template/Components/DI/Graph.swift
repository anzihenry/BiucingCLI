/// SafeDI CLI input only. Generated Swift is compiled against the real types.
@Instantiable(isRoot: true)
public struct FeatureAssembly {
    @Instantiated let policy: FeaturePolicy
    public init(policy: FeaturePolicy) {}
}

@Instantiable
public struct FeaturePolicy {
    public init() {}
}
