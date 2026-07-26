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
make archive
make beta
make release
```

- `make release-doctor` validates local release credentials and signing configuration.
- `make archive` generates the workspace, lints, tests, syncs App Store signing, and builds a signed archive.
- `make beta` runs `archive` and uploads the signed ipa/pkg to TestFlight.
- `make release` runs `archive` and uploads the signed ipa/pkg to App Store Connect.

By default, `make release` uploads the binary but does not submit it for review. Set `APP_STORE_SUBMIT_FOR_REVIEW=true` only after metadata, screenshots, review information, privacy details, and compliance answers are ready.

## Local Secrets

Keep these files local or in your CI secret store:

- `fastlane/.env`
- `fastlane/app-store-connect-api-key.json` when viewed from the project root, or `app-store-connect-api-key.json` in `fastlane/.env`
- `fastlane/*.p8`

Do not commit API keys, certificate repository credentials, provisioning profiles, or Apple ID sessions.
