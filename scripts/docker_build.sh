#!/bin/bash
# Script to build the Docker image

IMAGE_NAME="multimodal-rag-api"

echo "Building Docker image: $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Run './scripts/docker_run.sh' to start the container."
else
    echo "Build failed."
    exit 1
fi
