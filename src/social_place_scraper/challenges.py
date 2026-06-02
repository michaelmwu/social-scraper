from __future__ import annotations

from pathlib import Path

from social_place_scraper.platforms import detect_platform
from social_place_scraper.schemas import HumanIntervention, Platform
from social_place_scraper.sessions import ManagedSession


class HumanInterventionRequired(RuntimeError):
    def __init__(self, intervention: HumanIntervention):
        super().__init__(intervention.message)
        self.intervention = intervention


LOGIN_MARKERS = [
    "log in",
    "login",
    "sign in",
    "sign up",
    "checkpoint",
    "security check",
    "verify it's you",
    "verification code",
    "enter the code",
    "captcha",
]


def maybe_raise_intervention(
    *,
    url: str,
    session: ManagedSession,
    title: str | None,
    html: str,
    screenshot_path: Path | None = None,
) -> None:
    text = " ".join(part for part in [title, html[:8000]] if part).lower()
    matched = [marker for marker in LOGIN_MARKERS if marker in text]
    if not matched:
        return

    platform = detect_platform(url)
    marker_text = ", ".join(matched[:3])
    kind = _kind_from_markers(matched)
    channel = "unknown"
    if "email" in text:
        channel = "email"
    elif "sms" in text or "phone" in text:
        channel = "sms"

    raise HumanInterventionRequired(
        HumanIntervention(
            kind=kind,
            platform=platform,
            sessionName=session.name,
            message=(
                "The social session appears to require human action "
                f"({marker_text}). Complete it in the persistent browser profile, "
                "then retry the same command with the same session name."
            ),
            url=url,
            profileDir=str(session.profile_dir),
            screenshotPath=str(screenshot_path) if screenshot_path else None,
            codeChannel=channel if kind == "verification_code" else None,
        )
    )


def _kind_from_markers(markers: list[str]) -> str:
    joined = " ".join(markers)
    if "verification code" in joined or "enter the code" in joined:
        return "verification_code"
    if "captcha" in joined:
        return "captcha"
    if "checkpoint" in joined or "security check" in joined or "verify it's you" in joined:
        return "checkpoint"
    if "log in" in joined or "login" in joined or "sign in" in joined:
        return "login"
    return "unknown"
