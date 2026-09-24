#include "CoreNative.h"

#include <stdio.h>
#include <string.h>

/* Explicit checks stay enabled in Release builds (unlike assert). */
#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "Failed at line %d: %s\n", __LINE__, #condition); \
        return 1; \
    } \
} while (0)

int main(void) {
    int64_t result = 99;
    const int64_t values[] = {20, -3, 25};
    const int64_t positive_overflow[] = {INT64_MAX, 1};
    const int64_t negative_overflow[] = {INT64_MIN, -1};
    const int64_t limits[] = {INT64_MIN, INT64_MAX};
    CHECK(strcmp(bc_version(), "0.1.0") == 0);
    CHECK(bc_sum(NULL, 0, &result) == BC_OK && result == 0);
    CHECK(bc_sum(values, 3, &result) == BC_OK && result == 42);
    CHECK(bc_sum(NULL, 1, &result) == BC_INVALID_ARGUMENT && result == 42);
    CHECK(bc_sum(values, 3, NULL) == BC_INVALID_ARGUMENT);
    CHECK(bc_sum(positive_overflow, 2, &result) == BC_OVERFLOW && result == 42);
    CHECK(bc_sum(negative_overflow, 2, &result) == BC_OVERFLOW && result == 42);
    CHECK(bc_sum(limits, 2, &result) == BC_OK && result == -1);
    CHECK(bc_abi_version() == 1);
    bc_session *session = NULL;
    bc_cancellation *token = NULL;
    char diagnostic[32] = {0};
    uint64_t completed = 99;
    CHECK(bc_session_create(&session) == BC_OK);
    CHECK(bc_cancellation_create(&token) == BC_OK);
    CHECK(bc_session_analyze(session, values, 3, token, &result, diagnostic, 32) == BC_OK);
    CHECK(result == 42 && diagnostic[0] == '\0');
    CHECK(bc_session_completed(session, &completed) == BC_OK && completed == 1);
    CHECK(bc_session_analyze(session, positive_overflow, 2, token, &result, diagnostic, 32) == BC_OVERFLOW);
    CHECK(result == 42 && strcmp(diagnostic, "integer overflow") == 0);
    bc_cancellation_request(token);
    bc_cancellation_request(token);
    CHECK(bc_session_analyze(session, values, 3, token, &result, diagnostic, 32) == BC_CANCELLED);
    CHECK(result == 42);
    CHECK(bc_session_analyze(session, NULL, 0, token, &result, NULL, 0) == BC_CANCELLED);
    CHECK(bc_session_completed(session, &completed) == BC_OK && completed == 1);
    CHECK(bc_session_analyze(session, values, 1000001, NULL, &result, NULL, 0) == BC_INVALID_ARGUMENT);
    bc_session *other = NULL;
    CHECK(bc_session_create(&other) == BC_OK);
    CHECK(bc_session_completed(other, &completed) == BC_OK && completed == 0);
    CHECK(bc_session_completed(session, &completed) == BC_OK && completed == 1);
    bc_session_destroy(other);
    bc_cancellation_destroy(token);
    bc_session_destroy(session);
    return 0;
}
