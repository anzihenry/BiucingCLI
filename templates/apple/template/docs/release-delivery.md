# Release Delivery

The generated starter includes fastlane lanes for release credential checks, signed archive creation, TestFlight upload, and App Store Connect upload.

## One-Time Setup

1. Register `{{BUNDLE_IDENTIFIER}}` in Apple Developer and App Store Connect.
2. Create an App Store Connect API key with access to manage builds for the app.
3. Save the fastlane API key JSON locally and keep it untracked.
4. Create a private certificate repository for `fastlane match`.
5. Copy `fastlane/.env.example` to `fastlane/.env` and replace the placeholders.
6. Run the first certificate/profile sync from a trusted machine:

```bash
MATCH_ALLOW_WRITE=true fastlane match appstore
```

After the first sync, keep `MATCH_ALLOW_WRITE=false` on developer and CI machines so release jobs consume known signing material instead of mutating it.

## Commands

```bash
make release-doctor
make release-generate
make release-identity-check
make archive
make beta
make release
```

- `make release-doctor` validates local release credentials and signing configuration.
- `make release-generate` regenerates the workspace with the configured release bundle identifier and ignores any `DEBUG_BUNDLE_SUFFIX` inherited from a worktree or shell.
- `make release-identity-check` verifies the Release target's resolved `PRODUCT_BUNDLE_IDENTIFIER` before signing material is requested.
- `make archive` generates and verifies the Release workspace, lints, tests, syncs App Store signing, builds a signed archive, and verifies the xcarchive bundle identifier.
- `make beta` runs `archive` and uploads the signed ipa/pkg to TestFlight.
- `make release` runs `archive` and uploads the signed ipa/pkg to App Store Connect.

By default, `make release` uploads the binary but does not submit it for review. Set `APP_STORE_SUBMIT_FOR_REVIEW=true` only after metadata, screenshots, review information, privacy details, and compliance answers are ready.

## Release Identity Boundary

`DEBUG_BUNDLE_SUFFIX` belongs only to local Debug/worktree workflows. Archive, beta, and release lanes always clear it, even when a caller exports a non-empty value. The delivery pipeline compares both the generated Release build settings and `Info.plist` inside the final xcarchive with `{{BUNDLE_IDENTIFIER}}`; any missing or different value stops the lane before upload.

## Local Secrets

Keep these files local or in your CI secret store:

- `fastlane/.env`
- `fastlane/app-store-connect-api-key.json` when viewed from the project root, or `app-store-connect-api-key.json` in `fastlane/.env`
- `fastlane/*.p8`

Do not commit API keys, certificate repository credentials, provisioning profiles, or Apple ID sessions.
