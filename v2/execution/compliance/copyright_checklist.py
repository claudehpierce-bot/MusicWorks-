"""MusicWorks™ V4.3 — Copyright Checklist: track ownership and permissions.

MusicWorks displays reminders and tracks founder confirmations only.
MusicWorks does NOT attempt legal conclusions.
Founder confirms ownership or permission for each item.
"""
from datetime import datetime, timezone
from .compliance_store import load_copyright, save_copyright

# ── Item definitions ──────────────────────────────────────────────────────────

COPYRIGHT_ITEMS = [
    (
        "original_song",
        "Original Song",
        "Is this an original composition you own the rights to?",
        "Confirm you own or co-own this song's copyright.",
    ),
    (
        "licensed_material",
        "Licensed Material",
        "Is any externally licensed content used in this release?",
        "If yes, document the license and its permitted uses.",
    ),
    (
        "samples",
        "Audio Samples",
        "Are any sampled recordings used in the music?",
        "Samples require clearance from both the master and publishing rights holders.",
    ),
    (
        "stock_assets",
        "Stock Assets",
        "Are any stock photos, video clips, or audio used in the media?",
        "Confirm each stock asset license permits commercial and digital distribution use.",
    ),
    (
        "fonts",
        "Fonts",
        "Are all fonts used in graphics and artwork licensed for commercial use?",
        "Free fonts may not permit commercial use — check each license.",
    ),
    (
        "images",
        "Third-Party Images",
        "Are any third-party images, illustrations, or photography used?",
        "Confirm each image has a commercial license or permission from the creator.",
    ),
    (
        "logos",
        "Third-Party Logos / Trademarks",
        "Does any artwork or video include logos or trademarks not owned by the artist?",
        "Unauthorized use of trademarks can result in takedowns and legal exposure.",
    ),
    (
        "third_party_music",
        "Third-Party Music",
        "Is any third-party recorded music (not original) used in videos or social content?",
        "Ensure you have sync and master licenses for any non-original music in video.",
    ),
    (
        "video_footage",
        "Third-Party Video Footage",
        "Is any third-party video footage, b-roll, or clips used in the media?",
        "All video footage must be licensed for commercial and social media distribution.",
    ),
]

ITEM_KEYS   = [k for k, _, _, _ in COPYRIGHT_ITEMS]
ITEM_MAP    = {k: (label, q, guidance) for k, label, q, guidance in COPYRIGHT_ITEMS}

OWNERSHIP_OPTIONS = [
    ("owned",          "Owned / Original",  "#22C55E"),
    ("licensed",       "Licensed",          "#3B82F6"),
    ("cleared",        "Cleared",           "#10B981"),
    ("not_applicable", "Not Applicable",    "#6A6460"),
    ("unresolved",     "Unresolved",        "#EF4444"),
    ("not_checked",    "Not Checked",       "#8A8480"),
]
OWNERSHIP_COLORS  = {k: c for k, _, c in OWNERSHIP_OPTIONS}
OWNERSHIP_LABELS  = {k: l for k, l, _ in OWNERSHIP_OPTIONS}


# ── CRUD ──────────────────────────────────────────────────────────────────────

def load_checklist(artist_id: str, song_id: str) -> dict:
    """Returns dict keyed by item_key with ownership_status and notes."""
    return load_copyright(artist_id, song_id).get("items", {})


def save_checklist_item(artist_id: str, song_id: str,
                        item_key: str, ownership_status: str,
                        notes: str = "") -> None:
    data = load_copyright(artist_id, song_id)
    data.setdefault("items", {})[item_key] = {
        "ownership_status": ownership_status,
        "notes":            notes,
        "confirmed_at":     datetime.now(timezone.utc).isoformat(),
    }
    save_copyright(artist_id, song_id, data)


def checklist_summary(artist_id: str, song_id: str) -> dict:
    items    = load_checklist(artist_id, song_id)
    total    = len(COPYRIGHT_ITEMS)
    resolved = sum(1 for k in ITEM_KEYS
                   if items.get(k, {}).get("ownership_status", "not_checked")
                   in ("owned", "licensed", "cleared", "not_applicable"))
    unresolved = sum(1 for k in ITEM_KEYS
                     if items.get(k, {}).get("ownership_status") == "unresolved")
    return {
        "total":      total,
        "resolved":   resolved,
        "unresolved": unresolved,
        "pct":        int(resolved / total * 100) if total else 0,
    }
