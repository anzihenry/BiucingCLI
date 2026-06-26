APP_NAME={{WORKER_NAME}}
IMAGE ?=$(APP_NAME)
TAG ?=latest
IMAGE_REF := $(IMAGE):$(TAG)
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
export GOCACHE

.PHONY: bootstrap doctor dev dev-shell test verify run build docker-build docker-run

bootstrap:
	GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) docker compose -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)

doctor:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) ./scripts/doctor

dev:
	WORKER_RUN_MODE=$(WORKER_RUN_MODE) WORKER_TICK_INTERVAL_SECONDS=$(WORKER_TICK_INTERVAL_SECONDS) WORKER_SHUTDOWN_TIMEOUT_SECONDS=$(WORKER_SHUTDOWN_TIMEOUT_SECONDS) GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) docker compose -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)

dev-shell:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) sh

test:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go test ./...

verify: doctor test

run:
	WORKER_RUN_MODE=$(WORKER_RUN_MODE) WORKER_TICK_INTERVAL_SECONDS=$(WORKER_TICK_INTERVAL_SECONDS) WORKER_SHUTDOWN_TIMEOUT_SECONDS=$(WORKER_SHUTDOWN_TIMEOUT_SECONDS) docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE)

build:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go build -o bin/$(APP_NAME) ./cmd/worker

docker-build:
	docker build --build-arg BUILDER_IMAGE=$(BUILDER_IMAGE) --build-arg RUNTIME_IMAGE=$(RUNTIME_IMAGE) --build-arg GOPROXY=$(GOPROXY) --build-arg GOSUMDB=$(GOSUMDB) -t $(IMAGE_REF) .

docker-run:
	docker run --rm -e WORKER_RUN_MODE=$(WORKER_RUN_MODE) -e WORKER_TICK_INTERVAL_SECONDS=$(WORKER_TICK_INTERVAL_SECONDS) -e WORKER_SHUTDOWN_TIMEOUT_SECONDS=$(WORKER_SHUTDOWN_TIMEOUT_SECONDS) $(IMAGE_REF)
