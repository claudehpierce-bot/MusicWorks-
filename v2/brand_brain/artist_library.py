"""Artist Library — load, save, and list artist Brand Brains from disk."""
import json
from pathlib import Path
from datetime import datetime, timezone
from brand_brain.models import ArtistBrain

ARTISTS_DIR = Path(__file__).parent.parent / "data" / "artists"


def _path(artist_id: str) -> Path:
    return ARTISTS_DIR / f"{artist_id}.json"


def load_artist(artist_id: str) -> ArtistBrain | None:
    """Return ArtistBrain for the given ID, or None if not found."""
    p = _path(artist_id)
    if not p.exists():
        return None
    return ArtistBrain.from_dict(json.loads(p.read_text(encoding="utf-8")))


def save_artist(brain: ArtistBrain) -> None:
    """Write the artist brain to disk, updating updated_at."""
    ARTISTS_DIR.mkdir(parents=True, exist_ok=True)
    brain.updated_at = datetime.now(timezone.utc).isoformat()
    data = _to_dict(brain)
    _path(brain.artist_id).write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def list_artists() -> list[dict]:
    """Return a list of {artist_id, artist_name} for all saved artists."""
    ARTISTS_DIR.mkdir(parents=True, exist_ok=True)
    result = []
    for f in sorted(ARTISTS_DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            result.append({
                "artist_id": d.get("artist_id", f.stem),
                "artist_name": d.get("artist_name", f.stem),
                "display_name": d.get("display_name", d.get("artist_name", f.stem)),
            })
        except Exception:
            pass
    return result


def add_campaign_memory(artist_id: str, memory: dict) -> bool:
    """Append a completed campaign's lessons to the artist's brain. Returns True on success."""
    brain = load_artist(artist_id)
    if brain is None:
        return False
    from brand_brain.models import CampaignMemory
    brain.campaign_history.append(CampaignMemory.from_dict(memory))
    save_artist(brain)
    return True


def _to_dict(obj) -> dict | list | str | int | float | bool | None:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    if isinstance(obj, list):
        return [_to_dict(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    return obj
