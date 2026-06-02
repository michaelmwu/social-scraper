from __future__ import annotations

from html.parser import HTMLParser


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: str | None = None
        self._in_title = False
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value for key, value in attrs if value is not None}
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() != "meta":
            return

        key = attr_map.get("property") or attr_map.get("name")
        content = attr_map.get("content")
        if key and content:
            self.meta[key] = content

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            text = data.strip()
            if text:
                self.title = text


def parse_metadata(html: str) -> tuple[str | None, dict[str, str]]:
    parser = MetadataParser()
    parser.feed(html)
    return parser.title, parser.meta
