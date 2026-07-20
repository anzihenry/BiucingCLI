APP_NAME={{PACKAGE_NAME}}
WORKTREE_ROOT ?=$(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_LABEL ?=$(shell basename "$(WORKTREE_ROOT)" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//; s/-$$//')
WORKTREE_ID ?=$(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?=$(APP_NAME)-$(WORKTREE_ID)
COMPOSE_PROJECT_NAME ?=$(WORKTREE_SLUG)
IMAGE ?=$(WORKTREE_SLUG)
TAG ?=dev
IMAGE_REF := $(IMAGE):$(TAG)
COMPOSE ?=COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) docker compose
DEV_COMPOSE_FILE ?=compose.dev.yaml
DEV_SERVICE ?=frontend-dev
DEV_DOCKERFILE ?=Dockerfile.dev
DEV_PORT ?=5173
DEV_HOST_PORT ?=$(DEV_PORT)
HOST_PORT ?=8080
CONTAINER_PORT ?=80
PNPM_HOME ?=$(WORKTREE_ROOT)/.pnpm-home/$(WORKTREE_ID)
PNPM_STORE_DIR ?=$(WORKTREE_ROOT)/.pnpm-store
export COMPOSE_PROJECT_NAME
export DEV_HOST_PORT
export DEV_PORT
export HOST_PORT
export CONTAINER_PORT
export PNPM_HOME
export PNPM_STORE_DIR

.PHONY: worktree-info worktree-doctor worktree-compose-config clean-worktree bootstrap bootstrap-full install dev dev-shell lint typecheck test build preview browser-install browser-smoke format format-check docker-build docker-run

worktree-info:
	@printf '%s\n' "Worktree root: $(WORKTREE_ROOT)"
	@printf '%s\n' "Worktree label: $(WORKTREE_LABEL)"
	@printf '%s\n' "Worktree ID: $(WORKTREE_ID)"
	@printf '%s\n' "Worktree slug: $(WORKTREE_SLUG)"
	@printf '%s\n' "Compose project: $(COMPOSE_PROJECT_NAME)"
	@printf '%s\n' "Dev URL: http://127.0.0.1:$(DEV_HOST_PORT)"
	@printf '%s\n' "Runtime URL: http://127.0.0.1:$(HOST_PORT)"
	@printf '%s\n' "Image ref: $(IMAGE_REF)"
	@printf '%s\n' "Compose file: $(DEV_COMPOSE_FILE)"
	@printf '%s\n' "pnpm home: $(PNPM_HOME)"
	@printf '%s\n' "pnpm store: $(PNPM_STORE_DIR)"

worktree-doctor:
	@$(MAKE) --no-print-directory worktree-info
	@case "$(PNPM_HOME)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "PNPM_HOME should stay inside this worktree: $(PNPM_HOME)"; exit 1;; esac
	@case "$(PNPM_STORE_DIR)" in "$(WORKTREE_ROOT)"/*) ;; *) printf '%s\n' "PNPM_STORE_DIR should stay inside this worktree: $(PNPM_STORE_DIR)"; exit 1;; esac
	@if [ "$(DEV_HOST_PORT)" = "5173" ]; then printf '%s\n' "Warning: DEV_HOST_PORT uses the default 5173; override it when another worktree is running."; fi
	@if [ "$(HOST_PORT)" = "8080" ]; then printf '%s\n' "Warning: HOST_PORT uses the default 8080; override it when another runtime container is running."; fi
	@if ! command -v lsof >/dev/null 2>&1; then printf '%s\n' "Port occupancy checks skipped: lsof is not available."; else \
		if lsof -nP -iTCP:$(DEV_HOST_PORT) -sTCP:LISTEN >/dev/null 2>&1; then printf '%s\n%s\n' "Warning: DEV_HOST_PORT $(DEV_HOST_PORT) is already in use." "Suggested override: DEV_HOST_PORT=$$(( $(DEV_HOST_PORT) + 10000 )) make dev"; fi; \
		if lsof -nP -iTCP:$(HOST_PORT) -sTCP:LISTEN >/dev/null 2>&1; then printf '%s\n%s\n' "Warning: HOST_PORT $(HOST_PORT) is already in use." "Suggested override: HOST_PORT=$$(( $(HOST_PORT) + 10000 )) make docker-run"; fi; \
	fi
	@printf '%s\n' "Compose config check: make worktree-compose-config"

worktree-compose-config:
	@if ! command -v docker >/dev/null 2>&1; then printf '%s\n' "Docker is not available; cannot render Compose config."; exit 1; fi
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) config

clean-worktree:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) down --remove-orphans --volumes

bootstrap:
	DEV_DOCKERFILE=$(DEV_DOCKERFILE) $(COMPOSE) -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)

bootstrap-full:
	DEV_DOCKERFILE=Dockerfile.dev.full $(COMPOSE) -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)

install:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm install

dev:
	DEV_DOCKERFILE=$(DEV_DOCKERFILE) $(COMPOSE) -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)

dev-shell:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) bash

lint:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm lint

typecheck:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm typecheck

test:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm test

build:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm build

preview:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm --service-ports $(DEV_SERVICE) pnpm preview --host 0.0.0.0 --port $(DEV_PORT)

browser-install:
	DEV_DOCKERFILE=$(DEV_DOCKERFILE) $(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm browser:install

browser-smoke:
	DEV_DOCKERFILE=$(DEV_DOCKERFILE) $(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm browser:smoke

format:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm format

format-check:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm format:check

docker-build:
	docker build -t $(IMAGE_REF) .

docker-run:
	docker run --rm -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_REF)
