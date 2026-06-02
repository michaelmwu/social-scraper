from social_place_scraper.maps import attach_maps_urls, google_maps_search_url
from social_place_scraper.schemas import PlaceCandidate, PlaceExtraction


def test_google_maps_search_url_includes_candidate_region_and_category() -> None:
    candidate = PlaceCandidate(
        name="Den",
        region="Tokyo, Japan",
        category="restaurant",
    )

    url = google_maps_search_url(candidate, overall_region="Japan")

    assert url == ("https://www.google.com/maps/search/?api=1&query=Den+Tokyo%2C+Japan+restaurant")


def test_attach_maps_urls_preserves_existing_url() -> None:
    extraction = PlaceExtraction(
        overallRegion="Seoul, South Korea",
        placeCandidates=[
            PlaceCandidate(
                name="Existing",
                mapsUrl="https://example.com/maps",
            )
        ],
    )

    updated = attach_maps_urls(extraction)

    assert updated.placeCandidates[0].mapsUrl == "https://example.com/maps"


def test_attach_maps_urls_uses_overall_region_when_candidate_region_is_missing() -> None:
    extraction = PlaceExtraction(
        overallRegion="Gwangju, South Korea",
        placeCandidates=[PlaceCandidate(name="Penguin Village")],
    )

    updated = attach_maps_urls(extraction)

    assert updated.placeCandidates[0].mapsUrl == (
        "https://www.google.com/maps/search/?api=1&query=Penguin+Village+Gwangju%2C+South+Korea"
    )
