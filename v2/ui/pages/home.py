"""MusicWorks™ V3 — Executive Dashboard (Home)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from datetime import datetime
from ui.components import countdown_days, navigate_to, progress_bar_html, status_badge, render_html


def _new_project():
    st.session_state.wizard_step = 0
    st.session_state.wizard_data = {}
    st.session_state.pop("wizard_campaign_id", None)
    navigate_to("wizard")


def render():
    # ── Greeting ──────────────────────────────────────────────────────────────
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

    st.markdown(
        f"""<div style="margin-bottom:1.5rem;">
            <h1 style="margin:0 0 4px 0;">{greeting}, Founder</h1>
            <p style="color:#8A8480; font-size:15px; margin:0;">
                MusicWorks™ is ready. Here's where things stand.
            </p>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Load data ─────────────────────────────────────────────────────────────
    try:
        from execution.asset_library import AssetLibrary
        lib = AssetLibrary()
        campaign_ids = lib.get_all_campaign_ids()
        active_campaign = campaign_ids[-1] if campaign_ids else None
        stats = lib.get_campaign_stats(active_campaign) if active_campaign else {"total": 0, "approved": 0, "pending": 0, "rejected": 0, "all_approved": False}
        log = lib.get_approval_log(active_campaign) if active_campaign else []
    except Exception:
        stats = {"total": 0, "approved": 0, "pending": 0, "rejected": 0, "all_approved": False}
        campaign_ids = []
        active_campaign = None
        log = []

    # ── Determine active song context ─────────────────────────────────────────
    # Try to load active song from data
    song_title = "HLANGANA"
    song_subtitle = "Zulu · Gather Together · Hebrews 10:25"
    artist_name = "Fire & Flow Gospel"
    album = "Becoming Vol. 1"
    release_date = "2026-07-03"

    if active_campaign:
        try:
            import json
            from pathlib import Path as _Path
            songs_dir = _Path(__file__).parent.parent.parent / "data" / "songs"
            song_files = list(songs_dir.glob("*.json"))
            if song_files:
                latest = sorted(song_files, key=lambda f: f.stat().st_mtime)[-1]
                s = json.loads(latest.read_text(encoding="utf-8"))
                song_title = s.get("title", song_title)
                song_subtitle = f"{s.get('title_language', '')} · {s.get('title_meaning', '')} · {s.get('scripture_primary', '')}".strip(" · ")
                artist_name = s.get("artist_name", artist_name)
                album = s.get("album_title", album)
                release_date = s.get("release_date", release_date)
        except Exception:
            pass

    days_left = countdown_days(release_date)
    if days_left > 0:
        days_label = f"days until launch"
    elif days_left == 0:
        days_label = "Launch Day!"
    else:
        days_label = f"days since launch"

    total = stats.get("total", 0)
    approved = stats.get("approved", 0)
    pending = stats.get("pending", 0)
    health_pct = (approved / total * 100) if total > 0 else 0

    # ── Hero Card ─────────────────────────────────────────────────────────────
    # Build as a single-line string — no internal newlines so the JS Markdown
    # parser never misreads a closing tag as an indented code block.
    _campaign_label = 'Active Campaign' if active_campaign else 'No campaigns yet'
    _pb = progress_bar_html(health_pct, f"Approval Progress — {health_pct:.0f}%")
    _left = (
        f'<div style="flex:1;min-width:260px;">'
        f'<div style="font-size:11px;color:#D4A853;font-weight:600;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:0.5rem;">{_campaign_label}</div>'
        f'<div style="font-size:30px;font-weight:800;color:#F0EDE8;letter-spacing:-0.5px;line-height:1.1;margin-bottom:4px;">{song_title}</div>'
        f'<div style="font-size:14px;color:#9B89D4;margin-bottom:0.75rem;">{song_subtitle}</div>'
        f'<div style="font-size:13px;color:#8A8480;margin-bottom:0.25rem;">{artist_name}</div>'
        f'<div style="font-size:13px;color:#8A8480;margin-bottom:1.5rem;">{album} · {release_date}</div>'
        f'<div style="display:flex;align-items:baseline;gap:8px;">'
        f'<span style="font-size:44px;font-weight:800;color:#FF6B2B;letter-spacing:-2px;line-height:1;">{abs(days_left)}</span>'
        f'<span style="font-size:14px;color:#8A8480;">{days_label}</span>'
        f'</div></div>'
    )
    _grid = (
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem;">'
        f'<div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.75rem 1rem;"><div style="font-size:22px;font-weight:700;color:#F0EDE8;">{total}</div><div style="font-size:11px;color:#8A8480;">Total Assets</div></div>'
        f'<div style="background:rgba(34,197,94,0.08);border-radius:8px;padding:0.75rem 1rem;"><div style="font-size:22px;font-weight:700;color:#22C55E;">{approved}</div><div style="font-size:11px;color:#8A8480;">Approved</div></div>'
        f'<div style="background:rgba(245,158,11,0.08);border-radius:8px;padding:0.75rem 1rem;"><div style="font-size:22px;font-weight:700;color:#F59E0B;">{pending}</div><div style="font-size:11px;color:#8A8480;">Pending</div></div>'
        f'<div style="background:rgba(255,107,43,0.08);border-radius:8px;padding:0.75rem 1rem;"><div style="font-size:22px;font-weight:700;color:#FF6B2B;">{len(campaign_ids)}</div><div style="font-size:11px;color:#8A8480;">Campaigns</div></div>'
        f'</div>'
    )
    _right = (
        f'<div style="flex:1;min-width:220px;">'
        f'<div style="font-size:11px;color:#8A8480;font-weight:600;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:1rem;">Campaign Health</div>'
        f'{_grid}{_pb}'
        f'</div>'
    )
    st.markdown(
        f'<div class="mw-hero"><div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:2rem;">{_left}{_right}</div></div>',
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        if st.button("➕  New Project", type="primary", use_container_width=True):
            _new_project()
    with col_b:
        if st.button("🚀  Build Campaign", type="secondary", use_container_width=True):
            if active_campaign:
                # Go to wizard at Build step with existing campaign context
                navigate_to("wizard")
            else:
                _new_project()
    with col_c:
        if st.button("✅  Approval Queue", type="secondary", use_container_width=True):
            if active_campaign:
                st.session_state.approval_campaign_id = active_campaign
            navigate_to("approval")

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Metrics row ───────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Assets", total)
    m2.metric("Approved", approved)
    m3.metric("Pending Approval", pending)
    m4.metric("Active Campaigns", len(campaign_ids))

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Content Calendar + Quick Actions ─────────────────────────────────────
    left, right = st.columns([1.5, 1])

    with left:
        st.markdown("<div class='mw-section-label'>Content Calendar</div>", unsafe_allow_html=True)
        calendar = [
            ("Jul 3", "8:30 AM", "Instagram Reels", "HLANGANA launch video"),
            ("Jul 3", "8:30 AM", "YouTube Shorts",  "HLANGANA launch video"),
            ("Jul 3", "9:00 AM", "TikTok",          "HLANGANA launch video"),
            ("Jul 3", "10:00 AM","Facebook Reels",  "HLANGANA launch video"),
            ("Jul 5", "8:00 AM", "Blog / Website",  "Devotional blog post"),
            ("Jul 7", "10:00 AM","Media Outreach",  "Press release"),
            ("Jul 10","9:00 AM", "Instagram",       "Behind-the-song"),
        ]
        entries_html = ""
        for date_s, time_s, platform, note in calendar:
            entries_html += f"""
            <div style="display:flex; align-items:flex-start; gap:10px; padding:8px 0;
                        border-bottom:1px solid #1E1E1E;">
                <div style="min-width:36px; font-size:10px; color:#D4A853; font-weight:600;
                            padding-top:2px; white-space:nowrap;">{date_s}</div>
                <div style="min-width:52px; font-size:10px; color:#8A8480;
                            padding-top:2px; white-space:nowrap;">{time_s}</div>
                <div>
                    <div style="font-size:12px; color:#F0EDE8; font-weight:500;">{platform}</div>
                    <div style="font-size:11px; color:#8A8480;">{note}</div>
                </div>
            </div>
            """
        st.markdown(f'<div class="mw-card" style="padding:1rem;">{entries_html}</div>', unsafe_allow_html=True)

    with right:
        st.markdown("<div class='mw-section-label'>Quick Actions</div>", unsafe_allow_html=True)
        actions = [
            ("➕", "New Project", "wizard", True),
            ("👥", "Artist Library", "artists", False),
            ("🎵", "Projects", "projects", False),
            ("✅", "Approval Queue", "approval", False),
            ("🚀", "Publishing", "publishing", False),
            ("🧠", "Brand Brain", "brand_brain", False),
            ("📊", "Analytics", "analytics", False),
        ]
        for icon, label, page, is_primary in actions:
            if st.button(f"{icon}  {label}", key=f"qa_{page}", use_container_width=True,
                         type="primary" if is_primary else "secondary"):
                if page == "wizard":
                    _new_project()
                else:
                    navigate_to(page)

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Recent Activity ───────────────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>Recent Activity</div>", unsafe_allow_html=True)

    if log:
        entries_html = ""
        for entry in log[-5:][::-1]:
            decision = entry.get("decision", "")
            desc = entry.get("asset_description", entry.get("asset_id", ""))
            at = entry.get("decision_at", "")
            try:
                dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
                at_fmt = dt.strftime("%b %d at %H:%M UTC")
            except Exception:
                at_fmt = at[:10] if at else ""

            dot_color = {
                "APPROVED": "#22C55E",
                "REJECTED": "#EF4444",
                "REVISION_REQUESTED": "#60A5FA",
            }.get(decision, "#F59E0B")

            entries_html += f"""
            <div class="timeline-entry">
                <div class="timeline-dot" style="background:{dot_color};"></div>
                <div>
                    <div style="font-size:13px; color:#F0EDE8;">{desc}</div>
                    <div style="font-size:11px; color:#8A8480;">{status_badge(decision)} · {at_fmt}</div>
                </div>
            </div>
            """
        st.markdown(f'<div class="mw-card" style="padding:1rem 1.5rem;">{entries_html}</div>', unsafe_allow_html=True)
    else:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:2rem; color:#8A8480;">
            No activity yet. Build your first campaign to see progress here.
        </div>
        """)

    # ── Brand statement ────────────────────────────────────────────────────────
    render_html("""
    <div style="margin-top:2rem; text-align:center; padding:1.5rem; border-top:1px solid #1E1E1E;">
        <div style="font-size:12px; color:#6A6460; letter-spacing:0.3px;">
            Human-led. AI-assisted. Scripture-rooted. Built to spread the Gospel through art.
        </div>
    </div>
    """)
