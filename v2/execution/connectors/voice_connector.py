"""MusicWorks™ V4.1 — Voice Connector: routes audio/avatar jobs to ElevenLabs, Hedra."""
from .base_connector import BaseConnector, ConnectorResult

VOICE_JOB_TYPES = ["behind_scenes"]


class VoiceConnector(BaseConnector):
    name             = "Voice Connector"
    description      = "Routes voice narration to ElevenLabs and avatar video to Hedra"
    icon             = "🔊"
    handles          = VOICE_JOB_TYPES
    providers        = ["hedra", "elevenlabs"]
    future_providers = ["heygen", "synthesia"]

    def _execute(self, job: dict, provider: str, brand_context: str) -> ConnectorResult:
        from execution.workers import get_worker
        # Hedra preferred for avatar video; ElevenLabs for audio-only
        worker_key = "hedra" if provider == "hedra" else "elevenlabs"
        worker = get_worker(worker_key)
        if not worker:
            return ConnectorResult(success=False, error=f"{worker_key} worker not found")
        result = worker.generate(job, brand_context=brand_context)
        return ConnectorResult(
            success=result.success,
            output_text=result.output_text,
            output_files=result.output_files,
            worker_used=worker_key,
            prompt_used=result.prompt_used,
            mock=result.mock,
            error=result.error,
            metadata=result.metadata,
        )
