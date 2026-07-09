"""MusicWorks™ V7 Phase 1 — The Live Creative Brief™.

The single source of creative truth every department reads from
(Constitutional Amendment I). Versioned: every save appends an immutable
version rather than overwriting, so the founder can compare and restore.
Fields are stored as an open dict, not a fixed dataclass, so future fields
or departments can be added without a schema migration (Principle 8).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR   = Path(__file__).parent.parent / "data"
BRIEFS_DIR = DATA_DIR / "briefs"

# campaign_duration and publishing_priority are creative-intent fields (how
# the campaign should FEEL) -- deliberately distinct from campaign_store's
# campaign_type/intensity (the literal scheduling mechanics Campaign
# Operations owns in the Media Blitz Control Center). See
# brief_dependencies.py for why they don't drive regeneration.
BRIEF_FIELDS = [
    "campaign_theme", "campaign_title", "core_message", "target_audience",
    "emotion", "mood", "story", "keywords", "seo", "tagline", "hashtags",
    "visual_direction", "colour_direction", "campaign_goals",
    "artist_narrative", "scripture_emphasis", "call_to_action",
    "platform_strategy", "playlist_direction", "campaign_duration",
    "publishing_priority",
]

FIELD_LABELS = {
    "campaign_theme": "Campaign Theme", "campaign_title": "Campaign Title",
    "core_message": "Core Message", "target_audience": "Target Audience",
    "emotion": "Emotion", "mood": "Mood", "story": "Story",
    "keywords": "Keywords", "seo": "SEO", "tagline": "Tagline",
    "hashtags": "Hashtags", "visual_direction": "Visual Direction",
    "colour_direction": "Colour Direction", "campaign_goals": "Campaign Goals",
    "artist_narrative": "Artist Narrative", "scripture_emphasis": "Scripture Emphasis",
    "call_to_action": "Call To Action", "platform_strategy": "Platform Strategy",
    "playlist_direction": "Playlist Direction", "campaign_duration": "Campaign Duration",
    "publishing_priority": "Publishing Priority",
}


def _path(artist_id: str) -> Path:
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    return BRIEFS_DIR / f"{artist_id}.json"


def _load_all(artist_id: str) -> dict:
    """{campaign_id: [version, version, ...]}"""
    p = _path(artist_id)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_all(artist_id: str, data: dict) -> None:
    _path(artist_id).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _empty_fields() -> dict:
    return {f: "" for f in BRIEF_FIELDS}


def _diff(old_fields: dict, new_fields: dict) -> list[str]:
    return [f for f in BRIEF_FIELDS if (old_fields.get(f, "") or "") != (new_fields.get(f, "") or "")]


def create_brief(artist_id: str, campaign_id: str, fields: dict, authored_by: str = "creative_director") -> dict:
    """Version 1 — idempotent per campaign_id, matching campaign_store's
    idempotency convention. Called once, right after the Creative Director
    produces the initial campaign plan."""
    all_data = _load_all(artist_id)
    if all_data.get(campaign_id):
        return all_data[campaign_id][-1]

    now = datetime.now(timezone.utc).isoformat()
    merged = {**_empty_fields(), **{k: v for k, v in fields.items() if k in BRIEF_FIELDS}}
    version = {
        "version": 1,
        "created_at": now,
        "authored_by": authored_by,
        "fields": merged,
        "changed_fields": list(BRIEF_FIELDS),  # everything is new on v1
    }
    all_data[campaign_id] = [version]
    _save_all(artist_id, all_data)
    return version


def save_version(artist_id: str, campaign_id: str, fields: dict, authored_by: str = "founder") -> dict:
    """A founder edit (or a restore) — always appends a new version, never
    overwrites a prior one."""
    all_data = _load_all(artist_id)
    versions = all_data.get(campaign_id, [])
    prev_fields = versions[-1]["fields"] if versions else _empty_fields()

    merged = {**prev_fields, **{k: v for k, v in fields.items() if k in BRIEF_FIELDS}}
    changed = _diff(prev_fields, merged)

    version = {
        "version": len(versions) + 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "authored_by": authored_by,
        "fields": merged,
        "changed_fields": changed,
    }
    versions.append(version)
    all_data[campaign_id] = versions
    _save_all(artist_id, all_data)
    return version


def get_current(artist_id: str, campaign_id: str) -> dict | None:
    versions = _load_all(artist_id).get(campaign_id, [])
    return versions[-1] if versions else None


def list_versions(artist_id: str, campaign_id: str) -> list[dict]:
    return _load_all(artist_id).get(campaign_id, [])


def get_version(artist_id: str, campaign_id: str, version_number: int) -> dict | None:
    for v in list_versions(artist_id, campaign_id):
        if v["version"] == version_number:
            return v
    return None


def restore_version(artist_id: str, campaign_id: str, version_number: int) -> dict | None:
    """Copies an old version's fields forward as a brand-new version — never
    destructive; full history is preserved either way."""
    old = get_version(artist_id, campaign_id, version_number)
    if not old:
        return None
    return save_version(
        artist_id, campaign_id, old["fields"], authored_by=f"restored_from_v{version_number}"
    )
