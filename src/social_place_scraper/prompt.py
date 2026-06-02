from __future__ import annotations

import json

from social_place_scraper.schemas import SocialPost


SYSTEM_PROMPT = """You extract real-world place candidates from social media posts.

Return only JSON matching this schema:
{
  "overallRegion": "Tokyo, Japan",
  "placeCandidates": [
    {
      "name": "Most salient place mentioned in the content",
      "region": "Tokyo, Japan",
      "category": "restaurant",
      "mapsUrl": null,
      "socialTag": "den_tokyo",
      "webUrl": null,
      "description": "Short evidence-backed description."
    }
  ]
}

Rules:
- Prefer the most salient visit-worthy places: restaurants, cafes, bars, hotels, shops, museums, parks, attractions, neighborhoods, event venues.
- Infer overallRegion from caption, language, hashtags, social tags, and explicit location labels.
- Include a candidate only when the post provides evidence for a real place.
- Keep mapsUrl null. The caller will fill it.
- Use socialTag for platform handles or tags associated with the place, without @.
- Use webUrl only for explicit official websites found in the content.
- If no place is supported, return {"overallRegion": null, "placeCandidates": []}.
"""


def build_user_prompt(post: SocialPost) -> str:
    evidence = {
        "platform": post.platform.value,
        "canonicalUrl": post.canonical_url,
        "postId": post.post_id,
        "author": post.author,
        "title": post.title,
        "caption": post.caption,
        "locationTag": post.location_tag,
        "media": [item.model_dump(exclude_none=True) for item in post.media],
        "rawMetadata": post.raw_metadata,
    }
    return "Extract place candidates from this normalized social post evidence:\n" + json.dumps(
        evidence,
        ensure_ascii=False,
        indent=2,
    )
