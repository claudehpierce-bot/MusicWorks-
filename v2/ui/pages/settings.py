"""MusicWorks™ V3 — Settings page."""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html


def render():
    page_header("Settings", "Configure your MusicWorks™ environment.", "⚙")

    try:
        from config import ANTHROPIC_API_KEY, MOCK_MODE, CLAUDE_MODEL, DB_PATH
        has_key = bool(ANTHROPIC_API_KEY)
    except ImportError:
        has_key = False
        MOCK_MODE = True
        CLAUDE_MODEL = "claude-sonnet-4-6"
        DB_PATH = "musicworks.db"

    # ── API Status ────────────────────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>API Configuration</div>", unsafe_allow_html=True)

    if has_key:
        st.markdown('<div class="mw-card" style="padding:1rem 1.5rem;border-left:3px solid #22C55E;"><div style="display:flex;align-items:center;gap:10px;"><div style="font-size:20px;">✓</div><div><div style="font-size:14px;font-weight:600;color:#22C55E;">Anthropic API Key Connected</div><div style="font-size:12px;color:#8A8480;margin-top:2px;">Real agent mode available. Agents will call Claude.</div></div></div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="mw-card" style="padding:1rem 1.5rem;border-left:3px solid #F59E0B;"><div style="display:flex;align-items:center;gap:10px;"><div style="font-size:20px;">⚠</div><div><div style="font-size:14px;font-weight:600;color:#F59E0B;">No Anthropic API Key</div><div style="font-size:12px;color:#8A8480;margin-top:2px;">Mock Mode is active. Create a <code>.env</code> file in the v2/ folder with <code>ANTHROPIC_API_KEY=your_key_here</code> to enable real agents.</div></div></div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── System Status ─────────────────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>System Status</div>", unsafe_allow_html=True)

    status_rows = [
        ("Claude Model", CLAUDE_MODEL, "The AI model powering all agents."),
        ("Mock Mode", "Active" if MOCK_MODE else "Off", "When On, no API calls are made — uses sample data."),
        ("Database", str(DB_PATH), "SQLite database storing all asset records and approval logs."),
        ("Assets Location", "v2/assets/", "Generated assets are stored here, organized by campaign."),
        ("Artist Library", "v2/data/artists/", "Brand Brain JSON files for each artist."),
        ("Song Library", "v2/data/songs/", "Song input JSON files for each project."),
    ]

    rows_html = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:1rem;padding:10px 0;border-bottom:1px solid #1E1E1E;">'
        f'<div style="min-width:180px;font-size:13px;color:#F0EDE8;font-weight:500;">{label}</div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:12px;color:#D4A853;font-family:monospace;">{value}</div>'
        f'<div style="font-size:11px;color:#6A6460;margin-top:2px;">{desc}</div>'
        f'</div></div>'
        for label, value, desc in status_rows
    )
    st.markdown(f'<div class="mw-card" style="padding:0.5rem 1.5rem;">{rows_html}</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Instructions ──────────────────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>Quick Start</div>", unsafe_allow_html=True)
    render_html("""
    <div class="mw-card" style="padding:1.5rem;">
    <div style="font-size:13px;color:#C8C4BE;line-height:1.8;">
    <div style="margin-bottom:0.75rem;font-weight:600;color:#F0EDE8;">To run MusicWorks™ V3 Executive Interface:</div>
    <div style="font-family:monospace;background:#0A0A0A;padding:0.75rem 1rem;border-radius:8px;border:1px solid #333;font-size:12px;color:#D4A853;margin-bottom:1rem;">cd C:\\Users\\claud\\musicworks\\v2<br>python -m streamlit run app.py</div>
    <div style="margin-bottom:0.75rem;font-weight:600;color:#F0EDE8;">To run in mock mode (no API key required):</div>
    <div style="font-family:monospace;background:#0A0A0A;padding:0.75rem 1rem;border-radius:8px;border:1px solid #333;font-size:12px;color:#D4A853;margin-bottom:1rem;">MOCK_MODE=true python -m streamlit run app.py</div>
    <div style="margin-bottom:0.75rem;font-weight:600;color:#F0EDE8;">To run the CLI campaign runner directly:</div>
    <div style="font-family:monospace;background:#0A0A0A;padding:0.75rem 1rem;border-radius:8px;border:1px solid #333;font-size:12px;color:#D4A853;">python main.py --song data/songs/hlangana.json --mode blitz --mock</div>
    </div>
    </div>
    """)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Version info ──────────────────────────────────────────────────────────
    st.markdown('<div style="text-align:center;padding:1.5rem;border-top:1px solid #1E1E1E;margin-top:1rem;"><div style="font-size:13px;color:#8A8480;margin-bottom:4px;">MindSpark MusicWorks™ V3 Executive Interface</div><div style="font-size:12px;color:#6A6460;">Human-led. AI-assisted. Scripture-rooted.</div></div>', unsafe_allow_html=True)
