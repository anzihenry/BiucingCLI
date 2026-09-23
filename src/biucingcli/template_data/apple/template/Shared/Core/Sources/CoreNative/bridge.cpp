#include "CoreNative.h"
#include "core.hpp"

extern "C" const char *bc_version(void) {
    return "0.1.0";
}

extern "C" bc_status bc_sum(const int64_t *values, size_t count, int64_t *out_result) {
    if (out_result == nullptr || (values == nullptr && count != 0)) {
        return BC_INVALID_ARGUMENT;
    }
    return biucing::core::checked_sum(values, count, *out_result) ? BC_OK : BC_OVERFLOW;
}

#include <atomic>
#include <cstring>
#include <limits>
#include <new>

struct bc_session { uint64_t completed = 0; };
struct bc_cancellation { std::atomic<bool> requested{false}; };

extern "C" uint32_t bc_abi_version(void) { return 1; }
extern "C" bc_status bc_session_create(bc_session **output) {
    if (!output) return BC_INVALID_ARGUMENT;
    try { *output = new bc_session; return BC_OK; }
    catch (const std::bad_alloc&) { return BC_OUT_OF_MEMORY; }
    catch (...) { return BC_INTERNAL; }
}
extern "C" void bc_session_destroy(bc_session *session) { delete session; }
extern "C" bc_status bc_cancellation_create(bc_cancellation **output) {
    if (!output) return BC_INVALID_ARGUMENT;
    try { *output = new bc_cancellation; return BC_OK; }
    catch (const std::bad_alloc&) { return BC_OUT_OF_MEMORY; }
    catch (...) { return BC_INTERNAL; }
}
extern "C" void bc_cancellation_request(bc_cancellation *token) {
    if (token) token->requested.store(true, std::memory_order_relaxed);
}
extern "C" void bc_cancellation_destroy(bc_cancellation *token) { delete token; }
static bc_status fail(bc_status status, const char *message, char *buffer, uint32_t capacity) {
    if (buffer && capacity) {
        const size_t length = std::strlen(message);
        const size_t copied = length < capacity - 1 ? length : capacity - 1;
        std::memcpy(buffer, message, copied);
        buffer[copied] = '\0';
    }
    return status;
}
extern "C" bc_status bc_session_analyze(bc_session *session, const int64_t *values,
    uint32_t count, const bc_cancellation *token, int64_t *output,
    char *diagnostic, uint32_t capacity) {
    if (!session || !output || (!values && count) || count > 1000000 || (!diagnostic && capacity))
        return fail(BC_INVALID_ARGUMENT, "invalid argument", diagnostic, capacity);
    try {
        int64_t result = 0;
        for (uint32_t index = 0; index < count; ++index) {
            if (token && token->requested.load(std::memory_order_relaxed))
                return fail(BC_CANCELLED, "cancelled", diagnostic, capacity);
            const int64_t pair[] = {result, values[index]};
            if (!biucing::core::checked_sum(pair, 2, result))
                return fail(BC_OVERFLOW, "integer overflow", diagnostic, capacity);
        }
        if (token && token->requested.load(std::memory_order_relaxed))
            return fail(BC_CANCELLED, "cancelled", diagnostic, capacity);
        if (session->completed == std::numeric_limits<uint64_t>::max())
            return fail(BC_OVERFLOW, "operation count overflow", diagnostic, capacity);
        ++session->completed;
        *output = result;
        if (diagnostic && capacity) diagnostic[0] = '\0';
        return BC_OK;
    } catch (const std::bad_alloc&) { return fail(BC_OUT_OF_MEMORY, "out of memory", diagnostic, capacity); }
    catch (...) { return fail(BC_INTERNAL, "internal error", diagnostic, capacity); }
}
extern "C" bc_status bc_session_completed(const bc_session *session, uint64_t *output) {
    if (!session || !output) return BC_INVALID_ARGUMENT;
    *output = session->completed;
    return BC_OK;
}
