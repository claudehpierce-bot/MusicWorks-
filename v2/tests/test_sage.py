"""MusicWorks(tm) -- regression tests for Sage Presence's core modules:
voice registry resolution, narrator honesty, voice synthesis graceful
degrade, history, and mute preference persistence.

Dependency-free, same pattern as tests/test_brand_assets.py: run directly
with `python tests/test_sage.py` from the v2/ directory.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

results = []


def check(name: str, passed: bool, detail: str = ""):
    results.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    line = f"[{status}] {name}"
    if detail and not passed:
        line += f" -- {detail}"
    print(line)


def run():
    from execution.voice_registry import VoiceNotFoundError, resolve_voice
    from execution.sage import narrator, voice as sage_voice, history, prefs

    # ── Voice registry ───────────────────────────────────────────────────────
    provider, voice_id = resolve_voice("SVS-1")
    check("SVS-1 resolves to elevenlabs", provider == "elevenlabs")
    check("SVS-1 resolves to the approved provider_voice_id", voice_id == "iClufiZuqgXWVCRt4s2o")
    try:
        resolve_voice("NOT-A-REAL-STANDARD")
        check("unknown voice standard raises VoiceNotFoundError", False, "no exception raised")
    except VoiceNotFoundError:
        check("unknown voice standard raises VoiceNotFoundError", True)

    # ── Narrator honesty ─────────────────────────────────────────────────────
    check("unknown moment returns None (never invents)", narrator.narrate("not_a_real_moment") is None)

    welcome_plain = narrator.narrate("welcome", artist_name="Fire & Flow Gospel", draft_title=None, draft_step_label=None)
    check("welcome (no draft) is non-empty and omits fabricated draft info", bool(welcome_plain) and "unfinished campaign" not in welcome_plain)

    welcome_draft = narrator.narrate("welcome", artist_name="Fire & Flow Gospel", draft_title="HLANGANA", draft_step_label="Artwork")
    check("welcome (with real draft) mentions the real draft", bool(welcome_draft) and "HLANGANA" in welcome_draft)

    for moment in ("step_artist", "step_creative_master", "step_lyrics", "step_artwork", "step_release_info", "creative_brief_intro", "campaign_operations_ready"):
        text = narrator.narrate(moment)
        check(f"moment '{moment}' returns non-empty text", bool(text))

    boardroom_none_pending = narrator.narrate("boardroom_intro", pending_departments=[])
    check("boardroom_intro (all done) doesn't claim anything is still pending", "still" not in boardroom_none_pending.lower())
    boardroom_pending = narrator.narrate("boardroom_intro", pending_departments=["Film Department"])
    check("boardroom_intro (real pending dept) names it honestly", "Film Department" in boardroom_pending)

    dept_line = narrator.narrate("department_moment", dept_label="Art Department", status_line="2 pieces ready for your review", rating=5)
    check("department_moment uses the real status_line verbatim", "2 pieces ready for your review" in dept_line)
    check("department_moment uses the real rating, not a placeholder", "5 of 5" in dept_line)

    # A moment function called with missing required args must fail closed
    # (None), never render a broken half-sentence.
    check("missing required args return None, not a broken string", narrator.narrate("department_moment") is None)

    check("known_moments() lists every registered moment", "welcome" in narrator.known_moments() and "boardroom_intro" in narrator.known_moments())

    # ── Voice synthesis graceful degrade (no ELEVENLABS_API_KEY in this env) ──
    check("voice.is_available() is False without an API key", sage_voice.is_available() is False)
    check("synthesize() returns None rather than raising without a key", sage_voice.synthesize("Hello, founder.") is None)
    check("synthesize() returns None for blank text", sage_voice.synthesize("") is None)

    # ── History: guidance moments only, never raw chat ───────────────────────
    orig_path = history.HISTORY_PATH
    try:
        with tempfile.TemporaryDirectory() as tmp:
            history.HISTORY_PATH = Path(tmp) / "history.json"
            check("history starts empty", history.list_history() == [])
            entry = history.append_moment("welcome", "Test transcript.", "Fire & Flow Gospel")
            check("append_moment records moment/transcript/context/timestamp", all(k in entry for k in ("moment", "transcript", "context_summary", "spoken_at")))
            check("get_last returns the most recent entry", history.get_last()["transcript"] == "Test transcript.")
            history.append_moment("step_artist", "Second.", "")
            check("list_history preserves order (oldest first)", [e["moment"] for e in history.list_history()] == ["welcome", "step_artist"])
    finally:
        history.HISTORY_PATH = orig_path

    # ── Prefs: mute persists to disk, not just session state ─────────────────
    orig_prefs_path = prefs.PREFS_PATH
    try:
        with tempfile.TemporaryDirectory() as tmp:
            prefs.PREFS_PATH = Path(tmp) / "sage_prefs.json"
            check("mute defaults to False", prefs.is_muted() is False)
            prefs.set_muted(True)
            check("set_muted(True) persists", prefs.is_muted() is True)
            prefs.set_muted(False)
            check("set_muted(False) persists", prefs.is_muted() is False)
    finally:
        prefs.PREFS_PATH = orig_prefs_path

    print()
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"{passed}/{total} checks passed")
    return passed == total


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
