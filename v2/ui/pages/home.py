"""MusicWorks™ V5 — Founder Home (Creator Mode experience)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from datetime import datetime
from ui.components import countdown_days, navigate_to, progress_bar_html, render_html


def _new_release():
    st.session_state.wizard_step = 0
    st.session_state.wizard_data = {}
    st.session_state.pop("wizard_campaign_id", None)
    navigate_to("wizard")


def _get_last_campaign() -> str | None:
    try:
        from execution.asset_library import AssetLibrary
        lib = AssetLibrary()
        ids = lib.get_all_campaign_ids()
        return ids[-1] if ids else None
    except Exception:
        return None


def _action_card(variant: str, icon: str, title: str, desc: str) -> str:
    desc_color = {
        "release":  "#9B89D4",
        "continue": "#93C5FD",
        "artists":  "#6EC894",
        "library":  "#F59E0B",
        "results":  "#D4A853",
    }.get(variant, "#8A8480")
    return (
        f'<div class="mw-action-card mw-action-card-{variant}">'
        f'<div style="font-size:36px;line-height:1;margin-bottom:0.6rem;">{icon}</div>'
        f'<div style="font-size:19px;font-weight:700;color:#F0EDE8;margin-bottom:0.35rem;">{title}</div>'
        f'<div style="font-size:13px;color:{desc_color};line-height:1.55;">{desc}</div>'
        f'</div>'
    )


def _release_snapshot():
    """Compact active release card below the action grid."""
    try:
        from execution.asset_library import AssetLibrary
        lib = AssetLibrary()
        campaign_ids = lib.get_all_campaign_ids()
        if not campaign_ids:
            return
        stats = lib.get_campaign_stats(campaign_ids[-1])
    except Exception:
        return

    song_title   = "HLANGANA"
    artist_name  = "Fire & Flow Gospel"
    release_date = "2026-07-03"
    album        = "Becoming Vol. 1"

    try:
        import json
        songs_dir = Path(__file__).parent.parent.parent / "data" / "songs"
        files = sorted(songs_dir.glob("*.json"), key=lambda f: f.stat().st_mtime)
        if files:
            s = json.loads(files[-1].read_text(encoding="utf-8"))
            song_title   = s.get("title",         song_title)
            artist_name  = s.get("artist_name",   artist_name)
            release_date = s.get("release_date",  release_date)
            album        = s.get("album_title",   album)
    except Exception:
        pass

    days_left   = countdown_days(release_date)
    days_label  = ("days until launch" if days_left > 0
                   else ("Launch Day! 🎉" if days_left == 0 else "days since launch"))
    total       = stats.get("total", 0)
    approved    = stats.get("approved", 0)
    pending     = stats.get("pending", 0)
    pct         = (approved / total * 100) if total > 0 else 0

    render_html(
        f'<div class="mw-release-snapshot">'
        f'<div style="font-size:10px;color:#A855F7;font-weight:600;letter-spacing:0.8px;'
        f'text-transform:uppercase;margin-bottom:0.6rem;">Active Release</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
        f'flex-wrap:wrap;gap:1.5rem;">'
        f'<div>'
        f'<div style="font-size:22px;font-weight:800;color:#F0EDE8;">{song_title}</div>'
        f'<div style="font-size:13px;color:#8A8480;margin-top:2px;">{artist_name} · {album}</div>'
        f'</div>'
        f'<div style="display:flex;gap:2rem;">'
        f'<div style="text-align:center;">'
        f'<div style="font-size:30px;font-weight:800;color:#FF6B2B;line-height:1;">{abs(days_left)}</div>'
        f'<div style="font-size:11px;color:#8A8480;">{days_label}</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-size:30px;font-weight:800;color:#22C55E;line-height:1;">{approved}</div>'
        f'<div style="font-size:11px;color:#8A8480;">Approved</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-size:30px;font-weight:800;color:#F59E0B;line-height:1;">{pending}</div>'
        f'<div style="font-size:11px;color:#8A8480;">Pending</div>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'<div style="margin-top:1rem;">{progress_bar_html(pct, f"Approval Progress — {pct:.0f}%")}</div>'
        f'</div>'
    )

    r1, r2, r3 = st.columns(3)
    with r1:
        if st.button("✅  Review Assets", key="snap_review", use_container_width=True):
            navigate_to("approval")
    with r2:
        if st.button("🚀  Publishing", key="snap_publish", use_container_width=True, type="primary"):
            navigate_to("publishing")
    with r3:
        if st.button("📊  See Analytics", key="snap_analytics", use_container_width=True):
            navigate_to("analytics")


def render():
    # ── Greeting ──────────────────────────────────────────────────────────────
    hour     = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

    render_html(
        f'<div style="margin-bottom:2rem;">'
        f'<h1 style="margin:0 0 6px 0;font-size:2.2rem;">{greeting}, Founder! 👋</h1>'
        f'<p style="color:#8A8480;font-size:16px;margin:0;">What would you like to do today?</p>'
        f'</div>'
    )

    # ── Hero: Launch a Media Campaign (primary CTA) ───────────────────────────
    render_html(_action_card(
        "release", "🚀", "Launch a Media Campaign",
        "Upload your Creative Master and MusicWorks builds the entire media "
        "campaign around it — videos, social posts, articles, and more."
    ))
    if st.button("🚀  Launch a Media Campaign", key="home_launch", type="primary", use_container_width=True):
        _new_release()

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # ── 4 secondary action cards ──────────────────────────────────────────────
    last_campaign = _get_last_campaign()

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        render_html(_action_card(
            "continue", "📂", "Continue Current Campaign",
            "Pick up where you left off on an active campaign."
        ))
        if last_campaign:
            if st.button("Continue →", key="home_continue", use_container_width=True):
                navigate_to("campaigns")
        else:
            st.button("No Active Campaigns", key="home_continue", use_container_width=True, disabled=True)

    with c2:
        render_html(_action_card(
            "artists", "👥", "Manage Artists",
            "View and update artist profiles, brand guidelines, and biography."
        ))
        if st.button("View Artists →", key="home_artists", use_container_width=True):
            navigate_to("artists")

    with c3:
        render_html(_action_card(
            "library", "🗂", "Media Library",
            "Browse every approved asset — searchable, downloadable, stored forever."
        ))
        if st.button("Open Library →", key="home_library", use_container_width=True):
            navigate_to("media_library")

    with c4:
        render_html(_action_card(
            "results", "📈", "Results & Analytics",
            "See how your music and media are reaching people."
        ))
        if st.button("See Analytics →", key="home_results", use_container_width=True):
            navigate_to("analytics")

    # ── Active release snapshot ───────────────────────────────────────────────
    _release_snapshot()

    # ── Brand statement ───────────────────────────────────────────────────────
    render_html("""
    <div style="margin-top:2.5rem;text-align:center;padding:1.5rem;border-top:1px solid #1E1E1E;">
        <div style="font-size:12px;color:#6A6460;letter-spacing:0.3px;">
            Human-led. AI-assisted. Scripture-rooted. Built to spread the Gospel through art.
        </div>
    </div>
    """)
