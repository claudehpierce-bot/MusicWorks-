"""MusicWorks™ V5.4 — Artist Presence Connector (Hero Worker #2).

Human connection: Shorts, TikTok, Reels, countdowns, artist introductions,
devotionals, scripture reflections, behind-the-song content. Routes to
Hedra, HeyGen (future). Long-form cinematic content lives in
video_connector.py.
"""
from .base_connector import BaseConnector, ConnectorResult

ARTIST_PRESENCE_JOB_TYPES = [
    "instagram_reel", "tiktok", "youtube_short", "facebook_reel", "x_video",
    "reaction", "behind_scenes", "countdown", "artist_welcome",
    "devotional", "scripture_reflection",
]


class ArtistPresenceConnector(BaseConnector):
    name             = "Artist Presence Connector"
    description      = "Routes short-form, human-connection video to Hedra or HeyGen"
    icon             = "🎙️"
    task_category    = "talking_avatar"
    handles          = ARTIST_PRESENCE_JOB_TYPES
    providers        = ["hedra", "heygen"]
    future_providers = ["heygen"]

    def _execute(self, job: dict, provider: str, brand_context: str) -> ConnectorResult:
        from execution.workers import get_worker
        worker = get_worker("hedra")
        if not worker:
            return ConnectorResult(success=False, error="Hedra worker not found")
        result = worker.generate(job, brand_context=brand_context)
        return ConnectorResult(
            success=result.success,
            output_text=result.output_text,
            output_files=result.output_files,
            worker_used="hedra",
            prompt_used=result.prompt_used,
            mock=result.mock,
            error=result.error,
            metadata=result.metadata,
        )
