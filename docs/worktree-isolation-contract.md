# Worktree Isolation Contract

This contract defines what BiucingCLI means by a worktree-first starter.

The contract applies to generated projects, not to BiucingCLI's own repository checkout.
The goal is to make generated starters reliable when a developer uses several Git worktrees from the same repository at the same time.

## User Promise

A generated project should support parallel worktree use without accidental interference.

At minimum, a developer should be able to:

- run one worktree in dev mode;
- run tests in another worktree;
- build or package from a third worktree;
- use local-only signing or environment files without sharing them through Git;
- clean runtime state for one worktree without damaging another.

## Identity Model

Every generated starter should expose a worktree identity.

Required variables:

| Variable | Meaning |
| --- | --- |
| `WORKTREE_ID` | short stable identifier for the current worktree |
| `WORKTREE_SLUG` | human-readable prefix for runtime names, usually project name plus `WORKTREE_ID` |

Default derivation should be deterministic and local:

- derive from the current worktree root path;
- keep the generated value short enough for Docker, app IDs, and filesystem names;
- allow explicit override through environment or Make variables;
- do not depend on branch names alone, because branch names can be long, reused, or contain awkward characters.

Recommended default shape:

```makefile
WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_ID ?= $(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?= {{PROJECT_NAME}}-$(WORKTREE_ID)
```

Templates may adapt the hashing command for platform constraints, but the override behavior should stay consistent.

## Required Commands

Every starter should expose these commands when the platform can support them:

```bash
make worktree-info
make worktree-doctor
make clean-worktree
```

### `make worktree-info`

Print the current worktree isolation values.

The output should include relevant values from this list:

- worktree root;
- `WORKTREE_ID`;
- `WORKTREE_SLUG`;
- Compose project name;
- image tag;
- host ports;
- cache paths;
- build output paths;
- native app identifier or identifier suffix;
- local-only config files.

This command must not print secrets.
It may print whether a secret file exists.

### `make worktree-doctor`

Check for likely collisions and missing local-only prerequisites.

The command should:

- warn when a host port uses a common default that may collide;
- warn when a cache path is global and likely to be shared unintentionally;
- report whether local-only files such as `.env.local` or `local.properties` exist when relevant;
- report native app identity choices for installed debug builds;
- avoid requiring network access or heavy builds.

### `make clean-worktree`

Remove state owned by the current worktree only.

Allowed cleanup:

- current worktree Docker Compose containers, networks, and volumes;
- project-local caches under the worktree root;
- generated build outputs under the worktree root;
- worktree-specific preview/test reports.

Disallowed cleanup by default:

- global Docker images;
- global SDK installs;
- global Gradle, Xcode, pnpm, ohpm, or Go caches;
- files outside the generated project root;
- signing files or secret-bearing config files.

If a template needs stronger cleanup, it should use a clearly named separate target such as `clean-all-local` and document the risk.

## Isolation Dimensions

Every template should declare and implement the dimensions that apply to it.

| Dimension | Applies To | Contract |
| --- | --- | --- |
| runtime names | Docker and native templates | containers, Compose projects, images, and installed app identities should not collide by default |
| ports | long-running services | host ports must be overridable and visible through diagnostics |
| dependency stores | service templates | local databases, Redis, OTel, and similar services should be isolated by Compose project, network, and volume |
| caches | all templates | caches should be project-local or worktree-local when shared state can corrupt, slow, or confuse workflows |
| generated outputs | all templates | build artifacts and generated files should stay under the worktree root unless the platform requires otherwise |
| local config | all templates | `.env.local`, `local.properties`, signing material, and other machine-local files must stay git-ignored |
| installed app identity | native templates | debug builds should support a worktree-specific identity when parallel install matters |
| cleanup | all templates | cleanup targets must be scoped to the current worktree |
| diagnostics | all templates | generated projects must make their isolation decisions visible |

## Docker-First Requirements

Applies to:

- `frontend`;
- `web-service`;
- `microservice`;
- `worker`.

Required behavior:

- route Docker Compose commands through a worktree-aware `COMPOSE_PROJECT_NAME`;
- avoid hard-coded named volumes that are shared across worktrees;
- make runtime image tags include `WORKTREE_SLUG` by default or make the default clearly worktree-local;
- expose every published host port as a Make variable;
- document how to override ports for parallel worktrees;
- keep dependency stores inside the worktree-specific Compose project;
- make `clean-worktree` run `docker compose down --remove-orphans --volumes` for the current project only.

Recommended naming:

```makefile
COMPOSE_PROJECT_NAME ?= $(WORKTREE_SLUG)
IMAGE ?= $(WORKTREE_SLUG)
TAG ?= dev
```

Compose commands should pass:

```bash
COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) docker compose -f $(DEV_COMPOSE_FILE) ...
```

## Native Requirements

Applies to:

- `apple`;
- `android`;
- `harmonyos`.

Required behavior:

- make local signing files worktree-local and git-ignored;
- make build/cache paths visible through `worktree-info`;
- avoid relying on branch-shared generated outputs outside the worktree root;
- document whether parallel installed debug apps are supported;
- provide an override path for app identity suffixes when supported by the platform.

Platform-specific focus:

| Template | Required Focus |
| --- | --- |
| `apple` | Xcode DerivedData, SwiftPM build output, Tuist cache/output, bundle identifier suffix for debug installs |
| `android` | Gradle user home/build cache, debug `applicationIdSuffix`, `local.properties`, emulator install behavior |
| `harmonyos` | `.hvigor`, `oh_modules`, build output, local signing properties, bundle-name suffix only if DevEco/hvigor supports it cleanly |

## Metadata Contract

Phase B should add worktree metadata to every template.

Recommended shape:

```json
{
  "worktree": {
    "support_level": "planned",
    "isolation_dimensions": [
      "runtime-names",
      "ports",
      "caches",
      "local-config"
    ],
    "diagnostics": [
      "make worktree-info",
      "make worktree-doctor"
    ],
    "cleanup": [
      "make clean-worktree"
    ]
  }
}
```

Allowed `support_level` values:

- `planned`: the template is included in the rollout but implementation has not landed;
- `partial`: some isolation is implemented but known gaps remain;
- `worktree-ready`: the template meets this contract.

Allowed `isolation_dimensions` values should include:

- `runtime-names`;
- `ports`;
- `dependency-stores`;
- `caches`;
- `generated-output`;
- `local-config`;
- `installed-app-identity`;
- `cleanup`;
- `diagnostics`.

## Verification Contract

Repo-level verification should always include:

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

Generated-project verification should include, at minimum:

```bash
make worktree-info
make worktree-doctor
```

Docker-first templates should additionally support fast identity checks:

```bash
WORKTREE_ID=alpha make worktree-info
WORKTREE_ID=beta make worktree-info
WORKTREE_ID=alpha docker compose -f compose.dev.yaml config
WORKTREE_ID=beta docker compose -f compose.dev.yaml config
```

Native templates should additionally verify the platform-specific diagnostic values that can collide:

- Apple: DerivedData path and bundle identifier;
- Android: Gradle cache path and debug application ID;
- HarmonyOS: hvigor/ohpm output paths and local signing file status.

## Non-Goals

This contract does not require BiucingCLI to:

- create or delete Git worktrees;
- coordinate multiple worktrees through a daemon;
- allocate ports dynamically through a registry;
- manage external cloud resources;
- migrate older generated projects automatically;
- delete global tool caches during cleanup.
