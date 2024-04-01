#!/usr/bin/env bash

if ! which pytest &>/dev/null || ! which coverage &>/dev/null; then
    pip install --upgrade pip
    pip install -r ./requirements-dev.txt
fi

if [ "$1" = "-c" ]; then
    shift
    coverage run -m pytest tests/ "$@" && coverage report -m
    rm .coverage
else
    pytest tests/ "$@"
fi
