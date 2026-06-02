from __future__ import annotations

from social_place_scraper.challenges import maybe_raise_intervention
from social_place_scraper.fetchers.base import Fetcher
from social_place_scraper.fetchers.html_metadata import parse_metadata
from social_place_scraper.platforms import detect_platform, extract_post_id
from social_place_scraper.schemas import MediaItem, SocialPost
from social_place_scraper.sessions import ManagedSession


class BotasaurusFetcher(Fetcher):
    def fetch(self, url: str, session: ManagedSession) -> SocialPost:
        try:
            from botasaurus.browser import Driver, browser
        except ImportError as exc:
            raise RuntimeError(
                "Install browser dependencies with `uv sync --extra browser`."
            ) from exc

        def get_profile(data: dict[str, str]) -> str:
            return data["profile"]

        @browser(profile=get_profile)
        def scrape_post(driver: Driver, data: dict[str, str]) -> dict[str, str | None]:
            driver.get(data["url"])
            html = driver.page_html
            title = driver.title
            return {
                "url": driver.current_url,
                "title": title,
                "html": html,
            }

        result = scrape_post({"url": url, "profile": session.name})
        html = result.get("html") or ""
        page_title, meta = parse_metadata(html)
        canonical_url = result.get("url") or url
        maybe_raise_intervention(
            url=canonical_url,
            session=session,
            title=page_title or result.get("title"),
            html=html,
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
            title=meta.get("og:title") or page_title or result.get("title"),
            caption=(
                meta.get("og:description")
                or meta.get("description")
                or meta.get("twitter:description")
            ),
            media=media,
            source_confidence="botasaurus",
            raw_metadata=meta,
        )
