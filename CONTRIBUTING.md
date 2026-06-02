# Contributing

This package extracts place candidates from Instagram or TikTok post evidence and returns Google Maps search URLs. Keep changes focused on that workflow.

## Local Setup

Use the locked environment when the lockfile is current:

```sh
uv sync --locked
```

For first-time dependency updates:

```sh
uv sync
```

Optional browser adapters are not required for the default HTTP metadata path:

```sh
uv sync --extra browser
```

## Local Checks

Run the narrowest relevant checks while iterating:

```sh
./scripts/lint.sh
./scripts/typecheck.sh
./scripts/test.sh
```

Before opening or updating a PR, run:

```sh
./scripts/check-all.sh
```

## Configuration

Copy `.env.example` to `.env` locally and fill in provider credentials. Never commit secrets, browser profiles, session cookies, screenshots, or raw challenge artifacts.

## Human Intervention Boundary

The scraper may detect login, checkpoint, CAPTCHA, or verification-code screens and return a `needsHumanIntervention` result. Do not add CAPTCHA solving, login challenge bypass, or account recovery automation.
