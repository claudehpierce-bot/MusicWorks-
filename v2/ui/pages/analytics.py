"""MusicWorks™ V3 — Analytics page (live campaign output summary + V3 roadmap preview)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html, navigate_to


def render():
    page_header("Analytics", "Campaign performance and ministry metrics.", "📊")

    from brand_brain.artist_library import list_artists

    artists = list_artists()
    if not artists:
        render_html("""
        <div class="mw-card" style="text-align:center;padding:2rem;color:#8A8480;">
            <div style="font-size:16px;color:#F0EDE8;margin-bottom:0.5rem;">No artists yet</div>
            <div style="font-size:13px;">Create an artist profile and launch a campaign to see your results here.</div>
        </div>
        """)
        if st.button("👥  Add Artist", type="primary", key="an_add_artist"):
            navigate_to("artists")
        return

    names = [a["artist_name"] for a in artists]
    ids   = [a["artist_id"]   for a in artists]
    sel   = st.selectbox("Artist:", range(len(names)),
                         format_func=lambda i: names[i], key="an_artist_sel")
    sel_id = ids[sel]

    _campaign_output_summary(sel_id)

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mw-section-label'>What's next for Results</div>", unsafe_allow_html=True)
    st.caption("Live audience metrics — streams, views, followers, engagement — connect once MusicWorks links to Spotify for Artists, YouTube Analytics, and Meta Business Suite.")

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


def _campaign_output_summary(artist_id: str):
    """Real numbers pulled from the same production-queue source Asset Review uses."""
    from execution.production_queue import list_jobs, queue_stats

    all_jobs = list_jobs(artist_id)
    stats = queue_stats(artist_id)
    total = stats.get("total", 0)

    if total == 0:
        render_html("""
        <div class="mw-card" style="text-align:center;padding:2rem;color:#8A8480;">
            <div style="font-size:16px;color:#F0EDE8;margin-bottom:0.5rem;">No campaign output yet</div>
            <div style="font-size:13px;">Launch a media campaign to see what MusicWorks has built for you.</div>
        </div>
        """)
        if st.button("🚀  Launch a Media Campaign", type="primary", key="an_launch"):
            st.session_state.wizard_step = 0
            st.session_state.wizard_data = {}
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("wizard")
        return

    approved  = stats.get("approved", 0)
    published = stats.get("published", 0)
    review    = stats.get("review", 0)
    approval_rate = round(approved / total * 100) if total else 0

    render_html("<div class='mw-section-label'>Campaign Output Summary</div>")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Assets", total)
    s2.metric("Approved", approved)
    s3.metric("Published", published)
    s4.metric("Approval Rate", f"{approval_rate}%")

    if review > 0:
        st.info(f"{review} asset(s) waiting for your review.")
        if st.button("✅  Open Asset Review", type="primary", key="an_open_review"):
            navigate_to("approval")

    # ── Breakdown by platform ───────────────────────────────────────────────
    by_platform: dict[str, list[dict]] = {}
    for j in all_jobs:
        by_platform.setdefault(j.get("platform", "other"), []).append(j)

    render_html("<div style='margin-top:1.5rem;'></div>")
    render_html("<div class='mw-section-label'>What MusicWorks built, by platform</div>")

    rows = ""
    for platform, jobs in sorted(by_platform.items(), key=lambda kv: -len(kv[1])):
        icon = jobs[0].get("job_icon", "📄")
        rows += f"""
        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:1px solid #1E1E1E;">
            <div style="font-size:13px; color:#F0EDE8;">{icon} {platform.title()}</div>
            <div style="font-size:13px; color:#8A8480;">{len(jobs)} asset{'s' if len(jobs) != 1 else ''}</div>
        </div>
        """
    render_html(f"""<div class="mw-card" style="padding:1.25rem;">{rows}</div>""")


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
