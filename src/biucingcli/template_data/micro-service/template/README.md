# {{PROJECT_NAME}}

Service-facing backend: versioned Protobuf/gRPC, mandatory mTLS, explicit method authorization,
optional PostgreSQL. Production delivery/HA and resilient outbound clients remain later stages.

## Workload identity

`bootstrap` creates a local-only CA and server/client certificates using pinned Smallstep CLI.
Private files stay in .secrets and are neither committed nor copied into images. Existing credentials
are preserved; `ROTATE_LOCAL_CERTS=yes ./scripts/local-ca` renews the leaves under the same local CA.
Local leaves expire after 24 hours. Never use this CA for production.

Every RPC, including health, requires a valid client certificate. TLS 1.3 verifies chains/client EKU;
identity comes from exactly one verified SPIFFE URI SAN. CN and identity metadata are not trusted.
Each full method name has an exact identity allowlist in workload.methods. Default local policy permits
only the generated technical Ping and health methods for spiffe://local/client. Unlisted methods deny.
HTTP exposes only a technical ping; it is not an alternative plaintext RPC transport.

workload.certificate/key/roots are re-read for each handshake. Rotate certificates and trust bundles
with atomic versioned-directory/symlink replacement; invalid files fail new handshakes closed.
For CA rollover, distribute old+new roots, rotate leaves, then retire old roots. Existing connections
are not re-handshaken on file change; drain/restart them when immediate root revocation is needed.
Certificate expiry is also checked on each RPC. Production workload issuance/rotation belongs to the platform.

User context is optional: x-user-issuer plus x-user-subject, one bounded printable value each.
The immediate authenticated workload must be listed for that method in workload.delegates.
Delegation is empty by default. Every hop must authorize independently; do not blindly copy inbound
metadata to another RPC. Pure service calls carry only workload identity and do not fabricate a user.
Web strips terminal X-User-* input; future outbound adapters construct context only from verified Principal.

`cmd/rpc-probe` demonstrates a consumer importing only api/gen/go, never server internal packages.
Run it in a dev container or with Go, using RPC_TARGET and the local client credentials. Production
clients verify the service DNS/SAN and trusted CA; they must never disable verification.

## RPC contract

Protobuf package {{PROTO_PACKAGE}} is versioned; consumers pin a published module revision and import
{{MODULE_NAME}}/api/gen/go/service/v1. Buf plugins are pinned. `scripts/check proto` regenerates clients;
CI lints and compares against the real committed api/baseline schema with Buf FILE breaking rules.
Commit generated api/gen/go files when publishing a module/tag so external consumers can import them.
Baselines change only with reviewed releases. Never reuse field numbers; reserve removed names/numbers.
Unknown protobuf fields are retained for compatible evolution; malformed wire encoding and oversized
messages are rejected by grpc-go. Ping validates its optional bounded request ID. Semantic validation
for future messages implements Validate before application work. Unary and streaming paths share limits.

Public gRPC errors preserve status codes and safe code names with stable ErrorInfo reason/domain;
internal error text/details are stripped. Use InvalidArgument for invalid requests, Unauthenticated for
invalid identity, PermissionDenied for denied application policy, ResourceExhausted for budgets,
DeadlineExceeded/Canceled for request lifetimes, and Unavailable for transient dependency failure.
Do not infer retry safety merely from a status; outbound retry policy and operation semantics are B16/B17.

## Docker and configuration

Use `./scripts/task bootstrap`, `dev`, `logs`, `verify`, `integration`, `image`, `down`.
Docker + Compose + Git + Bash are sufficient; Make is an optional wrapper.
`dev/up` starts in the background. `verify` runs lint, race tests, contract checks and build;
`integration` starts isolated PostgreSQL and runs real database tests when enabled.
`./scripts/verify-container` uses a new project and removes only its own containers/volumes on exit.

Worktree path determines project, volume, cache and image names. Dev containers use your UID/GID.
Air sends SIGINT and waits before rebuilding. `down` retains data. Only
`CONFIRM_DELETE_DATA=yes ./scripts/task clean-worktree` removes this project's data/cache.
Never use that command against a production project. No database/admin ports are published.

`compose.dev.yaml` and `compose.yaml` are standalone, never implicit overlays.
`image` builds server and separate migration executables. `docker-run` runs local runtime fixtures,
executes migration once before starting the application, and uses a separate runtime Compose project.
It is not the production deployment pipeline. B20 provides production proxy, hardening and delivery.

Configuration order: CONFIG_FILE YAML → defaults → documented environment overrides.
Unknown YAML fields and invalid budgets fail startup. Common overrides: APP_ENV, SERVICE_NAME,
HTTP_PORT, ADMIN_ADDR, LOG_LEVEL, DATABASE_DSN, CACHE_DSN. Secret `_FILE` forms are supported;
setting both direct and file forms fails even when empty. Files are read once, limited to 64 KiB,
and errors/diagnostics never print their values. Rotate secrets by replacing mounts and restarting.
Do not commit `.secrets/`, `.env*` or private keys; they are excluded from the image context.
Production requires explicitly supplied database/cache secrets, PostgreSQL verify-full and Redis TLS;
local starter passwords are rejected. `/app/server check-config` performs safe validation only.

## PostgreSQL and migrations

Database `{{DATABASE}}`, cache `{{CACHE}}`. Redis remains a later adapter; it is not used for sessions.
Micro with database=none does not initialize a pool. PostgreSQL uses pgx; default max pool size 10,
query/transaction budget 3 seconds. Every repository operation must use Store.Context or Store.Within;
a parent deadline remains effective. Transaction failure/cancellation rolls back with a separate finite cleanup budget.
Pool lifetime/idle expiry and connection replacement permit reconnection after transient failures.

Budget all replicas together: `peak replicas (including rollout surge) × max_connections + migration/
maintenance/other clients < database max_connections - reserved connections`. Measure memory, queueing
and latency under load before raising the limit. Do not multiply pools inside one process.

Each generated service owns its database and roles. PostgreSQL service names are limited to 54
characters so role names fit the PostgreSQL identifier limit. Local init SQL creates `{{SERVICE_NAME}}_app`
(DML only) and `{{SERVICE_NAME}}_migrator` (schema owner), revokes PUBLIC database/schema access,
and sets default grants. The role names differ between services. Production provisioning must also
revoke PUBLIC CONNECT on every service database and grant only its owner/service roles; a shared
physical PostgreSQL cluster does not grant permission to read another service's tables.
Provision roles before migration; never use the local superuser or local passwords in production.
Runtime cannot CREATE tables or change schema_migrations. Backup/restore delivery is a later stage.

`./scripts/task migrate` is a development helper. Production runs `/app/migrate` from the same image
once in the release pipeline, with `MIGRATION_DSN_FILE`, `APP_ENV=production`, and
`DATABASE_RUNTIME_ROLE` if the provisioned runtime role differs from `{{SERVICE_NAME}}_app`.
Migration credentials are never injected into the API container. No API replica runs migrations.
SQL files are embedded in the migration binary. Advisory locking serializes concurrent runners;
a failed version stays dirty and blocks retry/startup. Inspect the failure, restore/repair under a
maintenance procedure, then explicitly set the reviewed version with the pinned migrate operator CLI.
No automatic force/down is provided. Take a backup before manual repair.

Application startup and readiness require a clean supported schema (currently version 1).
Upgrade with expand → data migration → rollout → contract; widen the supported version interval in
both old/new applications before a compatible rollout. Do not combine destructive SQL with a rolling
release that still serves old binaries. Application rollback never assumes database rollback.
Existing P1 development volumes lack the new roles: migrate their grants deliberately or explicitly
recreate disposable local data; startup does not silently delete or rebuild volumes.

## Runtime and operations

Default body/message limit 1 MiB, concurrency 64, request deadline 5 seconds. HTTP errors use
`{"error":"stable_code"}`: 400 invalid input, 401 missing/invalid identity, 403 denied, 413 too large,
429 overload, 500 internal, 503 timeout/unavailable. Request IDs accept only bounded safe characters.
Internal errors, panic text, query strings, request bodies and credentials are not exposed in logs.
Handlers must honor context; a timed-out uncooperative handler retains its admission slot until exit.
Buffered HTTP timeout handling does not support streaming (E07).

Private admin defaults to container loopback 127.0.0.1:9000: /livez, /readyz, /version.
Liveness does not query PostgreSQL; readiness checks required pool/schema and startup/drain state.
Reflection/pprof are not public. SIGTERM marks unready, closes admission, drains with finite budgets,
and closes remaining connections. Pool cleanup has a separate five-second cap; optional telemetry
cleanup has its own configured deadline. Container/Air grace defaults to 30 seconds; if increasing
shutdown budgets, increase the enclosing process grace period accordingly. Telemetry does not decide readiness.

Structured slog access/audit events share a bounded process budget and redact sensitive keys.
They are not a lossless compliance ledger. Storage/retention and full metrics/tracing remain B18/platform work.
