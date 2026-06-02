import json
from pathlib import Path

from social_place_scraper.cli import main


def test_main_can_print_normalized_post_without_fetching_or_llm(
    tmp_path: Path,
    capsys,
) -> None:
    post_path = tmp_path / "post.json"
    post_path.write_text(
        json.dumps(
            {
                "platform": "instagram",
                "canonical_url": "https://www.instagram.com/p/abc123/",
                "caption": "Dinner at Den in Tokyo.",
                "source_confidence": "manual",
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "https://www.instagram.com/p/abc123/",
            "--post-json",
            str(post_path),
            "--no-llm",
            "--json",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["platform"] == "instagram"
    assert output["canonical_url"] == "https://www.instagram.com/p/abc123/"
    assert output["caption"] == "Dinner at Den in Tokyo."
