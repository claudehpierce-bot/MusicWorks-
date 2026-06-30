"""MusicWorks™ V4.1 — Base connector interface.

Connectors sit between the Production Queue and Workers.
They route each job to the best available provider, making the
system provider-agnostic. When new AI tools emerge, only the
connector changes — the rest of the system stays intact.

Flow: Job → Connector → Provider/Worker → Output → Asset Review
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConnectorResult:
    success:      bool
    output_text:  str = ""
    output_files: list[str] = field(default_factory=list)
    provider_used: str = ""
    worker_used:   str = ""
    prompt_used:   str = ""
    tokens_used:   int = 0
    generation_time_ms: int = 0
    mock:         bool = False
    error:        str = ""
    metadata:     dict = field(default_factory=dict)


class BaseConnector:
    """Abstract base for all MusicWorks connectors.

    V4.2: _select_provider() now delegates to provider_router.route(),
    which checks API keys, subscription status, overrides, and fallbacks
    automatically. Subclasses set task_category to enable this.
    """

    name:          str = ""
    description:   str = ""
    icon:          str = "🔌"
    task_category: str = ""   # e.g. "writing", "video", "graphics" — drives router

    # Job types this connector handles
    handles: list[str] = []

    # Ordered list of providers to try (legacy fallback list)
    providers: list[str] = []

    # Future providers (not yet integrated — shown in Connections UI)
    future_providers: list[str] = []

    def dispatch(self, job: dict, brand_context: str = "") -> ConnectorResult:
        """Dispatch job through the intelligent provider router."""
        import time
        start    = time.time()
        provider = self._select_provider(job)
        result   = self._execute(job, provider, brand_context)
        result.generation_time_ms = int((time.time() - start) * 1000)
        result.provider_used = provider
        return result

    def _select_provider(self, job: dict | None = None) -> str:
        """Return best available provider via router, falling back to legacy list."""
        from execution.provider_router import route, route_for_job

        # Prefer job-type specific routing if job provided
        if job and job.get("job_type"):
            return route_for_job(job["job_type"])

        # Connector-level task category routing
        if self.task_category:
            return route(self.task_category)

        # Legacy: first available from providers list
        from execution.provider_router import is_available
        for p in self.providers:
            if is_available(p):
                return p
        return self.providers[0] if self.providers else "mock"

    def _execute(self, job: dict, provider: str, brand_context: str) -> ConnectorResult:
        raise NotImplementedError

    def available_provider(self) -> str | None:
        """Return the currently routed provider key, or None if mock."""
        from execution.provider_router import route, is_available
        category = self.task_category
        if not category:
            return next((p for p in self.providers if is_available(p)), None)
        selected = route(category)
        return selected if selected != "mock" else None
