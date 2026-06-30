"""MusicWorks™ V4.1 — Image Connector: routes static design jobs to Canva, Adobe (future)."""
from .base_connector import BaseConnector, ConnectorResult

IMAGE_JOB_TYPES = ["quote_card", "story_slides", "thumbnail_set", "countdown"]


class ImageConnector(BaseConnector):
    name             = "Image Connector"
    description      = "Routes design briefs to Canva or future AI image providers"
    icon             = "🎨"
    handles          = IMAGE_JOB_TYPES
    providers        = ["canva"]
    future_providers = ["adobe_firefly", "midjourney", "imagen"]

    def _execute(self, job: dict, provider: str, brand_context: str) -> ConnectorResult:
        from execution.workers import get_worker
        worker = get_worker("canva")
        if not worker:
            return ConnectorResult(success=False, error="Canva worker not found")
        result = worker.generate(job, brand_context=brand_context)
        return ConnectorResult(
            success=result.success,
            output_text=result.output_text,
            output_files=result.output_files,
            worker_used="canva",
            prompt_used=result.prompt_used,
            mock=result.mock,
            error=result.error,
            metadata=result.metadata,
        )
