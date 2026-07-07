"""MusicWorks™ V3 — Settings page."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html, navigate_to


def render():
    page_header("Settings", "Configure your MusicWorks™ environment.", "⚙")

    # ── Provider Connections ─────────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>Connections</div>", unsafe_allow_html=True)
    try:
        from execution.provider_registry import PROVIDERS
        from execution.provider_router import is_available
        connected_n = sum(1 for p in PROVIDERS if p.requires_api_key and is_available(p.key))
        total_n = len(PROVIDERS)
    except Exception:
        connected_n, total_n = 0, 0

    render_html(f"""
    <div class="mw-card" style="padding:1rem 1.5rem; border-left:3px solid #9B89D4; margin-bottom:0.75rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.75rem;">
            <div>
                <div style="font-size:14px; font-weight:700; color:#F0EDE8;">🔌 Creative Engine Connections</div>
                <div style="font-size:12px; color:#8A8480; margin-top:2px;">
                    {connected_n} of {total_n} creative engines connected — manage connections
                    and see live status for everything MusicWorks can call on.
                </div>
            </div>
        </div>
    </div>
    """)
    if st.button("🔌  Open Connections →", key="settings_open_connections", type="primary"):
        navigate_to("connections")

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    try:
        from config import ANTHROPIC_API_KEY
        has_key = bool(ANTHROPIC_API_KEY)
    except ImportError:
        has_key = False

    # ── Creative Engine status ───────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>Content Generation</div>", unsafe_allow_html=True)

    if has_key:
        render_html("""
        <div class="mw-card" style="padding:1rem 1.5rem;border-left:3px solid #22C55E;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="font-size:20px;">✓</div>
                <div>
                    <div style="font-size:14px;font-weight:600;color:#22C55E;">Your Creative Engines are connected</div>
                    <div style="font-size:12px;color:#8A8480;margin-top:2px;">MusicWorks will generate real content for your campaigns.</div>
                </div>
            </div>
        </div>
        """)
    else:
        render_html("""
        <div class="mw-card" style="padding:1rem 1.5rem;border-left:3px solid #F59E0B;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="font-size:20px;">✨</div>
                <div>
                    <div style="font-size:14px;font-weight:600;color:#F59E0B;">Using sample content for now</div>
                    <div style="font-size:12px;color:#8A8480;margin-top:2px;">Connect a Creative Engine to start generating real campaign assets.</div>
                </div>
            </div>
        </div>
        """)
        if st.button("🔌  Connect a Creative Engine →", key="settings_connect_engine"):
            navigate_to("connections")

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Your workspace ────────────────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>Your Workspace</div>", unsafe_allow_html=True)

    try:
        from brand_brain.artist_library import list_artists
        artist_count = len(list_artists())
    except Exception:
        artist_count = 0

    try:
        songs_dir = Path(__file__).parent.parent.parent / "data" / "songs"
        song_count = len(list(songs_dir.glob("*.json"))) if songs_dir.exists() else 0
    except Exception:
        song_count = 0

    workspace_rows = [
        ("Artists", str(artist_count), "Artist profiles you've set up."),
        ("Songs", str(song_count), "Creative Masters you've uploaded."),
    ]
    rows_html = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:1rem;padding:10px 0;border-bottom:1px solid #1E1E1E;">'
        f'<div style="min-width:120px;font-size:13px;color:#F0EDE8;font-weight:500;">{label}</div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:14px;color:#D4A853;font-weight:600;">{value}</div>'
        f'<div style="font-size:11px;color:#6A6460;margin-top:2px;">{desc}</div>'
        f'</div></div>'
        for label, value, desc in workspace_rows
    )
    st.markdown(f'<div class="mw-card" style="padding:0.5rem 1.5rem;">{rows_html}</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Version info ──────────────────────────────────────────────────────────
    st.markdown('<div style="text-align:center;padding:1.5rem;border-top:1px solid #1E1E1E;margin-top:1rem;"><div style="font-size:13px;color:#8A8480;margin-bottom:4px;">MindSpark MusicWorks™</div><div style="font-size:12px;color:#6A6460;">Human-led. AI-assisted. Scripture-rooted.</div></div>', unsafe_allow_html=True)
