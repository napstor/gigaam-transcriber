#!/bin/bash
set -e

IMAGE="ghcr.io/napstor/gigaam-transcriber:latest"

echo "→ Логин в ghcr.io..."
echo "$GITHUB_PAT" | docker login ghcr.io -u napstor --password-stdin

echo "→ Сборка образа (linux/amd64, ~15-20 мин)..."
docker buildx build \
  --platform linux/amd64 \
  --tag "$IMAGE" \
  --push \
  .

echo "✓ Образ запушен: $IMAGE"
