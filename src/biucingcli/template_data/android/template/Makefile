SHELL := /bin/zsh

PLATFORM ?= mobile
ifeq ($(PLATFORM),mobile)
APP_MODULE := app
PLATFORM_SUFFIX :=
else ifeq ($(PLATFORM),wear)
APP_MODULE := wear
PLATFORM_SUFFIX := .wear
else ifeq ($(PLATFORM),tv)
APP_MODULE := tv
PLATFORM_SUFFIX := .tv
else
$(error PLATFORM must be mobile, wear, or tv)
endif
export PLATFORM

APP_NAME={{PROJECT_NAME}}
WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_LABEL ?= $(shell basename "$(WORKTREE_ROOT)" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//; s/-$$//')
WORKTREE_ID ?= w$(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?= $(APP_NAME)-$(WORKTREE_ID)
GRADLE_USER_HOME ?= $(WORKTREE_ROOT)/.gradle/worktree/$(WORKTREE_ID)
GRADLE_PROJECT_CACHE ?= $(WORKTREE_ROOT)/.gradle
ANDROID_LOCAL_PROPERTIES ?= $(WORKTREE_ROOT)/local.properties
DEBUG_APPLICATION_ID_SUFFIX ?= .debug.$(WORKTREE_ID)
EFFECTIVE_DEBUG_APPLICATION_ID ?= {{APPLICATION_ID}}$(PLATFORM_SUFFIX)$(DEBUG_APPLICATION_ID_SUFFIX)
GRADLE := GRADLE_USER_HOME=$(GRADLE_USER_HOME) ./gradlew -Dorg.gradle.project.biucing.worktree.applicationIdSuffix=$(DEBUG_APPLICATION_ID_SUFFIX)

export GRADLE_USER_HOME

.PHONY: bootstrap doctor wrapper verify-supply-chain clean build bundle-release artifact-info verify-release-artifact verify verify-release-signing test test-ui lint format install-debug release-doctor archive beta release worktree-info worktree-doctor clean-worktree help

bootstrap:
	./scripts/bootstrap

doctor:
	./scripts/doctor

wrapper:
	./scripts/sync-gradle-wrapper

verify-supply-chain:
	./scripts/verify-gradle-supply-chain

clean build bundle-release verify-release-signing test test-ui lint format install-debug: verify-supply-chain

clean:
	$(GRADLE) clean

build:
	$(GRADLE) :$(APP_MODULE):assembleDebug

bundle-release:
	$(GRADLE) :$(APP_MODULE):bundleRelease

artifact-info:
	./scripts/artifact-info

verify-release-artifact:
	./scripts/verify-release-artifact

verify: verify-supply-chain doctor lint test build core-test

verify-release-signing:
	$(GRADLE) :$(APP_MODULE):verifyReleaseSigning

test:
	$(GRADLE) :$(APP_MODULE):test

test-ui:
	$(GRADLE) :$(APP_MODULE):connectedDebugAndroidTest

lint:
	$(GRADLE) :$(APP_MODULE):lint

format:
	$(GRADLE) spotlessApply
	$(GRADLE) -p components spotlessApply

install-debug:
	$(GRADLE) :$(APP_MODULE):installDebug

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
	@printf '%s\n' "Gradle user home: $(GRADLE_USER_HOME)"
	@printf '%s\n' "Gradle project cache: $(GRADLE_PROJECT_CACHE)"
	@printf '%s\n' "local.properties: $(ANDROID_LOCAL_PROPERTIES)"
	@printf '%s\n' "Debug application ID suffix: $(DEBUG_APPLICATION_ID_SUFFIX)"
	@printf '%s\n' "Debug application ID: $(EFFECTIVE_DEBUG_APPLICATION_ID)"

worktree-doctor:
	@printf '%s\n' "Checking Android worktree isolation..."
	@test -n "$(WORKTREE_ID)" || (printf '%s\n' "WORKTREE_ID is empty" && exit 1)
	@case "$(GRADLE_USER_HOME)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "Gradle user home should stay inside this worktree: $(GRADLE_USER_HOME)"; exit 1;; esac
	@if [ -f "$(ANDROID_LOCAL_PROPERTIES)" ]; then printf '%s\n' "local.properties is local to this worktree and must remain untracked."; else printf '%s\n' "local.properties is absent; run make bootstrap or configure Android SDK paths if needed."; fi
	@printf '%s\n' "Android worktree isolation looks ready."

clean-worktree:
	rm -rf "$(GRADLE_USER_HOME)" app/build wear/build tv/build core/*/build feature/*/build components/build .build build

help:
	@printf '%s\n' "Common commands (PLATFORM=mobile|wear|tv, default mobile):" "  make verify-all Validate all three applications" "  make bootstrap  Prepare project dependencies and tooling" "  make doctor     Check the local environment" "  make lint       Run static checks" "  make test       Run automated tests" "  make verify     Run the template quality gate" "  make build      Build the project" "  make clean      Remove generated build state" "  make help       Show this command contract"

.PHONY: components-bootstrap components-test components-info components-resolve core-test
components-bootstrap:
	python3 scripts/components bootstrap
	$(GRADLE) :app:dependencies :wear:dependencies :tv:dependencies --write-locks

components-test:
	$(GRADLE) -p components testReleaseUnitTest

components-info:
	python3 scripts/components info

components-resolve:
	python3 scripts/components resolve

core-test:
	cmake -S shared/core -B .build/core -DCMAKE_BUILD_TYPE=Release
	cmake --build .build/core
	ctest --test-dir .build/core --output-on-failure

.PHONY: build-all test-all lint-all verify-all
build-all: verify-supply-chain
	$(GRADLE) :app:assembleDebug :wear:assembleDebug :tv:assembleDebug

test-all: verify-supply-chain
	$(GRADLE) :app:test :wear:test :tv:test

lint-all: verify-supply-chain
	$(GRADLE) :app:lint :wear:lint :tv:lint

verify-all: doctor lint-all test-all build-all components-test core-test
