# Google Play Release Delivery

The generated starter uses fastlane `supply` to validate release inputs, build a signed Android App Bundle (AAB), upload internal test builds, and create a draft production release in Google Play Console.

## One-Time Setup

1. Create `{{APPLICATION_ID}}` in Google Play Console and finish the required app-registration steps.
2. Enable the Google Play Developer API for the Google Cloud project that owns the service account.
3. Create a service-account JSON key, invite that account in Play Console with the least privileges needed for the intended tracks, and save it locally as `credentials/play-store-service-account.json`.
4. Configure an upload keystore through `local.properties` or the `BIUCING_RELEASE_*` CI variables. For Play App Signing, this is the upload key, not the app-signing key managed by Google.
5. Copy `fastlane/.env.example` to `fastlane/.env` and replace its placeholder values.
6. Verify the credential independently before the first delivery:

```bash
fastlane run validate_play_store_json_key json_key:credentials/play-store-service-account.json
```

Google Play requires an app record to exist before API-driven delivery. Complete the first app-registration flow in Play Console before relying on a CI upload.

## Commands

```bash
make release-doctor
make verify-supply-chain
make archive
make artifact-info
make verify-release-artifact
make beta
make release
```

- `make release-doctor` verifies the service-account JSON, the four release-signing inputs, upload keystore, private key alias, and any enabled metadata directory.
- `make verify-supply-chain` validates the pinned Gradle distribution and wrapper JAR, exact dependency versions, and Gradle dependency checksum metadata.
- `make archive` runs lint and unit tests, validates the signing key, builds a signed `app-release.aab`, then verifies its cryptographic signature and signer certificate without uploading it.
- `make verify-release-artifact` checks AAB structure and compares the embedded signer SHA-256 fingerprint with the configured upload key. `make artifact-info` performs the same gate before printing the handoff checksum.
- `make beta` runs the archive lane and uploads the AAB to the `internal` track by default.
- `make release` runs the archive lane and uploads the AAB to the `production` track as a `draft` by default.

Set `PLAY_STORE_BETA_TRACK`, `PLAY_STORE_BETA_RELEASE_STATUS`, `PLAY_STORE_RELEASE_TRACK`, or `PLAY_STORE_RELEASE_STATUS` only when the target promotion and rollout have been reviewed. Valid release statuses include `draft`, `inProgress`, `halted`, and `completed`.

## Store Listing Assets

fastlane can upload metadata, changelogs, images, and screenshots from `fastlane/metadata/android`. For an existing app, initialize that tree from Play Console:

```bash
fastlane supply init
```

After reviewing the downloaded files, set the relevant `PLAY_STORE_SKIP_*` value to `false`. Keep the defaults while the listing is managed directly in Play Console.

Data safety declarations, content rating, target audience, app access instructions, privacy policy, managed publishing choices, and Play Console review answers remain product and compliance decisions. Complete and review them in Play Console before changing a production draft to a live release.

## Local Secrets

Keep these out of version control and store them in the CI secret manager:

- `fastlane/.env`
- `credentials/play-store-service-account.json`
- the upload keystore under `signing/` and its passwords
- `local.properties` when it contains signing values

For direct Gradle use, keep signing values in `~/.gradle/gradle.properties`; never add them to the tracked project-level `gradle.properties`. Keep `.env.example` and signing-property examples as placeholders only.

Ignore rules only protect untracked files and do not override `git add -f`. If real credentials have already been committed, revoke or rotate them first, remove them from the index, and assess whether repository history must be rewritten.

## Dependency Verification Maintenance

The committed wrapper properties include the Gradle distribution SHA-256, while `gradle-wrapper.jar.sha256` pins the official wrapper executable. Gradle automatically enforces the artifact checksums in `gradle/verification-metadata.xml`. When intentionally upgrading a plugin or dependency, generate new SHA-256 metadata in a clean review branch, inspect the repository coordinates and checksum diff, and only then commit it. A checksum should never be copied from a failed build or an untrusted mirror.
