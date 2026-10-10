#!/usr/bin/env bash
set -euo pipefail

IMAGE="zoiaflorian/summarizer"
TAG="${1:-latest}"

docker buildx build \
  --platform linux/amd64 \
  -t "${IMAGE}:${TAG}" \
  --push \
  .

echo "Gepusht: ${IMAGE}:${TAG}"
