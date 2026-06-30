"""MusicWorks™ V4.3 — Compliance Store: persistence layer for all compliance data."""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR      = Path(__file__).parent.parent.parent / "data"
COMPLIANCE_DIR = DATA_DIR / "compliance"
PROFILES_DIR   = DATA_DIR / "platform_profiles"


# ── Path helpers ──────────────────────────────────────────────────────────────

def compliance_path(artist_id: str, song_id: str) -> Path:
    p = COMPLIANCE_DIR / artist_id / song_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["_updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Readiness ─────────────────────────────────────────────────────────────────

def load_readiness(artist_id: str, song_id: str) -> dict:
    return _load(compliance_path(artist_id, song_id) / "readiness.json")


def save_readiness(artist_id: str, song_id: str, data: dict) -> None:
    _save(compliance_path(artist_id, song_id) / "readiness.json", data)


# ── Copyright ─────────────────────────────────────────────────────────────────

def load_copyright(artist_id: str, song_id: str) -> dict:
    return _load(compliance_path(artist_id, song_id) / "copyright.json")


def save_copyright(artist_id: str, song_id: str, data: dict) -> None:
    _save(compliance_path(artist_id, song_id) / "copyright.json", data)


# ── Platform Profiles ─────────────────────────────────────────────────────────

def load_profile(platform_key: str) -> dict:
    return _load(PROFILES_DIR / f"{platform_key}.json")


def save_profile(platform_key: str, data: dict) -> None:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    _save(PROFILES_DIR / f"{platform_key}.json", data)


# ── AI Usage records ──────────────────────────────────────────────────────────

def load_ai_usage(artist_id: str, song_id: str) -> dict:
    return _load(compliance_path(artist_id, song_id) / "ai_usage.json")


def save_ai_usage(artist_id: str, song_id: str, data: dict) -> None:
    _save(compliance_path(artist_id, song_id) / "ai_usage.json", data)


# ── Governance log ────────────────────────────────────────────────────────────

def load_governance_log(artist_id: str) -> list:
    p = COMPLIANCE_DIR / artist_id / "governance_log.json"
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def append_governance_log(artist_id: str, entry: dict) -> None:
    log = load_governance_log(artist_id)
    entry["logged_at"] = datetime.now(timezone.utc).isoformat()
    log.append(entry)
    p = COMPLIANCE_DIR / artist_id / "governance_log.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
