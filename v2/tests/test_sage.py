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

    # ── Circular import guard ────────────────────────────────────────────────
    # ui.sage imports ui.components (for render_html) at module level. If
    # ui.components ever imports ui.sage back, Python can hand a caller a
    # partially-initialized ui.sage module depending on import order -- this
    # is exactly what took production down (Cloud diagnostic showed
    # ui.sage.__file__ correct but begin_script_run() absent). Both
    # orderings must produce a fully initialized module, and the source
    # itself must never reintroduce the back-edge.
    import re as _re
    components_src = (Path(__file__).parent.parent / "ui" / "components.py").read_text(encoding="utf-8")
    check(
        "ui/components.py contains no import of ui.sage",
        not _re.search(r"import\s+ui\.sage\b|from\s+ui\.sage\s+import", components_src),
    )

    for mod in ("ui.sage", "ui.components"):
        sys.modules.pop(mod, None)
    import ui.sage as _sage_order_a
    import ui.components as _components_order_a
    check("ui.sage imported before ui.components is fully initialized", hasattr(_sage_order_a, "begin_script_run"))

    for mod in ("ui.sage", "ui.components"):
        sys.modules.pop(mod, None)
    import ui.components as _components_order_b
    import ui.sage as _sage_order_b
    check("ui.components imported before ui.sage is fully initialized", hasattr(_sage_order_b, "begin_script_run"))

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

    # ── First-arrival playback fix: state-machine correctness ────────────────
    # Real audio can't be exercised here (no ElevenLabs key in this dev
    # environment), so sage_voice.synthesize is monkeypatched to return
    # deterministic fake bytes -- what's under test is the queue/catch-up
    # logic in ui/sage.py, not the network call itself (already covered above).
    import streamlit as st
    import ui.sage as sage
    from execution.sage import voice as sage_voice_mod

    def _reset_session():
        for k in list(st.session_state.keys()):
            if k.startswith("sage_"):
                del st.session_state[k]

    orig_synthesize = sage_voice_mod.synthesize
    sage_voice_mod.synthesize = lambda text, voice_standard="SVS-1": b"FAKE_AUDIO_BYTES"
    orig_history_path = history.HISTORY_PATH
    history_tmpdir = tempfile.TemporaryDirectory()
    history.HISTORY_PATH = Path(history_tmpdir.name) / "history.json"
    try:
        # Execution 1: fresh session, first render, welcome wants to speak.
        _reset_session()
        sage.begin_script_run()
        check("execution 1 is not treated as an interaction", st.session_state.get("sage_had_interaction") is False)
        rendered = sage.render_moment("welcome", key="home_welcome", artist_name="Fire & Flow Gospel", draft_title=None, draft_step_label=None)
        check("welcome still renders (transcript) on execution 1", rendered is True)
        check("welcome's audio is queued, not played, before any interaction",
              st.session_state.get("sage_pending_first_greeting", {}).get("key") == "home_welcome")
        check("first_greeting_played is not set yet", not st.session_state.get("sage_first_greeting_played"))

        # Execution 2: a real interaction happens (e.g. clicking Launch
        # Campaign) -- begin_script_run() should catch the pending welcome
        # up before the destination page renders its own moment.
        sage.begin_script_run()
        check("execution 2 is treated as a real interaction", st.session_state.get("sage_had_interaction") is True)
        check("pending welcome was consumed by catch-up", "sage_pending_first_greeting" not in st.session_state)
        check("first_greeting_played is now set", st.session_state.get("sage_first_greeting_played") is True)
        check("catch-up used this run's one audio slot", st.session_state.get("sage_audio_slot_used_this_run") is True)

        # The destination page's own moment (e.g. Wizard step_artist) also
        # wants to speak this same run -- it must NOT overlap the welcome;
        # it should be held as the new pending moment instead.
        sage.render_moment("step_artist", key="wizard_step_artist")
        check("a second moment in the same run doesn't overlap the catch-up",
              st.session_state.get("sage_pending_first_greeting", {}).get("key") == "wizard_step_artist")

        # Execution 3: next interaction -- the deferred step_artist moment
        # gets its turn, with no welcome left to compete with.
        sage.begin_script_run()
        check("the deferred second moment gets caught up on the next interaction",
              st.session_state.get("sage_last_played_message_id") == "wizard_step_artist")

        # Muted session: nothing should ever be queued.
        _reset_session()
        sage.begin_script_run()
        sage._toggle_mute()  # mutes
        sage.render_moment("welcome", key="home_welcome", artist_name="Fire & Flow Gospel", draft_title=None, draft_step_label=None)
        check("muted session never queues a pending greeting", "sage_pending_first_greeting" not in st.session_state)
        sage._toggle_mute()  # restore unmuted for any later tests reusing prefs
    finally:
        sage_voice_mod.synthesize = orig_synthesize
        history.HISTORY_PATH = orig_history_path
        history_tmpdir.cleanup()
        _reset_session()

    print()
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"{passed}/{total} checks passed")
    return passed == total


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
