#!/usr/bin/env sh
set -eu

./scripts/ensure-uv.sh
uv run ruff check src tests
