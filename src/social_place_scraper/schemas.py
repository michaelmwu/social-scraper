from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Platform(StrEnum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    UNKNOWN = "unknown"


class MediaItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: Literal["image", "video", "unknown"] = "unknown"
    url: str | None = None
    thumbnail_url: str | None = None
    alt: str | None = None
    position: int | None = None


class SocialPost(BaseModel):
    model_config = ConfigDict(extra="allow")

    platform: Platform = Platform.UNKNOWN
    canonical_url: str
    post_id: str | None = None
    author: str | None = None
    title: str | None = None
    caption: str | None = None
    accessibility_caption: str | None = None
    location_tag: str | None = None
    taken_at: int | None = None
    hashtags: list[str] = Field(default_factory=list)
    mentions: list[str] = Field(default_factory=list)
    media: list[MediaItem] = Field(default_factory=list)
    source_confidence: Literal[
        "http_metadata",
        "botasaurus",
        "cloakbrowser",
        "manual",
    ] = "http_metadata"
    raw_metadata: dict[str, Any] = Field(default_factory=dict)


class PlaceCandidate(BaseModel):
    name: str
    region: str | None = None
    category: str | None = None
    mapsUrl: str | None = None
    socialTag: str | None = None
    webUrl: str | None = None
    description: str | None = None


class PlaceExtraction(BaseModel):
    overallRegion: str | None = None
    placeCandidates: list[PlaceCandidate] = Field(default_factory=list)


class IngestResult(BaseModel):
    post: SocialPost
    extraction: PlaceExtraction


class HumanIntervention(BaseModel):
    kind: Literal["login", "verification_code", "captcha", "checkpoint", "unknown"]
    platform: Platform = Platform.UNKNOWN
    sessionName: str
    message: str
    url: str | None = None
    profileDir: str | None = None
    screenshotPath: str | None = None
    codeChannel: Literal["email", "sms", "authenticator", "unknown"] | None = None


class InterventionResult(BaseModel):
    status: Literal["needsHumanIntervention"] = "needsHumanIntervention"
    intervention: HumanIntervention
