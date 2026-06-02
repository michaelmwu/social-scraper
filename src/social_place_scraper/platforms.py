from __future__ import annotations

import re
from urllib.parse import urlparse

from social_place_scraper.schemas import Platform

INSTAGRAM_POST_RE = re.compile(r"/(?:p|reel|tv)/([^/?#]+)/?")
TIKTOK_VIDEO_RE = re.compile(r"/video/(\d+)")


def detect_platform(url: str) -> Platform:
    host = (urlparse(url).hostname or "").lower()
    if _is_host_or_subdomain(host, "instagram.com"):
        return Platform.INSTAGRAM
    if _is_host_or_subdomain(host, "tiktok.com"):
        return Platform.TIKTOK
    return Platform.UNKNOWN


def _is_host_or_subdomain(host: str, root_domain: str) -> bool:
    return host == root_domain or host.endswith(f".{root_domain}")


def extract_post_id(url: str, platform: Platform) -> str | None:
    if platform == Platform.INSTAGRAM:
        match = INSTAGRAM_POST_RE.search(urlparse(url).path)
        return match.group(1) if match else None
    if platform == Platform.TIKTOK:
        match = TIKTOK_VIDEO_RE.search(urlparse(url).path)
        return match.group(1) if match else None
    return None
