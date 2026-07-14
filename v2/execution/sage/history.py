"""MusicWorks(tm) -- Sage's Conversation History.

Per the Sage Presence milestone: "Conversation History replaces the concept
of transcripts... Do not build unrestricted chat. This is institutional
guidance history." This store holds only narrated moments (welcome,
institutional explanations, department introductions, Boardroom briefing,
campaign summaries, recovery guidance, major teaching moments) -- never
arbitrary chat turns, because Sage never takes arbitrary chat turns.

Single global, append-only log (mirrors the wizard draft's single-file
pattern -- this is a single-founder workspace today, not a multi-user
history store). Never rewritten in place; a moment once spoken stays in
history even if later moments supersede it.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

HISTORY_PATH = Path(__file__).parent.parent.parent / "data" / "sage_history" / "history.json"
MAX_ENTRIES = 300  # oldest entries drop off; this is a guidance log, not a permanent audit trail


def _load() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(entries: list[dict]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(entries[-MAX_ENTRIES:], indent=2, ensure_ascii=False), encoding="utf-8")


def append_moment(moment: str, transcript: str, context_summary: str = "") -> dict:
    """Record a narrated moment. `context_summary` is a short human-readable
    note of what real state this was narrated from (e.g. "Fire & Flow Gospel
    -- HLANGANA"), for the founder's own scanning in the History view --
    never re-derived or guessed at display time."""
    entry = {
        "moment": moment,
        "transcript": transcript,
        "context_summary": context_summary,
        "spoken_at": datetime.now(timezone.utc).isoformat(),
    }
    entries = _load()
    entries.append(entry)
    _save(entries)
    return entry


def list_history() -> list[dict]:
    """Oldest first."""
    return _load()


def get_last() -> dict | None:
    entries = _load()
    return entries[-1] if entries else None
