cmake_minimum_required(VERSION 3.20)
project(BiucingCore VERSION 0.1.0 LANGUAGES C CXX)

add_library(biucing_core STATIC
    Sources/CoreNative/core.cpp
    Sources/CoreNative/bridge.cpp
)
add_library(Biucing::Core ALIAS biucing_core)
target_compile_features(biucing_core PUBLIC cxx_std_20)
target_include_directories(biucing_core PUBLIC
    "${CMAKE_CURRENT_SOURCE_DIR}/Sources/CoreNative/include"
)
set_target_properties(biucing_core PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
    POSITION_INDEPENDENT_CODE ON
)

# Embedders (JNI / Node-API / desktop) opt in to tests explicitly.
set(core_tests_default OFF)
if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    set(core_tests_default ON)
endif()
option(BIUCING_CORE_BUILD_TESTS "Build portable core tests" ${core_tests_default})
if(BIUCING_CORE_BUILD_TESTS)
    enable_testing()
    # Compile the public header and client as C, then link the C++ implementation.
    add_executable(biucing_core_tests Tests/Native/core_test.c)
    target_link_libraries(biucing_core_tests PRIVATE Biucing::Core)
    set_target_properties(biucing_core_tests PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED ON)
    add_test(NAME core_boundary COMMAND biucing_core_tests)
endif()
