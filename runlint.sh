#!/bin/bash

docker-compose run --rm hotnow-htkn-platform mypy ./token_platform/ --ignore-missing-imports
