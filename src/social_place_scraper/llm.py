from __future__ import annotations

import json

from openai import OpenAI

from social_place_scraper.config import LlmConfig
from social_place_scraper.prompt import SYSTEM_PROMPT, build_user_prompt
from social_place_scraper.schemas import PlaceExtraction, SocialPost


class LlmExtractor:
    def __init__(self, config: LlmConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def extract(self, post: SocialPost) -> PlaceExtraction:
        response = self.client.chat.completions.create(
            model=self.config.model,
            temperature=self.config.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(post)},
            ],
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        return PlaceExtraction.model_validate(data)
