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

    func testOwnerRetainsModelAndClosesOnlyItsSession() async throws {
        let application = ApplicationComposition()
        let first = SessionOwner(sessions: application.sessions)
        let second = SessionOwner(sessions: application.sessions)
        let model = first.model
        await model.run()
        XCTAssertTrue(first.model === model)
        XCTAssertEqual(model.result, "42")
        XCTAssertFalse(first.model === second.model)
        await first.close()
        await first.close()
        XCTAssertTrue(first.isClosed)
        await model.run()
        XCTAssertEqual(model.result, "42")
        do {
            _ = try await first.composition.service.analyze([1])
            XCTFail("Ended owner accepted work")
        } catch { XCTAssertEqual(error as? SharedCoreError, .closed) }
        await second.model.run()
        XCTAssertEqual(second.model.result, "42")
        await second.close()
    }

    func testSceneOwnerReleaseClosesService() async throws {
        var owner: SessionOwner? = SessionOwner(sessions: SessionFactory())
        weak var reference = owner
        let service = try XCTUnwrap(owner?.composition.service)
        _ = try await service.analyze([1])
        owner = nil
        XCTAssertNil(reference)
        // Teardown is asynchronous; poll a bounded interval for its observable completion.
        for _ in 0..<100 {
            do { _ = try await service.analyze([1]) }
            catch {
                if error as? SharedCoreError == .closed { return }
                // Close may cancel a call that raced with teardown before rejecting later work.
                if !(error is CancellationError) { throw error }
            }
            try await Task.sleep(for: .milliseconds(10))
        }
        XCTFail("Owner release did not close its service")
    }

    func testComponentResourceIsDelivered() {
        XCTAssertNotNil(Bundle.main.url(forResource: "HomeFeature", withExtension: "bundle"))
    }
}
