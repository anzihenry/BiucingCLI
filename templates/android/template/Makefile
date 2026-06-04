SHELL := /bin/zsh

.PHONY: bootstrap doctor wrapper clean build test test-ui lint format install-debug beta release

bootstrap:
	./scripts/bootstrap

doctor:
	./scripts/doctor

wrapper:
	./scripts/sync-gradle-wrapper

clean:
	./gradlew clean

build:
	./gradlew assembleDebug

test:
	./gradlew test

test-ui:
	./gradlew connectedDebugAndroidTest

lint:
	./gradlew lint

format:
	@echo "Formatting task is not configured in the starter yet."

install-debug:
	./gradlew installDebug

beta:
	fastlane beta

release:
	fastlane release
