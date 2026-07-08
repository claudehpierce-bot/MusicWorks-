"""MusicWorks™ V4 — DistroKid metadata store (release info only — no API automation)."""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DK_DIR   = DATA_DIR / "distrokid"


def _path(artist_id: str) -> Path:
    DK_DIR.mkdir(parents=True, exist_ok=True)
    return DK_DIR / f"{artist_id}.json"


def _default(artist_id: str) -> dict:
    return {
        "artist_id": artist_id,
        "releases":  [],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def load_distrokid(artist_id: str) -> dict:
    p = _path(artist_id)
    if not p.exists():
        return _default(artist_id)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return _default(artist_id)


def save_distrokid(data: dict) -> None:
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    _path(data["artist_id"]).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def get_release(artist_id: str, song_id: str) -> dict | None:
    data = load_distrokid(artist_id)
    for r in data.get("releases", []):
        if r.get("song_id") == song_id:
            return r
    return None


def upsert_release(artist_id: str, song_id: str, fields: dict) -> dict:
    """Insert or update a release record. Returns the updated release dict."""
    data  = load_distrokid(artist_id)
    releases = data.setdefault("releases", [])
    for r in releases:
        if r.get("song_id") == song_id:
            r.update(fields)
            r["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_distrokid(data)
            return r
    new_release = {
        "song_id":        song_id,
        "song_title":     fields.get("song_title", ""),
        "release_date":   fields.get("release_date", ""),
        "release_time":   fields.get("release_time", ""),
        "pre_save_link":  fields.get("pre_save_link", ""),
        "streaming_url":  fields.get("streaming_url", ""),
        "spotify_url":    fields.get("spotify_url", ""),
        "apple_music_url": fields.get("apple_music_url", ""),
        "youtube_music_url": fields.get("youtube_music_url", ""),
        "audiomack_url":  fields.get("audiomack_url", ""),
        "upc":            fields.get("upc", ""),
        "isrc":           fields.get("isrc", ""),
        "store_url":      fields.get("store_url", ""),
        "album_url":      fields.get("album_url", ""),
        "status":         fields.get("status", "upcoming"),
        "created_at":     datetime.now(timezone.utc).isoformat(),
        "updated_at":     datetime.now(timezone.utc).isoformat(),
    }
    releases.append(new_release)
    save_distrokid(data)
    return new_release


def list_releases(artist_id: str) -> list[dict]:
    return load_distrokid(artist_id).get("releases", [])
