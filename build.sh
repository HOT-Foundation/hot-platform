#!/bin/bash
set -eux
export TAG=$(git describe --always --tags)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" == "develop" ]]; then
  export TAG="latest"
fi

export REGISTRY="registry-hotnow.proteus-tech.com/hotnow-htkn-platform"
docker-compose build --pull --no-cache hotnow-htkn-platform

if [[ "$BRANCH" == "develop" ]] || [[ "$BRANCH" == "master" ]]; then
    docker-compose push hotnow-htkn-platform
fi
