#!/bin/bash

docker-compose run --rm hotnow-token-platform mypy ./token_platform/wallet/ --ignore-missing-imports