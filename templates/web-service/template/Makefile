APP_NAME={{SERVICE_NAME}}
IMAGE ?=$(APP_NAME)
TAG ?=latest
IMAGE_REF := $(IMAGE):$(TAG)
CONTAINER_PORT ?={{HTTP_PORT}}
HOST_PORT ?={{HTTP_PORT}}
DOCKER_VARIANT ?=alpine
DOCKER_PLATFORM ?=linux/arm64
GOCACHE ?= $(CURDIR)/.cache/go-build
GOLANGCI_LINT_CACHE ?= $(CURDIR)/.cache/golangci-lint
export GOCACHE
export GOLANGCI_LINT_CACHE

ifeq ($(DOCKER_VARIANT),ubuntu)
BUILDER_IMAGE ?= public.ecr.aws/docker/library/golang:1.26
RUNTIME_IMAGE ?= public.ecr.aws/docker/library/ubuntu:26.04
else
BUILDER_IMAGE ?= golang:1.26-alpine
RUNTIME_IMAGE ?= alpine:3.20
endif

.PHONY: bootstrap doctor tidy lint test verify run build docker-build docker-run docker-push

bootstrap:
	./scripts/bootstrap

doctor:
	./scripts/doctor

tidy:
	@mkdir -p "$(GOCACHE)"
	go mod tidy

lint:
	@if ! command -v golangci-lint >/dev/null 2>&1; then \
		echo "golangci-lint is not installed. Run ./scripts/bootstrap or install it via Brewfile."; \
		exit 1; \
	fi
	@mkdir -p "$(GOCACHE)"
	@mkdir -p "$(GOLANGCI_LINT_CACHE)"
	golangci-lint run --disable-all --enable=errcheck --enable=govet --enable=ineffassign --enable=staticcheck --enable=unused ./...

test:
	@mkdir -p "$(GOCACHE)"
	go test ./...

verify: doctor lint test

run:
	@mkdir -p "$(GOCACHE)"
	go run ./cmd/server

build:
	@mkdir -p "$(GOCACHE)"
	go build -o bin/$(APP_NAME) ./cmd/server

docker-build:
	docker build --platform $(DOCKER_PLATFORM) --build-arg BUILDER_IMAGE=$(BUILDER_IMAGE) --build-arg RUNTIME_IMAGE=$(RUNTIME_IMAGE) -t $(IMAGE_REF) .

docker-run:
	docker run --rm -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_REF)

docker-push:
	docker push $(IMAGE_REF)
