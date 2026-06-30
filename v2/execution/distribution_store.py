"""Distribution Store — save and load artist publishing destinations."""
import json
from pathlib import Path
from datetime import datetime, timezone

from config import DATA_DIR

_STORE_DIR = DATA_DIR / "distribution"  # dedicated dir so list_artists() ignores these

SOCIAL_FIELDS = {
    "youtube_channel_url":  "YouTube Channel URL",
    "tiktok_username":      "TikTok Username (@handle)",
    "instagram_username":   "Instagram Username (@handle)",
    "facebook_page_url":    "Facebook Page URL",
    "threads_username":     "Threads Username (@handle)",
}

STREAMING_FIELDS = {
    "spotify_artist_url":      "Spotify Artist URL",
    "apple_music_artist_url":  "Apple Music Artist URL",
    "audiomack_profile_url":   "Audiomack Profile URL",
    "youtube_music_url":       "YouTube Music URL",
}

OWNED_FIELDS = {
    "website_url":          "Website URL",
    "email_list_platform":  "Email List Platform (e.g. Mailchimp, Klaviyo)",
    "newsletter_url":       "Newsletter Sign-up URL",
}

PRESS_FIELDS = {
    "press_contact_email":     "Press Contact Email",
    "church_outreach_notes":   "Church Outreach List Notes",
    "media_list_notes":        "Media List Notes",
}

PLATFORM_ICONS = {
    "youtube_channel_url":    "▶️",
    "tiktok_username":        "📱",
    "instagram_username":     "📷",
    "facebook_page_url":      "📘",
    "threads_username":       "🧵",
    "spotify_artist_url":     "🎵",
    "apple_music_artist_url": "🍎",
    "audiomack_profile_url":  "🎧",
    "youtube_music_url":      "🎶",
    "website_url":            "🌐",
    "email_list_platform":    "📧",
    "newsletter_url":         "📰",
    "press_contact_email":    "📣",
    "church_outreach_notes":  "⛪",
    "media_list_notes":       "📋",
}


def _empty_dist(artist_id: str) -> dict:
    return {
        "artist_id": artist_id,
        "social":    {k: "" for k in SOCIAL_FIELDS},
        "streaming": {k: "" for k in STREAMING_FIELDS},
        "owned":     {k: "" for k in OWNED_FIELDS},
        "press":     {k: "" for k in PRESS_FIELDS},
        "updated_at": "",
    }


def _dist_path(artist_id: str) -> Path:
    return _STORE_DIR / f"{artist_id}.json"


def load_distribution(artist_id: str) -> dict:
    p = _dist_path(artist_id)
    if not p.exists():
        return _empty_dist(artist_id)
    try:
        saved = json.loads(p.read_text(encoding="utf-8"))
        base = _empty_dist(artist_id)
        for section in ["social", "streaming", "owned", "press"]:
            base[section].update(saved.get(section, {}))
        base["updated_at"] = saved.get("updated_at", "")
        return base
    except Exception:
        return _empty_dist(artist_id)


def save_distribution(artist_id: str, data: dict):
    p = _dist_path(artist_id)
    _STORE_DIR.mkdir(parents=True, exist_ok=True)
    data["artist_id"] = artist_id
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def dist_configured_count(dist: dict) -> int:
    """Count non-empty social + streaming + owned fields."""
    total = 0
    for section in ["social", "streaming", "owned"]:
        total += sum(1 for v in dist.get(section, {}).values() if str(v).strip())
    return total


def dist_platform_display(dist: dict) -> list[dict]:
    """Return a flat list of {key, label, icon, value, section} for all configured platforms."""
    result = []
    section_map = {
        "social":    SOCIAL_FIELDS,
        "streaming": STREAMING_FIELDS,
        "owned":     OWNED_FIELDS,
        "press":     PRESS_FIELDS,
    }
    for section, fields in section_map.items():
        for key, label in fields.items():
            value = dist.get(section, {}).get(key, "")
            result.append({
                "key":     key,
                "label":   label,
                "icon":    PLATFORM_ICONS.get(key, "•"),
                "value":   value,
                "section": section,
                "set":     bool(str(value).strip()),
            })
    return result
