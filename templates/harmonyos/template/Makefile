SHELL := /bin/zsh
HVIGOR ?= hvigorw

WORKTREE_ROOT := $(shell pwd)
WORKTREE_ID ?= $(shell basename "$(WORKTREE_ROOT)" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//; s/-$$//')
WORKTREE_SLUG ?= {{PROJECT_NAME}}-$(WORKTREE_ID)
HVIGOR_HOME ?= $(WORKTREE_ROOT)/.hvigor/worktree/$(WORKTREE_ID)
OHPM_HOME ?= $(WORKTREE_ROOT)/.ohpm/worktree/$(WORKTREE_ID)
OH_MODULES_DIR ?= $(WORKTREE_ROOT)/oh_modules
MODULE_BUILD_DIR ?= $(WORKTREE_ROOT)/{{HARMONY_MODULE_NAME}}/build
LOCAL_PROPERTIES ?= $(WORKTREE_ROOT)/local.properties
DEBUG_BUNDLE_SUFFIX ?= .$(WORKTREE_ID)
EFFECTIVE_DEBUG_BUNDLE_NAME ?= {{BUNDLE_NAME}}$(DEBUG_BUNDLE_SUFFIX)
HVIGOR_PROPS := -p module={{HARMONY_MODULE_NAME}} -p biucing.worktree.id=$(WORKTREE_ID) -p biucing.worktree.bundleSuffix=$(DEBUG_BUNDLE_SUFFIX)

export HVIGOR_HOME
export OHPM_HOME
export BIUCING_HARMONY_DEBUG_BUNDLE_SUFFIX := $(DEBUG_BUNDLE_SUFFIX)

.PHONY: bootstrap doctor lint build package release signing-info clean open worktree-info worktree-doctor clean-worktree

bootstrap:
	./scripts/bootstrap

doctor:
	./scripts/doctor

lint:
	./scripts/lint

build:
	$(HVIGOR) assembleHap --mode module $(HVIGOR_PROPS)

package: build

release:
	./scripts/release-build

signing-info:
	@printf '%s\n' "Configure signing in DevEco Studio or copy docs/release-signing.local.properties.example to local.properties, then run make release."

clean:
	$(HVIGOR) clean

open:
	open -a "DevEco Studio" .

worktree-info:
	@printf '%s\n' "Project: {{PROJECT_NAME}}"
	@printf '%s\n' "Worktree root: $(WORKTREE_ROOT)"
	@printf '%s\n' "WORKTREE_ID: $(WORKTREE_ID)"
	@printf '%s\n' "WORKTREE_SLUG: $(WORKTREE_SLUG)"
	@printf '%s\n' "HVIGOR_HOME: $(HVIGOR_HOME)"
	@printf '%s\n' "OHPM_HOME: $(OHPM_HOME)"
	@printf '%s\n' "oh_modules: $(OH_MODULES_DIR)"
	@printf '%s\n' "Module build dir: $(MODULE_BUILD_DIR)"
	@printf '%s\n' "local.properties: $(LOCAL_PROPERTIES)"
	@printf '%s\n' "Debug bundle suffix: $(DEBUG_BUNDLE_SUFFIX)"
	@printf '%s\n' "Requested debug bundle name: $(EFFECTIVE_DEBUG_BUNDLE_NAME)"
	@printf '%s\n' "Bundle-name suffix is passed as a build property; keep AppScope/app.json5 stable unless your DevEco setup explicitly supports per-worktree bundle rewriting."

worktree-doctor:
	@printf '%s\n' "Checking HarmonyOS worktree isolation..."
	@test -n "$(WORKTREE_ID)" || (printf '%s\n' "WORKTREE_ID is empty" && exit 1)
	@case "$(HVIGOR_HOME)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "HVIGOR_HOME should stay inside this worktree: $(HVIGOR_HOME)"; exit 1;; esac
	@case "$(OHPM_HOME)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "OHPM_HOME should stay inside this worktree: $(OHPM_HOME)"; exit 1;; esac
	@if [ -f "$(LOCAL_PROPERTIES)" ]; then printf '%s\n' "local.properties is local to this worktree and must remain untracked."; else printf '%s\n' "local.properties is absent; make release requires local signing material."; fi
	@printf '%s\n' "HarmonyOS worktree isolation looks ready."

clean-worktree:
	rm -rf "$(HVIGOR_HOME)" "$(OHPM_HOME)" "$(MODULE_BUILD_DIR)" build .biucing/release
