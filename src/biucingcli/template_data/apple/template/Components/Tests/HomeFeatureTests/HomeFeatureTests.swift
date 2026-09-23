import HomeFeature
import ProductContracts
import XCTest

@MainActor
final class HomeFeatureTests: XCTestCase {
    func testInjectedServiceDrivesFeature() async {
        let model = HomeModel(service: PreviewAnalysisService())
        await model.run()
        XCTAssertEqual(model.result, "42")
        XCTAssertFalse(model.isRunning)
    }
}
