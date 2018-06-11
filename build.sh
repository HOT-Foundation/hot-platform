#!/bin/bash
set -eux
export TAG=$(git describe --always --tags --dirty)
export REGISTRY="registry-hotnow.proteus-tech.com/hotnow-htkn-platform"
docker-compose build --pull --no-cache hotnow-htkn-platform
docker-compose push hotnow-htkn-platform
