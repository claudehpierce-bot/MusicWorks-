"""MusicWorks™ V5.4 — Voice Connector: routes pure audio narration to ElevenLabs.

Talking-avatar video (Hedra) is owned by artist_presence_connector.py — this
connector is audio-only (voice narration, spoken scripture, devotional audio).
"""
from .base_connector import BaseConnector, ConnectorResult

VOICE_JOB_TYPES: list[str] = []


class VoiceConnector(BaseConnector):
    name             = "Voice Connector"
    description      = "Routes voice narration and spoken-word audio to ElevenLabs"
    icon             = "🔊"
    task_category    = "voice"
    handles          = VOICE_JOB_TYPES
    providers        = ["elevenlabs"]
    future_providers = ["synthesia"]

    def _execute(self, job: dict, provider: str, brand_context: str) -> ConnectorResult:
        from execution.workers import get_worker
        worker = get_worker("elevenlabs")
        if not worker:
            return ConnectorResult(success=False, error="ElevenLabs worker not found")
        result = worker.generate(job, brand_context=brand_context)
        return ConnectorResult(
            success=result.success,
            output_text=result.output_text,
            output_files=result.output_files,
            worker_used="elevenlabs",
            prompt_used=result.prompt_used,
            mock=result.mock,
            error=result.error,
            metadata=result.metadata,
        )
