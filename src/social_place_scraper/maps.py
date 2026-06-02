from __future__ import annotations

from urllib.parse import urlencode

from social_place_scraper.schemas import PlaceCandidate, PlaceExtraction


def google_maps_search_url(candidate: PlaceCandidate, overall_region: str | None) -> str:
    query_parts = [candidate.name]
    region = candidate.region or overall_region
    if region:
        query_parts.append(region)
    if candidate.category:
        query_parts.append(candidate.category)
    query = " ".join(part for part in query_parts if part)
    return "https://www.google.com/maps/search/?" + urlencode({"api": "1", "query": query})


def attach_maps_urls(extraction: PlaceExtraction) -> PlaceExtraction:
    candidates = []
    for candidate in extraction.placeCandidates:
        if candidate.mapsUrl:
            candidates.append(candidate)
            continue
        candidates.append(
            candidate.model_copy(
                update={
                    "mapsUrl": google_maps_search_url(candidate, extraction.overallRegion),
                }
            )
        )
    return extraction.model_copy(update={"placeCandidates": candidates})
