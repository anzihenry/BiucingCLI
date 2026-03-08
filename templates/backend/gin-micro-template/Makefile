# Makefile for {{project_name}}

.PHONY: build run test clean lint fmt deps docs

# Build the application
build:
	go build -o bin/{{project_name}} main.go

# Run the application
run:
	go run main.go

# Run tests
test:
	go test -v ./...

# Run tests with coverage
test-coverage:
	go test -cover -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html

# Clean build artifacts
clean:
	rm -rf bin/
	rm -f coverage.out coverage.html

# Lint the code
lint:
	golangci-lint run

# Format the code
fmt:
	go fmt ./...

# Install dependencies
deps:
	go mod download
	go mod tidy

# Generate API documentation
docs:
	swag init -g main.go -o ./docs

# Build and run
dev: deps fmt build run
