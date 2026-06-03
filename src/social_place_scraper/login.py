from __future__ import annotations

import json
import sys
from typing import Any

from social_place_scraper.sessions import ManagedSession

DEFAULT_LOGIN_URL = "https://www.instagram.com/accounts/login/"
DEFAULT_WAIT_SECONDS = 300


class LoginSessionNotReady(RuntimeError):
    pass


def prepare_browser_login(
    *,
    session: ManagedSession,
    url: str | None = None,
    wait_seconds: int = DEFAULT_WAIT_SECONDS,
) -> None:
    try:
        from cloakbrowser import launch_persistent_context
    except ImportError as exc:
        raise RuntimeError(
            "Login preparation requires browser dependencies. Run `uv sync --extra browser`."
        ) from exc

    context = launch_persistent_context(user_data_dir=str(session.profile_dir))
    screenshot_path = session.root / "last-login.png"
    try:
        page = context.new_page()
        page.goto(url or DEFAULT_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        print(
            "Complete Instagram login or verification in the opened browser window. "
            f"Waiting up to {wait_seconds} seconds...",
            file=sys.stderr,
        )
        session_ready = _wait_for_session_cookie(context, page, wait_seconds)
        page.screenshot(path=str(screenshot_path), full_page=True)
        if not session_ready:
            raise LoginSessionNotReady(
                "Instagram login was not completed before the timeout. "
                "The existing cookie jar was left unchanged."
            )
        _save_browser_cookies(context, session)
    finally:
        context.close()


def _wait_for_session_cookie(context: Any, page: Any, wait_seconds: int) -> bool:
    remaining = max(wait_seconds, 0)
    while remaining > 0:
        if _has_instagram_session_cookie(context) and not _page_looks_like_challenge(page):
            return True
        step = min(2, remaining)
        page.wait_for_timeout(step * 1000)
        remaining -= step
    return _has_instagram_session_cookie(context) and not _page_looks_like_challenge(page)


def _has_instagram_session_cookie(context: Any) -> bool:
    return any(
        cookie.get("name") == "sessionid"
        and cookie.get("value")
        and "instagram.com" in (cookie.get("domain") or "")
        for cookie in context.cookies()
    )


def _page_looks_like_challenge(page: Any) -> bool:
    url = (getattr(page, "url", "") or "").lower()
    return any(marker in url for marker in ("/accounts/login", "/challenge", "/checkpoint"))


def _save_browser_cookies(context: Any, session: ManagedSession) -> None:
    cookies = context.cookies()
    payload = [
        {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie.get("domain"),
            "path": cookie.get("path", "/"),
        }
        for cookie in cookies
        if cookie.get("name") and cookie.get("value")
    ]
    session.cookie_file.parent.mkdir(parents=True, exist_ok=True)
    session.cookie_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
