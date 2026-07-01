"""MusicWorks™ V4.1 — Connector package: provider-agnostic routing layer.

Connectors sit between the Production Queue and Workers.
Adding a new AI provider only requires updating the relevant connector —
no changes to jobs, workers, or UI.
"""
from .base_connector import BaseConnector, ConnectorResult
from .video_connector import VideoConnector
from .artist_presence_connector import ArtistPresenceConnector
from .image_connector import ImageConnector
from .voice_connector import VoiceConnector
from .writing_connector import WritingConnector
from .publishing_connector import PublishingConnector, PUBLISHING_PLATFORMS, PLATFORM_LABEL, PLATFORM_ICON
from .analytics_connector import AnalyticsConnector

# All connectors in dispatch priority order
ALL_CONNECTORS: list[BaseConnector] = [
    WritingConnector(),
    VideoConnector(),
    ArtistPresenceConnector(),
    ImageConnector(),
    VoiceConnector(),
    PublishingConnector(),
    AnalyticsConnector(),
]

# Job type → connector mapping (built from handles lists)
_JOB_CONNECTOR_MAP: dict[str, BaseConnector] = {}
for _c in ALL_CONNECTORS:
    for _jt in _c.handles:
        _JOB_CONNECTOR_MAP[_jt] = _c


def get_connector(job_type: str) -> BaseConnector:
    """Return the appropriate connector for a given job type.
    Falls back to WritingConnector (Claude) for unknown types."""
    return _JOB_CONNECTOR_MAP.get(job_type, WritingConnector())


def dispatch_job(job: dict, brand_context: str = "") -> ConnectorResult:
    """Route a job through the correct connector to the best available provider."""
    connector = get_connector(job.get("job_type", ""))
    return connector.dispatch(job, brand_context=brand_context)
