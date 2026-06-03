SHELL := /bin/zsh

.PHONY: bootstrap doctor generate clean build test lint format beta release

bootstrap:
	./scripts/bootstrap

doctor:
	./scripts/doctor

generate:
	tuist install
	tuist generate --no-open

clean:
	tuist clean

build:
	xcodebuild \
		-workspace {{PROJECT_NAME}}.xcworkspace \
		-scheme {{SWIFT_MODULE_NAME}} \
		-destination 'platform=iOS Simulator,name=iPhone 16' \
		build

test:
	xcodebuild \
		-workspace {{PROJECT_NAME}}.xcworkspace \
		-scheme {{SWIFT_MODULE_NAME}} \
		-destination 'platform=iOS Simulator,name=iPhone 16' \
		test

lint:
	swiftlint

format:
	swiftformat .

beta:
	fastlane beta

release:
	fastlane release
