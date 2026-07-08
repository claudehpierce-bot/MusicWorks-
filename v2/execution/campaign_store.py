"""MusicWorks™ V6.2 — Media Campaign lifecycle store.

A "Campaign" here is the media-campaign entity around one song: it tracks
lifecycle status, chosen blitz schedule, and links to the DistroKid release
record. It is distinct from `contracts.models.CampaignPlan` (an in-memory
content-calendar object from campaign_agent, never persisted) and from the
folder-scanned "campaign_id" used by `execution/asset_library.py` /
`ui/pages/campaigns.py` — those two keep working independently.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR      = Path(__file__).parent.parent / "data"
CAMPAIGNS_DIR = DATA_DIR / "campaigns"

STATUSES = [
    "draft",                  # Assets are being collected.
    "building",               # MusicWorks is generating campaign assets.
    "review",                 # Founder is reviewing generated assets.
    "approved",               # Assets are approved and ready.
    "waiting_for_distrokid",  # Founder has not yet confirmed release links.
    "ready_to_launch",        # Approved assets + release schedule are ready.
    "live_blitz",             # Media blitz is actively running.
    "paused",                 # Founder paused the campaign.
    "completed",              # Campaign finished.
    "relaunch_ready",         # Campaign can be restarted or extended.
]

# Manual states: only founder actions (Control Center buttons) move a campaign
# into or out of these — recompute_status() never overrides them automatically.
MANUAL_STATUSES = {"live_blitz", "paused", "completed", "relaunch_ready"}

STATUS_LABELS = {
    "draft":                  "Draft",
    "building":                "Building",
    "review":                  "In Review",
    "approved":                "Approved",
    "waiting_for_distrokid":   "Waiting for DistroKid",
    "ready_to_launch":         "Ready to Launch",
    "live_blitz":              "Live Blitz",
    "paused":                  "Paused",
    "completed":               "Completed",
    "relaunch_ready":          "Relaunch Ready",
}

CAMPAIGN_TYPES = ["48h", "7d", "14d", "30d", "custom"]
CAMPAIGN_TYPE_LABELS = {
    "48h":    "48-Hour Launch Blitz",
    "7d":     "7-Day Release Campaign",
    "14d":    "14-Day Momentum Campaign",
    "30d":    "30-Day Full Campaign",
    "custom": "Custom",
}

INTENSITIES = ["light", "standard", "aggressive"]
INTENSITY_POSTS_PER_DAY = {"light": 1, "standard": 3, "aggressive": 6}

# DistroKid release-link fields that count as "DistroKid has returned something" —
# deliberately excludes release_date (the wizard's date picker always defaults to
# today, so gating on release_date presence would never actually fire).
RELEASE_LINK_FIELDS = (
    "streaming_url", "spotify_url", "apple_music_url",
    "youtube_music_url", "audiomack_url", "album_url",
)


# ── Paths ─────────────────────────────────────────────────────────────────────

def _path(artist_id: str) -> Path:
    CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
    return CAMPAIGNS_DIR / f"{artist_id}.json"


def _load_all(artist_id: str) -> list[dict]:
    p = _path(artist_id)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_all(artist_id: str, campaigns: list[dict]) -> None:
    _path(artist_id).write_text(
        json.dumps(campaigns, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def make_campaign_id(song_id: str) -> str:
    """Deterministic per-song id — makes campaign creation idempotent across
    repeated wizard runs for the same song, and keeps this id independent of
    CampaignPlan.campaign_id (which is LLM-generated and not guaranteed unique)."""
    return f"campaign-{song_id}"


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_campaign(
    artist_id: str,
    song_id: str,
    song_title: str,
    campaign_name: str,
    campaign_mode: str = "blitz",
) -> dict:
    """Create the campaign for this song, or return the existing one unchanged
    (idempotent — a founder re-running the wizard for the same song reuses the
    same campaign record rather than orphaning a duplicate)."""
    campaign_id = make_campaign_id(song_id)
    existing = get_campaign(artist_id, campaign_id)
    if existing:
        return existing

    now = datetime.now(timezone.utc).isoformat()
    campaign = {
        "campaign_id":      campaign_id,
        "artist_id":        artist_id,
        "song_id":          song_id,
        "song_title":       song_title,
        "campaign_name":    campaign_name,
        "status":           "draft",
        "campaign_mode":    campaign_mode,
        "campaign_type":    "",
        "intensity":        "",
        "platforms":        [],
        "launch_datetime":  "",
        "window_start":     "",
        "window_end":       "",
        "launched_at":      None,
        "paused_at":        None,
        "completed_at":     None,
        "extension_count":  0,
        "created_at":       now,
        "updated_at":       now,
    }
    campaigns = _load_all(artist_id)
    campaigns.append(campaign)
    _save_all(artist_id, campaigns)
    return campaign


def get_campaign(artist_id: str, campaign_id: str) -> dict | None:
    for c in _load_all(artist_id):
        if c.get("campaign_id") == campaign_id:
            return c
    return None


def save_campaign(campaign: dict) -> None:
    campaign["updated_at"] = datetime.now(timezone.utc).isoformat()
    campaigns = _load_all(campaign["artist_id"])
    for i, c in enumerate(campaigns):
        if c.get("campaign_id") == campaign["campaign_id"]:
            campaigns[i] = campaign
            break
    else:
        campaigns.append(campaign)
    _save_all(campaign["artist_id"], campaigns)


def list_campaigns(artist_id: str) -> list[dict]:
    return sorted(_load_all(artist_id), key=lambda c: c.get("created_at", ""), reverse=True)


def update_campaign_status(artist_id: str, campaign_id: str, status: str, **fields) -> dict | None:
    campaign = get_campaign(artist_id, campaign_id)
    if not campaign:
        return None
    campaign["status"] = status
    campaign.update(fields)
    save_campaign(campaign)
    return campaign


# ── Status derivation ─────────────────────────────────────────────────────────

def recompute_status(campaign: dict, jobs: list[dict], release: dict | None) -> str:
    """Pure function — derives the campaign's status from current job/release
    data. Called fresh every time the Control Center renders rather than pushed
    from Approval Queue or elsewhere, so no other page needs to know about
    campaigns at all.

    Manual states (live_blitz/paused/completed/relaunch_ready) are founder-
    controlled via Control Center buttons and are never auto-overridden here.
    """
    current = campaign.get("status", "draft")
    if current in MANUAL_STATUSES:
        return current

    if not jobs:
        return "draft"

    if any(j.get("status") in ("pending", "queued", "generating") for j in jobs) and \
       not any(j.get("status") == "review" for j in jobs):
        return "building"

    if any(j.get("status") == "review" for j in jobs):
        return "review"

    approved = [j for j in jobs if j.get("status") == "approved"]
    if not approved:
        # Every job resolved (rejected/scheduled/published) but none approved —
        # nothing to gate on yet; treat like still-in-review.
        return "review"

    has_link = bool(release) and any(release.get(f) for f in RELEASE_LINK_FIELDS)
    if not has_link:
        return "waiting_for_distrokid"

    if campaign.get("campaign_type") and campaign.get("platforms"):
        return "ready_to_launch"

    return "approved"
