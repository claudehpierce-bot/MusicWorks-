"""MusicWorks™ V4.1 — Learning Engine: capture release insights, feed back to Artist Brain.

Architecture only — no AI recommendations yet.
After every release, MusicWorks stores what performed best.
Future versions will surface recommendations automatically.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR      = Path(__file__).parent.parent / "data"
LEARNING_DIR  = DATA_DIR / "learning"

# ── Learning signal keys ──────────────────────────────────────────────────────

LEARNING_KEYS = [
    ("best_hook",          "Best Hook",          "Which opening line drove the most retention"),
    ("best_thumbnail",     "Best Thumbnail",     "Which visual style drove the most CTR"),
    ("best_cta",           "Best CTA",           "Which call-to-action drove the most clicks"),
    ("best_time",          "Best Posting Time",  "Which time slot drove the most engagement"),
    ("best_platform",      "Best Platform",      "Which platform drove the most streams/growth"),
    ("best_duration",      "Best Duration",      "Which video length drove the best completion"),
    ("best_visual_style",  "Best Visual Style",  "Which visual approach resonated most"),
    ("best_caption_length","Best Caption Length","Short vs long — which performed better"),
    ("best_hashtag_set",   "Best Hashtag Set",   "Which hashtag group drove the most discovery"),
    ("top_comment_theme",  "Top Comment Theme",  "What the audience responded to most"),
    ("fastest_growth_post","Fastest Growth Post","Which post drove the most follower growth"),
    ("devotional_uptake",  "Devotional Uptake",  "How many downloaded the devotional guide"),
]

SIGNAL_LABELS = {k: l for k, l, _ in LEARNING_KEYS}
SIGNAL_DESCS  = {k: d for k, _, d in LEARNING_KEYS}


def _path(artist_id: str) -> Path:
    LEARNING_DIR.mkdir(parents=True, exist_ok=True)
    return LEARNING_DIR / f"{artist_id}.json"


def load_learning(artist_id: str) -> dict:
    p = _path(artist_id)
    if not p.exists():
        return {"artist_id": artist_id, "releases": {}, "global": {}}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"artist_id": artist_id, "releases": {}, "global": {}}


def save_learning(data: dict) -> None:
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    _path(data["artist_id"]).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def record_signal(artist_id: str, song_id: str, signal_key: str, value: str, notes: str = "") -> None:
    """Record a learning signal for a specific release."""
    data = load_learning(artist_id)
    data["releases"].setdefault(song_id, {})
    data["releases"][song_id][signal_key] = {
        "value":      value,
        "notes":      notes,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    # Update global (rolling — latest per artist)
    data["global"][signal_key] = {
        "value":      value,
        "notes":      notes,
        "song_id":    song_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_learning(data)


def get_release_signals(artist_id: str, song_id: str) -> dict:
    data = load_learning(artist_id)
    return data.get("releases", {}).get(song_id, {})


def get_global_signals(artist_id: str) -> dict:
    return load_learning(artist_id).get("global", {})


def signals_for_brain_injection(artist_id: str) -> str:
    """Format learning signals as text for injection into the Brand Brain / AI prompts."""
    signals = get_global_signals(artist_id)
    if not signals:
        return ""
    lines = ["LEARNING ENGINE — Insights from past releases:"]
    for key, sig in signals.items():
        label = SIGNAL_LABELS.get(key, key)
        lines.append(f"  {label}: {sig.get('value', '')} (from release: {sig.get('song_id', '')})")
    return "\n".join(lines)
