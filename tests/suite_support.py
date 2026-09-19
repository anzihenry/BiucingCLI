"""Explicit external-tool boundaries used by scripts/run-tests."""


def platform_test(method):
    method.test_suite = "platform"
    return method


def android_test(method):
    method.test_suite = "android"
    return method
