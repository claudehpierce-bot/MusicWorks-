from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone
import uuid


@dataclass
class SongInput:
    song_id: str
    title: str
    title_meaning: str
    title_language: str
    artist_name: str
    album_title: str
    release_date: str
    scripture_primary: str
    scripture_primary_text: str
    themes: list
    theology_approved: bool
    audio_qc_approved: bool
    genre: list = field(default_factory=list)
    mood: list = field(default_factory=list)
    scripture_supporting: list = field(default_factory=list)
    series_name: Optional[str] = None
    series_episode: Optional[int] = None
    cultural_notes: Optional[str] = None
    isrc: Optional[str] = None
    album_id: Optional[str] = None
    track_number: Optional[int] = None
    duration_seconds: Optional[int] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    content_advisory: str = "none"
    artist_id: str = ""
    brand_color_primary: str = "#2D1B69"
    brand_color_secondary: str = "#D4A853"
    target_geography: list = field(default_factory=list)
    target_audience_age: str = "18-45"
    target_faith_background: str = "Christian — all denominations"
    lyrics_text: Optional[str] = None
    tempo_estimate: Optional[int] = None
    mood_estimate: list = field(default_factory=list)
    energy_level_estimate: Optional[str] = None
    hook_timestamps: list = field(default_factory=list)
    structure_segments: list = field(default_factory=list)
    audio_analysis_source: Optional[str] = None

    def validate(self):
        """Hard gate: theology and audio QC must both be approved."""
        if not self.theology_approved:
            raise ValueError(
                f"HARD GATE BLOCKED: {self.title} has not passed Theology Review (Agent 03). "
                "Complete the theology review before running a campaign."
            )
        if not self.audio_qc_approved:
            raise ValueError(
                f"HARD GATE BLOCKED: {self.title} has not passed Audio QC (Agent 04). "
                "Complete audio quality control before running a campaign."
            )

    @classmethod
    def from_dict(cls, data: dict) -> "SongInput":
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class CampaignPlan:
    campaign_id: str
    campaign_name: str
    campaign_mode: str
    campaign_goal: str
    platforms: list
    content_calendar: list
    risk_log: list
    ministry_angle: str
    song_id: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AssetRecord:
    asset_id: str
    campaign_id: str
    song_id: str
    asset_type: str
    asset_description: str
    file_name: str
    file_path: str
    status: str = "READY_FOR_REVIEW"
    platform_targets: list = field(default_factory=list)
    rendered_by: str = "claude_api"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    revision_count: int = 0
    is_revision: bool = False
    revision_of_asset_id: Optional[str] = None
    revision_notes: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    preview_text: Optional[str] = None
    approved_at: Optional[str] = None
    approval_decision: Optional[str] = None
    founder_notes: Optional[str] = None

    @staticmethod
    def new_id() -> str:
        return f"asset-{uuid.uuid4().hex[:12]}"
