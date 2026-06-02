from __future__ import annotations

from abc import ABC, abstractmethod

from social_place_scraper.schemas import SocialPost
from social_place_scraper.sessions import ManagedSession


class Fetcher(ABC):
    @abstractmethod
    def fetch(self, url: str, session: ManagedSession) -> SocialPost:
        raise NotImplementedError
