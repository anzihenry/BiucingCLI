"""Apple platform derivations and Swift snippets."""

from biucingcli.escaping import swift_string
from biucingcli.template_rules.common import RuleResult, default_type_name

default_swift_module_name = default_type_name


def apple_platform_config(platform: str | None, minimum_os_version: str | None) -> dict[str, str]:
    """Return derived Apple platform values for template rendering."""
    requested = (platform or "ios").lower()
    supported = {
        "ios": {
            "apple_platform": "ios",
            "apple_platform_name": "iOS",
            "fastlane_platform": "ios",
            "app_store_platform": "ios",
            "minimum_os_version": "26.0",
            "tuist_destinations": ".iOS",
            "tuist_deployment_targets": '.iOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "generic/platform=iOS Simulator",
            "swiftpm_supported_platform": '.iOS("{{MINIMUM_OS_VERSION}}")',
        },
        "macos": {
            "apple_platform": "macos",
            "apple_platform_name": "macOS",
            "fastlane_platform": "mac",
            "app_store_platform": "osx",
            "minimum_os_version": "26.0",
            "tuist_destinations": ".macOS",
            "tuist_deployment_targets": '.macOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "platform=macOS",
            "swiftpm_supported_platform": '.macOS("{{MINIMUM_OS_VERSION}}")',
        },
        "watchos": {
            "apple_platform": "watchos",
            "apple_platform_name": "watchOS",
            "fastlane_platform": "ios",
            "app_store_platform": "ios",
            "minimum_os_version": "26.0",
            "tuist_destinations": ".watchOS",
            "tuist_deployment_targets": '.watchOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "generic/platform=watchOS Simulator",
            "swiftpm_supported_platform": '.watchOS("{{MINIMUM_OS_VERSION}}")',
        },
        "tvos": {
            "apple_platform": "tvos",
            "apple_platform_name": "tvOS",
            "fastlane_platform": "ios",
            "app_store_platform": "appletvos",
            "minimum_os_version": "26.0",
            "tuist_destinations": ".tvOS",
            "tuist_deployment_targets": '.tvOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "generic/platform=tvOS Simulator",
            "swiftpm_supported_platform": '.tvOS("{{MINIMUM_OS_VERSION}}")',
        },
    }
    if requested not in supported:
        raise ValueError(
            "Unsupported Apple platform. Expected one of: ios, macos, watchos, tvos"
        )

    resolved = dict(supported[requested])
    resolved["minimum_os_version"] = minimum_os_version or resolved["minimum_os_version"]
    resolved["tuist_deployment_targets"] = resolved["tuist_deployment_targets"].replace(
        "{{MINIMUM_OS_VERSION}}", resolved["minimum_os_version"]
    )
    resolved["swiftpm_supported_platform"] = resolved["swiftpm_supported_platform"].replace(
        "{{MINIMUM_OS_VERSION}}", resolved["minimum_os_version"]
    )
    return resolved


def apple_platform_snippets(values: dict[str, str]) -> dict[str, str]:
    """Return platform-specific Apple template snippets using resolved values."""
    platform = values.get("apple_platform", "ios")
    display_name = swift_string(values.get("display_name", "App"))

    if platform == "macos":
        return {
            "apple_scene_body": "\n".join(
                [
                    f'        WindowGroup("{display_name}") {{',
                    "            HomeView()",
                    "        }",
                    "        .defaultSize(width: 1100, height: 720)",
                ]
            ),
            "apple_home_body": "\n".join(
                [
                    "    var body: some View {",
                    "        NavigationSplitView {",
                    '            List {',
                    '                Section("Workspace") {',
                    '                    Label("Overview", systemImage: "sidebar.left")',
                    '                    Label("Release Checklist", systemImage: "checkmark.circle")',
                    "                }",
                    "            }",
                    "            .navigationSplitViewColumnWidth(min: 220, ideal: 240)",
                    "        } detail: {",
                    "            ScrollView {",
                    "                VStack(alignment: .leading, spacing: 20) {",
                    "                    Text(viewModel.title)",
                    "                        .font(BiucingTheme.titleFont)",
                    "",
                    "                    Text(viewModel.subtitle)",
                    "                        .font(BiucingTheme.bodyFont)",
                    "                        .foregroundStyle(.secondary)",
                    "",
                    '                    GroupBox("Project Summary") {',
                    "                        VStack(alignment: .leading, spacing: 8) {",
                    "                            ForEach(viewModel.facts, id: \\.label) { fact in",
                    '                                Label("\\(fact.label): \\(fact.value)", systemImage: fact.systemImage)',
                    "                            }",
                    "                        }",
                    "                        .font(BiucingTheme.captionFont)",
                    "                    }",
                    "",
                    '                    GroupBox("Release Checklist") {',
                    "                        VStack(alignment: .leading, spacing: 8) {",
                    "                            ForEach(viewModel.releaseChecklist(), id: \\.self) { item in",
                    '                                Label(item, systemImage: "checkmark.circle")',
                    "                            }",
                    "                        }",
                    "                        .font(BiucingTheme.captionFont)",
                    "                    }",
                    "                }",
                    "                .frame(maxWidth: 680, alignment: .leading)",
                    "                .padding(24)",
                    "            }",
                    '            .navigationTitle("Overview")',
                    "        }",
                    "    }",
                ]
            ),
            "apple_platform_output_note": (
                "macOS starters use a split-view workspace with a fixed desktop window size."
            ),
        }

    if platform == "ios":
        return {
            "apple_scene_body": "\n".join(
                [
                    "        WindowGroup {",
                    "            HomeView()",
                    "        }",
                ]
            ),
            "apple_home_body": "\n".join(
                [
                    "    var body: some View {",
                    "        NavigationStack {",
                    "            List {",
                    '                Section("Project Summary") {',
                    "                    ForEach(viewModel.facts, id: \\.label) { fact in",
                    '                        Label("\\(fact.label): \\(fact.value)", systemImage: fact.systemImage)',
                    "                    }",
                    "                }",
                    "",
                    '                Section("Release Checklist") {',
                    "                    ForEach(viewModel.releaseChecklist(), id: \\.self) { item in",
                    '                        Label(item, systemImage: "checkmark.circle")',
                    "                    }",
                    "                }",
                    "            }",
                    "            .listStyle(.insetGrouped)",
                    '            .navigationTitle("Starter Overview")',
                    "        }",
                    "    }",
                ]
            ),
            "apple_platform_output_note": (
                "iOS starters use a stacked overview screen tuned for simulator-first mobile flows."
            ),
        }

    return {
        "apple_scene_body": "\n".join(
            [
                "        WindowGroup {",
                "            HomeView()",
                "        }",
            ]
        ),
        "apple_home_body": "\n".join(
            [
                "    var body: some View {",
                "        NavigationStack {",
                "            VStack(alignment: .leading, spacing: 16) {",
                "                Text(viewModel.title)",
                "                    .font(BiucingTheme.titleFont)",
                "",
                "                Text(viewModel.subtitle)",
                "                    .font(BiucingTheme.bodyFont)",
                "                    .foregroundStyle(.secondary)",
                "",
                "                VStack(alignment: .leading, spacing: 8) {",
                "                    ForEach(viewModel.facts, id: \\.label) { fact in",
                '                        Label("\\(fact.label): \\(fact.value)", systemImage: fact.systemImage)',
                "                    }",
                "                }",
                "                .font(BiucingTheme.captionFont)",
                "",
                "                VStack(alignment: .leading, spacing: 8) {",
                '                    Text("Release Checklist")',
                "                        .font(BiucingTheme.sectionTitleFont)",
                "",
                "                    ForEach(viewModel.releaseChecklist(), id: \\.self) { item in",
                '                        Label(item, systemImage: "checkmark.circle")',
                "                    }",
                "                }",
                "                .font(BiucingTheme.captionFont)",
                "            }",
                "            .padding(24)",
                '            .navigationTitle("Overview")',
                "        }",
                "    }",
            ]
        ),
        "apple_platform_output_note": (
            f"{values.get('apple_platform_name', 'Apple')} starters currently keep the shared overview layout."
        ),
    }


def derive(values: dict[str, str]) -> RuleResult:
    derived = apple_platform_config(values.get("apple_platform"), values.get("minimum_os_version"))
    derived["swift_module_name"] = values.get("swift_module_name") or default_swift_module_name(values["project_name"])
    snippets = apple_platform_snippets({**values, **derived})
    return RuleResult(derived, snippets)
