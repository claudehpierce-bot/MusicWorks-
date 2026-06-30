"""MusicWorks™ V4 — Analytics store: track performance data per asset."""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR     = Path(__file__).parent.parent / "data"
ANALYTICS_DIR = DATA_DIR / "analytics"


def _artist_dir(artist_id: str) -> Path:
    d = ANALYTICS_DIR / artist_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _song_path(artist_id: str, song_id: str) -> Path:
    return _artist_dir(artist_id) / f"{song_id}.json"


def _default_song(artist_id: str, song_id: str) -> dict:
    return {
        "artist_id": artist_id,
        "song_id":   song_id,
        "snapshots": [],
        "by_platform": {},
        "learning": {},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def load_analytics(artist_id: str, song_id: str) -> dict:
    p = _song_path(artist_id, song_id)
    if not p.exists():
        return _default_song(artist_id, song_id)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return _default_song(artist_id, song_id)


def save_analytics(data: dict) -> None:
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    _song_path(data["artist_id"], data["song_id"]).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def record_snapshot(
    artist_id: str,
    song_id: str,
    platform: str,
    metrics: dict,
) -> dict:
    """
    Record a performance snapshot for a platform at a point in time.
    metrics: {views, watch_time_seconds, ctr, shares, comments, likes, followers_gained, ...}
    """
    data = load_analytics(artist_id, song_id)
    snap = {
        "platform":   platform,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **metrics,
    }
    data["snapshots"].append(snap)

    # Update by_platform aggregate
    agg = data["by_platform"].setdefault(platform, {
        "views": 0, "shares": 0, "comments": 0, "likes": 0,
        "watch_time_seconds": 0, "followers_gained": 0, "snapshots": 0,
    })
    agg["snapshots"] += 1
    for k in ("views", "shares", "comments", "likes", "watch_time_seconds", "followers_gained"):
        agg[k] = max(agg.get(k, 0), metrics.get(k, 0))  # store peak

    save_analytics(data)
    return snap


def get_totals(artist_id: str, song_id: str) -> dict:
    """Aggregate across all platforms for a song."""
    data = load_analytics(artist_id, song_id)
    totals: dict[str, int | float] = {"views": 0, "shares": 0, "comments": 0, "likes": 0, "followers_gained": 0}
    for platform_data in data["by_platform"].values():
        for k in totals:
            totals[k] += platform_data.get(k, 0)
    return totals


def update_learning(artist_id: str, song_id: str, key: str, value: str) -> None:
    """Store a learning insight (best posting time, best platform, etc.)."""
    data = load_analytics(artist_id, song_id)
    data["learning"][key] = {"value": value, "updated_at": datetime.now(timezone.utc).isoformat()}
    save_analytics(data)


def list_song_analytics(artist_id: str) -> list[dict]:
    d = _artist_dir(artist_id)
    results = []
    for f in sorted(d.glob("*.json")):
        try:
            results.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return results
