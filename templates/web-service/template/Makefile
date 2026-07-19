APP_NAME={{SERVICE_NAME}}
WORKTREE_ROOT ?=$(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_LABEL ?=$(shell basename "$(WORKTREE_ROOT)" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//; s/-$$//')
WORKTREE_ID ?=$(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?=$(APP_NAME)-$(WORKTREE_ID)
COMPOSE_PROJECT_NAME ?=$(WORKTREE_SLUG)
IMAGE ?=$(WORKTREE_SLUG)
TAG ?=dev
IMAGE_REF := $(IMAGE):$(TAG)
COMPOSE ?=COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) docker compose
CONTAINER_PORT ?={{HTTP_PORT}}
HOST_PORT ?={{HTTP_PORT}}
DEV_COMPOSE_FILE ?=compose.dev.yaml
DEV_SERVICE ?=app-dev
DOCKER_VARIANT ?=alpine
DOCKER_PLATFORM ?=linux/arm64
GOPROXY ?=https://proxy.golang.org,direct
GOSUMDB ?=sum.golang.org
GOCACHE ?= $(CURDIR)/.cache/go-build
GOLANGCI_LINT_CACHE ?= $(CURDIR)/.cache/golangci-lint
export COMPOSE_PROJECT_NAME
export IMAGE
export TAG
export HOST_PORT
export CONTAINER_PORT
export GOCACHE
export GOLANGCI_LINT_CACHE

ifeq ($(DOCKER_VARIANT),ubuntu)
BUILDER_IMAGE ?= public.ecr.aws/docker/library/golang:1.26
RUNTIME_IMAGE ?= public.ecr.aws/docker/library/ubuntu:26.04
else
BUILDER_IMAGE ?= golang:1.26-alpine
RUNTIME_IMAGE ?= alpine:3.20
endif

.PHONY: worktree-info worktree-doctor clean-worktree bootstrap doctor dev dev-shell tidy lint test verify run build docker-build docker-run docker-push

worktree-info:
	@printf '%s\n' "Worktree root: $(WORKTREE_ROOT)"
	@printf '%s\n' "Worktree label: $(WORKTREE_LABEL)"
	@printf '%s\n' "Worktree ID: $(WORKTREE_ID)"
	@printf '%s\n' "Worktree slug: $(WORKTREE_SLUG)"
	@printf '%s\n' "Compose project: $(COMPOSE_PROJECT_NAME)"
	@printf '%s\n' "HTTP URL: http://127.0.0.1:$(HOST_PORT)"
	@printf '%s\n' "Image ref: $(IMAGE_REF)"
	@printf '%s\n' "Go cache: $(GOCACHE)"
	@printf '%s\n' "golangci-lint cache: $(GOLANGCI_LINT_CACHE)"

worktree-doctor:
	@$(MAKE) --no-print-directory worktree-info
	@if [ "$(HOST_PORT)" = "{{HTTP_PORT}}" ]; then printf '%s\n' "Warning: HOST_PORT uses the generated default {{HTTP_PORT}}; override it when another worktree is running."; fi

clean-worktree:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) down --remove-orphans --volumes

bootstrap:
	GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) $(COMPOSE) -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)

doctor:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) ./scripts/doctor

dev:
	GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) $(COMPOSE) -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)

dev-shell:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) bash

tidy:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go mod tidy

lint:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) golangci-lint run --disable-all --enable=errcheck --enable=govet --enable=ineffassign --enable=staticcheck --enable=unused ./...

test:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go test ./...

verify: doctor lint test

run:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm --service-ports $(DEV_SERVICE)

build:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go build -o bin/$(APP_NAME) ./cmd/server

docker-build:
	docker build --platform $(DOCKER_PLATFORM) --build-arg BUILDER_IMAGE=$(BUILDER_IMAGE) --build-arg RUNTIME_IMAGE=$(RUNTIME_IMAGE) --build-arg GOPROXY=$(GOPROXY) --build-arg GOSUMDB=$(GOSUMDB) -t $(IMAGE_REF) .

docker-run:
	docker run --rm -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_REF)

docker-push:
	docker push $(IMAGE_REF)
