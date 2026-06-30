"""Brand Brain™ data models — artist memory that persists forever."""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone


@dataclass
class CreativeDNA:
    lighting: list = field(default_factory=list)
    color_palette: dict = field(default_factory=dict)
    architecture: list = field(default_factory=list)
    environment: list = field(default_factory=list)
    lens_style: str = ""
    camera_movement: str = ""
    composition: str = ""
    typography: dict = field(default_factory=dict)
    visual_keywords: list = field(default_factory=list)
    rendering_keywords: list = field(default_factory=list)
    emotion: list = field(default_factory=list)
    energy: list = field(default_factory=list)
    movement: list = field(default_factory=list)
    festival_style: str = ""
    church_style: str = ""
    performance_style: str = ""
    what_to_avoid: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "CreativeDNA":
        valid = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass
class BrandVoice:
    tone: list = field(default_factory=list)
    style: list = field(default_factory=list)
    vocabulary: list = field(default_factory=list)
    avoid: list = field(default_factory=list)
    scripture_style: str = ""
    cta_style: str = ""
    platform_voice: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "BrandVoice":
        valid = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass
class TheoGuardrails:
    required: list = field(default_factory=list)
    forbidden: list = field(default_factory=list)
    scripture_accuracy: str = ""
    theological_stance: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "TheoGuardrails":
        valid = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass
class CampaignMemory:
    campaign_id: str
    song_title: str
    date: str
    mode: str
    winning_hooks: list = field(default_factory=list)
    winning_thumbnails: list = field(default_factory=list)
    winning_captions: list = field(default_factory=list)
    best_platform: str = ""
    lessons_learned: list = field(default_factory=list)
    founder_revisions: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "CampaignMemory":
        valid = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass
class ArtistBrain:
    artist_id: str
    artist_name: str
    display_name: str
    tagline: str
    mission: str
    bio_short: str
    bio_long: str
    genre: list = field(default_factory=list)
    heritage: list = field(default_factory=list)
    team_members: list = field(default_factory=list)
    creative_dna: CreativeDNA = field(default_factory=CreativeDNA)
    brand_voice: BrandVoice = field(default_factory=BrandVoice)
    theological_guardrails: TheoGuardrails = field(default_factory=TheoGuardrails)
    discography: list = field(default_factory=list)
    series: list = field(default_factory=list)
    platform_handles: dict = field(default_factory=dict)
    audience: dict = field(default_factory=dict)
    campaign_history: list = field(default_factory=list)
    founder_preferences: list = field(default_factory=list)
    brand_rules: list = field(default_factory=list)
    future_notes: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def from_dict(cls, d: dict) -> "ArtistBrain":
        data = dict(d)
        if "creative_dna" in data and isinstance(data["creative_dna"], dict):
            data["creative_dna"] = CreativeDNA.from_dict(data["creative_dna"])
        if "brand_voice" in data and isinstance(data["brand_voice"], dict):
            data["brand_voice"] = BrandVoice.from_dict(data["brand_voice"])
        if "theological_guardrails" in data and isinstance(data["theological_guardrails"], dict):
            data["theological_guardrails"] = TheoGuardrails.from_dict(data["theological_guardrails"])
        if "campaign_history" in data:
            data["campaign_history"] = [
                CampaignMemory.from_dict(c) if isinstance(c, dict) else c
                for c in data["campaign_history"]
            ]
        valid = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in valid})
