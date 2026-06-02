# Hermes Skill: Social Place Extractor

## Intent

When the user sends an Instagram or TikTok post URL, fetch the post content, infer place candidates, and return Google Maps candidate URLs.

## Tool Call

```sh
uv run social-post-ingest "$POST_URL" --session "$SESSION_NAME" --json
```

Choose `SESSION_NAME` by platform/account:

- `ig-personal-1`
- `ig-personal-2`
- `tiktok-main`

## Response Contract

Return the JSON object from the tool without inventing places that are not present in the tool output.

If no high-confidence places are found, say that no place candidates were found and include the most relevant content evidence.

## Human-In-The-Loop Protocol

If the command exits with code `2`, parse the JSON as:

```json
{
  "status": "needsHumanIntervention",
  "intervention": {
    "kind": "login",
    "sessionName": "ig-personal-1",
    "profileDir": ".sessions/ig-personal-1/browser-profile",
    "screenshotPath": ".sessions/ig-personal-1/last-challenge.png"
  }
}
```

Then:

1. Tell the user which session needs attention.
2. Include the screenshot path if present.
3. Ask the user to complete the challenge through VNC or local browser access.
4. Wait for the user to say it is complete.
5. Retry the original command with the same `--session`.

For email login codes:

1. If mailbox tools are available, wait for the expected code email.
2. Ask the user before entering or using the code.
3. Retry the post extraction after the session is authenticated.

## Notes

- Do not auto-save to Google Maps in V1.
- Do not bypass login challenges or CAPTCHAs.
- If a session requires login, tell the user to open the browser profile and complete login manually.
