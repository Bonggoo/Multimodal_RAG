#!/bin/bash
# Script to run the Docker container with compose

if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose could not be found. Trying 'docker compose'..."
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo "Starting services with Docker Compose..."
$DOCKER_COMPOSE_CMD up -d --build

echo "Services are starting..."
echo "API Docs: http://localhost:8000/docs"
echo "Logs: $DOCKER_COMPOSE_CMD logs -f"
