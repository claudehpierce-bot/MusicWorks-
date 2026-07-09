"""MusicWorks™ V6.2 — Media Blitz Control Center.

MusicWorks doesn't release music — DistroKid does. This page is where a
founder configures and launches the MEDIA campaign around a release: confirm
DistroKid release links, choose a schedule, press Launch Media Blitz, and
pause/resume/stop/extend/reschedule from here. No external publishing API is
ever called — "launch" only assigns scheduled_date locally; founders mark
items posted manually once they've actually gone out.
"""
import sys
from pathlib import Path
from datetime import datetime, date, time as dtime, timezone
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html, navigate_to
from brand_brain.artist_library import list_artists
from execution import campaign_store
from execution.campaign_store import STATUS_LABELS, CAMPAIGN_TYPES, CAMPAIGN_TYPE_LABELS, INTENSITIES
from execution.blitz_scheduler import PLATFORM_OPTIONS, launch_blitz, extend_blitz, reset_schedule, pull_back_job
from execution.production_queue import list_jobs, queue_stats, update_job_status
from execution.distrokid_store import get_release, upsert_release

_STATUS_COLORS = {
    "draft": "#6A6460", "building": "#9B89D4", "review": "#3B82F6",
    "approved": "#22C55E", "waiting_for_distrokid": "#F59E0B",
    "ready_to_launch": "#10B981", "live_blitz": "#FF6B2B",
    "paused": "#F59E0B", "completed": "#8A8480", "relaunch_ready": "#9B89D4",
}


def _status_badge(status: str):
    color = _STATUS_COLORS.get(status, "#8A8480")
    label = STATUS_LABELS.get(status, status.title())
    render_html(
        f'<span style="background:{color}22;color:{color};font-size:13px;font-weight:700;'
        f'padding:5px 14px;border-radius:20px;border:1px solid {color}44;">{label}</span>'
    )


def render():
    page_header("Media Blitz Control Center", "Schedule and launch the media campaign around your release.", "🎯")

    artists = list_artists()
    if not artists:
        render_html(
            '<div class="mw-card" style="text-align:center;padding:3rem;color:#8A8480;">'
            'Create an artist first.</div>'
        )
        return

    names = [a["artist_name"] for a in artists]
    ids = [a["artist_id"] for a in artists]
    a_idx = st.selectbox("Artist:", range(len(names)), format_func=lambda i: names[i], key="mb_artist")
    artist_id = ids[a_idx]

    campaigns = campaign_store.list_campaigns(artist_id)
    if not campaigns:
        render_html(
            '<div class="mw-card" style="text-align:center;padding:2rem;color:#8A8480;">'
            '<div style="font-size:16px;color:#F0EDE8;margin-bottom:0.5rem;">No media campaigns yet</div>'
            '<div style="font-size:13px;">Build one from the Launch Campaign wizard first.</div></div>'
        )
        if st.button("🚀  Launch Campaign", type="primary", key="mb_go_wizard"):
            navigate_to("wizard")
        return

    # Recompute status per campaign up front so the dropdown label never shows
    # a stale on-disk status lagging one render behind the badge below it.
    live_statuses, live_jobs, live_releases = [], [], []
    for c in campaigns:
        c_jobs = list_jobs(artist_id, campaign_id=c["campaign_id"])
        c_release = get_release(artist_id, c["song_id"])
        live_jobs.append(c_jobs)
        live_releases.append(c_release)
        live_statuses.append(campaign_store.recompute_status(c, c_jobs, c_release))

    camp_labels = [
        f"{c['song_title']} — {STATUS_LABELS.get(s, s)}" for c, s in zip(campaigns, live_statuses)
    ]
    c_idx = st.selectbox("Media Campaign:", range(len(camp_labels)), format_func=lambda i: camp_labels[i], key="mb_campaign")
    campaign = campaigns[c_idx]
    campaign_id = campaign["campaign_id"]
    jobs = live_jobs[c_idx]
    release = live_releases[c_idx]
    status = live_statuses[c_idx]

    if status != campaign.get("status"):
        campaign["status"] = status
        campaign_store.save_campaign(campaign)

    st.markdown(f"### {campaign['song_title']}")
    _status_badge(status)
    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

    stats = queue_stats(artist_id, campaign_id=campaign_id)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Assets", stats["total"])
    m2.metric("In Review", stats["review"])
    m3.metric("Approved Assets", stats["approved"])
    m4.metric("Scheduled", stats["scheduled"])

    if status in ("live_blitz", "paused"):
        attention = [j for j in jobs if j.get("status") in ("pending", "review")]
        if attention:
            st.warning(
                f"⚠ {len(attention)} asset(s) need attention — likely re-rendered or revised "
                f"after launch. Review them in Asset Review before they go out."
            )
            if st.button("Open Asset Review", key="mb_attn_open"):
                navigate_to("approval")

    if status == "waiting_for_distrokid":
        st.warning(
            f"⏳ {stats['approved']} asset(s) approved and ready. Add at least one release link "
            f"below (DistroKid Status) to unlock scheduling."
        )

    with st.expander(f"Approved Assets ({stats['approved']})"):
        approved_jobs = [j for j in jobs if j.get("status") == "approved"]
        if not approved_jobs:
            st.caption("None yet — approve assets in Asset Review first.")
        for j in approved_jobs:
            st.caption(f"{j.get('job_icon', '📄')} {j.get('job_label', j['job_type'])}")

    # ── Release Links (DistroKid Status) ──────────────────────────────────────
    render_html('<div class="mw-section-label" style="margin-top:1.5rem;">Release Links · DistroKid Status</div>')
    release = release or {}
    dk_status = release.get("status", "upcoming").title()
    dk_date = release.get("release_date") or "—"
    st.caption(f"DistroKid Status: **{dk_status}** · Release Date: **{dk_date}**")

    with st.form("mb_release_form"):
        col1, col2 = st.columns(2)
        with col1:
            streaming_url = st.text_input("Streaming URL:", value=release.get("streaming_url", "") or "")
            spotify_url = st.text_input("Spotify URL:", value=release.get("spotify_url", "") or "")
            apple_music_url = st.text_input("Apple Music URL:", value=release.get("apple_music_url", "") or "")
        with col2:
            youtube_music_url = st.text_input("YouTube Music URL:", value=release.get("youtube_music_url", "") or "")
            audiomack_url = st.text_input("Audiomack URL:", value=release.get("audiomack_url", "") or "")
            album_url = st.text_input("Album URL:", value=release.get("album_url", "") or "")
        if st.form_submit_button("💾  Save Release Links"):
            upsert_release(artist_id, campaign["song_id"], {
                "song_title": campaign["song_title"],
                "streaming_url": streaming_url.strip(),
                "spotify_url": spotify_url.strip(),
                "apple_music_url": apple_music_url.strip(),
                "youtube_music_url": youtube_music_url.strip(),
                "audiomack_url": audiomack_url.strip(),
                "album_url": album_url.strip(),
            })
            st.success("Release links saved.")
            st.rerun()

    # ── Campaign Calendar (schedule config) ───────────────────────────────────
    render_html('<div class="mw-section-label" style="margin-top:1.5rem;">Campaign Calendar</div>')
    with st.form("mb_schedule_form"):
        type_default = campaign.get("campaign_type") or "7d"
        type_idx = CAMPAIGN_TYPES.index(type_default) if type_default in CAMPAIGN_TYPES else 1
        campaign_type = st.radio(
            "Campaign Type:", CAMPAIGN_TYPES, index=type_idx,
            format_func=lambda k: CAMPAIGN_TYPE_LABELS[k], horizontal=True,
        )

        window_start, window_end = None, None
        if campaign_type == "custom":
            cc1, cc2 = st.columns(2)
            with cc1:
                window_start = st.date_input("Start date:", value=date.today())
            with cc2:
                window_end = st.date_input("End date:", value=date.today())

        intensity_default = campaign.get("intensity") or "standard"
        intensity_idx = INTENSITIES.index(intensity_default) if intensity_default in INTENSITIES else 1
        intensity = st.radio(
            "Posting Intensity:", INTENSITIES, index=intensity_idx,
            format_func=lambda k: k.title(), horizontal=True,
        )

        platforms = st.multiselect("Platforms:", PLATFORM_OPTIONS, default=campaign.get("platforms") or [])

        lc1, lc2 = st.columns(2)
        with lc1:
            launch_date = st.date_input("Launch date:", value=date.today())
        with lc2:
            launch_time = st.time_input("Launch time:", value=dtime(9, 0))

        if st.form_submit_button("💾  Save Schedule"):
            campaign["campaign_type"] = campaign_type
            campaign["intensity"] = intensity
            campaign["platforms"] = platforms
            campaign["launch_datetime"] = datetime.combine(launch_date, launch_time).isoformat()
            if campaign_type == "custom" and window_start and window_end:
                campaign["window_start"] = str(window_start)
                campaign["window_end"] = str(window_end)
            campaign_store.save_campaign(campaign)
            st.success("Schedule saved.")
            st.rerun()

    # ── Actions ────────────────────────────────────────────────────────────────
    render_html('<div class="mw-section-label" style="margin-top:1.5rem;">Actions</div>')

    if status in ("ready_to_launch", "relaunch_ready"):
        if st.button("🚀  LAUNCH MEDIA BLITZ", type="primary", use_container_width=True, key="mb_launch"):
            result = launch_blitz(artist_id, campaign_id)
            campaign_store.update_campaign_status(
                artist_id, campaign_id, "live_blitz",
                launched_at=datetime.now(timezone.utc).isoformat(),
            )
            msg = f"Blitz launched — {result['scheduled']} asset(s) scheduled."
            if result["leftover"]:
                msg += f" {result['leftover']} more matched asset(s) didn't fit this window — use Extend to include them."
            if result["unmatched"]:
                msg += f" {result['unmatched']} approved asset(s) aren't on your chosen platforms."
            st.success(msg)
            st.rerun()

    elif status == "live_blitz":
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button("⏸  Pause", use_container_width=True, key="mb_pause"):
                campaign_store.update_campaign_status(
                    artist_id, campaign_id, "paused", paused_at=datetime.now(timezone.utc).isoformat()
                )
                st.rerun()
        with b2:
            if st.button("⏹  Stop", use_container_width=True, key="mb_stop"):
                campaign_store.update_campaign_status(
                    artist_id, campaign_id, "completed", completed_at=datetime.now(timezone.utc).isoformat()
                )
                from execution.campaign_history import record_completion
                record_completion(artist_id, campaign_id)
                st.rerun()
        with b3:
            if st.button("🗓  Reschedule", use_container_width=True, key="mb_reschedule"):
                reset_schedule(artist_id, campaign_id)
                result = launch_blitz(artist_id, campaign_id)
                st.success(f"Rescheduled — {result['scheduled']} asset(s) scheduled.")
                st.rerun()
        with b4:
            with st.popover("➕  Extend"):
                days = st.number_input("Additional days:", min_value=1, max_value=60, value=7, key="mb_extend_days")
                if st.button("Confirm Extend", key="mb_extend_confirm"):
                    result = extend_blitz(artist_id, campaign_id, int(days))
                    st.success(f"Extended — {result['scheduled']} more asset(s) scheduled.")
                    st.rerun()

    elif status == "paused":
        b1, b2 = st.columns(2)
        with b1:
            if st.button("▶  Resume", type="primary", use_container_width=True, key="mb_resume"):
                campaign_store.update_campaign_status(artist_id, campaign_id, "live_blitz")
                st.rerun()
        with b2:
            if st.button("⏹  Stop", use_container_width=True, key="mb_stop_paused"):
                campaign_store.update_campaign_status(
                    artist_id, campaign_id, "completed", completed_at=datetime.now(timezone.utc).isoformat()
                )
                from execution.campaign_history import record_completion
                record_completion(artist_id, campaign_id)
                st.rerun()

    elif status == "completed":
        if st.button("♻  Prepare Relaunch / Extend", use_container_width=True, key="mb_relaunch"):
            campaign_store.update_campaign_status(artist_id, campaign_id, "relaunch_ready")
            st.rerun()

    else:
        st.info(
            "Approve all assets in Asset Review and confirm your DistroKid release links above, "
            "then save a schedule to unlock Launch Media Blitz."
        )

    # ── Upcoming Posts ─────────────────────────────────────────────────────────
    render_html('<div class="mw-section-label" style="margin-top:1.5rem;">Upcoming Posts</div>')
    upcoming = sorted(
        list_jobs(artist_id, status="scheduled", campaign_id=campaign_id),
        key=lambda j: j.get("scheduled_date", ""),
    )
    if not upcoming:
        st.caption("No posts scheduled yet.")
    else:
        for job in upcoming:
            jid = job["job_id"]
            sched = (job.get("scheduled_date") or "")[:16].replace("T", " ")
            r1, r2, r3 = st.columns([3, 1, 1])
            with r1:
                st.markdown(f"**{job.get('job_icon', '📄')} {job.get('job_label', job['job_type'])}** — {sched}")
            with r2:
                if st.button("✓ Mark Posted", key=f"mb_post_{jid}", use_container_width=True):
                    update_job_status(artist_id, jid, "published")
                    st.rerun()
            with r3:
                if st.button("↩ Pull Back", key=f"mb_pull_{jid}", use_container_width=True):
                    pull_back_job(artist_id, jid)
                    st.rerun()
