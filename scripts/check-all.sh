#!/usr/bin/env sh
set -eu

./scripts/ensure-uv.sh
./scripts/lint.sh
uv run ruff format --check src tests
./scripts/typecheck.sh
./scripts/test.sh
