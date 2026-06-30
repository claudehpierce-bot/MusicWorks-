"""MusicWorks™ V4.1 — Analytics Connector: fetches performance data from platform APIs.

NOTE: Platform API integrations are stubs. Analytics are entered manually or
imported. The architecture is prepared for future API connections.
"""
from .base_connector import BaseConnector, ConnectorResult


class AnalyticsConnector(BaseConnector):
    name             = "Analytics Connector"
    description      = "Fetches views, CTR, watch time, engagement from platform APIs"
    icon             = "📊"
    handles          = []
    providers        = ["manual"]
    future_providers = ["youtube_analytics", "meta_insights", "tiktok_analytics", "spotify_analytics"]

    def fetch(self, artist_id: str, song_id: str, platform: str) -> dict:
        """Stub: returns empty metrics. Future: calls platform API."""
        return {
            "platform":           platform,
            "views":              0,
            "watch_time_seconds": 0,
            "ctr":                0.0,
            "retention_pct":      0.0,
            "comments":           0,
            "shares":             0,
            "likes":              0,
            "followers_gained":   0,
            "traffic_referrals":  0,
            "source":             "manual",
        }

    def _execute(self, job: dict, provider: str, brand_context: str) -> ConnectorResult:
        return ConnectorResult(success=True, output_text="Analytics ready for manual entry.", mock=True)
