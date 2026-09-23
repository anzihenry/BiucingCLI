#include <jni.h>
#include <CoreNative.h>
#include <cstdint>
#include <new>
#include <vector>
static jclass findType(JNIEnv* env, bool exception) {
    char errorName[] = "{{PACKAGE_NAME}}/core/sharedcore/CoreException";
    char bridgeName[] = "{{PACKAGE_NAME}}/core/sharedcore/NativeBridge";
    char* name = exception ? errorName : bridgeName;
    for (char* p = name; *p; ++p) if (*p == '.') *p = '/';
    return env->FindClass(name);
}

// Private bridge, never part of the business SDK. All handles are owned by CoreSession.
static void fail(JNIEnv* env, bc_status status) {
    if (env->ExceptionCheck()) return;
    jclass type = findType(env, true);
    if (!type) return;
    jmethodID ctor = env->GetMethodID(type, "<init>", "(I)V");
    if (!ctor) return;
    jobject error = env->NewObject(type, ctor, static_cast<jint>(status));
    if (error) env->Throw(static_cast<jthrowable>(error));
    env->DeleteLocalRef(error);
    env->DeleteLocalRef(type);
}
static jlong create(JNIEnv* env, jobject) {
    bc_session* session = nullptr;
    auto status = bc_session_create(&session);
    if (status != BC_OK) fail(env, status);
    return reinterpret_cast<jlong>(session);
}
static void destroy(JNIEnv*, jobject, jlong h) { bc_session_destroy(reinterpret_cast<bc_session*>(h)); }
static jlong tokenCreate(JNIEnv* env, jobject) {
    bc_cancellation* token = nullptr;
    auto status = bc_cancellation_create(&token);
    if (status != BC_OK) fail(env, status);
    return reinterpret_cast<jlong>(token);
}
static void tokenCancel(JNIEnv*, jobject, jlong h) { bc_cancellation_request(reinterpret_cast<bc_cancellation*>(h)); }
static void tokenDestroy(JNIEnv*, jobject, jlong h) { bc_cancellation_destroy(reinterpret_cast<bc_cancellation*>(h)); }
static jlong analyze(JNIEnv* env, jobject, jlong h, jlong t, jlongArray input) {
    if (!h || !t || !input) { fail(env, BC_INVALID_ARGUMENT); return 0; }
    const auto count = env->GetArrayLength(input);
    if (count > 1000000) { fail(env, BC_INVALID_ARGUMENT); return 0; }
    try {
        std::vector<jlong> values(static_cast<size_t>(count));
        if (count) env->GetLongArrayRegion(input, 0, count, values.data());
        if (env->ExceptionCheck()) return 0;
        // Convert rather than alias jlong storage as int64_t (types can differ by ABI).
        std::vector<int64_t> copied(values.begin(), values.end());
        int64_t result = 0;
        const auto status = bc_session_analyze(reinterpret_cast<bc_session*>(h), copied.data(),
            static_cast<uint32_t>(count), reinterpret_cast<bc_cancellation*>(t), &result, nullptr, 0);
        if (status != BC_OK) fail(env, status);
        return static_cast<jlong>(result);
    } catch (const std::bad_alloc&) { fail(env, BC_OUT_OF_MEMORY); }
      catch (...) { fail(env, BC_INTERNAL); }
    return 0;
}
static jlong completed(JNIEnv* env, jobject, jlong h) {
    uint64_t result = 0;
    auto status = bc_session_completed(reinterpret_cast<bc_session*>(h), &result);
    if (status != BC_OK) { fail(env, status); return 0; }
    if (result > INT64_MAX) { fail(env, BC_OVERFLOW); return 0; }
    return static_cast<jlong>(result);
}
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void*) {
    JNIEnv* env = nullptr;
    if (vm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6) != JNI_OK) return JNI_ERR;
    jclass type = findType(env, false);
    if (!type) return JNI_ERR;
    const JNINativeMethod methods[] = {
        {const_cast<char*>("create"), const_cast<char*>("()J"), reinterpret_cast<void*>(create)},
        {const_cast<char*>("destroy"), const_cast<char*>("(J)V"), reinterpret_cast<void*>(destroy)},
        {const_cast<char*>("tokenCreate"), const_cast<char*>("()J"), reinterpret_cast<void*>(tokenCreate)},
        {const_cast<char*>("tokenCancel"), const_cast<char*>("(J)V"), reinterpret_cast<void*>(tokenCancel)},
        {const_cast<char*>("tokenDestroy"), const_cast<char*>("(J)V"), reinterpret_cast<void*>(tokenDestroy)},
        {const_cast<char*>("analyze"), const_cast<char*>("(JJ[J)J"), reinterpret_cast<void*>(analyze)},
        {const_cast<char*>("completed"), const_cast<char*>("(J)J"), reinterpret_cast<void*>(completed)}
    };
    auto status = env->RegisterNatives(type, methods, sizeof(methods) / sizeof(methods[0]));
    env->DeleteLocalRef(type);
    return status == JNI_OK ? JNI_VERSION_1_6 : JNI_ERR;
}
