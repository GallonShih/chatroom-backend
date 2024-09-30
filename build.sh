#!/bin/bash

# Define image name and tag
IMAGE_NAME="chatroom-backend"
IMAGE_TAG="test"

# Full image name
FULL_IMAGE_NAME="$IMAGE_NAME:$IMAGE_TAG"

# Check if the image already exists
if docker image inspect "$FULL_IMAGE_NAME" > /dev/null 2>&1; then
    echo "Image $FULL_IMAGE_NAME already exists. Removing..."
    docker rmi "$FULL_IMAGE_NAME"
fi

# Build the new Docker image
echo "Building Docker image $FULL_IMAGE_NAME..."
docker build -t "$FULL_IMAGE_NAME" .

echo "Docker image $FULL_IMAGE_NAME built successfully."
