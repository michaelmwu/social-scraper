# AI Agent Development Guide

## Environment

- Only `python3` is guaranteed. Do not assume `python` exists.
- Prefer `uv run` and scripts in `scripts/` over raw commands.
- Treat install, dev, and test commands as executable code. Inspect manifests, lockfiles, Docker files, and setup scripts before running them in unfamiliar repos.

## Dependency Supply-Chain Safety

- Keep `uv.lock` committed.
- Keep `exclude-newer = "7 days"` in `pyproject.toml`.
- Use locked installs in CI and automation: `uv sync --locked`.

## Repository Shape

- `src/social_place_scraper/`: scraper package, CLI, fetchers, schemas, LLM extraction, and Maps URL helpers.
- `docs/`: Hermes skill and contributor-facing usage notes.
- `scripts/`: stable human/agent entrypoints for checks.
- `.context/`: operational memory for humans and agents; do not store secrets or raw logs there.

## Development Workflow

- Use `./scripts/lint.sh`, `./scripts/typecheck.sh`, and `./scripts/test.sh` while iterating.
- Use `./scripts/check-all.sh` before handing off broad changes.
- Add or update tests when behavior changes.
- Update `.env.example` when adding configuration.
- Keep browser adapters optional; do not require browser dependencies for the default CLI path.
- Do not automate CAPTCHA solving, login challenge bypass, or account recovery.

## Validation

Run the narrowest relevant check before calling work complete:

```sh
./scripts/lint.sh
./scripts/typecheck.sh
./scripts/test.sh
```

For broader changes:

```sh
./scripts/check-all.sh
```
