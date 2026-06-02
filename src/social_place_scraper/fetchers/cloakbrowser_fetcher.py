from __future__ import annotations

from social_place_scraper.challenges import maybe_raise_intervention
from social_place_scraper.fetchers.base import Fetcher
from social_place_scraper.fetchers.html_metadata import parse_metadata
from social_place_scraper.platforms import detect_platform, extract_post_id
from social_place_scraper.schemas import MediaItem, SocialPost
from social_place_scraper.sessions import ManagedSession


class CloakBrowserFetcher(Fetcher):
    def fetch(self, url: str, session: ManagedSession) -> SocialPost:
        try:
            from cloakbrowser import launch_persistent_context
        except ImportError as exc:
            raise RuntimeError(
                "Install browser dependencies with `uv sync --extra browser`."
            ) from exc

        context = launch_persistent_context(user_data_dir=str(session.profile_dir))
        screenshot_path = session.root / "last-challenge.png"
        try:
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html = page.content()
            canonical_url = page.url
            title = page.title()
            page.screenshot(path=str(screenshot_path), full_page=True)
        finally:
            context.close()

        page_title, meta = parse_metadata(html)
        maybe_raise_intervention(
            url=canonical_url,
            session=session,
            title=page_title or title,
            html=html,
            screenshot_path=screenshot_path,
        )
        platform = detect_platform(canonical_url)
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
            post_id=extract_post_id(canonical_url, platform),
            title=meta.get("og:title") or page_title or title,
            caption=(
                meta.get("og:description")
                or meta.get("description")
                or meta.get("twitter:description")
            ),
            media=media,
            source_confidence="cloakbrowser",
            raw_metadata=meta,
        )
