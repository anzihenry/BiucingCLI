@testable import {{SWIFT_MODULE_NAME}}_macos
import Foundation
import SharedCore
import XCTest

@MainActor
final class AppTests: XCTestCase {
    func testBinaryCoreThroughInjectedService() async throws {
        let composition = AppComposition()
        let value = try await composition.service.analyze([10, 20, 12])
        XCTAssertEqual(value, 42)
        await composition.close()
        do {
            _ = try await composition.service.analyze([1])
            XCTFail("Closed service accepted work")
        } catch { XCTAssertEqual(error as? SharedCoreError, .closed) }
    }

    func testAppFactoryCreatesIndependentSessions() async throws {
        let application = ApplicationComposition()
        let first = application.sessions.make()
        let second = application.sessions.make()
        await first.close()
        let value = try await second.service.analyze([40, 2])
        XCTAssertEqual(value, 42)
        await second.close()
    }

    func testComponentResourceIsDelivered() {
        XCTAssertNotNil(Bundle.main.url(forResource: "HomeFeature", withExtension: "bundle"))
    }
}
