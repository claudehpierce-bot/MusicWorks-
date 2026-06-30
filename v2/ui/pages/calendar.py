"""MusicWorks™ V4 — Media Calendar: visualize the full campaign schedule."""
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, render_html
from brand_brain.artist_library import list_artists
from execution.production_queue import list_jobs, STATUS_COLOR, STATUS_LABELS, PHASE_LABELS, PHASES
from execution.media_calendar import get_upcoming_jobs, get_jobs_by_phase, get_calendar_meta
from execution.distrokid_store import list_releases

_PHASE_COLORS = {
    "pre_release":  "#9B89D4",
    "launch":       "#D4A853",
    "post_release": "#22C55E",
    "evergreen":    "#3B82F6",
}

_WORKER_ICONS = {"claude": "🧠", "veo": "🎥", "hedra": "🎙️", "elevenlabs": "🔊", "canva": "🎨"}


def render():
    page_header("Media Calendar", "Every job. Every platform. Every date.", "📅")

    artists = list_artists()
    if not artists:
        render_html('<div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;"><div style="font-size:36px; margin-bottom:1rem;">📅</div><div>Create an artist to use the Media Calendar.</div></div>')
        return

    artist_names = [a["artist_name"] for a in artists]
    artist_ids   = [a["artist_id"]   for a in artists]
    sel_idx  = st.selectbox("Artist:", range(len(artist_names)),
                             format_func=lambda i: artist_names[i], key="cal_artist")
    sel_id   = artist_ids[sel_idx]

    releases = list_releases(sel_id)
    all_jobs = list_jobs(sel_id)

    if not all_jobs:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;">
            <div style="font-size:40px; margin-bottom:1rem;">📅</div>
            <div style="font-size:16px; color:#F0EDE8; margin-bottom:0.5rem;">No campaign calendar yet</div>
            <div style="font-size:13px;">Register a release in the Production Queue to generate your media calendar.</div>
        </div>
        """)
        if st.button("📋  Go to Production Queue", type="primary"):
            navigate_to("production")
        return

    # ── Release selector / summary ────────────────────────────────────────────
    if releases:
        render_html('<div class="mw-section-label">Active Releases</div>')
        rel_cols = st.columns(min(len(releases), 3))
        for col, rel in zip(rel_cols, releases):
            with col:
                rd = rel.get("release_date", "")
                _phase = _get_release_phase(rd)
                phase_color = {"pre_release": "#9B89D4", "launch": "#D4A853", "post_release": "#22C55E", "live": "#22C55E"}.get(_phase, "#6A6460")
                render_html(f"""
                <div class="mw-card" style="padding:1rem; border-top:3px solid {phase_color};">
                    <div style="font-size:14px; font-weight:700; color:#F0EDE8;">{rel.get("song_title","")}</div>
                    <div style="font-size:12px; color:#8A8480; margin-top:2px;">Release: {rd}</div>
                    <div style="font-size:11px; color:{phase_color}; margin-top:4px; font-weight:600;">
                        {_phase.replace("_"," ").title()}
                    </div>
                </div>
                """)

    # ── View controls ─────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    view_tab, list_tab, upcoming_tab = st.tabs(["📆  Timeline View", "📋  List View", "⏰  Upcoming (14 Days)"])

    # ── Timeline View ─────────────────────────────────────────────────────────
    with view_tab:
        jobs_by_phase = get_jobs_by_phase(sel_id)
        for phase in PHASES:
            phase_jobs = jobs_by_phase.get(phase, [])
            if not phase_jobs:
                continue
            pc = _PHASE_COLORS.get(phase, "#6A6460")
            label = PHASE_LABELS.get(phase, phase)
            done  = sum(1 for j in phase_jobs if j.get("status") in ("approved","published"))
            total = len(phase_jobs)

            st.markdown(f"""
            <div style="border-left:4px solid {pc}; padding-left:1rem; margin:1.5rem 0 0.75rem 0;">
                <div style="font-size:16px; font-weight:800; color:{pc};">{label}</div>
                <div style="font-size:12px; color:#8A8480;">{done}/{total} complete</div>
            </div>
            """, unsafe_allow_html=True)

            # Progress bar
            if total > 0:
                pct = done / total
                bar_width = int(pct * 100)
                render_html(f"""
                <div style="background:#1A1A1A; border-radius:4px; height:6px; margin-bottom:1rem;">
                    <div style="background:{pc}; border-radius:4px; height:6px; width:{bar_width}%;
                                transition:width 0.3s;"></div>
                </div>
                """)

            # Group by scheduled date
            by_date: dict[str, list] = {}
            for j in phase_jobs:
                sd = (j.get("scheduled_date") or "")[:10]
                by_date.setdefault(sd or "Unscheduled", []).append(j)

            for date_str, date_jobs in sorted(by_date.items()):
                day_label = _fmt_day(date_str)
                render_html(f'<div style="font-size:11px; color:#6A6460; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; margin:0.75rem 0 0.25rem 0;">{day_label}</div>')
                cols = st.columns(min(len(date_jobs), 4))
                for col, job in zip(cols, date_jobs):
                    with col:
                        _render_timeline_card(job, pc)
                if len(date_jobs) > 4:
                    st.caption(f"+{len(date_jobs)-4} more on this date")

    # ── List View ─────────────────────────────────────────────────────────────
    with list_tab:
        col_f1, col_f2 = st.columns([2, 2])
        with col_f1:
            phase_filter = st.selectbox("Phase:", ["All"] + [PHASE_LABELS[p] for p in PHASES], key="cal_phase_filter")
        with col_f2:
            status_filter = st.selectbox("Status:", ["All", "Pending", "Queued", "Generating", "In Review", "Approved", "Published"], key="cal_status_filter")

        phase_rev  = {v: k for k, v in PHASE_LABELS.items()}
        status_rev = {"Pending":"pending","Queued":"queued","Generating":"generating","In Review":"review","Approved":"approved","Published":"published"}
        filtered = [j for j in all_jobs
                    if (phase_filter == "All" or j.get("phase") == phase_rev.get(phase_filter))
                    and (status_filter == "All" or j.get("status") == status_rev.get(status_filter))]
        filtered.sort(key=lambda j: j.get("scheduled_date") or "")

        st.caption(f"{len(filtered)} job(s)")

        # Table header
        render_html("""
        <div style="display:flex; gap:8px; padding:6px 0; border-bottom:1px solid #242424;
                    font-size:10px; color:#6A6460; font-weight:700; letter-spacing:0.5px; text-transform:uppercase;">
            <div style="min-width:28px;"></div>
            <div style="flex:2;">Job</div>
            <div style="flex:1;">Phase</div>
            <div style="flex:1;">Scheduled</div>
            <div style="flex:1;">Worker</div>
            <div style="flex:1;">Status</div>
        </div>
        """)
        for job in filtered:
            icon   = job.get("job_icon", "📄")
            label  = job.get("job_label", "")
            phase  = PHASE_LABELS.get(job.get("phase",""), "")
            sd     = (job.get("scheduled_date") or "")[:10]
            worker = job.get("worker", "")
            w_icon = _WORKER_ICONS.get(worker, "🤖")
            status = job.get("status", "pending")
            color  = STATUS_COLOR.get(status, "#6A6460")
            slabel = STATUS_LABELS.get(status, status)
            render_html(f"""
            <div style="display:flex; align-items:center; gap:8px; padding:7px 0;
                        border-bottom:1px solid #1A1A1A;">
                <div style="min-width:28px; font-size:16px;">{icon}</div>
                <div style="flex:2; font-size:13px; color:#C8C4BE;">{label}</div>
                <div style="flex:1; font-size:11px; color:#8A8480;">{phase}</div>
                <div style="flex:1; font-size:11px; color:#8A8480;">{_fmt_day(sd)}</div>
                <div style="flex:1; font-size:12px;">{w_icon} {worker.title()}</div>
                <div style="flex:1; font-size:11px; color:{color}; font-weight:600;">● {slabel}</div>
            </div>
            """)

    # ── Upcoming 14 days ──────────────────────────────────────────────────────
    with upcoming_tab:
        render_html('<div class="mw-section-label">Next 14 Days</div>')
        upcoming = get_upcoming_jobs(sel_id, days_ahead=14)

        if not upcoming:
            render_html('<div class="mw-card" style="padding:2rem; text-align:center; color:#8A8480; font-size:13px;">No jobs scheduled in the next 14 days.</div>')
        else:
            # Group by day
            by_day: dict[str, list] = {}
            for j in upcoming:
                sd = (j.get("scheduled_date") or "")[:10]
                by_day.setdefault(sd, []).append(j)

            for date_str, day_jobs in sorted(by_day.items()):
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    now = datetime.now()
                    diff = (dt - now).days
                    if diff == 0:
                        day_label = "TODAY"
                        day_color = "#D4A853"
                    elif diff == 1:
                        day_label = "TOMORROW"
                        day_color = "#22C55E"
                    elif diff < 0:
                        day_label = f"{abs(diff)} DAYS AGO"
                        day_color = "#6A6460"
                    else:
                        day_label = dt.strftime("%A, %B %d")
                        day_color = "#F0EDE8"
                except Exception:
                    day_label = date_str
                    day_color = "#F0EDE8"

                st.markdown(f'<div style="font-size:13px; font-weight:700; color:{day_color}; margin:1.25rem 0 0.5rem 0;">{day_label}</div>', unsafe_allow_html=True)
                for job in day_jobs:
                    icon   = job.get("job_icon", "📄")
                    label  = job.get("job_label", "")
                    time_s = (job.get("scheduled_date") or "")[11:16]
                    worker = job.get("worker", "")
                    w_icon = _WORKER_ICONS.get(worker, "🤖")
                    status = job.get("status", "pending")
                    color  = STATUS_COLOR.get(status, "#6A6460")
                    slabel = STATUS_LABELS.get(status, status)
                    render_html(f"""
                    <div class="mw-card" style="padding:0.75rem 1rem; margin-bottom:0.4rem; display:flex; align-items:center; gap:12px;">
                        <span style="font-size:18px;">{icon}</span>
                        <div style="flex:1;">
                            <div style="font-size:13px; color:#F0EDE8; font-weight:500;">{label}</div>
                            <div style="font-size:11px; color:#8A8480; margin-top:2px;">{time_s} · {w_icon} {worker.title()}</div>
                        </div>
                        <span style="font-size:11px; color:{color}; font-weight:600; min-width:70px; text-align:right;">● {slabel}</span>
                    </div>
                    """)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _render_timeline_card(job: dict, phase_color: str):
    icon   = job.get("job_icon", "📄")
    label  = job.get("job_label", "")
    status = job.get("status", "pending")
    color  = STATUS_COLOR.get(status, "#6A6460")
    slabel = STATUS_LABELS.get(status, status)
    time_s = (job.get("scheduled_date") or "")[11:16]
    render_html(f"""
    <div class="mw-card" style="padding:0.75rem; border-top:2px solid {phase_color}; text-align:center; margin-bottom:0.5rem;">
        <div style="font-size:22px; margin-bottom:4px;">{icon}</div>
        <div style="font-size:11px; color:#F0EDE8; font-weight:600; line-height:1.3;">{label}</div>
        {f'<div style="font-size:10px; color:#8A8480; margin-top:2px;">{time_s}</div>' if time_s else ""}
        <div style="font-size:10px; color:{color}; margin-top:4px; font-weight:600;">{slabel}</div>
    </div>
    """)


def _fmt_day(date_str: str) -> str:
    if not date_str or date_str == "Unscheduled":
        return "Unscheduled"
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        now = datetime.now()
        diff = (dt.date() - now.date()).days
        if diff == 0:
            return f"Today ({dt.strftime('%b %d')})"
        if diff == 1:
            return f"Tomorrow ({dt.strftime('%b %d')})"
        if diff == -1:
            return f"Yesterday ({dt.strftime('%b %d')})"
        return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str[:10]


def _get_release_phase(release_date_str: str) -> str:
    if not release_date_str:
        return "upcoming"
    try:
        rd = datetime.strptime(release_date_str[:10], "%Y-%m-%d")
        now = datetime.now()
        diff = (rd.date() - now.date()).days
        if diff > 0:
            return "pre_release"
        if diff == 0:
            return "launch"
        return "post_release"
    except Exception:
        return "upcoming"
