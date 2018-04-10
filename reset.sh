#!/bin/bash

set -eux

docker network create hotnow-network || echo "hotnow-network already is created"
docker-compose build --no-cache
docker-compose down
docker-compose up -d
