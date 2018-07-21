#!/bin/bash
set -eux

./runlint.sh
TEST_PASSPHRASE='TESTNET'
TEST_HORIZON_URL='https://horizon-testnet.stellar.org'
docker-compose run -e PASSPHRASE=$TEST_PASSPHRASE -e HORIZON_URL=$TEST_HORIZON_URL --rm hotnow-htkn-platform pytest -v --cov-report html --cov-report term-missing  --cov=. $*
