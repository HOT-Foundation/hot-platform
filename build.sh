#!/bin/bash
set -eux

OPT=$1
BRANCH=${2:=default}
COMPOSE=${3:=docker-compose.yml}

export TAG=$(git describe --always --tags)

if [[ "$BRANCH" == "default" ]]; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
fi

if [[ "$BRANCH" == "develop" ]]; then
    export TAG="latest"
fi

export REGISTRY="registry-hotnow.proteus-tech.com/hotnow-htkn-platform"
if [[ "$OPT" == "build" ]]; then
    docker-compose build --pull --no-cache hotnow-htkn-platform
fi

if [[ "$OPT" == "push" ]]; then
    docker-compose push hotnow-htkn-platform
fi

if [[ "$OPT" == "remove" ]]; then
    docker-compose -f $COMPOSE down --rmi all
fi

if [[ "$OPT" == "down" ]]; then
    docker-compose -f $COMPOSE down
fi