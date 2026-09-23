import SharedCore
import XCTest

@MainActor
final class SharedCoreTests: XCTestCase {
    func testNativeResultsThroughSwiftBoundary() throws {
        XCTAssertEqual(SharedCore.version, "0.1.0")
        XCTAssertEqual(try SharedCore.sum([]), 0)
        XCTAssertEqual(try SharedCore.sum([20, -3, 25]), 42)
        XCTAssertEqual(try SharedCore.sum([Int64.min, Int64.max]), -1)
    }

    func testOverflowBecomesSwiftError() {
        for values: [Int64] in [[Int64.max, 1], [Int64.min, -1]] {
            XCTAssertThrowsError(try SharedCore.sum(values)) { error in
                XCTAssertEqual(error as? SharedCoreError, .overflow)
            }
        }
    }

    func testStatefulSessionClosesAndRejectsNewWork() async throws {
        let session = try CoreSession()
        let value = try await session.analyze([20, 22])
        XCTAssertEqual(value, 42)
        await session.close()
        await session.close()
        do {
            _ = try await session.analyze([])
            XCTFail("Closed session accepted work")
        } catch { XCTAssertEqual(error as? SharedCoreError, .closed) }
    }

    func testPreCancelledTaskAndIndependentSession() async throws {
        let session = try CoreSession()
        let task = Task {
            withUnsafeCurrentTask { $0?.cancel() }
            return try await session.analyze([1, 2])
        }
        do {
            _ = try await task.value
            XCTFail("Cancelled task succeeded")
        } catch { XCTAssertTrue(error is CancellationError) }
        let value = try await session.analyze([40, 2])
        XCTAssertEqual(value, 42)
        await session.close()
    }

    func testCloseDuringConcurrentSubmissionsAlwaysCompletes() async throws {
        let session = try CoreSession()
        await withTaskGroup(of: Void.self) { group in
            for _ in 0 ..< 20 {
                group.addTask {
                    do { _ = try await session.analyze(Array(repeating: 1, count: 100_000))
                    } catch is CancellationError { } catch SharedCoreError
                        .closed { } catch { XCTFail("Unexpected failure: \(error)") }
                }
            }
            group.addTask { await session.close() }
        }
        await session.close()
    }
}
