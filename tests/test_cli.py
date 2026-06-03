import json
from pathlib import Path

import social_place_scraper.cli as cli
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


def test_login_only_prepares_session_and_exits(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    prepared = []

    def fake_prepare_browser_login(**kwargs) -> None:
        prepared.append(kwargs)

    monkeypatch.setattr(cli, "prepare_browser_login", fake_prepare_browser_login)

    exit_code = main(
        [
            "https://www.instagram.com/",
            "--session-root",
            str(tmp_path),
            "--session",
            "ig personal",
            "--login-only",
            "--json",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "loginSessionPrepared"
    assert output["sessionName"] == "ig_personal"
    assert prepared[0]["url"] == "https://www.instagram.com/"
