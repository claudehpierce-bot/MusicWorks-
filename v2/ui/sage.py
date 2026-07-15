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


# ── TEMPORARY -- Sage Voice Diagnostics™. Studio Mode only. Remove this
# whole block (down to the end of _render_voice_diagnostics) once the
# silent-speech root cause is confirmed. Never used in Creator Mode. ───────

_DIAG_CACHE_LABELS = {
    "fresh": "Fresh synthesis",
    "cached": "Cached synthesis",
    "invalidated": "Cache invalidated",
    "bypassed": "Cache bypassed (diagnostic mode)",
    None: "—",
}


def _diag_banner(diag: dict) -> tuple[str, str]:
    """Computed from the stage results, not inferred separately -- one
    banner, one source of truth. Playback (stage 7) can't be known at
    Python-render time (it happens async in the browser after this
    renders), so a successful synthesis reports "generated" here and
    points at the live playback test below for the final word."""
    outcome = diag["final_outcome"]
    if outcome in ("success", "success_cached"):
        return ("🟢", "Audio Generated — confirm playback below ↓")
    if outcome == "missing_secret":
        return ("🔴", "Missing API Key")
    if outcome == "auth_failed":
        return ("🔴", "ElevenLabs Authentication Failed")
    if outcome == "api_rejected":
        return ("🔴", f"ElevenLabs Rejected Request (HTTP {diag.get('http_status')})")
    if outcome == "network_failure":
        return ("🔴", "Network Failure Reaching ElevenLabs")
    if outcome == "empty_audio":
        return ("🔴", "Audio Generation Failed (Empty Response)")
    if outcome == "voice_not_registered":
        return ("🔴", "Voice Standard Not Registered")
    if outcome == "empty_text":
        return ("⚪", "No Transcript To Speak")
    return ("🔴", "Unknown Failure")


def _render_voice_diagnostics(diag: dict, dom_key: str):
    """TEMPORARY -- Studio Mode only. Renders the 9-stage pass/fail report
    plus a live in-browser playback test. Never shows the API key value --
    only booleans, HTTP status, byte counts, duration, and the voice ID
    (not a secret; already public in the governed registry)."""
    emoji, label = _diag_banner(diag)
    with st.expander("🔬 Sage Voice Diagnostics — TEMPORARY, Studio Mode only", expanded=True):
        st.markdown(f"### {emoji} {label}")
        st.caption("Remove this panel once the silent-speech root cause is confirmed.")

        st.markdown(f"**1. Streamlit Secret present:** {'✅ Yes' if diag['secret_present'] else '❌ No'}")
        st.markdown(f"**2. Environment bootstrap:** {'✅ Copied into os.environ' if diag['env_bootstrap'] else '❌ Not in os.environ'}")
        st.markdown(f"**3. Provider availability:** {'✅ Available' if diag['provider_available'] else '❌ Unavailable'}")
        if diag["registry_resolved"]:
            st.markdown(f"**4. Voice registry:** ✅ SVS-1 resolved — provider=`{diag['provider']}`, voice_id=`{diag['voice_id']}`")
        else:
            st.markdown("**4. Voice registry:** ❌ SVS-1 did not resolve")
        if diag["http_attempted"]:
            st.markdown(f"**5. ElevenLabs request:** ✅ Attempted — HTTP `{diag['http_status']}` in `{diag['http_duration_ms']}ms`")
        else:
            st.markdown("**5. ElevenLabs request:** ⏭️ Not attempted (blocked at an earlier stage)")
        st.markdown(f"**6. Response validation:** `{diag['bytes_received']}` bytes received — {'✅ valid audio' if diag['valid_audio'] else '❌ invalid/empty'}")
        st.markdown("**7. Playback:** see live test below ↓" if diag["audio_bytes"] else "**7. Playback:** ⏭️ No audio was generated to test")
        st.markdown(f"**8. Final outcome:** `{diag['final_outcome']}`")
        st.markdown(f"**9. Cache source:** {_DIAG_CACHE_LABELS.get(diag['cache_source'], '—')}")

        if diag["audio_bytes"]:
            st.markdown("---")
            st.caption(
                "Live playback test — a second copy of this clip, self-contained so the "
                "result below is genuinely observed, not assumed. If muted or silent, this "
                "reports it as blocked rather than staying silent about it."
            )
            b64 = base64.b64encode(diag["audio_bytes"]).decode("ascii")
            import streamlit.components.v1 as components
            components.html(
                f"""
                <div id="result" style="font-family:sans-serif;font-size:14px;color:#F0EDE8;
                     background:#141414;padding:10px 14px;border-radius:8px;">⏳ Testing browser playback…</div>
                <audio id="diag-audio" autoplay>
                  <source src="data:audio/mpeg;base64,{b64}">
                </audio>
                <script>
                  var a = document.getElementById("diag-audio");
                  var r = document.getElementById("result");
                  var p = a.play();
                  if (p !== undefined) {{
                    p.then(function() {{
                      r.innerHTML = "🟢 Playback succeeded — the browser allowed autoplay.";
                      r.style.color = "#22C55E";
                    }}).catch(function(err) {{
                      r.innerHTML = "🟡 Playback blocked by the browser: " + err.name + " — " + err.message;
                      r.style.color = "#F59E0B";
                    }});
                  }}
                </script>
                """,
                height=60,
            )

# ── END TEMPORARY Sage Voice Diagnostics block ──────────────────────────────


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
    # TEMPORARY (Sage Voice Diagnostics): in Studio Mode, capture the full
    # diagnostics dict from the same real call Creator Mode makes -- one
    # implementation (_synthesize_core), never a second parallel path.
    studio_mode = bool(st.session_state.get("studio_mode"))
    diag = None
    if should_speak_audio and not muted:
        if studio_mode:
            diag = sage_voice._synthesize_core(transcript)
            audio_bytes = diag["audio_bytes"]
        else:
            audio_bytes = sage_voice.synthesize(transcript)
    else:
        audio_bytes = None

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

    # TEMPORARY (Sage Voice Diagnostics): Studio Mode only, rendered outside
    # the card. Creator Mode never sees `diag` at all (it's None there).
    if diag is not None:
        _render_voice_diagnostics(diag, key)

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
