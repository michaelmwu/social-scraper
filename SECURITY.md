# Security Policy

## Reporting Vulnerabilities

Do not open public issues for vulnerabilities, leaked secrets, session cookies, or account-access problems. Report security concerns through the private maintainer channel configured for this repository.

## Secret And Session Handling

- Keep API keys and provider credentials in environment variables or encrypted config.
- Never commit real `.env` files, tokens, private keys, browser profiles, cookies, screenshots, verification codes, or challenge artifacts.
- Use `.env.example` for documented configuration only.
- Treat `.sessions/` as sensitive local state.

## Human Intervention Boundary

The scraper may detect login, checkpoint, CAPTCHA, or verification-code screens and return a `needsHumanIntervention` result. Do not add CAPTCHA solving, login challenge bypass, or account recovery automation.

## Dependency Policy

This repo uses `uv` dependency cooldowns and a committed lockfile:

```toml
[tool.uv]
exclude-newer = "7 days"

[tool.uv.pip]
exclude-newer = "7 days"
```

Automation should use locked installs:

```sh
uv sync --locked
```
