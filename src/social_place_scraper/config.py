from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class LlmConfig:
    provider: str
    base_url: str | None
    api_key: str | None
    model: str
    temperature: float = 0.0


@dataclass(frozen=True)
class AppConfig:
    llm: LlmConfig
    session_name: str
    session_root: Path


def load_config(
    *,
    provider: str | None = None,
    model: str | None = None,
    session_name: str | None = None,
    session_root: str | None = None,
) -> AppConfig:
    load_dotenv()

    llm_provider = provider or _env_default(
        "SOCIAL_PLACE_LLM_PROVIDER",
        "openai-compatible",
    )
    llm_model = model or _env_default("SOCIAL_PLACE_LLM_MODEL", "gpt-4.1-mini")
    root = Path(session_root or _env_default("SOCIAL_PLACE_SESSION_ROOT", ".sessions"))
    resolved_session_name = session_name or _env_default("SOCIAL_PLACE_SESSION_NAME", "default")

    return AppConfig(
        llm=LlmConfig(
            provider=llm_provider,
            base_url=os.getenv("SOCIAL_PLACE_LLM_BASE_URL"),
            api_key=os.getenv("SOCIAL_PLACE_LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
            model=llm_model,
            temperature=float(os.getenv("SOCIAL_PLACE_LLM_TEMPERATURE", "0")),
        ),
        session_name=resolved_session_name,
        session_root=root,
    )


def _env_default(name: str, default: str) -> str:
    return os.getenv(name) or default
