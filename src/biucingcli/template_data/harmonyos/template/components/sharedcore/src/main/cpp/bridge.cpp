#ifdef BIUCING_NODE_TEST
#include <node_api.h>
#else
#include <napi/native_api.h>
#endif
#include <CoreNative.h>
#include <charconv>
#include <memory>
#include <mutex>
#include <new>
#include <string>
#include <vector>

namespace {
struct Session {
    bc_session* core = nullptr;
    bc_cancellation* active = nullptr;
    std::mutex mutex;
    ~Session() { bc_session_destroy(core); }
};
using Owner = std::shared_ptr<Session>;
constexpr napi_type_tag sessionTag = {0xBA8F4A971EB94D29ULL, 0xBD21738AF2153E60ULL};
struct Job {
    Owner owner;
    std::vector<int64_t> input;
    bc_cancellation* token = nullptr;
    napi_async_work work = nullptr;
    napi_deferred deferred = nullptr;
    int64_t result = 0;
    bc_status status = BC_INTERNAL;
    char diagnostic[256] = {};
    ~Job() { bc_cancellation_destroy(token); }
};
napi_value error(napi_env env, int32_t code, const char* message) {
    napi_value text = nullptr, result = nullptr, number = nullptr;
    if (napi_create_string_utf8(env, message, NAPI_AUTO_LENGTH, &text) != napi_ok ||
        napi_create_error(env, nullptr, text, &result) != napi_ok ||
        napi_create_int32(env, code, &number) != napi_ok ||
        napi_set_named_property(env, result, "code", number) != napi_ok) return nullptr;
    return result;
}
napi_value fail(napi_env env, int32_t code, const char* message) {
    napi_value value = error(env, code, message);
    if (value) napi_throw(env, value);
    return nullptr;
}
napi_value undefined(napi_env env) {
    napi_value value = nullptr;
    napi_get_undefined(env, &value);
    return value;
}
Owner unwrap(napi_env env, napi_value value) {
    bool tagged = false;
    if (napi_check_object_type_tag(env, value, &sessionTag, &tagged) != napi_ok || !tagged) return {};
    void* pointer = nullptr;
    if (napi_unwrap(env, value, &pointer) != napi_ok || !pointer) return {};
    return *static_cast<Owner*>(pointer);
}
napi_value create(napi_env env, napi_callback_info) {
    try {
        auto owner = std::make_unique<Owner>(std::make_shared<Session>());
        auto status = bc_session_create(&(*owner)->core);
        if (status != BC_OK) return fail(env, status, "Unable to create session");
        napi_value value = nullptr;
        if (napi_create_object(env, &value) != napi_ok ||
            napi_type_tag_object(env, value, &sessionTag) != napi_ok ||
            napi_wrap(env, value, owner.get(), [](napi_env, void* data, void*) {
                delete static_cast<Owner*>(data);
            }, nullptr, nullptr) != napi_ok) return fail(env, BC_INTERNAL, "Unable to wrap session");
        owner.release();
        return value;
    } catch (...) { return fail(env, BC_OUT_OF_MEMORY, "Unable to allocate session"); }
}
void execute(napi_env, void* data) {
    auto* job = static_cast<Job*>(data);
    job->status = bc_session_analyze(job->owner->core, job->input.data(),
        static_cast<uint32_t>(job->input.size()), job->token, &job->result,
        job->diagnostic, sizeof(job->diagnostic));
}
void complete(napi_env env, napi_status status, void* data) {
    std::unique_ptr<Job> job(static_cast<Job*>(data));
    {
        std::lock_guard<std::mutex> lock(job->owner->mutex);
        job->owner->active = nullptr;
    }
    if (status != napi_ok) job->status = BC_CANCELLED;
    napi_value value = nullptr;
    if (job->status == BC_OK) {
        char buffer[32];
        auto converted = std::to_chars(buffer, buffer + sizeof(buffer), job->result);
        if (napi_create_string_utf8(env, buffer, converted.ptr - buffer, &value) == napi_ok)
            napi_resolve_deferred(env, job->deferred, value);
        else {
            value = error(env, BC_INTERNAL, "Unable to convert result");
            if (value) napi_reject_deferred(env, job->deferred, value);
        }
    } else {
        value = error(env, job->status, job->diagnostic[0] ? job->diagnostic : "Native operation failed");
        if (value) napi_reject_deferred(env, job->deferred, value);
    }
    napi_delete_async_work(env, job->work);
}
napi_value analyze(napi_env env, napi_callback_info info) {
    try {
        size_t argc = 2;
        napi_value args[2] = {};
        if (napi_get_cb_info(env, info, &argc, args, nullptr, nullptr) != napi_ok || argc != 2)
            return fail(env, BC_INVALID_ARGUMENT, "Expected session and decimal values");
        auto owner = unwrap(env, args[0]);
        if (!owner) return fail(env, BC_INVALID_ARGUMENT, "Invalid session");
        bool array = false;
        uint32_t count = 0;
        if (napi_is_array(env, args[1], &array) != napi_ok || !array ||
            napi_get_array_length(env, args[1], &count) != napi_ok || count > 1000000)
            return fail(env, BC_INVALID_ARGUMENT, "Expected at most 1000000 values");
        auto job = std::make_unique<Job>();
        job->owner = owner;
        job->input.reserve(count);
        for (uint32_t i = 0; i < count; ++i) {
            napi_value item = nullptr;
            char text[32];
            size_t length = 0, copied = 0;
            if (napi_get_element(env, args[1], i, &item) != napi_ok ||
                napi_get_value_string_utf8(env, item, nullptr, 0, &length) != napi_ok ||
                length == 0 || length >= sizeof(text) ||
                napi_get_value_string_utf8(env, item, text, sizeof(text), &copied) != napi_ok || copied != length)
                return fail(env, BC_INVALID_ARGUMENT, "Expected signed 64-bit decimal string");
            int64_t value = 0;
            auto result = std::from_chars(text, text + length, value);
            if (result.ec != std::errc() || result.ptr != text + length)
                return fail(env, BC_INVALID_ARGUMENT, "Invalid or out-of-range integer");
            job->input.push_back(value);
        }
        auto tokenStatus = bc_cancellation_create(&job->token);
        if (tokenStatus != BC_OK) return fail(env, tokenStatus, "Unable to allocate cancellation");
        std::lock_guard<std::mutex> lock(owner->mutex);
        if (!owner->core) return fail(env, BC_CLOSED, "Session closed");
        if (owner->active) return fail(env, BC_INVALID_ARGUMENT, "Session must be called serially");
        napi_value promise = nullptr, label = nullptr;
        if (napi_create_string_utf8(env, "SharedCore.analyze", NAPI_AUTO_LENGTH, &label) != napi_ok ||
            napi_create_promise(env, &job->deferred, &promise) != napi_ok)
            return fail(env, BC_INTERNAL, "Unable to create promise");
        if (napi_create_async_work(env, nullptr, label, execute, complete, job.get(), &job->work) != napi_ok) {
            auto value = error(env, BC_INTERNAL, "Unable to create native work");
            if (value) napi_reject_deferred(env, job->deferred, value);
            return promise;
        }
        owner->active = job->token;
        if (napi_queue_async_work(env, job->work) != napi_ok) {
            owner->active = nullptr;
            napi_delete_async_work(env, job->work);
            auto value = error(env, BC_INTERNAL, "Unable to schedule native work");
            if (value) napi_reject_deferred(env, job->deferred, value);
            return promise;
        }
        job.release();
        return promise;
    } catch (...) { return fail(env, BC_OUT_OF_MEMORY, "Unable to allocate operation"); }
}
napi_value control(napi_env env, napi_callback_info info, bool closing) {
    size_t argc = 1;
    napi_value arg = nullptr;
    if (napi_get_cb_info(env, info, &argc, &arg, nullptr, nullptr) != napi_ok || argc != 1)
        return fail(env, BC_INVALID_ARGUMENT, "Expected session");
    auto owner = unwrap(env, arg);
    if (!owner) return fail(env, BC_INVALID_ARGUMENT, "Invalid session");
    std::lock_guard<std::mutex> lock(owner->mutex);
    if (owner->active) {
        bc_cancellation_request(owner->active);
        if (closing) return fail(env, BC_INVALID_ARGUMENT, "Wait for active operation before close");
    } else if (closing) {
        bc_session_destroy(owner->core);
        owner->core = nullptr;
    }
    return undefined(env);
}
napi_value cancel(napi_env env, napi_callback_info info) { return control(env, info, false); }
napi_value close(napi_env env, napi_callback_info info) { return control(env, info, true); }
napi_value init(napi_env env, napi_value exports) {
    napi_property_descriptor methods[] = {
        {"create", nullptr, create, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"analyze", nullptr, analyze, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"cancel", nullptr, cancel, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"close", nullptr, close, nullptr, nullptr, nullptr, napi_default, nullptr}
    };
    if (napi_define_properties(env, exports, sizeof(methods) / sizeof(methods[0]), methods) != napi_ok) return nullptr;
    return exports;
}
}
#ifdef BIUCING_NODE_TEST
NAPI_MODULE(biucing_shared, init)
#else
EXTERN_C_START
static napi_module module = {1, 0, nullptr, init, "biucing_shared", nullptr, {0}};
__attribute__((constructor)) void registerModule() { napi_module_register(&module); }
EXTERN_C_END
#endif
