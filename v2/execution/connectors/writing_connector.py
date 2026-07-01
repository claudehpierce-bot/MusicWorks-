"""MusicWorks™ V4.1 — Writing Connector: routes text generation to Claude."""
from .base_connector import BaseConnector, ConnectorResult

WRITING_JOB_TYPES = [
    "blog", "email", "press_release", "church_outreach", "post_launch",
]


class WritingConnector(BaseConnector):
    name             = "Writing Connector"
    description      = "Routes text generation to Claude or Perplexity"
    icon             = "✍️"
    task_category    = "writing"
    handles          = WRITING_JOB_TYPES
    providers        = ["claude", "perplexity"]
    future_providers = ["gpt4", "gemini"]

    def _execute(self, job: dict, provider: str, brand_context: str) -> ConnectorResult:
        from execution.workers import get_worker
        worker = get_worker("claude")
        if not worker:
            return ConnectorResult(success=False, error="Claude worker not found")
        result = worker.generate(job, brand_context=brand_context)
        return ConnectorResult(
            success=result.success,
            output_text=result.output_text,
            output_files=result.output_files,
            worker_used="claude",
            prompt_used=result.prompt_used,
            tokens_used=result.tokens_used,
            mock=result.mock,
            error=result.error,
            metadata=result.metadata,
        )
