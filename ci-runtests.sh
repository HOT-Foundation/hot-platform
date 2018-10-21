#!/bin/bash
set -eux

COMPOSE='ci-compose.yml'
export TAG=$(git describe --always --tags)

docker-compose -f $COMPOSE run --rm hotnow-htkn-platform mypy ./token_platform/ --ignore-missing-imports

TEST_PASSPHRASE='TESTNET'
TEST_HORIZON_URL='https://horizon-testnet.stellar.org'
docker-compose -f $COMPOSE run -e PASSPHRASE=$TEST_PASSPHRASE -e HORIZON_URL=$TEST_HORIZON_URL --rm hotnow-htkn-platform pytest -v --cov-report html --cov-report term-missing  --cov=. $*
