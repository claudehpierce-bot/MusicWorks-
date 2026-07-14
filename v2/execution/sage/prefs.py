"""MusicWorks(tm) -- Sage founder preferences (mute state).

Persisted to disk, not just st.session_state -- a mute preference set
before a browser crash or refresh must survive it, the same lesson the
Wizard Stability milestone already applied to campaign drafts. A muted
founder should never have Sage start talking again just because the
session reset.
"""
import json
from pathlib import Path

PREFS_PATH = Path(__file__).parent.parent.parent / "data" / "sage_prefs.json"


def _load() -> dict:
    if not PREFS_PATH.exists():
        return {}
    try:
        return json.loads(PREFS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def is_muted() -> bool:
    return bool(_load().get("muted", False))


def set_muted(muted: bool) -> None:
    PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = _load()
    data["muted"] = bool(muted)
    PREFS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
