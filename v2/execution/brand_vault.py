"""Brand Vault — upload and manage artist brand assets (stored locally)."""
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

from config import DATA_DIR

UPLOADS_BASE = Path(__file__).parent.parent / "uploads" / "artists"
_META_DIR = DATA_DIR / "vault"  # dedicated dir so list_artists() ignores these

VAULT_TYPES = [
    ("artist_photo",         "Artist Photo",               "📸"),
    ("duo_photo",            "Duo Photo",                  "👥"),
    ("album_cover",          "Album Cover",                "💿"),
    ("mood_board",           "Mood Board / Creative DNA",  "🎨"),
    ("bonfire_logo",         "Bonfire Logo",               "🔥"),
    ("main_logo",            "Main Artist Logo",           "✨"),
    ("typography_reference", "Typography Reference",       "🔤"),
    ("color_reference",      "Color Reference",            "🖌️"),
    ("promo_image",          "Promo Image",                "🖼️"),
    ("reference_video",      "Reference Video",            "🎬"),
]

_LABEL = {k: lbl for k, lbl, _ in VAULT_TYPES}
_ICON  = {k: icon for k, _, icon in VAULT_TYPES}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".webm"}


def _meta_path(artist_id: str) -> Path:
    return _META_DIR / f"{artist_id}.json"


def load_vault_meta(artist_id: str) -> dict:
    p = _meta_path(artist_id)
    if not p.exists():
        return {"artist_id": artist_id, "assets": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"artist_id": artist_id, "assets": []}


def save_vault_meta(artist_id: str, meta: dict):
    p = _meta_path(artist_id)
    _META_DIR.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def store_vault_asset(artist_id: str, asset_type: str, uploaded_file) -> dict:
    """Write an uploaded file to disk and register it in vault metadata."""
    upload_dir = UPLOADS_BASE / artist_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    raw = uploaded_file.read()
    dest = upload_dir / uploaded_file.name
    dest.write_bytes(raw)

    record = {
        "asset_id":   f"vault-{uuid.uuid4().hex[:10]}",
        "asset_type": asset_type,
        "label":      _LABEL.get(asset_type, asset_type),
        "icon":       _ICON.get(asset_type, "📁"),
        "file_name":  uploaded_file.name,
        "file_path":  str(dest),
        "file_size":  len(raw),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

    meta = load_vault_meta(artist_id)
    meta.setdefault("assets", []).append(record)
    save_vault_meta(artist_id, meta)
    return record


def delete_vault_asset(artist_id: str, asset_id: str):
    meta = load_vault_meta(artist_id)
    asset = next((a for a in meta.get("assets", []) if a["asset_id"] == asset_id), None)
    if asset:
        try:
            Path(asset["file_path"]).unlink(missing_ok=True)
        except Exception:
            pass
        meta["assets"] = [a for a in meta["assets"] if a["asset_id"] != asset_id]
        save_vault_meta(artist_id, meta)


def vault_asset_count(artist_id: str) -> int:
    return len(load_vault_meta(artist_id).get("assets", []))


def vault_has_visuals(artist_id: str) -> bool:
    visual_types = {"artist_photo", "duo_photo", "album_cover", "mood_board", "promo_image", "main_logo"}
    assets = load_vault_meta(artist_id).get("assets", [])
    return any(a.get("asset_type") in visual_types for a in assets)
