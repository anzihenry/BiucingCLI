internal import CoreNative
import Foundation

public enum SharedCoreError: Error, Equatable {
    case overflow
    case invalidArgument
    case cancelled
    case closed
    case nativeFailure(Int32)
}

public enum SharedCore {
    public static var version: String {
        String(cString: bc_version())
    }

    public static func sum(_ values: [Int64]) throws -> Int64 {
        var result: Int64 = 0
        let status = values.withUnsafeBufferPointer { buffer in
            bc_sum(buffer.baseAddress, buffer.count, &result)
        }
        switch Int(status) {
        case BC_OK:
            return result
        case BC_OVERFLOW:
            throw SharedCoreError.overflow
        default:
            throw SharedCoreError.invalidArgument
        }
    }
}

/// The token is immutable after creation; the only mutation is a native atomic.
private final class CancellationToken: @unchecked Sendable {
    let pointer: OpaquePointer

    init() throws {
        var token: OpaquePointer?
        let status = bc_cancellation_create(&token)
        guard status == BC_OK, let token else { throw SharedCoreError.nativeFailure(status) }
        pointer = token
    }

    func cancel() {
        bc_cancellation_request(pointer)
    }

    deinit { bc_cancellation_destroy(pointer) }
}

/// Session state lives in C++. The queue owns the handle, and the lock protects
/// admission and tokens only. Never hold the lock while executing native work.
public final class CoreSession: @unchecked Sendable {
    private let queue = DispatchQueue(label: "SharedCore.session", qos: .userInitiated)
    private let lock = NSLock()
    private var accepting = true
    private var tokens: [UUID: CancellationToken] = [:]
    private var handle: OpaquePointer?

    public init() throws {
        let status = bc_session_create(&handle)
        guard status == BC_OK else { throw SharedCoreError.nativeFailure(status) }
    }

    public func analyze(_ values: [Int64]) async throws -> Int64 {
        guard values.count <= 1_000_000, let count = UInt32(exactly: values.count) else {
            throw SharedCoreError.invalidArgument
        }
        let token = try CancellationToken()
        let identifier = UUID()
        return try await withTaskCancellationHandler {
            try await withCheckedThrowingContinuation { continuation in
                lock.lock()
                guard accepting else {
                    lock.unlock()
                    continuation.resume(throwing: SharedCoreError.closed)
                    return
                }
                tokens[identifier] = token
                // Enqueue under admission lock: close must be queued after all accepted work.
                queue.async { [self] in
                    var result: Int64 = 0
                    let status = values.withUnsafeBufferPointer { buffer in
                        bc_session_analyze(handle, buffer.baseAddress, count, token.pointer, &result, nil, 0)
                    }
                    lock.withLock { tokens[identifier] = nil }
                    switch Int(status) {
                    case BC_OK: continuation.resume(returning: result)
                    case BC_CANCELLED: continuation.resume(throwing: CancellationError())
                    case BC_OVERFLOW: continuation.resume(throwing: SharedCoreError.overflow)
                    case BC_INVALID_ARGUMENT: continuation.resume(throwing: SharedCoreError.invalidArgument)
                    default: continuation.resume(throwing: SharedCoreError.nativeFailure(status))
                    }
                }
                lock.unlock()
            }
        } onCancel: {
            token.cancel()
        }
    }

    /// Idempotent, rejects new work immediately and waits without blocking the UI.
    public func close() async {
        await withCheckedContinuation { continuation in
            lock.lock()
            accepting = false
            for token in tokens.values {
                token.cancel()
            }
            queue.async { [self] in
                if let handle {
                    bc_session_destroy(handle)
                }
                handle = nil
                continuation.resume()
            }
            lock.unlock()
        }
    }

    /// Accepted operations retain self, so no native call is live during deinit.
    deinit {
        if let handle {
            bc_session_destroy(handle)
        }
    }
}
