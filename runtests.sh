#!/bin/bash

docker-compose run --rm hotnow-token-platform pytest -v --cov-report html --cov-report term-missing  --cov=.
