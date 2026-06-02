# Social Place Scraper

Clean-room prototype for a Hermes skill that turns an Instagram or TikTok post URL into location candidates and Google Maps search URLs.

## V1 Scope

- Fetch social post metadata with reusable session state.
- Normalize caption/title/location/media-ish metadata into one shape.
- Ask an OpenAI-compatible LLM for structured place candidates.
- Add Google Maps candidate URLs.
- Skip Google saved-list automation for now.

## Install

Use a locked install once a lockfile exists:

```sh
uv sync --locked
```

For first-time local setup:

```sh
uv sync
```

Browser adapters are optional:

```sh
uv sync --extra browser
```

## Development

Stable check entrypoints live in `scripts/`:

```sh
./scripts/lint.sh
./scripts/typecheck.sh
./scripts/test.sh
```

Run the full local gate before handoff or PR work:

```sh
./scripts/check-all.sh
```

Configuration starts from `.env.example`; local `.env` and `.sessions/` state are ignored.

## Configuration

Create `.env` locally:

```sh
SOCIAL_PLACE_LLM_BASE_URL=https://api.openai.com/v1
SOCIAL_PLACE_LLM_API_KEY=...
SOCIAL_PLACE_LLM_MODEL=gpt-4.1-mini
SOCIAL_PLACE_SESSION_NAME=default
SOCIAL_PLACE_SESSION_ROOT=.sessions
```

For local Bifrost or another OpenAI-compatible gateway, point `SOCIAL_PLACE_LLM_BASE_URL` and `SOCIAL_PLACE_LLM_API_KEY` at that service.

## Usage

```sh
uv run social-post-ingest "https://www.instagram.com/p/..."
```

Useful flags:

```sh
uv run social-post-ingest "https://www.tiktok.com/@user/video/123" \
  --session ig-personal-1 \
  --provider openai-compatible \
  --model gpt-4.1-mini \
  --fetcher auto
```

The output schema is:

```json
{
  "overallRegion": "Tokyo, Japan",
  "placeCandidates": [
    {
      "name": "Most salient place mentioned in the content",
      "region": "Tokyo, Japan",
      "category": "restaurant",
      "mapsUrl": "https://www.google.com/maps/search/?api=1&query=...",
      "socialTag": "den_tokyo",
      "webUrl": null,
      "description": "Two-Michelin-star kaiseki restaurant known for chef Hasegawa's playful monaka wagyu sliders."
    }
  ]
}
```

## Session Model

Each named session gets:

- a persistent browser profile directory
- a cookie jar for HTTP fetches
- a small metadata file

This lets each account accumulate normal browser state over time. Use one session name per social account, for example `ig-personal-1`, `ig-personal-2`, or `tiktok-main`.

## Human-In-The-Loop Challenges

If a login, checkpoint, CAPTCHA, or verification-code screen is detected, the CLI exits with code `2` and returns:

```json
{
  "status": "needsHumanIntervention",
  "intervention": {
    "kind": "verification_code",
    "platform": "instagram",
    "sessionName": "ig-personal-1",
    "message": "The social session appears to require human action...",
    "url": "https://www.instagram.com/...",
    "profileDir": ".sessions/ig-personal-1/browser-profile",
    "screenshotPath": ".sessions/ig-personal-1/last-challenge.png",
    "codeChannel": "email"
  }
}
```

Hermes should send that object back to you, wait for you to complete the challenge, then retry the same URL with the same `sessionName`.

Supported human loops:

- VNC/screen-share into the Mac, open the persistent profile, complete the challenge, retry.
- Messenger loop: Hermes sends the screenshot/message and waits for you to respond when complete.
- Email/SMS code loop: Hermes can tell you which channel appears to be requested; if Hermes has mailbox access, it can wait for the code and ask you before submitting it.

Do not build CAPTCHA solving, challenge bypass, or account recovery automation into the scraper. The tool should pause and route those states to you.

## Hermes Skill Pattern

The Hermes skill should call:

```sh
uv run social-post-ingest "$POST_URL" --session "$SESSION_NAME" --json
```

Then return the `placeCandidates` to you. Keep the skill thin; keep scraping, LLM extraction, and Maps URL generation in this package.
