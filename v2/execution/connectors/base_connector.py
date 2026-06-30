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
    """Abstract base for all MusicWorks connectors."""

    name:        str = ""
    description: str = ""
    icon:        str = "🔌"

    # Job types this connector handles
    handles: list[str] = []

    # Ordered list of providers to try (first available wins)
    providers: list[str] = []

    # Future providers (not yet integrated)
    future_providers: list[str] = []

    def dispatch(self, job: dict, brand_context: str = "") -> ConnectorResult:
        """Dispatch job to the best available provider."""
        import time
        start = time.time()
        provider = self._select_provider()
        result = self._execute(job, provider, brand_context)
        result.generation_time_ms = int((time.time() - start) * 1000)
        result.provider_used = provider
        return result

    def _select_provider(self) -> str:
        """Return the key of the best available provider."""
        from execution.connections_store import is_connected
        for p in self.providers:
            if is_connected(p):
                return p
        return self.providers[0] if self.providers else "mock"

    def _execute(self, job: dict, provider: str, brand_context: str) -> ConnectorResult:
        raise NotImplementedError

    def available_provider(self) -> str | None:
        """Return first available provider key, or None."""
        from execution.connections_store import is_connected
        return next((p for p in self.providers if is_connected(p)), None)
