from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from social_place_scraper.challenges import HumanInterventionRequired
from social_place_scraper.config import load_config
from social_place_scraper.fetchers.http_metadata import HttpMetadataFetcher
from social_place_scraper.llm import LlmExtractor
from social_place_scraper.login import DEFAULT_WAIT_SECONDS, prepare_browser_login
from social_place_scraper.maps import attach_maps_urls
from social_place_scraper.schemas import InterventionResult, SocialPost
from social_place_scraper.sessions import SessionManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Google Maps place candidates from a social post URL."
    )
    parser.add_argument("url", help="Instagram or TikTok post URL.")
    parser.add_argument("--session", help="Named session/account profile to reuse.")
    parser.add_argument("--session-root", help="Directory for browser profiles and cookie jars.")
    parser.add_argument(
        "--provider",
        help="LLM provider label. OpenAI-compatible APIs are supported.",
    )
    parser.add_argument("--model", help="LLM model name, e.g. gpt-4.1-mini.")
    parser.add_argument(
        "--fetcher",
        choices=["auto", "http", "botasaurus", "cloakbrowser"],
        default="auto",
        help="Fetcher backend. auto currently tries HTTP metadata first.",
    )
    parser.add_argument(
        "--post-json",
        help="Bypass fetching and extract from a normalized SocialPost JSON file.",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Only fetch and print normalized post evidence.",
    )
    parser.add_argument("--json", action="store_true", help="Print compact JSON.")
    parser.add_argument(
        "--login",
        action="store_true",
        help="Open the persistent browser session for login before fetching.",
    )
    parser.add_argument(
        "--login-only",
        action="store_true",
        help="Prepare the persistent browser session and exit without scraping.",
    )
    parser.add_argument(
        "--interactive-challenges",
        action="store_true",
        help=(
            "When a login/checkpoint challenge is detected, open the persistent browser "
            "and retry once."
        ),
    )
    parser.add_argument(
        "--login-wait-seconds",
        type=int,
        default=DEFAULT_WAIT_SECONDS,
        help="Seconds to wait while the user completes login in the persistent browser.",
    )
    return parser


def select_fetcher(name: str):
    if name in {"auto", "http"}:
        return HttpMetadataFetcher()
    if name == "botasaurus":
        from social_place_scraper.fetchers.botasaurus_fetcher import BotasaurusFetcher

        return BotasaurusFetcher()
    if name == "cloakbrowser":
        from social_place_scraper.fetchers.cloakbrowser_fetcher import CloakBrowserFetcher

        return CloakBrowserFetcher()
    raise ValueError(f"Unsupported fetcher: {name}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(
        provider=args.provider,
        model=args.model,
        session_name=args.session,
        session_root=args.session_root,
    )
    session = SessionManager(config.session_root).get(config.session_name)

    if args.login or args.login_only:
        prepare_browser_login(
            session=session,
            url=args.url,
            wait_seconds=args.login_wait_seconds,
        )
        if args.login_only:
            print_json(
                {
                    "status": "loginSessionPrepared",
                    "sessionName": session.name,
                    "profileDir": str(session.profile_dir),
                    "cookieFile": str(session.cookie_file),
                },
                compact=args.json,
            )
            return 0

    try:
        post = _fetch_or_load_post(args, session)
    except HumanInterventionRequired as exc:
        if args.interactive_challenges and not args.post_json:
            prepare_browser_login(
                session=session,
                url=exc.intervention.url or args.url,
                wait_seconds=args.login_wait_seconds,
            )
            try:
                post = _fetch_or_load_post(args, session)
            except HumanInterventionRequired as retry_exc:
                print_json(
                    InterventionResult(intervention=retry_exc.intervention).model_dump(mode="json"),
                    compact=args.json,
                )
                return 2
        else:
            print_json(
                InterventionResult(intervention=exc.intervention).model_dump(mode="json"),
                compact=args.json,
            )
            return 2

    if args.no_llm:
        print_json(post.model_dump(mode="json"), compact=args.json)
        return 0

    extraction = LlmExtractor(config.llm).extract(post)
    extraction = attach_maps_urls(extraction)
    print_json(extraction.model_dump(mode="json"), compact=args.json)
    return 0


def _fetch_or_load_post(args: argparse.Namespace, session) -> SocialPost:
    if args.post_json:
        return SocialPost.model_validate_json(Path(args.post_json).read_text(encoding="utf-8"))
    return select_fetcher(args.fetcher).fetch(args.url, session)


def print_json(payload: object, *, compact: bool) -> None:
    indent = None if compact else 2
    print(json.dumps(payload, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"social-post-ingest failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
