from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from curl_cffi import requests

from social_place_scraper.challenges import maybe_raise_intervention
from social_place_scraper.fetchers.base import Fetcher
from social_place_scraper.fetchers.html_metadata import parse_metadata
from social_place_scraper.platforms import detect_platform, extract_post_id
from social_place_scraper.schemas import MediaItem, SocialPost
from social_place_scraper.sessions import ManagedSession


class HttpMetadataFetcher(Fetcher):
    def __init__(self, *, client_factory: Callable[[], Any] | None = None):
        self._client_factory = client_factory or (lambda: requests.Session(impersonate="chrome"))

    def fetch(self, url: str, session: ManagedSession) -> SocialPost:
        client = self._client_factory()
        self._load_cookies(client, session.cookie_file)
        response = client.get(
            url,
            timeout=30,
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
            },
        )
        self._save_cookies(client, session.cookie_file)

        page_title, meta = parse_metadata(response.text)
        canonical_url = str(response.url)
        maybe_raise_intervention(
            url=canonical_url,
            session=session,
            title=page_title,
            html=response.text,
        )
        response.raise_for_status()
        platform = detect_platform(canonical_url)
        post_id = extract_post_id(canonical_url, platform)

        image_url = meta.get("og:image") or meta.get("twitter:image")
        video_url = meta.get("og:video") or meta.get("twitter:player:stream")
        media = []
        if image_url:
            media.append(MediaItem(type="image", url=image_url, position=0))
        if video_url:
            media.append(
                MediaItem(type="video", url=video_url, thumbnail_url=image_url, position=0)
            )

        return SocialPost(
            platform=platform,
            canonical_url=canonical_url,
            post_id=post_id,
            title=meta.get("og:title") or page_title,
            caption=(
                meta.get("og:description")
                or meta.get("description")
                or meta.get("twitter:description")
            ),
            media=media,
            source_confidence="http_metadata",
            raw_metadata=meta,
        )

    def _load_cookies(self, client: requests.Session, cookie_file: Path) -> None:
        if not cookie_file.exists():
            return
        data = json.loads(cookie_file.read_text())
        for cookie in data:
            client.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain"),
                path=cookie.get("path", "/"),
            )

    def _save_cookies(self, client: requests.Session, cookie_file: Path) -> None:
        cookie_file.parent.mkdir(parents=True, exist_ok=True)
        payload = []
        for cookie in client.cookies.jar:
            payload.append(
                {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                }
            )
        cookie_file.write_text(json.dumps(payload, indent=2) + "\n")
