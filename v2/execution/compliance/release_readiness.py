"""MusicWorks™ V4.3 — Release Readiness: per-release readiness report model.

MusicWorks provides guidance only. Founder makes all publishing decisions.
MusicWorks does NOT guarantee compliance or provide legal advice.
"""
from datetime import datetime, timezone
from .compliance_store import load_readiness, save_readiness

# ── Status constants ──────────────────────────────────────────────────────────

STATUS_READY        = "ready"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_BLOCKED      = "blocked"
STATUS_NOT_CHECKED  = "not_checked"

STATUS_LABELS = {
    STATUS_READY:        "Ready",
    STATUS_NEEDS_REVIEW: "Needs Review",
    STATUS_BLOCKED:      "Blocked",
    STATUS_NOT_CHECKED:  "Not Checked",
}
STATUS_COLORS = {
    STATUS_READY:        "#22C55E",
    STATUS_NEEDS_REVIEW: "#F59E0B",
    STATUS_BLOCKED:      "#EF4444",
    STATUS_NOT_CHECKED:  "#6A6460",
}
STATUS_ICONS = {
    STATUS_READY:        "✓",
    STATUS_NEEDS_REVIEW: "⚠",
    STATUS_BLOCKED:      "✗",
    STATUS_NOT_CHECKED:  "○",
}

# Item score weights
ITEM_SCORES = {
    STATUS_READY:        1.0,
    STATUS_NEEDS_REVIEW: 0.5,
    STATUS_BLOCKED:      0.0,
    STATUS_NOT_CHECKED:  0.75,
}

# ── Readiness sections & default items ────────────────────────────────────────

SECTIONS = [
    {
        "key":   "artwork",
        "label": "Artwork",
        "icon":  "🎨",
        "items": [
            ("hero_image",      "Hero Image / Album Cover",   "High-resolution artwork ready (min 3000×3000 px)"),
            ("thumbnail",       "Platform Thumbnails",         "Thumbnails prepared for each publishing platform"),
            ("social_graphics", "Social Graphics",             "Quote cards, story slides, and countdown assets prepared"),
            ("no_trademark",    "No Unlicensed Trademarks",   "Artwork contains no unlicensed logos or third-party trademarks"),
        ],
    },
    {
        "key":   "lyrics",
        "label": "Lyrics",
        "icon":  "📝",
        "items": [
            ("lyrics_ready",    "Lyrics Written",              "Final lyrics documented and confirmed"),
            ("scripture_cited", "Scripture References Cited",  "All scripture references noted and verified"),
            ("no_samples",      "No Uncleared Lyric Samples",  "No unlicensed lyric samples used"),
        ],
    },
    {
        "key":   "music",
        "label": "Music",
        "icon":  "🎵",
        "items": [
            ("master_ready",    "Master Recording Ready",      "Final master audio file exported and quality-checked"),
            ("stems_ready",     "Stems Available",             "Individual track stems saved if needed for remixes/edits"),
            ("samples_cleared", "Samples Cleared",             "All audio samples licensed or cleared for distribution"),
            ("credits_done",    "Credits Documented",          "All contributing artists, producers, and engineers credited"),
        ],
    },
    {
        "key":   "video",
        "label": "Video",
        "icon":  "🎥",
        "items": [
            ("video_ready",     "Video Content Ready",         "At least one video asset ready for publishing"),
            ("aspect_ratios",   "Aspect Ratios Checked",       "Video exported in all required aspect ratios (9:16, 16:9, 1:1)"),
            ("captions_added",  "Captions / Subtitles Added",  "Captions included for accessibility"),
            ("no_faces",        "AI Face Policy Observed",     "No uncleared identifiable faces in AI-generated video"),
            ("content_check",   "Content Reviewed",            "Video content reviewed for platform community guidelines"),
        ],
    },
    {
        "key":   "metadata",
        "label": "Metadata",
        "icon":  "🏷️",
        "items": [
            ("title_set",       "Song Title Confirmed",        "Official song title set and consistent across platforms"),
            ("release_date",    "Release Date Set",            "Official release date confirmed"),
            ("isrc_ready",      "ISRC Code Obtained",          "ISRC code assigned for tracking streams"),
            ("genre_tagged",    "Genre & Mood Tagged",         "Genre, mood, and style tags prepared"),
            ("description",     "Descriptions Written",        "Platform-specific descriptions and bios ready"),
        ],
    },
    {
        "key":   "publishing",
        "label": "Publishing",
        "icon":  "🚀",
        "items": [
            ("assets_approved", "Assets Approved",             "All planned assets reviewed and founder-approved"),
            ("schedule_set",    "Publishing Schedule Set",     "Publishing dates and times confirmed for each platform"),
            ("captions_ready",  "Captions & Hashtags Ready",   "Platform-specific captions and hashtag sets prepared"),
            ("pre_save",        "Pre-Save Link Active",        "Pre-save link set up and shared (if applicable)"),
        ],
    },
    {
        "key":   "distribution",
        "label": "Distribution",
        "icon":  "📦",
        "items": [
            ("distrokid_submitted", "DistroKid Submission",    "Song submitted to DistroKid for streaming distribution"),
            ("release_set",     "Release Configuration Set",   "Release type, explicit tag, and territories configured"),
            ("artwork_uploaded","Artwork Uploaded to DSPs",    "Artwork uploaded to distribution platform and approved"),
        ],
    },
    {
        "key":   "brand",
        "label": "Brand",
        "icon":  "🧠",
        "items": [
            ("brand_voice",     "Brand Voice Consistent",      "Content tone matches the Artist Brand Voice guidelines"),
            ("theology_check",  "Theology Reviewed",           "Theological messaging reviewed for accuracy and consistency"),
            ("visual_identity", "Visual Identity Consistent",  "Colors, fonts, and visual style match brand guidelines"),
        ],
    },
    {
        "key":   "ai_usage",
        "label": "AI Usage",
        "icon":  "🤖",
        "items": [
            ("ai_disclosed",    "AI Disclosure Ready",         "AI usage noted in descriptions where platform requires disclosure"),
            ("ai_reviewed",     "AI Output Reviewed",          "All AI-generated content reviewed by a human before publishing"),
            ("ai_approved",     "Founder AI Approval",         "Founder has reviewed and approved all AI-generated assets"),
            ("no_deepfake",     "No Deceptive Deepfakes",      "No AI-generated content intended to deceive or misrepresent"),
        ],
    },
    {
        "key":   "copyright",
        "label": "Copyright",
        "icon":  "©️",
        "items": [
            ("original_confirmed",  "Original Work Confirmed",  "Song is confirmed as an original work"),
            ("samples_documented",  "Samples Documented",       "Any samples are documented with licensing status"),
            ("stock_assets_cleared","Stock Assets Cleared",     "Any stock images/video/audio properly licensed"),
            ("no_infringement",     "No Known Infringement",    "No known copyright issues identified"),
        ],
    },
    {
        "key":   "platform_review",
        "label": "Platform Review",
        "icon":  "📱",
        "items": [
            ("guidelines_checked",  "Community Guidelines",     "Content reviewed against platform community guidelines"),
            ("music_policy",        "Music Policy",             "Music usage complies with each platform's music policy"),
            ("monetization_ready",  "Monetization Ready",       "Account and content set up for monetization where applicable"),
            ("sponsor_disclosed",   "Sponsorship Disclosed",    "Any sponsored or branded content properly disclosed"),
        ],
    },
]

SECTION_MAP = {s["key"]: s for s in SECTIONS}

# ── Score computation ─────────────────────────────────────────────────────────

def compute_section_score(items_data: dict) -> float:
    """0.0–1.0 score for a section based on item statuses."""
    if not items_data:
        return ITEM_SCORES[STATUS_NOT_CHECKED]
    scores = [ITEM_SCORES.get(v.get("status", STATUS_NOT_CHECKED), ITEM_SCORES[STATUS_NOT_CHECKED])
              for v in items_data.values()]
    return sum(scores) / len(scores) if scores else 0.0


def compute_section_status(items_data: dict) -> str:
    """Worst-case status for a section."""
    statuses = [v.get("status", STATUS_NOT_CHECKED) for v in items_data.values()]
    if STATUS_BLOCKED in statuses:
        return STATUS_BLOCKED
    if STATUS_NEEDS_REVIEW in statuses:
        return STATUS_NEEDS_REVIEW
    if all(s == STATUS_READY for s in statuses):
        return STATUS_READY
    return STATUS_NOT_CHECKED


def compute_release_score(artist_id: str, song_id: str) -> dict:
    """Return {score: int, status: str, sections: {key: status}}."""
    data    = load_readiness(artist_id, song_id)
    items   = data.get("items", {})
    scores  = []
    section_statuses = {}

    for section in SECTIONS:
        skey = section["key"]
        section_items = {ikey: items.get(ikey, {}) for ikey, _, _ in section["items"]}
        score = compute_section_score(section_items)
        scores.append(score)
        section_statuses[skey] = compute_section_status(section_items)

    overall_score  = int((sum(scores) / len(scores)) * 100) if scores else 0
    if any(s == STATUS_BLOCKED for s in section_statuses.values()):
        overall_status = STATUS_BLOCKED
    elif any(s == STATUS_NEEDS_REVIEW for s in section_statuses.values()):
        overall_status = STATUS_NEEDS_REVIEW
    elif all(s == STATUS_READY for s in section_statuses.values()):
        overall_status = STATUS_READY
    else:
        overall_status = STATUS_NOT_CHECKED

    return {
        "score":    overall_score,
        "status":   overall_status,
        "sections": section_statuses,
    }


# ── CRUD helpers ──────────────────────────────────────────────────────────────

def get_item(artist_id: str, song_id: str, item_key: str) -> dict:
    data = load_readiness(artist_id, song_id)
    return data.get("items", {}).get(item_key, {"status": STATUS_NOT_CHECKED, "note": ""})


def set_item(artist_id: str, song_id: str, item_key: str,
             status: str, note: str = "") -> None:
    data = load_readiness(artist_id, song_id)
    data.setdefault("items", {})[item_key] = {
        "status":       status,
        "note":         note,
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
    }
    save_readiness(artist_id, song_id, data)
