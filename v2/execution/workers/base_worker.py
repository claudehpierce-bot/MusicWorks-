"""MusicWorks™ V4 — Base worker interface."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkerResult:
    success:     bool
    output_text: str = ""
    output_files: list[str] = field(default_factory=list)
    prompt_used: str = ""
    tokens_used: int = 0
    error:       str = ""
    mock:        bool = False
    metadata:    dict = field(default_factory=dict)


class BaseWorker:
    key:          str  = ""
    name:         str  = ""
    description:  str  = ""
    icon:         str  = "🤖"
    color:        str  = "#6A6460"
    provider_url: str  = ""

    # Job types this worker handles
    supported_types: list[str] = []

    @property
    def available(self) -> bool:
        """True when the required API key/credentials are present."""
        return False

    def generate(self, job: dict, brand_context: str = "") -> WorkerResult:
        raise NotImplementedError(f"{self.__class__.__name__}.generate() not implemented")

    def estimate_time(self, job: dict) -> str:
        """Human-readable estimate for this job type."""
        return "~5 min"

    def build_prompt(self, job: dict, brand_context: str = "") -> str:
        """Build the generation prompt for this job."""
        return ""

    def status_pill(self) -> str:
        if self.available:
            return f'<span style="background:#22C55E22; color:#22C55E; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600;">LIVE</span>'
        return f'<span style="background:#6A646022; color:#6A6460; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600;">NOT CONFIGURED</span>'
