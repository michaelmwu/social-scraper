from social_place_scraper.login import _wait_for_session_cookie


def test_wait_for_session_cookie_does_not_return_while_on_challenge_url() -> None:
    context = _FakeContext()
    page = _FakePage(
        urls=[
            "https://www.instagram.com/challenge/",
            "https://www.instagram.com/",
        ]
    )

    ready = _wait_for_session_cookie(context, page, wait_seconds=4)

    assert ready is True
    assert page.waits == 1


def test_wait_for_session_cookie_returns_immediately_when_session_is_ready() -> None:
    context = _FakeContext()
    page = _FakePage(urls=["https://www.instagram.com/"])

    ready = _wait_for_session_cookie(context, page, wait_seconds=4)

    assert ready is True
    assert page.waits == 0


def test_wait_for_session_cookie_reports_failure_after_timeout_on_challenge_url() -> None:
    context = _FakeContext()
    page = _FakePage(urls=["https://www.instagram.com/checkpoint/"])

    ready = _wait_for_session_cookie(context, page, wait_seconds=2)

    assert ready is False
    assert page.waits == 1


class _FakeContext:
    def cookies(self) -> list[dict[str, str]]:
        return [
            {
                "name": "sessionid",
                "value": "abc",
                "domain": ".instagram.com",
            }
        ]


class _FakePage:
    def __init__(self, *, urls: list[str]) -> None:
        self.urls = urls
        self.waits = 0

    @property
    def url(self) -> str:
        index = min(self.waits, len(self.urls) - 1)
        return self.urls[index]

    def wait_for_timeout(self, timeout_ms: int) -> None:
        assert timeout_ms == 2000
        self.waits += 1
