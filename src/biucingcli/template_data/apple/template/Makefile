SHELL := /bin/zsh
# SDK resolution and generated graphs are shared by the four shells.
.NOTPARALLEL:

APP_NAME={{PROJECT_NAME}}
PLATFORM ?= {{APPLE_PLATFORM}}
SCHEME := {{SWIFT_MODULE_NAME}}_$(PLATFORM)
export PLATFORM

ifneq ($(MAKECMDGOALS),help)
ifeq ($(filter $(PLATFORM),ios macos watchos tvos),)
$(error PLATFORM must be ios, macos, watchos or tvos)
endif
endif
WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_LABEL ?= $(shell basename "$(WORKTREE_ROOT)" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//; s/-$$//')
WORKTREE_ID ?= $(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?= $(APP_NAME)-$(WORKTREE_ID)
DERIVED_DATA_PATH ?= $(WORKTREE_ROOT)/DerivedData/$(WORKTREE_ID)
SWIFTPM_BUILD_PATH ?= $(WORKTREE_ROOT)/.build/$(WORKTREE_ID)
CORE_BUILD_PATH ?= $(WORKTREE_ROOT)/.build/core/$(WORKTREE_ID)
CORE_SWIFT_BUILD_PATH ?= $(SWIFTPM_BUILD_PATH)/shared-core
TUIST_HOME ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/home
TUIST_XDG_CACHE_HOME ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/xdg-cache
TUIST_XDG_STATE_HOME ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/xdg-state
TUIST_XDG_CONFIG_HOME ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/xdg-config
TUIST_TMPDIR ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/tmp
SWIFTLINT_CACHE ?= $(WORKTREE_ROOT)/.swiftlint-cache/$(WORKTREE_ID)
SWIFTFORMAT_CACHE ?= $(WORKTREE_ROOT)/.swiftformat.cache/$(WORKTREE_ID)
DEBUG_BUNDLE_SUFFIX ?= .$(WORKTREE_ID)
EFFECTIVE_BUNDLE_IDENTIFIER ?= {{BUNDLE_IDENTIFIER}}.$(PLATFORM)$(DEBUG_BUNDLE_SUFFIX)
RELEASE_BUNDLE_IDENTIFIER := {{BUNDLE_IDENTIFIER}}.$(PLATFORM)
TUIST_DEBUG_BUNDLE_SUFFIX := $(DEBUG_BUNDLE_SUFFIX)
XCODEBUILD := xcodebuild -derivedDataPath $(DERIVED_DATA_PATH)
TUIST_ENV := HOME=$(TUIST_HOME) XDG_CACHE_HOME=$(TUIST_XDG_CACHE_HOME) XDG_STATE_HOME=$(TUIST_XDG_STATE_HOME) XDG_CONFIG_HOME=$(TUIST_XDG_CONFIG_HOME) TMPDIR=$(TUIST_TMPDIR)
TEST_DESTINATION ?= $(shell ./scripts/test-destination $(PLATFORM) 2>/dev/null)

export TUIST_HOME
export TUIST_XDG_CACHE_HOME
export TUIST_XDG_STATE_HOME
export TUIST_XDG_CONFIG_HOME
export TUIST_TMPDIR
export DEBUG_BUNDLE_SUFFIX
export TUIST_DEBUG_BUNDLE_SUFFIX

.PHONY: components-bootstrap components-resolve component-test di-test build-all test-all bootstrap doctor generate release-generate release-identity-check clean build test lint verify format core-build core-test core-swift-test release-doctor archive beta release worktree-info worktree-doctor clean-worktree help

bootstrap:
	$(TUIST_ENV) WORKTREE_ID=$(WORKTREE_ID) ./scripts/bootstrap

doctor:
	$(TUIST_ENV) WORKTREE_ID=$(WORKTREE_ID) ./scripts/doctor

generate: components-resolve
	mkdir -p "$(TUIST_HOME)" "$(TUIST_XDG_CACHE_HOME)" "$(TUIST_XDG_STATE_HOME)" "$(TUIST_XDG_CONFIG_HOME)" "$(TUIST_TMPDIR)"
	$(TUIST_ENV) tuist install
	$(TUIST_ENV) tuist generate --no-open

release-generate:
	./scripts/components resolve --release
	@if [ -n "$(DEBUG_BUNDLE_SUFFIX)" ]; then printf '%s\n' "Release generation ignores DEBUG_BUNDLE_SUFFIX=$(DEBUG_BUNDLE_SUFFIX) and uses $(RELEASE_BUNDLE_IDENTIFIER)."; fi
	$(MAKE) --no-print-directory DEBUG_BUNDLE_SUFFIX= generate

release-identity-check:
	./scripts/verify-release-identity workspace

clean:
	tuist clean

build: components-resolve
	$(XCODEBUILD) \
		-workspace {{PROJECT_NAME}}.xcworkspace \
		-scheme $(SCHEME) \
		-destination '$(TEST_DESTINATION)' \
		build

test: components-resolve
	$(XCODEBUILD) \
		-workspace {{PROJECT_NAME}}.xcworkspace \
		-scheme $(SCHEME) \
		-destination '$(TEST_DESTINATION)' \
		test

lint:
	mkdir -p "$(SWIFTLINT_CACHE)"
	swiftlint lint --cache-path $(SWIFTLINT_CACHE)

core-build:
	cmake -S Shared/Core -B "$(CORE_BUILD_PATH)" -DCMAKE_BUILD_TYPE=Release -DBIUCING_CORE_BUILD_TESTS=ON
	cmake --build "$(CORE_BUILD_PATH)" --config Release

core-test: core-build
	ctest --test-dir "$(CORE_BUILD_PATH)" -C Release --output-on-failure

core-swift-test:
	swift test --package-path Shared/Core --scratch-path "$(CORE_SWIFT_BUILD_PATH)"

verify: doctor lint core-test core-swift-test component-test di-test test-all build-all

format:
	mkdir -p "$(SWIFTFORMAT_CACHE)"
	swiftformat . --cache $(SWIFTFORMAT_CACHE)

release-doctor:
	fastlane release_doctor

archive:
	@if [ -n "$(DEBUG_BUNDLE_SUFFIX)" ]; then printf '%s\n' "Archive ignores DEBUG_BUNDLE_SUFFIX=$(DEBUG_BUNDLE_SUFFIX) and uses $(RELEASE_BUNDLE_IDENTIFIER)."; fi
	DEBUG_BUNDLE_SUFFIX= fastlane archive

beta:
	@if [ -n "$(DEBUG_BUNDLE_SUFFIX)" ]; then printf '%s\n' "Beta delivery ignores DEBUG_BUNDLE_SUFFIX=$(DEBUG_BUNDLE_SUFFIX) and uses $(RELEASE_BUNDLE_IDENTIFIER)."; fi
	DEBUG_BUNDLE_SUFFIX= fastlane beta

release:
	@if [ -n "$(DEBUG_BUNDLE_SUFFIX)" ]; then printf '%s\n' "App Store delivery ignores DEBUG_BUNDLE_SUFFIX=$(DEBUG_BUNDLE_SUFFIX) and uses $(RELEASE_BUNDLE_IDENTIFIER)."; fi
	DEBUG_BUNDLE_SUFFIX= fastlane release

worktree-info:
	@printf '%s\n' "Project: {{PROJECT_NAME}}"
	@printf '%s\n' "Worktree root: $(WORKTREE_ROOT)"
	@printf '%s\n' "WORKTREE_LABEL: $(WORKTREE_LABEL)"
	@printf '%s\n' "WORKTREE_ID: $(WORKTREE_ID)"
	@printf '%s\n' "WORKTREE_SLUG: $(WORKTREE_SLUG)"
	@printf '%s\n' "DerivedData: $(DERIVED_DATA_PATH)"
	@printf '%s\n' "SwiftPM build path: $(SWIFTPM_BUILD_PATH)"
	@printf '%s\n' "C++ core build path: $(CORE_BUILD_PATH)"
	@printf '%s\n' "Shared core Swift build path: $(CORE_SWIFT_BUILD_PATH)"
	@printf '%s\n' "Tuist HOME: $(TUIST_HOME)"
	@printf '%s\n' "Tuist XDG cache: $(TUIST_XDG_CACHE_HOME)"
	@printf '%s\n' "Tuist XDG state: $(TUIST_XDG_STATE_HOME)"
	@printf '%s\n' "Tuist XDG config: $(TUIST_XDG_CONFIG_HOME)"
	@printf '%s\n' "Tuist tmp: $(TUIST_TMPDIR)"
	@printf '%s\n' "SwiftLint cache: $(SWIFTLINT_CACHE)"
	@printf '%s\n' "SwiftFormat cache: $(SWIFTFORMAT_CACHE)"
	@printf '%s\n' "Debug bundle suffix: $(DEBUG_BUNDLE_SUFFIX)"
	@printf '%s\n' "Debug bundle identifier: $(EFFECTIVE_BUNDLE_IDENTIFIER)"
	@printf '%s\n' "Release bundle identifier: $(RELEASE_BUNDLE_IDENTIFIER)"
	@printf '%s\n' "Test destination: $(TEST_DESTINATION)"

worktree-doctor:
	@printf '%s\n' "Checking Apple worktree isolation..."
	@test -n "$(WORKTREE_ID)" || (printf '%s\n' "WORKTREE_ID is empty" && exit 1)
	@case "$(DERIVED_DATA_PATH)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "DerivedData should stay inside this worktree: $(DERIVED_DATA_PATH)"; exit 1;; esac
	@case "$(CORE_BUILD_PATH)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "C++ core build should stay inside this worktree: $(CORE_BUILD_PATH)"; exit 1;; esac
	@case "$(CORE_SWIFT_BUILD_PATH)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "Shared core Swift build should stay inside this worktree: $(CORE_SWIFT_BUILD_PATH)"; exit 1;; esac
	@case "$(TUIST_HOME)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "Tuist home should stay inside this worktree: $(TUIST_HOME)"; exit 1;; esac
	@case "$(TUIST_XDG_CACHE_HOME)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "Tuist cache should stay inside this worktree: $(TUIST_XDG_CACHE_HOME)"; exit 1;; esac
	@if [ -f fastlane/.env ]; then printf '%s\n' "fastlane/.env is local to this worktree and must remain untracked."; fi
	@printf '%s\n' "Apple worktree isolation looks ready."

clean-worktree:
	rm -rf "$(DERIVED_DATA_PATH)" "$(SWIFTPM_BUILD_PATH)" "$(CORE_BUILD_PATH)" "$(CORE_SWIFT_BUILD_PATH)" "$(TUIST_HOME)" "$(TUIST_XDG_CACHE_HOME)" "$(TUIST_XDG_STATE_HOME)" "$(TUIST_XDG_CONFIG_HOME)" "$(TUIST_TMPDIR)" "$(SWIFTLINT_CACHE)" "$(SWIFTFORMAT_CACHE)"

help:
	@printf '%s\n' "Component commands:" "  make components-bootstrap  Publish initial static SDKs and lock" "  make components-resolve    Resolve verified binaries" "  make component-test        Test component source" "  make di-test               Validate SafeDI and invalid graphs" "  make build-all test-all    Verify all four shells" "  make build PLATFORM=macos  Select one shell"
	@printf '%s\n' "Shared C++ commands:" "  make core-build       Build portable C++20 core with CMake" "  make core-test        Test the C boundary on the host" "  make core-swift-test  Test the Swift wrapper on the host"
	@printf '%s\n' "Common commands:" "  make bootstrap  Prepare project dependencies and tooling" "  make doctor     Check the local environment" "  make lint       Run static checks" "  make test       Run automated tests" "  make verify     Run the template quality gate" "  make build      Build the project" "  make clean      Remove generated build state" "  make help       Show this command contract"

# Explicit first publication. Subsequent changes require a new immutable version.
components-bootstrap:
	./scripts/components build --version 0.1.0
	./scripts/components lock
	./scripts/components resolve
	./scripts/components di

components-resolve:
	./scripts/components resolve
	./scripts/components di

di-test:
	./scripts/components check-di

component-test: di-test
	swift test --package-path Components --scratch-path "$(SWIFTPM_BUILD_PATH)/components"

build-all:
	@for platform in ios macos watchos tvos; do $(MAKE) build PLATFORM=$$platform || exit $$?; done

test-all:
	@for platform in ios macos watchos tvos; do $(MAKE) test PLATFORM=$$platform || exit $$?; done
