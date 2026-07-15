"""MusicWorks™ — Sage Presence™ UI component.

DS-1 / SAGE_PERSONA.md compliant: Sage's portrait is always static (no
facial or lip animation — this is a governance rule, not a shortcut).
Presence comes from light, waveform, voice, transcript, and calm movement
around her, never from the portrait itself. The only founder controls are
Mute/Unmute and Repeat Last Guidance — there is deliberately no Play or
Replay button; audio begins naturally with the moment when unmuted and
available, exactly once per moment, and transcript is always shown
regardless of audio state.

This is the one place in the app that renders Sage. Every page that wants
her presence calls render_moment(); nothing else touches her avatar,
narration, or voice directly (no parallel truth).
"""
import base64

import streamlit as st

from execution.brand_asset_registry import AssetNotFoundError, get_asset_metadata, get_derivative_path
from execution.sage import history, narrator, prefs
from execution.sage import voice as sage_voice
from ui.components import render_html


def _is_muted() -> bool:
    if "sage_muted" not in st.session_state:
        st.session_state.sage_muted = prefs.is_muted()
    return st.session_state.sage_muted


def _toggle_mute():
    new_val = not _is_muted()
    st.session_state.sage_muted = new_val
    prefs.set_muted(new_val)


# ── First-arrival playback fix ───────────────────────────────────────────────
#
# Browsers block audio autoplay until the page has seen a real user gesture.
# The very first script execution of a session (Home, before any click) can
# never reliably play sound -- no gesture has happened yet. Every execution
# after that one is, by construction, the result of a widget interaction (a
# click) or an st.rerun() called from inside one; Streamlit has no "passive"
# reruns of its own. So "has at least one prior execution completed" is
# exactly the signal for "a real interaction has now happened."
#
# begin_script_run() must be called once, at the very top of app.py, before
# any page renders. It marks whether this execution is the first one, and if
# not, catches up whichever Sage moment was left pending from before -- this
# is the entire mechanism; no general event system, just one deferred slot.

def begin_script_run():
    """Call once per script execution, before any page content renders."""
    had_prior_run = "sage_run_marker" in st.session_state
    st.session_state["sage_run_marker"] = True
    st.session_state["sage_had_interaction"] = had_prior_run
    st.session_state["sage_audio_slot_used_this_run"] = False
    if had_prior_run:
        _catch_up_pending_greeting()


def _catch_up_pending_greeting():
    """If a moment was queued because no interaction had happened yet, and
    a real interaction has now occurred, speak it -- once, here, before the
    destination page renders its own moment. Muted founders never had
    anything queued in the first place (render_moment() only queues when
    unmuted), so there's nothing to silently play here."""
    pending = st.session_state.pop("sage_pending_first_greeting", None)
    if not pending or _is_muted():
        return
    audio_bytes = sage_voice.synthesize(pending["transcript"])
    if audio_bytes:
        render_html(_autoplay_audio_html(audio_bytes))
        st.session_state["sage_audio_slot_used_this_run"] = True
        st.session_state["sage_last_played_message_id"] = pending["key"]
        if pending["key"] == "home_welcome":
            st.session_state["sage_first_greeting_played"] = True


def avatar_html(variant: str = "avatar_square", width: int = 64) -> str:
    """The one accessible way to render Sage's avatar anywhere in the app.

    st.image() in this Streamlit version has no `alt` parameter -- it emits
    alt="0" by default, which fails real accessibility requirements. This
    renders a plain <img> instead, with alt text sourced from the governed
    accessibility_description in the asset registry (never a filename, per
    that registry's own test suite). Returns "" if the asset can't resolve
    -- callers simply render nothing rather than a broken image.
    """
    try:
        path = get_derivative_path("SAGE-AVATAR-1", variant)
        meta = get_asset_metadata("SAGE-AVATAR-1")
    except AssetNotFoundError:
        return ""
    alt = meta.get("accessibility_description", "Sage, MindSpark Labs' institutional guide")
    ext = path.suffix.lstrip(".") or "webp"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img src="data:image/{ext};base64,{b64}" width="{width}" alt="{alt}" style="border-radius:8px;display:block;">'


# ── DS-1: restrained motion only, and only while actually speaking.
# Reduced-motion is respected via the media query -- the bars fall back to
# a static height with no @keyframes applied at all when the founder's OS
# requests less motion, not just a slower version of the same animation.
_WAVEFORM_CSS = """
<style>
.sage-waveform { display: flex; align-items: center; gap: 3px; height: 20px; margin: 6px 0; }
.sage-waveform-bar {
  width: 3px; border-radius: 2px; background: #D4A853; height: 60%;
  transform-origin: center;
}
@media (prefers-reduced-motion: no-preference) {
  .sage-waveform-bar { animation: sage-wave 1.1s ease-in-out infinite; height: 100%; }
}
@keyframes sage-wave {
  0%, 100% { transform: scaleY(0.35); }
  50% { transform: scaleY(1); }
}
</style>
"""


def _waveform_html() -> str:
    delays = [0.0, 0.15, 0.3, 0.1, 0.25, 0.05, 0.2]
    bars = "".join(f'<div class="sage-waveform-bar" style="animation-delay:{d}s;"></div>' for d in delays)
    return f'<div class="sage-waveform">{bars}</div>'


def _autoplay_audio_html(audio_bytes: bytes) -> str:
    """Raw <audio autoplay>, no visible controls -- the browser's native play
    button must never appear; Mute/Repeat are the only sanctioned controls."""
    b64 = base64.b64encode(audio_bytes).decode("ascii")
    return f'<audio autoplay style="display:none;"><source src="data:audio/mpeg;base64,{b64}"></audio>'


def render_moment(moment: str, key: str, context_summary: str = "", **context) -> bool:
    """Render Sage's presence card for one narrated moment.

    `key` must uniquely identify this occurrence (e.g.
    "wizard_step_artist", f"boardroom_intro_{campaign_id}") so revisiting
    the same spot in a session doesn't re-narrate or re-speak it -- per
    SAGE_PERSONA.md's Conversation Rhythm, she becomes quiet after saying
    something once; Repeat Last Guidance is the only way to hear it again.

    Returns True if Sage had real institutional state to narrate and
    something was rendered; False if she stayed silent (nothing invented).
    """
    transcript = narrator.narrate(moment, **context)
    if not transcript:
        return False

    seen = st.session_state.setdefault("sage_seen_moments", set())
    is_first_time = key not in seen
    if is_first_time:
        seen.add(key)
        history.append_moment(moment, transcript, context_summary)

    repeat_flag = f"sage_repeat_{key}"
    should_speak_audio = is_first_time or st.session_state.pop(repeat_flag, False)

    muted = _is_muted()
    # First-arrival fix: only actually attempt audio once a real interaction
    # has happened in this session, and only if no other moment already used
    # this run's one audio turn (see begin_script_run() / _catch_up_pending_
    # greeting() above). Otherwise this moment is held as the pending one,
    # to be spoken the instant an interaction occurs -- never lost, never
    # played into a browser autoplay block, never overlapping another.
    had_interaction = st.session_state.get("sage_had_interaction", False)
    slot_used = st.session_state.get("sage_audio_slot_used_this_run", False)
    can_use_audio_slot = should_speak_audio and not muted and had_interaction and not slot_used

    audio_bytes = None
    if can_use_audio_slot:
        audio_bytes = sage_voice.synthesize(transcript)
        if audio_bytes:
            st.session_state["sage_audio_slot_used_this_run"] = True
            st.session_state["sage_last_played_message_id"] = key
            if key == "home_welcome":
                st.session_state["sage_first_greeting_played"] = True
    elif should_speak_audio and not muted:
        st.session_state.setdefault("sage_pending_first_greeting", {"key": key, "transcript": transcript})

    st.markdown(_WAVEFORM_CSS, unsafe_allow_html=True)

    with st.container(key=f"sage_card_{key}"):
        col_a, col_b = st.columns([1, 5])
        with col_a:
            render_html(avatar_html("avatar_square", width=64))
        with col_b:
            render_html(
                '<div style="font-size:10px;color:#D4A853;font-weight:600;letter-spacing:0.8px;'
                'text-transform:uppercase;margin-bottom:4px;">Sage · Institutional Guide</div>'
            )
            if audio_bytes:
                render_html(_waveform_html())
                render_html(_autoplay_audio_html(audio_bytes))
            render_html(f'<div style="font-size:14px;color:#F0EDE8;line-height:1.7;">{transcript}</div>')

        c1, c2 = st.columns([1, 1])
        with c1:
            label = "🔇 Unmute Sage" if muted else "🔈 Mute Sage"
            if st.button(label, key=f"sage_mute_{key}"):
                _toggle_mute()
                st.rerun()
        with c2:
            if st.button("↺ Repeat Last Guidance", key=f"sage_repeat_btn_{key}"):
                st.session_state[repeat_flag] = True
                st.rerun()

    return True


def render_history_panel(key: str = "sage_history_default", limit: int = 15):
    """Compact, collapsed-by-default Conversation History -- institutional
    guidance moments only, never raw chat (per the milestone's explicit
    'do not build unrestricted chat')."""
    entries = list(reversed(history.list_history()))[:limit]
    with st.expander(f"📖 Conversation History ({len(entries)})", expanded=False):
        if not entries:
            st.caption("Nothing yet — Sage's guidance moments will appear here as you work.")
            return
        for entry in entries:
            when = entry.get("spoken_at", "")[:16].replace("T", " ")
            ctx = entry.get("context_summary", "")
            label = f"{when} — {ctx}" if ctx else when
            st.caption(label)
            st.markdown(f"<div style='font-size:13px;color:#C8C4BE;margin-bottom:0.75rem;'>{entry.get('transcript','')}</div>", unsafe_allow_html=True)
