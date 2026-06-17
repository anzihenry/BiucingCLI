# Apple and Android Template Roadmap

This roadmap turns the current Apple and Android template backlog into an execution plan that can be implemented as a sequence of focused commits.

The goals are:

- make the templates more operationally complete;
- improve first-run developer experience;
- strengthen validation and test coverage;
- keep the work shippable in small, reviewable slices.

## Principles

- Prefer small commits that improve one workflow at a time.
- Update the full surface together: template files, README content, CLI next steps when needed, and test coverage.
- Favor real commands and runnable verification over placeholder docs.
- Keep Android and Apple aligned in quality bar, even if their native workflows differ.

## P0

### 1. Android: add a real formatting workflow

Commit:
`android: add real formatting workflow with spotless`

Why this is P0:
- the template already exposes a `format` command slot;
- it currently does not do real work;
- formatting is a low-cost, high-signal baseline for a starter.

Checklist:
- [ ] Choose the formatting stack: `spotless + ktlint` or `spotless + ktfmt`
- [ ] Add the required Gradle plugin and configuration
- [ ] Wire `./gradlew spotlessApply` or equivalent into `make format`
- [ ] Add a check task for CI-friendly usage
- [ ] Update the Android README command list
- [ ] Update tests to assert the formatting workflow exists in generated output
- [ ] Run a real generated-project formatting verification

Verification target:
- generated Android starter can run the formatting task successfully

### 2. Apple: add default swiftlint and swiftformat configuration

Commit:
`apple: add swiftlint and swiftformat starter config`

Why this is P0:
- the Apple starter already advertises `lint` and `format`;
- the command surface should be backed by real config and predictable defaults.

Checklist:
- [ ] Add `.swiftlint.yml`
- [ ] Add `.swiftformat`
- [ ] Confirm `make lint` and `make format` use the new config
- [ ] Update bootstrap or docs so the tools are installed consistently
- [ ] Update the Apple README command and notes sections
- [ ] Update tests to assert config files and command usage
- [ ] Run a real generated-project lint and format verification

Verification target:
- generated Apple starter can run lint and format with no missing-config surprises

### 3. Android: improve doctor checks for SDK, JDK, and emulator readiness

Commit:
`android: improve doctor checks for sdk jdk and emulator`

Why this is P0:
- Android environment drift is a frequent source of wasted setup time;
- `doctor` should catch environment issues before Gradle tasks fail.

Checklist:
- [ ] Check `JAVA_HOME` or active JDK availability
- [ ] Check Android SDK root availability
- [ ] Check `cmdline-tools/latest` presence
- [ ] Check `adb` availability
- [ ] Check at least one emulator or device detection path
- [ ] Improve error messages with concrete next steps
- [ ] Update README to reflect what `make doctor` validates
- [ ] Update tests for doctor output expectations
- [ ] Run a real generated-project doctor verification

Verification target:
- generated Android starter reports missing environment dependencies clearly and predictably

### 4. Apple: improve doctor checks for Xcode, Tuist, fastlane, and simulator readiness

Commit:
`apple: improve doctor checks for xcode tuist and simulators`

Why this is P0:
- Apple platform workflows are highly environment-shaped;
- better doctor output reduces fragile first-run behavior.

Checklist:
- [ ] Check `xcodebuild` availability and version
- [ ] Check `tuist` availability
- [ ] Check `fastlane` availability
- [ ] Check simulator/runtime visibility through `xcrun simctl`
- [ ] Improve errors around missing native tooling
- [ ] Update README to describe what `make doctor` covers
- [ ] Update tests for doctor behavior or generated script expectations
- [ ] Run a real generated-project doctor verification

Verification target:
- generated Apple starter surfaces native toolchain problems before `make generate` or `make test`

## P1

### 5. Android: add a minimal Compose UI smoke test path

Commit:
`android: add compose ui smoke test starter`

Why this is P1:
- `test-ui` already exists in the command surface;
- the starter should include at least one real UI test example.

Checklist:
- [ ] Add a minimal `connectedDebugAndroidTest` example
- [ ] Use the existing Compose screen as the test target
- [ ] Ensure dependencies for UI testing are present
- [ ] Update README with emulator/device prerequisites
- [ ] Update tests to assert the generated UI test file and wiring
- [ ] Run a real generated-project UI test verification when feasible

Verification target:
- generated Android starter contains a real UI test path rather than a placeholder command

### 6. Apple: expand starter test coverage with mocks or view-model examples

Commit:
`apple: expand starter test coverage with mocks`

Why this is P1:
- the starter has a basic test target;
- adding realistic tests makes the template a stronger real-world base.

Checklist:
- [ ] Add one view-model or state-oriented unit test example
- [ ] Add one mock/service test example if appropriate
- [ ] Keep the examples small and easy to understand
- [ ] Update README with test structure notes
- [ ] Update generated-file assertions in tests
- [ ] Run a real generated-project test verification

Verification target:
- generated Apple starter includes more than a trivial smoke-style test target

### 7. Android: extend the modular project skeleton

Commit:
`android: extend modular project skeleton`

Why this is P1:
- current structure is good but still somewhat demo-like;
- a second layer of modules would make the starter feel more production-shaped.

Checklist:
- [ ] Add `core/network` or equivalent shared infrastructure module
- [ ] Add `core/testing` or equivalent shared test-support module
- [ ] Consider a second feature module to demonstrate scaling
- [ ] Keep settings and Gradle wiring consistent
- [ ] Update README project layout section
- [ ] Update tests for the expanded generated file set
- [ ] Run a real generated-project build verification

Verification target:
- generated Android starter feels closer to a real mid-sized app baseline

### 8. Apple: specialize structure for iOS and macOS first

Commit:
`apple: specialize starter structure for ios and macos`

Why this is P1:
- platform support already exists;
- template output can become more platform-authentic without changing the CLI surface much.

Checklist:
- [ ] Decide which files should differ between iOS and macOS starters
- [ ] Adjust app scene or navigation defaults for iOS
- [ ] Adjust app scene, window, or sidebar defaults for macOS
- [ ] Keep watchOS and tvOS stable if not expanding them yet
- [ ] Update README notes to explain platform-specific output
- [ ] Update tests for iOS and macOS generated expectations
- [ ] Run real generation verification for both iOS and macOS

Verification target:
- generated iOS and macOS starters look intentionally platform-specific

## P2

### 9. Android: add release environment and signing placeholders

Commit:
`android: add release environment and signing placeholders`

Why this is P2:
- valuable for production handoff;
- less urgent than formatting, doctor, and tests.

Checklist:
- [ ] Add placeholder strategy for signing config
- [ ] Add environment variable or local property loading guidance
- [ ] Clarify debug/staging/release or build-type strategy
- [ ] Update fastlane notes for beta and release flows
- [ ] Update README release guidance
- [ ] Add tests for generated config placeholders where practical

Verification target:
- generated Android starter provides a clear release integration path

### 10. Apple: document signing and release integration

Commit:
`apple: document signing and release integration`

Why this is P2:
- the starter already has fastlane and team placeholders;
- the next step is better onboarding and release documentation.

Checklist:
- [ ] Document `development_team` usage clearly
- [ ] Clarify bundle identifier expectations
- [ ] Document fastlane beta and release prerequisites
- [ ] Explain what users need to supply for signing
- [ ] Update README and in-template notes
- [ ] Add tests if any generated text becomes contractually important

Verification target:
- generated Apple starter explains release setup without requiring guesswork

### 11. Android: expand the design system starter layer

Commit:
`android: expand design system starter layer`

Why this is P2:
- useful for long-term scale;
- less urgent than baseline workflow reliability.

Checklist:
- [ ] Add clearer theme token structure
- [ ] Add one or two reusable component examples
- [ ] Add dark mode guidance or starter tokens
- [ ] Update README and project layout notes
- [ ] Update tests for the new generated files
- [ ] Run real generated-project build verification

Verification target:
- generated Android starter includes a more intentional UI foundation

### 12. Apple: expand shared package architecture

Commit:
`apple: expand shared package architecture`

Why this is P2:
- the starter already has `Packages/DesignSystem`;
- additional package patterns can improve extensibility.

Checklist:
- [ ] Decide whether to add a shared utilities or services package
- [ ] Keep package boundaries easy to understand
- [ ] Update Tuist manifests and package references
- [ ] Update README package structure notes
- [ ] Update tests for generated file expectations
- [ ] Run real generated-project generation and test verification

Verification target:
- generated Apple starter demonstrates a more scalable internal package structure

## Suggested Commit Order

1. `android: add real formatting workflow with spotless`
2. `apple: add swiftlint and swiftformat starter config`
3. `android: improve doctor checks for sdk jdk and emulator`
4. `apple: improve doctor checks for xcode tuist and simulators`
5. `android: add compose ui smoke test starter`
6. `apple: expand starter test coverage with mocks`
7. `android: extend modular project skeleton`
8. `apple: specialize starter structure for ios and macos`
9. `android: add release environment and signing placeholders`
10. `apple: document signing and release integration`
11. `android: expand design system starter layer`
12. `apple: expand shared package architecture`

## Recommended Working Style

- Complete one roadmap item per commit.
- After each commit, run the generated-template verification that matches the item.
- Keep README and tests updated in the same commit as the implementation.
- Prefer shipping P0 completely before taking on P1 platform polish work.
