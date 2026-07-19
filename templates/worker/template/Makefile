APP_NAME={{WORKER_NAME}}
WORKTREE_ROOT ?=$(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_ID ?=$(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?=$(APP_NAME)-$(WORKTREE_ID)
COMPOSE_PROJECT_NAME ?=$(WORKTREE_SLUG)
IMAGE ?=$(WORKTREE_SLUG)
TAG ?=dev
IMAGE_REF := $(IMAGE):$(TAG)
DEV_IMAGE ?=$(WORKTREE_SLUG)-dev
DEV_TAG ?=dev
DEV_IMAGE_REF := $(DEV_IMAGE):$(DEV_TAG)
COMPOSE ?=COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) docker compose
DEV_COMPOSE_FILE ?=compose.dev.yaml
DEV_SERVICE ?=app-dev
GOPROXY ?=https://proxy.golang.org,direct
GOSUMDB ?=sum.golang.org
BUILDER_IMAGE ?=golang:1.26-alpine
RUNTIME_IMAGE ?=alpine:3.20
WORKER_RUN_MODE ?={{RUN_MODE}}
WORKER_TICK_INTERVAL_SECONDS ?={{TICK_INTERVAL_SECONDS}}
WORKER_SHUTDOWN_TIMEOUT_SECONDS ?={{SHUTDOWN_TIMEOUT_SECONDS}}
GOCACHE ?= $(CURDIR)/.cache/go-build
export COMPOSE_PROJECT_NAME
export DEV_IMAGE
export DEV_TAG
export WORKER_RUN_MODE
export WORKER_TICK_INTERVAL_SECONDS
export WORKER_SHUTDOWN_TIMEOUT_SECONDS
export GOCACHE

.PHONY: worktree-info worktree-doctor clean-worktree bootstrap doctor dev dev-shell test verify run build docker-build docker-run

worktree-info:
	@printf '%s\n' "Worktree root: $(WORKTREE_ROOT)"
	@printf '%s\n' "Worktree ID: $(WORKTREE_ID)"
	@printf '%s\n' "Worktree slug: $(WORKTREE_SLUG)"
	@printf '%s\n' "Compose project: $(COMPOSE_PROJECT_NAME)"
	@printf '%s\n' "Dev image ref: $(DEV_IMAGE_REF)"
	@printf '%s\n' "Runtime image ref: $(IMAGE_REF)"
	@printf '%s\n' "Go cache: $(GOCACHE)"
	@printf '%s\n' "Worker run mode: $(WORKER_RUN_MODE)"

worktree-doctor:
	@$(MAKE) --no-print-directory worktree-info
	@printf '%s\n' "Worker has no published host ports by default."

clean-worktree:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) down --remove-orphans --volumes

bootstrap:
	GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) $(COMPOSE) -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)

doctor:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) ./scripts/doctor

dev:
	WORKER_RUN_MODE=$(WORKER_RUN_MODE) WORKER_TICK_INTERVAL_SECONDS=$(WORKER_TICK_INTERVAL_SECONDS) WORKER_SHUTDOWN_TIMEOUT_SECONDS=$(WORKER_SHUTDOWN_TIMEOUT_SECONDS) GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) $(COMPOSE) -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)

dev-shell:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) sh

test:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go test ./...

verify: doctor test

run:
	WORKER_RUN_MODE=$(WORKER_RUN_MODE) WORKER_TICK_INTERVAL_SECONDS=$(WORKER_TICK_INTERVAL_SECONDS) WORKER_SHUTDOWN_TIMEOUT_SECONDS=$(WORKER_SHUTDOWN_TIMEOUT_SECONDS) $(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE)

build:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go build -o bin/$(APP_NAME) ./cmd/worker

docker-build:
	docker build --build-arg BUILDER_IMAGE=$(BUILDER_IMAGE) --build-arg RUNTIME_IMAGE=$(RUNTIME_IMAGE) --build-arg GOPROXY=$(GOPROXY) --build-arg GOSUMDB=$(GOSUMDB) -t $(IMAGE_REF) .

docker-run:
	docker run --rm -e WORKER_RUN_MODE=$(WORKER_RUN_MODE) -e WORKER_TICK_INTERVAL_SECONDS=$(WORKER_TICK_INTERVAL_SECONDS) -e WORKER_SHUTDOWN_TIMEOUT_SECONDS=$(WORKER_SHUTDOWN_TIMEOUT_SECONDS) $(IMAGE_REF)
