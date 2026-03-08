# {{project_name}}

A Go microservice built with Gin, Go Micro, GORM, and go-redis.

## Tech Stack

- **Gin**: High-performance HTTP web framework
- **Go Micro**: Microservice framework with service discovery
- **GORM**: ORM library for Go
- **go-redis**: Redis client library
- **Viper**: Configuration management
- **JWT-Go**: JWT authentication
- **Zap**: High-performance logging
- **Swaggo**: API documentation generator

## Project Structure

```
{{project_name}}/
├── cmd/                    # Application entry points
│   ├── api/               # API service
│   └── worker/            # Background worker
├── internal/              # Private application code
│   ├── handlers/          # HTTP handlers
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   ├── repositories/      # Data access layer
│   ├── middleware/        # HTTP middleware
│   ├── config/            # Configuration
│   └── utils/             # Utility functions
├── pkg/                   # Public library code
├── migrations/            # Database migrations
├── configs/               # Configuration files
├── scripts/               # Utility scripts
├── tests/                 # Test files
└── docs/                  # API documentation
```

## Getting Started

### Prerequisites

- Go 1.21+
- MySQL (or your preferred database)
- Redis

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {{project_name}}

# Install dependencies
go mod download

# Run the application
go run main.go
```

### Configuration

Edit `configs/config.yaml` to configure the application.

### Running Tests

```bash
go test ./...
```

### Building

```bash
go build -o bin/{{project_name}} main.go
```

## API Documentation

After running the application, access Swagger UI at:
http://localhost:8080/swagger/index.html

## License

MIT
