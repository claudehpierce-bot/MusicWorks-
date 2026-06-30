"""Artist Library — load, save, create, and list artist Brand Brains from disk."""
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from brand_brain.models import ArtistBrain

ARTISTS_DIR = Path(__file__).parent.parent / "data" / "artists"


def _path(artist_id: str) -> Path:
    return ARTISTS_DIR / f"{artist_id}.json"


def _to_dict(obj) -> dict | list | str | int | float | bool | None:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    if isinstance(obj, list):
        return [_to_dict(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    return obj


def artist_id_exists(artist_id: str) -> bool:
    return _path(artist_id).exists()


def make_slug(name: str) -> str:
    """Convert an artist name to a safe file slug."""
    s = name.lower().strip()
    s = re.sub(r"[&]+", "and", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def backup_artist(artist_id: str) -> Path | None:
    """Copy the current artist JSON to data/backups/ before overwriting."""
    p = _path(artist_id)
    if not p.exists():
        return None
    backups = ARTISTS_DIR.parent / "backups"
    backups.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = backups / f"{artist_id}_{ts}.json"
    dest.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    return dest


def load_artist(artist_id: str) -> ArtistBrain | None:
    """Return ArtistBrain for the given ID, or None if not found."""
    p = _path(artist_id)
    if not p.exists():
        return None
    return ArtistBrain.from_dict(json.loads(p.read_text(encoding="utf-8")))


def save_artist(brain: ArtistBrain) -> None:
    """Write the artist brain to disk (with backup). Updates updated_at."""
    ARTISTS_DIR.mkdir(parents=True, exist_ok=True)
    backup_artist(brain.artist_id)
    brain.updated_at = datetime.now(timezone.utc).isoformat()
    _path(brain.artist_id).write_text(
        json.dumps(_to_dict(brain), indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def create_artist(artist_id: str, fields: dict) -> ArtistBrain:
    """Create a brand-new artist from form fields. Raises ValueError if slug exists."""
    if artist_id_exists(artist_id):
        raise ValueError(f"Artist '{artist_id}' already exists.")

    from brand_brain.models import BrandVoice, TheoGuardrails

    genre = fields.get("genre", [])
    if isinstance(genre, str):
        genre = [g.strip() for g in genre.split(",") if g.strip()]

    heritage = fields.get("heritage", [])
    if isinstance(heritage, str):
        heritage = [h.strip() for h in heritage.splitlines() if h.strip()]

    now = datetime.now(timezone.utc).isoformat()
    brain = ArtistBrain(
        artist_id=artist_id,
        artist_name=fields.get("artist_name", ""),
        display_name=fields.get("artist_name", ""),
        tagline=fields.get("tagline", ""),
        mission=fields.get("mission", ""),
        bio_short=fields.get("bio_short", ""),
        bio_long=fields.get("bio_long", ""),
        genre=genre,
        heritage=heritage,
        brand_voice=BrandVoice(
            tone=[t.strip() for t in fields.get("brand_voice_tone", "").split(",") if t.strip()],
        ),
        theological_guardrails=TheoGuardrails(
            theological_stance=fields.get("theology_notes", ""),
        ),
        created_at=now,
        updated_at=now,
    )

    ARTISTS_DIR.mkdir(parents=True, exist_ok=True)
    _path(artist_id).write_text(
        json.dumps(_to_dict(brain), indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    # Ensure uploads directory exists
    uploads = ARTISTS_DIR.parent.parent / "uploads" / "artists" / artist_id
    uploads.mkdir(parents=True, exist_ok=True)

    return brain


def list_artists() -> list[dict]:
    """Return [{artist_id, artist_name, display_name}] for all saved artists."""
    ARTISTS_DIR.mkdir(parents=True, exist_ok=True)
    result = []
    for f in sorted(ARTISTS_DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            if not d.get("artist_id"):
                continue
            result.append({
                "artist_id":   d.get("artist_id", f.stem),
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
