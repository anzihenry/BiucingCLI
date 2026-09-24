#ifndef BIUCING_CORE_NATIVE_H
#define BIUCING_CORE_NATIVE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef int32_t bc_status;
enum {
    BC_OK = 0,
    BC_INVALID_ARGUMENT = 1,
    BC_OVERFLOW = 2,
    BC_CANCELLED = 3,
    BC_CLOSED = 4,
    BC_INTERNAL = 5,
    BC_OUT_OF_MEMORY = 6
};

/* Borrowed, immutable, process-lifetime UTF-8 string. Never free it. */
const char *bc_version(void);

/* Synchronous, thread-safe, retains no pointers. NULL values is valid only for
 * count == 0. out_result must be non-NULL; it is unchanged on error.
 * Sums left-to-right, reporting overflow at any intermediate step.
 * No C++ exceptions or owned C++ objects cross this boundary. */
bc_status bc_sum(const int64_t *values, size_t count, int64_t *out_result);

/* ABI v1. All outputs remain unchanged on failure. Diagnostics are optional,
 * call-local, caller-owned UTF-8 buffers; capacity includes the trailing NUL.
 * No platform types, STL, or exceptions cross this boundary. */
typedef struct bc_session bc_session;
typedef struct bc_cancellation bc_cancellation;
uint32_t bc_abi_version(void);
bc_status bc_session_create(bc_session **out_session);
void bc_session_destroy(bc_session *session);
bc_status bc_cancellation_create(bc_cancellation **out_token);
/* Only cancellation may run concurrently with analyze; cancel is idempotent. */
void bc_cancellation_request(bc_cancellation *token);
void bc_cancellation_destroy(bc_cancellation *token);
/* Serial per session. Maximum 1,000,000 elements. Empty input yields zero.
 * Transactional: successful result and completed-count commit together.
 * Cancellation/failure leaves session state and out_result unchanged.
 * Inputs/token are borrowed until return. No callbacks. Safe to retry after
 * failure; retrying a success increments the completed-operation count again. */
bc_status bc_session_analyze(bc_session *session, const int64_t *values,
    uint32_t count, const bc_cancellation *token, int64_t *out_result,
    char *diagnostic, uint32_t diagnostic_capacity);
bc_status bc_session_completed(const bc_session *session, uint64_t *out_count);

#ifdef __cplusplus
}
#endif

#endif
