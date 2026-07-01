"""MusicWorks™ V5.4 — Cinematic Video Connector (Hero Worker #1).

Long-form storytelling: official music videos, trailers, visualizers,
cinematic scenes, worship backgrounds. Routes to Veo, Runway, Pika (future).
Short-form artist-presence content lives in artist_presence_connector.py.
"""
from .base_connector import BaseConnector, ConnectorResult

VIDEO_JOB_TYPES = [
    "music_video", "trailer", "lyric_visualizer", "cinematic_scenes",
    "worship_background", "youtube_video", "rumble_video", "spotify_canvas",
]


class VideoConnector(BaseConnector):
    name             = "Cinematic Video Connector"
    description      = "Routes long-form cinematic video to Veo or HeyGen"
    icon             = "🎬"
    task_category    = "video"
    handles          = VIDEO_JOB_TYPES
    providers        = ["veo", "heygen"]
    future_providers = ["runway", "pika", "sora"]

    def _execute(self, job: dict, provider: str, brand_context: str) -> ConnectorResult:
        from execution.workers import get_worker
        worker = get_worker("veo")
        if not worker:
            return ConnectorResult(success=False, error="Veo worker not found")
        result = worker.generate(job, brand_context=brand_context)
        return ConnectorResult(
            success=result.success,
            output_text=result.output_text,
            output_files=result.output_files,
            worker_used="veo",
            prompt_used=result.prompt_used,
            mock=result.mock,
            error=result.error,
            metadata=result.metadata,
        )
