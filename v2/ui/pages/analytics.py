"""MusicWorks™ V3 — Analytics page (V3 roadmap preview)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html


def render():
    page_header("Analytics", "Campaign performance and ministry metrics.", "📊")

    render_html("""
    <div style="background:linear-gradient(135deg, #1A0F42, #2D1B69);
                border:1px solid rgba(212,168,83,0.2); border-radius:16px;
                padding:2.5rem; text-align:center; margin-bottom:2rem;">
        <div style="font-size:36px; margin-bottom:0.75rem;">📊</div>
        <div style="font-size:20px; font-weight:700; color:#F0EDE8; margin-bottom:0.5rem;">
            Analytics Dashboard
        </div>
        <div style="font-size:14px; color:#9B89D4; margin-bottom:1rem;">
            Live campaign metrics arriving in V3
        </div>
        <span class="badge badge-revision">Coming in V3</span>
    </div>
    """)

    # ── Preview of what's coming ───────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>What you'll track in V3</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        _preview_card("Commercial Metrics", [
            ("🎵", "Streams", "Spotify, Apple Music, YouTube Music"),
            ("▶️", "Video Views", "Reels, Shorts, TikTok combined"),
            ("👥", "Followers", "New followers per platform per week"),
            ("❤️", "Engagement Rate", "Likes + saves + shares ÷ impressions"),
            ("💬", "Comments", "Sentiment tracking + scripture mentions"),
            ("🔁", "Shares", "Platform-by-platform share velocity"),
        ])

    with col_b:
        _preview_card("Ministry Metrics", [
            ("📖", "Devotional Downloads", "Free guide downloads per campaign"),
            ("⛪", "Church Outreach", "Pastoral inquiry volume"),
            ("🌍", "Diaspora Reach", "UK, Africa, Caribbean impression split"),
            ("🔤", "Word Recognition", "Kingdom Words vocabulary retention"),
            ("🙏", "Prayer Requests", "Inbound ministry contact volume"),
            ("📝", "Email Subscribers", "List growth from devotional offers"),
        ])

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    _preview_card("Campaign Health Score (0-100)", [
        ("✅", "Approval Rate", "% of assets approved without revision"),
        ("⚡", "Launch Velocity", "First 48-hour stream + engagement total"),
        ("📅", "Calendar Adherence", "% of posts published within 30 min of schedule"),
        ("🎯", "Goal Achievement", "Campaign goal vs. actual outcome"),
        ("📈", "Benchmark vs. Industry", "Afro-Gospel average stream benchmarks"),
    ])

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    st.caption("V3 Analytics will connect to Spotify for Artists API, YouTube Analytics, and Meta Business Suite. Manual data entry available in V2.")


def _preview_card(title: str, items: list):
    rows = ""
    for icon, label, desc in items:
        rows += f"""
        <div style="display:flex; align-items:flex-start; gap:10px; padding:8px 0;
                    border-bottom:1px solid #1E1E1E;">
            <span style="font-size:16px; min-width:22px;">{icon}</span>
            <div>
                <div style="font-size:13px; color:#F0EDE8; font-weight:500;">{label}</div>
                <div style="font-size:11px; color:#8A8480;">{desc}</div>
            </div>
        </div>
        """
    render_html(f"""
    <div class="mw-card" style="padding:1.25rem; margin-bottom:1rem;">
        <div style="font-size:11px; font-weight:600; color:#8A8480; letter-spacing:0.8px;
                    text-transform:uppercase; margin-bottom:0.75rem;">{title}</div>
        {rows}
    </div>
    """)
