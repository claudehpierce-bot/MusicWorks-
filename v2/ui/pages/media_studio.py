"""MusicWorks™ V4 — Media Studio: mission control dashboard."""
import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, render_html
from brand_brain.artist_library import list_artists, load_artist
from execution.production_queue import list_jobs, queue_stats, STATUS_COLOR, STATUS_LABELS, PHASE_LABELS
from execution.distrokid_store import list_releases
from execution.media_calendar import get_upcoming_jobs


def render():
    page_header("Media Studio™", "The artist finishes the music. MusicWorks finishes the release.", "🎬")

    artists = list_artists()
    if not artists:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:4rem; color:#8A8480;">
            <div style="font-size:48px; margin-bottom:1rem;">🎬</div>
            <div style="font-size:20px; color:#F0EDE8; margin-bottom:0.5rem;">Media Studio is ready.</div>
            <div style="font-size:14px; margin-bottom:2rem;">Create an artist to activate your AI media department.</div>
        </div>
        """)
        if st.button("👥  Add Artist", type="primary"):
            st.session_state.creating_artist = True
            navigate_to("artists")
        return

    # Artist selector (top-level for entire studio)
    artist_names = [a["artist_name"] for a in artists]
    artist_ids   = [a["artist_id"]   for a in artists]
    sel_idx  = st.selectbox("Active artist:", range(len(artist_names)),
                             format_func=lambda i: artist_names[i], key="ms_artist")
    sel_id   = artist_ids[sel_idx]
    sel_name = artist_names[sel_idx]
    brain    = load_artist(sel_id)

    # ── Hero banner ───────────────────────────────────────────────────────────
    tagline = brain.tagline if brain else ""
    render_html(f"""
    <div style="background:linear-gradient(135deg, #0A0512 0%, #1A0F42 60%, #2D1B69 100%);
                border:1px solid rgba(212,168,83,0.25); border-radius:20px;
                padding:2rem 2.5rem; margin:1.5rem 0 2rem 0; position:relative; overflow:hidden;">
        <div style="position:absolute; top:-20px; right:-20px; font-size:120px; opacity:0.04;">🎬</div>
        <div style="font-size:11px; color:#D4A853; letter-spacing:1.2px; text-transform:uppercase;
                    font-weight:700; margin-bottom:8px;">AI MEDIA DEPARTMENT</div>
        <div style="font-size:28px; font-weight:900; color:#F0EDE8; margin-bottom:6px;">{sel_name}</div>
        <div style="font-size:14px; color:#9B89D4; margin-bottom:1.5rem;">{tagline}</div>
        <div style="font-size:13px; color:#C8C4BE; max-width:600px; line-height:1.7;">
            You make the music. MusicWorks makes the media.<br>
            Every release becomes a full production campaign — automatically.
        </div>
    </div>
    """)

    # ── Quick actions ─────────────────────────────────────────────────────────
    render_html('<div class="mw-section-label">Quick Actions</div>')
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("📋  New Release", use_container_width=True, type="primary"):
            navigate_to("production")
    with qa2:
        if st.button("📅  Media Calendar", use_container_width=True):
            navigate_to("calendar")
    with qa3:
        if st.button("✅  Asset Review", use_container_width=True):
            navigate_to("approval")
    with qa4:
        if st.button("🚀  Publishing Queue", use_container_width=True):
            navigate_to("publishing")

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────────────────────
    stats  = queue_stats(sel_id)
    total  = stats.get("total", 0)
    pending_n  = stats.get("pending", 0) + stats.get("queued", 0)
    review_n   = stats.get("review", 0)
    approved_n = stats.get("approved", 0)
    published_n = stats.get("published", 0)

    render_html('<div class="mw-section-label">Production Overview</div>')
    c1, c2, c3, c4, c5 = st.columns(5)
    _stat_card(c1, "Total Jobs",  str(total),       "#9B89D4")
    _stat_card(c2, "In Queue",    str(pending_n),   "#F59E0B")
    _stat_card(c3, "In Review",   str(review_n),    "#3B82F6")
    _stat_card(c4, "Approved",    str(approved_n),  "#22C55E")
    _stat_card(c5, "Published",   str(published_n), "#10B981")

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)

    # ── Releases (DistroKid) ──────────────────────────────────────────────────
    releases = list_releases(sel_id)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        render_html('<div class="mw-section-label">Active Releases</div>')
        if not releases:
            render_html("""
            <div class="mw-card" style="padding:1.5rem; text-align:center; color:#8A8480;">
                <div style="font-size:28px; margin-bottom:0.5rem;">🎵</div>
                <div style="font-size:14px; color:#F0EDE8; margin-bottom:4px;">No releases registered yet</div>
                <div style="font-size:12px;">Add a release to start building your campaign.</div>
            </div>
            """)
            if st.button("+ Register Release", key="ms_add_release"):
                navigate_to("production")
        else:
            for rel in releases:
                _render_release_card(rel, sel_id)

    with col_right:
        # ── Upcoming jobs ─────────────────────────────────────────────────────
        render_html('<div class="mw-section-label">Upcoming (14 Days)</div>')
        upcoming = get_upcoming_jobs(sel_id, days_ahead=14)
        if not upcoming:
            render_html("""
            <div class="mw-card" style="padding:1.25rem; text-align:center; color:#8A8480; font-size:13px;">
                No jobs scheduled in the next 14 days.
            </div>
            """)
        else:
            for job in upcoming[:8]:
                _render_upcoming_job(job)
            if len(upcoming) > 8:
                st.caption(f"+{len(upcoming)-8} more on the calendar")

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)

    # ── Worker status panel ───────────────────────────────────────────────────
    render_html('<div class="mw-section-label">AI Worker Status</div>')
    _render_worker_panel()

    # ── Recent production jobs ─────────────────────────────────────────────────
    all_jobs = list_jobs(sel_id)
    if all_jobs:
        render_html('<div class="mw-section-label" style="margin-top:2rem;">Production Queue — All Jobs</div>')
        review_jobs = [j for j in all_jobs if j.get("status") == "review"]
        if review_jobs:
            st.warning(f"{len(review_jobs)} job(s) waiting for your review.")
        jobs_by_status = {}
        for j in all_jobs:
            jobs_by_status.setdefault(j.get("status", "pending"), []).append(j)
        for status, status_jobs in sorted(jobs_by_status.items(),
                                          key=lambda x: ["review","generating","queued","pending","approved","scheduled","published","rejected"].index(x[0]) if x[0] in ["review","generating","queued","pending","approved","scheduled","published","rejected"] else 99):
            color = STATUS_COLOR.get(status, "#6A6460")
            label = STATUS_LABELS.get(status, status)
            with st.expander(f"**{label}** ({len(status_jobs)})", expanded=(status in ("review", "generating"))):
                for j in status_jobs[:10]:
                    _render_job_row(j, sel_id)

        if st.button("View Full Production Queue →", key="ms_goto_prod"):
            navigate_to("production")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _stat_card(col, label: str, value: str, color: str):
    with col:
        render_html(f"""
        <div class="mw-card" style="padding:1.25rem; text-align:center; border-top:3px solid {color};">
            <div style="font-size:28px; font-weight:800; color:{color};">{value}</div>
            <div style="font-size:11px; color:#8A8480; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">{label}</div>
        </div>
        """)


def _render_release_card(rel: dict, artist_id: str):
    status_colors = {"live": "#22C55E", "upcoming": "#F59E0B", "pre_release": "#9B89D4", "archived": "#6A6460"}
    s = rel.get("status", "upcoming")
    sc = status_colors.get(s, "#6A6460")
    rd = rel.get("release_date", "")
    render_html(f"""
    <div class="mw-card" style="padding:1rem 1.25rem; margin-bottom:0.75rem; border-left:3px solid {sc};">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div style="font-size:15px; font-weight:700; color:#F0EDE8;">{rel.get("song_title","")}</div>
                <div style="font-size:12px; color:#8A8480; margin-top:2px;">Release: {rd} · {s.replace("_"," ").title()}</div>
            </div>
            <span style="font-size:11px; color:{sc}; font-weight:600;">●  {s.upper()}</span>
        </div>
        {"<div style='font-size:11px; color:#D4A853; margin-top:6px;'>UPC: " + rel.get("upc","") + "</div>" if rel.get("upc") else ""}
        {"<div style='font-size:11px; color:#8A8480; margin-top:4px; word-break:break-all;'>" + rel.get("streaming_url","") + "</div>" if rel.get("streaming_url") else ""}
    </div>
    """)


def _render_upcoming_job(job: dict):
    sd = job.get("scheduled_date", "")
    dt_str = ""
    if sd:
        try:
            dt = datetime.fromisoformat(sd)
            dt_str = dt.strftime("%b %d")
        except Exception:
            dt_str = sd[:10]
    icon   = job.get("job_icon", "📄")
    label  = job.get("job_label", "")
    status = job.get("status", "pending")
    color  = STATUS_COLOR.get(status, "#6A6460")
    render_html(f"""
    <div class="mw-card" style="padding:0.6rem 0.9rem; margin-bottom:0.4rem; display:flex; align-items:center; gap:10px;">
        <span style="font-size:16px; min-width:20px;">{icon}</span>
        <div style="flex:1; min-width:0;">
            <div style="font-size:12px; color:#F0EDE8; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{label}</div>
            <div style="font-size:10px; color:#8A8480;">{PHASE_LABELS.get(job.get("phase",""),"")}</div>
        </div>
        <div style="text-align:right; min-width:48px;">
            <div style="font-size:11px; color:{color}; font-weight:600;">{dt_str}</div>
        </div>
    </div>
    """)


def _render_job_row(job: dict, artist_id: str):
    icon  = job.get("job_icon", "📄")
    label = job.get("job_label", job.get("job_type", ""))
    phase = PHASE_LABELS.get(job.get("phase", ""), "")
    sd    = (job.get("scheduled_date", "") or "")[:10]
    status = job.get("status", "pending")
    color  = STATUS_COLOR.get(status, "#6A6460")
    render_html(f"""
    <div style="display:flex; align-items:center; gap:10px; padding:5px 0; border-bottom:1px solid #1A1A1A;">
        <span style="font-size:14px;">{icon}</span>
        <div style="flex:1; font-size:13px; color:#C8C4BE;">{label}</div>
        <div style="font-size:11px; color:#6A6460;">{phase}</div>
        <div style="font-size:11px; color:#6A6460;">{sd}</div>
        <span style="font-size:11px; color:{color}; font-weight:600; min-width:60px; text-align:right;">{STATUS_LABELS.get(status, status)}</span>
    </div>
    """)


def _render_worker_panel():
    from execution.workers import ALL_WORKERS
    cols = st.columns(len(ALL_WORKERS))
    for col, worker in zip(cols, ALL_WORKERS):
        with col:
            avail_html = worker.status_pill()
            render_html(f"""
            <div class="mw-card" style="padding:1rem; text-align:center; border-top:3px solid {worker.color};">
                <div style="font-size:28px; margin-bottom:6px;">{worker.icon}</div>
                <div style="font-size:13px; font-weight:700; color:#F0EDE8; margin-bottom:4px;">{worker.name}</div>
                <div style="font-size:10px; color:#8A8480; margin-bottom:8px; line-height:1.4;">{worker.description[:60]}...</div>
                {avail_html}
            </div>
            """)
