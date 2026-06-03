APP_NAME={{SERVICE_NAME}}

.PHONY: tidy test run build docker-build

tidy:
	go mod tidy

test:
	go test ./...

run:
	go run ./cmd/server

build:
	go build -o bin/$(APP_NAME) ./cmd/server

docker-build:
	docker build -t $(APP_NAME) .
