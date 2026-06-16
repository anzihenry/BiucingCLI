APP_NAME={{PACKAGE_NAME}}
IMAGE ?=$(APP_NAME)
TAG ?=latest
IMAGE_REF := $(IMAGE):$(TAG)
DEV_COMPOSE_FILE ?=compose.dev.yaml
DEV_SERVICE ?=frontend-dev
DEV_PORT ?=5173
HOST_PORT ?=8080
CONTAINER_PORT ?=80

.PHONY: install dev dev-shell lint typecheck test build preview browser-install browser-smoke format format-check docker-build docker-run

install:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm install

dev:
	docker compose -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)

dev-shell:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) bash

lint:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm lint

typecheck:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm typecheck

test:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm test

build:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm build

preview:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm --service-ports $(DEV_SERVICE) pnpm preview --host 0.0.0.0 --port $(DEV_PORT)

browser-install:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) bash -lc "pnpm install && pnpm browser:install"

browser-smoke:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) bash -lc "pnpm install && pnpm browser:smoke"

format:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm format

format-check:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm format:check

docker-build:
	docker build -t $(IMAGE_REF) .

docker-run:
	docker run --rm -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_REF)
