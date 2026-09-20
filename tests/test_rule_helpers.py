"""Focused rules regression coverage; extracted without changing assertions."""

import unittest

from biucingcli.template_rules.apple import apple_platform_config
from biucingcli.template_rules.android import default_kotlin_module_name


from cli_support import CLIHelpers


class RuleHelperTests(CLIHelpers, unittest.TestCase):
    def test_apple_platform_config_sets_release_platforms(self):
        expected = {
            "ios": ("ios", "ios"),
            "macos": ("mac", "osx"),
            "watchos": ("ios", "ios"),
            "tvos": ("ios", "appletvos"),
        }

        for platform, (fastlane_platform, app_store_platform) in expected.items():
            with self.subTest(platform=platform):
                config = apple_platform_config(platform, None)
                self.assertEqual(config["fastlane_platform"], fastlane_platform)
                self.assertEqual(config["app_store_platform"], app_store_platform)

    def test_default_kotlin_module_name_derives_pascal_case(self):
        self.assertEqual(default_kotlin_module_name("demo-android_app"), "DemoAndroidApp")
        self.assertEqual(default_kotlin_module_name(""), "App")


if __name__ == "__main__":
    unittest.main()
