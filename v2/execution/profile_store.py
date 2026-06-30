"""Extended artist profile — fields not in the ArtistBrain dataclass."""
import json
from pathlib import Path
from datetime import datetime, timezone

from config import DATA_DIR

# Store in a dedicated sub-dir so list_artists() doesn't pick these up
_STORE_DIR = DATA_DIR / "profiles"

_DEFAULTS: dict = {
    "cultural_pillars":      [],
    "cities_of_influence":   [],
    "countries_of_influence": [],
    "target_audience":       "",
    "ministry_focus":        "",
    "visual_style_notes":    "",
    "notes":                 "",
}


def _path(artist_id: str) -> Path:
    return _STORE_DIR / f"{artist_id}.json"


def load_profile(artist_id: str) -> dict:
    p = _path(artist_id)
    if not p.exists():
        return dict(_DEFAULTS)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return {**_DEFAULTS, **data}
    except Exception:
        return dict(_DEFAULTS)


def save_profile(artist_id: str, data: dict):
    p = _path(artist_id)
    _STORE_DIR.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
