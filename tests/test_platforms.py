from social_place_scraper.platforms import detect_platform, extract_post_id
from social_place_scraper.schemas import Platform


def test_detect_platform_accepts_subdomains() -> None:
    assert detect_platform("https://www.instagram.com/p/abc123/") == Platform.INSTAGRAM
    assert detect_platform("https://m.tiktok.com/@user/video/123456") == Platform.TIKTOK


def test_detect_platform_rejects_lookalike_domains() -> None:
    assert detect_platform("https://instagram.com.example.org/p/abc123/") == Platform.UNKNOWN
    assert detect_platform("https://not-tiktok.com/@user/video/123456") == Platform.UNKNOWN


def test_extract_post_id_for_known_platforms() -> None:
    assert (
        extract_post_id("https://www.instagram.com/reel/abc123/?igsh=1", Platform.INSTAGRAM)
        == "abc123"
    )
    assert (
        extract_post_id(
            "https://www.tiktok.com/@user/video/123456?lang=en",
            Platform.TIKTOK,
        )
        == "123456"
    )


def test_extract_post_id_unknown_platform_returns_none() -> None:
    assert extract_post_id("https://example.com/posts/abc123", Platform.UNKNOWN) is None
