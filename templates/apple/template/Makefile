SHELL := /bin/zsh

APP_NAME={{PROJECT_NAME}}
WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_LABEL ?= $(shell basename "$(WORKTREE_ROOT)" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//; s/-$$//')
WORKTREE_ID ?= $(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?= $(APP_NAME)-$(WORKTREE_ID)
DERIVED_DATA_PATH ?= $(WORKTREE_ROOT)/DerivedData/$(WORKTREE_ID)
SWIFTPM_BUILD_PATH ?= $(WORKTREE_ROOT)/.build/$(WORKTREE_ID)
TUIST_HOME ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/home
TUIST_XDG_CACHE_HOME ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/xdg-cache
TUIST_XDG_STATE_HOME ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/xdg-state
TUIST_XDG_CONFIG_HOME ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/xdg-config
TUIST_TMPDIR ?= $(WORKTREE_ROOT)/.cache/tuist/$(WORKTREE_ID)/tmp
SWIFTLINT_CACHE ?= $(WORKTREE_ROOT)/.swiftlint-cache/$(WORKTREE_ID)
SWIFTFORMAT_CACHE ?= $(WORKTREE_ROOT)/.swiftformat.cache/$(WORKTREE_ID)
DEBUG_BUNDLE_SUFFIX ?= .$(WORKTREE_ID)
EFFECTIVE_BUNDLE_IDENTIFIER ?= {{BUNDLE_IDENTIFIER}}$(DEBUG_BUNDLE_SUFFIX)
XCODEBUILD := xcodebuild -derivedDataPath $(DERIVED_DATA_PATH)
TUIST_ENV := HOME=$(TUIST_HOME) XDG_CACHE_HOME=$(TUIST_XDG_CACHE_HOME) XDG_STATE_HOME=$(TUIST_XDG_STATE_HOME) XDG_CONFIG_HOME=$(TUIST_XDG_CONFIG_HOME) TMPDIR=$(TUIST_TMPDIR)

export TUIST_HOME
export TUIST_XDG_CACHE_HOME
export TUIST_XDG_STATE_HOME
export TUIST_XDG_CONFIG_HOME
export TUIST_TMPDIR
export DEBUG_BUNDLE_SUFFIX

.PHONY: bootstrap doctor generate clean build test lint format release-doctor archive beta release worktree-info worktree-doctor clean-worktree

bootstrap:
	$(TUIST_ENV) WORKTREE_ID=$(WORKTREE_ID) ./scripts/bootstrap

doctor:
	$(TUIST_ENV) WORKTREE_ID=$(WORKTREE_ID) ./scripts/doctor

generate:
	mkdir -p "$(TUIST_HOME)" "$(TUIST_XDG_CACHE_HOME)" "$(TUIST_XDG_STATE_HOME)" "$(TUIST_XDG_CONFIG_HOME)" "$(TUIST_TMPDIR)"
	$(TUIST_ENV) tuist install
	$(TUIST_ENV) tuist generate --no-open

clean:
	tuist clean

build:
	$(XCODEBUILD) \
		-workspace {{PROJECT_NAME}}.xcworkspace \
		-scheme {{SWIFT_MODULE_NAME}} \
		-destination '{{XCODEBUILD_DESTINATION}}' \
		build

test:
	$(XCODEBUILD) \
		-workspace {{PROJECT_NAME}}.xcworkspace \
		-scheme {{SWIFT_MODULE_NAME}} \
		-destination '{{XCODEBUILD_DESTINATION}}' \
		test

lint:
	swiftlint lint --cache-path $(SWIFTLINT_CACHE)

format:
	swiftformat . --cache $(SWIFTFORMAT_CACHE)

release-doctor:
	fastlane release_doctor

archive:
	fastlane archive

beta:
	fastlane beta

release:
	fastlane release

worktree-info:
	@printf '%s\n' "Project: {{PROJECT_NAME}}"
	@printf '%s\n' "Worktree root: $(WORKTREE_ROOT)"
	@printf '%s\n' "WORKTREE_LABEL: $(WORKTREE_LABEL)"
	@printf '%s\n' "WORKTREE_ID: $(WORKTREE_ID)"
	@printf '%s\n' "WORKTREE_SLUG: $(WORKTREE_SLUG)"
	@printf '%s\n' "DerivedData: $(DERIVED_DATA_PATH)"
	@printf '%s\n' "SwiftPM build path: $(SWIFTPM_BUILD_PATH)"
	@printf '%s\n' "Tuist HOME: $(TUIST_HOME)"
	@printf '%s\n' "Tuist XDG cache: $(TUIST_XDG_CACHE_HOME)"
	@printf '%s\n' "Tuist XDG state: $(TUIST_XDG_STATE_HOME)"
	@printf '%s\n' "Tuist XDG config: $(TUIST_XDG_CONFIG_HOME)"
	@printf '%s\n' "Tuist tmp: $(TUIST_TMPDIR)"
	@printf '%s\n' "SwiftLint cache: $(SWIFTLINT_CACHE)"
	@printf '%s\n' "SwiftFormat cache: $(SWIFTFORMAT_CACHE)"
	@printf '%s\n' "Debug bundle suffix: $(DEBUG_BUNDLE_SUFFIX)"
	@printf '%s\n' "Debug bundle identifier: $(EFFECTIVE_BUNDLE_IDENTIFIER)"

worktree-doctor:
	@printf '%s\n' "Checking Apple worktree isolation..."
	@test -n "$(WORKTREE_ID)" || (printf '%s\n' "WORKTREE_ID is empty" && exit 1)
	@case "$(DERIVED_DATA_PATH)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "DerivedData should stay inside this worktree: $(DERIVED_DATA_PATH)"; exit 1;; esac
	@case "$(TUIST_HOME)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "Tuist home should stay inside this worktree: $(TUIST_HOME)"; exit 1;; esac
	@case "$(TUIST_XDG_CACHE_HOME)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "Tuist cache should stay inside this worktree: $(TUIST_XDG_CACHE_HOME)"; exit 1;; esac
	@if [ -f fastlane/.env ]; then printf '%s\n' "fastlane/.env is local to this worktree and must remain untracked."; fi
	@printf '%s\n' "Apple worktree isolation looks ready."

clean-worktree:
	rm -rf "$(DERIVED_DATA_PATH)" "$(SWIFTPM_BUILD_PATH)" "$(TUIST_HOME)" "$(TUIST_XDG_CACHE_HOME)" "$(TUIST_XDG_STATE_HOME)" "$(TUIST_XDG_CONFIG_HOME)" "$(TUIST_TMPDIR)" "$(SWIFTLINT_CACHE)" "$(SWIFTFORMAT_CACHE)"
