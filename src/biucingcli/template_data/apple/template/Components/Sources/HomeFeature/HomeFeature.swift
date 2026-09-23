import DesignSystem
import Observation
import ProductContracts
import SwiftUI

@MainActor @Observable
public final class HomeModel {
    public private(set) var result = "—"
    public private(set) var isRunning = false
    private let service: any AnalysisService
    private var generation = 0

    public init(service: any AnalysisService) {
        self.service = service
    }

    public func run() async {
        generation += 1
        let current = generation
        isRunning = true
        defer {
            if current == generation {
                isRunning = false
            }
        }
        do {
            let value = try await service.analyze([10, 20, 12])
            guard !Task.isCancelled, current == generation else { return }
            result = String(value)
        } catch is CancellationError {
            // A departing page must not publish a stale result.
        } catch {
            guard !Task.isCancelled, current == generation else { return }
            result = "计算失败，请重试"
        }
    }
}

/// SafeDI generates this component-internal root's initializer at publication.
@MainActor
struct FeatureAssembly {
    let policy: FeaturePolicy
}

@MainActor
struct FeaturePolicy {
    func makeModel(service: any AnalysisService) -> HomeModel {
        HomeModel(service: service)
    }
}

@MainActor
public struct HomeFactory {
    private let service: any AnalysisService
    public init(service: any AnalysisService) {
        self.service = service
    }

    public func makeView(
        style: FeatureStyle? = nil,
        onOutput: @escaping @MainActor (HomeOutput) -> Void
    ) -> HomeView {
        let assembly = FeatureAssembly()
        return HomeView(
            model: assembly.policy.makeModel(service: service),
            style: style ?? FeatureStyle(title: HomeResources.title),
            onOutput: onOutput
        )
    }
}

@MainActor
public struct HomeView: View {
    @State private var model: HomeModel
    private let style: FeatureStyle
    private let onOutput: @MainActor (HomeOutput) -> Void
    @State private var task: Task<Void, Never>?

    public init(model: HomeModel, style: FeatureStyle, onOutput: @escaping @MainActor (HomeOutput) -> Void) {
        self.model = model
        self.style = style
        self.onOutput = onOutput
    }

    public var body: some View {
        VStack(spacing: 16) {
            Text(style.title).font(.headline)
            ResultLabel(value: model.result)
            Button(model.isRunning ? "计算中…" : "计算示例") {
                task?.cancel()
                task = Task { await model.run() }
            }
            .disabled(model.isRunning)
            Button("关于") { onOutput(.showAbout) }
        }
        .padding()
        .onDisappear { task?.cancel() }
    }
}

#Preview {
    HomeFactory(service: PreviewAnalysisService()).makeView { _ in }
}

private enum HomeResources {
    static var title: String {
        guard let url = Bundle.main.url(forResource: "HomeFeature", withExtension: "bundle"),
              let bundle = Bundle(url: url) else { return "共享计算" }
        return bundle.localizedString(forKey: "feature.name", value: "共享计算", table: nil)
    }
}
