#!/bin/bash

# Initialize script for {{project_name}}

set -e

echo "Installing dependencies..."
go mod download
go mod tidy

echo "Running migrations..."
# migrate -path migrations -database "mysql://user:pass@tcp(host:port)/dbname?parseTime=true" up

echo "Building application..."
go build -o bin/{{project_name}} main.go

echo "Done! Run './bin/{{project_name}}' to start the server."
