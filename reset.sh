#!/bin/bash

set -eux

docker-compose build --no-cache
docker-compose down
docker-compose up -d
