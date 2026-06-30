"""MusicWorks™ V4.1 — Video Connector: routes video jobs to Veo, Runway, Pika (future)."""
from .base_connector import BaseConnector, ConnectorResult

VIDEO_JOB_TYPES = [
    "instagram_reel", "tiktok", "youtube_short", "facebook_reel",
    "x_video", "rumble_video", "spotify_canvas", "reaction",
]


class VideoConnector(BaseConnector):
    name             = "Video Connector"
    description      = "Routes video generation to Veo, Runway, or Pika"
    icon             = "🎥"
    handles          = VIDEO_JOB_TYPES
    providers        = ["veo"]
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
