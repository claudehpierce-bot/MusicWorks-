"""MusicWorks™ V5 — Publishing page."""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone, date, timedelta
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, render_html
from execution.asset_library import AssetLibrary
from execution.distribution_store import (
    load_distribution, dist_configured_count, dist_platform_display, PLATFORM_ICONS
)
from brand_brain.artist_library import list_artists


_PLATFORMS = [
    ("youtube",      "▶️",  "YouTube"),
    ("instagram",    "📸",  "Instagram"),
    ("tiktok",       "🎵",  "TikTok"),
    ("facebook",     "📘",  "Facebook"),
    ("x",            "🐦",  "X / Twitter"),
    ("apple_music",  "🍎",  "Apple Music"),
    ("spotify",      "💚",  "Spotify"),
    ("threads",      "🧵",  "Threads"),
    ("rumble",       "📹",  "Rumble"),
    ("newsletter",   "📧",  "Newsletter"),
]


@st.cache_resource
def _get_library():
    return AssetLibrary()


def render():
    page_header("Publishing", "Your music is ready. Let's get it out there.", "🚀")

    # ── V4 queue: approved jobs ───────────────────────────────────────────────
    _render_v4_publish_section()

    # ── Legacy V3 campaign publishing ─────────────────────────────────────────
    try:
        lib = _get_library()
        campaign_ids = lib.get_all_campaign_ids()
    except Exception as e:
        st.error(f"Could not load campaigns: {e}")
        return

    if not campaign_ids:
        return

    with st.expander("Legacy Release Publishing", expanded=False):
        _render_legacy_publishing(lib, campaign_ids)


def _render_v4_publish_section():
    """V5 publishing experience for V4 production queue jobs."""
    artists = list_artists()
    if not artists:
        return

    artist_id   = artists[0]["artist_id"]
    artist_name = artists[0]["artist_name"]

    try:
        from execution.production_queue import list_jobs, update_job_status
    except Exception:
        return

    all_jobs    = list_jobs(artist_id)
    approved    = [j for j in all_jobs if j.get("status") == "approved"]
    published   = [j for j in all_jobs if j.get("status") == "published"]
    review_only = [j for j in all_jobs if j.get("status") == "review"]

    if review_only:
        st.warning(f"{len(review_only)} asset(s) still waiting for your review. Approve them before publishing.")
        if st.button("✅  Review Assets First", type="primary", key="pub_review_first"):
            navigate_to("approval")
        st.divider()

    # ── Stats ─────────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Approved",    len(approved))
    m2.metric("Published",   len(published))
    m3.metric("In Review",   len(review_only))
    m4.metric("Total Jobs",  len(all_jobs))

    if not approved and not published:
        render_html("""
        <div class="mw-card" style="text-align:center;padding:3rem;color:#8A8480;margin-top:1rem;">
            <div style="font-size:40px;margin-bottom:1rem;">🎵</div>
            <div style="font-size:18px;color:#F0EDE8;margin-bottom:0.5rem;">Nothing approved yet</div>
            <div style="font-size:13px;">Review and approve assets before publishing.</div>
        </div>
        """)
        if st.button("✅  Open Asset Review", type="primary", key="pub_goto_review"):
            navigate_to("approval")
        return

    # ── Hero banner ───────────────────────────────────────────────────────────
    render_html(f"""
    <div style="background:linear-gradient(135deg,#0F1E0F 0%,#0A2A0A 100%);
                border:1px solid rgba(34,197,94,0.25);border-radius:20px;
                padding:2rem 2.5rem;margin-bottom:2rem;text-align:center;">
        <div style="font-size:48px;margin-bottom:0.75rem;">🚀</div>
        <div style="font-size:26px;font-weight:800;color:#F0EDE8;margin-bottom:0.4rem;">
            Ready to Share Your Music!
        </div>
        <div style="font-size:15px;color:#6EC894;">
            {len(approved)} asset(s) approved for <strong style="color:#F0EDE8;">{artist_name}</strong>
            — choose your platforms and schedule below.
        </div>
    </div>
    """)

    # ── Platform selector ─────────────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>Select Platforms</div>", unsafe_allow_html=True)

    # Toggle state per platform
    if "pub_platforms" not in st.session_state:
        st.session_state.pub_platforms = {"youtube", "instagram", "tiktok", "facebook"}

    # Show distribution config if available
    dist = load_distribution(artist_id)
    configured_dist = {p["key"] for p in dist_platform_display(dist) if p["set"]}

    # Build platform pills HTML (visual only — buttons below)
    pill_html = '<div class="mw-platform-row">'
    selected_platforms = st.session_state.pub_platforms
    for key, icon, label in _PLATFORMS:
        is_on = key in selected_platforms
        cls   = "mw-platform-pill mw-platform-pill-on" if is_on else "mw-platform-pill"
        cfg_note = " ✓" if key in configured_dist else ""
        pill_html += f'<span class="{cls}">{icon} {label}{cfg_note}</span>'
    pill_html += "</div>"
    render_html(pill_html)

    # Toggle checkboxes (styled)
    render_html('<div style="font-size:11px;color:#6A6460;margin-bottom:0.5rem;">Toggle platforms:</div>')
    cols_per_row = 5
    rows = [_PLATFORMS[i:i+cols_per_row] for i in range(0, len(_PLATFORMS), cols_per_row)]
    for row in rows:
        pcols = st.columns(cols_per_row)
        for col, (key, icon, label) in zip(pcols, row):
            with col:
                checked = key in st.session_state.pub_platforms
                if st.checkbox(f"{icon} {label}", value=checked, key=f"pub_plt_{key}"):
                    st.session_state.pub_platforms.add(key)
                else:
                    st.session_state.pub_platforms.discard(key)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    # ── Schedule ──────────────────────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>Schedule Release</div>", unsafe_allow_html=True)
    date_col, time_col = st.columns([1, 1])
    with date_col:
        release_date = st.date_input(
            "Release Date",
            value=date.today() + timedelta(days=3),
            min_value=date.today(),
            key="pub_release_date",
        )
    with time_col:
        release_time = st.time_input(
            "Release Time",
            value=datetime.strptime("08:30", "%H:%M").time(),
            key="pub_release_time",
        )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    # ── Add to queue ──────────────────────────────────────────────────────────
    if st.session_state.pub_platforms:
        platforms_label = ", ".join(
            label for key, _, label in _PLATFORMS if key in st.session_state.pub_platforms
        )
        schedule_str = f"{release_date.strftime('%B %d, %Y')} at {release_time.strftime('%I:%M %p')}"

        render_html(f"""
        <div class="mw-card" style="border-left:3px solid #22C55E;margin-bottom:1rem;">
            <div style="font-size:13px;color:#F0EDE8;font-weight:600;margin-bottom:4px;">Publishing Summary</div>
            <div style="font-size:13px;color:#8A8480;">
                <strong style="color:#22C55E;">{len(approved)}</strong> asset(s) →
                <strong style="color:#F0EDE8;">{platforms_label}</strong> on
                <strong style="color:#D4A853;">{schedule_str}</strong>
            </div>
        </div>
        """)

        if st.button(
            f"🚀  Add {len(approved)} Asset(s) to Publish Queue",
            type="primary",
            use_container_width=True,
            key="pub_add_queue",
        ):
            # Mark all approved as published
            for job in approved:
                try:
                    update_job_status(artist_id, job["job_id"], "published")
                except Exception:
                    pass

            # Build download checklist
            checklist_lines = [
                f"# Publishing Queue — {artist_name}\n",
                f"*Scheduled: {schedule_str}*\n\n",
                f"**Platforms:** {platforms_label}\n\n---\n\n",
            ]
            gen_dir = Path(__file__).parent.parent.parent / "data" / "generated" / artist_id
            for job in approved:
                label_j = job.get("job_label", "Asset")
                icon_j  = job.get("job_icon", "📄")
                checklist_lines.append(f"## {icon_j} {label_j}\n\n")
                for k, _, plbl in _PLATFORMS:
                    if k in st.session_state.pub_platforms:
                        checklist_lines.append(f"- [ ] Post to {plbl}\n")
                checklist_lines.append("- [ ] Confirm post is live\n- [ ] Record live link\n\n")

            checklist_txt = "".join(checklist_lines)

            st.success(f"✓ {len(approved)} asset(s) added to Publish Queue! Scheduled for {schedule_str}.")

            dl_col, back_col = st.columns([1, 1])
            with dl_col:
                st.download_button(
                    "⬇  Download Publishing Checklist",
                    checklist_txt,
                    file_name=f"{artist_id}_publish_queue.md",
                    mime="text/markdown",
                    key="pub_dl_checklist",
                )
            with back_col:
                if st.button("🏠  Return Home", key="pub_home", use_container_width=True):
                    navigate_to("home")
            st.rerun()
    else:
        st.warning("Select at least one platform to continue.")

    # ── Approved asset list ───────────────────────────────────────────────────
    if approved:
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='mw-section-label'>Assets Ready to Publish</div>", unsafe_allow_html=True)
        for job in approved:
            lbl  = job.get("job_label", "Asset")
            icon = job.get("job_icon", "📄")
            render_html(
                f'<div class="mw-card" style="padding:0.875rem 1.25rem;margin-bottom:0.5rem;border-left:3px solid #22C55E;">'
                f'<div style="font-size:14px;font-weight:600;color:#F0EDE8;">{icon} {lbl}</div>'
                f'</div>'
            )

    # ── Publishing tips ───────────────────────────────────────────────────────
    st.info(
        "**Publishing Reminder:** Replace any `[STREAMING_LINK]` and `[DEVOTIONAL_LINK]` "
        "placeholders with live URLs before posting. Confirm your streaming link is live on "
        "all platforms before sharing social captions."
    )

    # ── Distribution destinations ─────────────────────────────────────────────
    _render_distribution_status(artist_id, artist_name)


def _render_distribution_status(artist_id: str, artist_name: str):
    """Show distribution destinations configured for the active artist."""
    dist  = load_distribution(artist_id)
    count = dist_configured_count(dist)

    if count == 0:
        return

    with st.expander(f"Configured Destinations — {artist_name}", expanded=False):
        platforms = dist_platform_display(dist)
        configured = [p for p in platforms if p["set"] and p["section"] in ("social", "streaming", "owned")]
        cols_per_row = 3
        rows = [configured[i:i+cols_per_row] for i in range(0, len(configured), cols_per_row)]
        for row in rows:
            cols = st.columns(cols_per_row)
            for col, p in zip(cols, row):
                with col:
                    render_html(
                        f'<div class="mw-card" style="padding:0.75rem 1rem;margin-bottom:0.5rem;">'
                        f'<div style="font-size:18px;margin-bottom:4px;">{p["icon"]}</div>'
                        f'<div style="font-size:12px;font-weight:600;color:#F0EDE8;">{p["label"]}</div>'
                        f'<div style="font-size:11px;color:#22C55E;margin-top:2px;">Configured</div>'
                        f'</div>'
                    )


def _render_legacy_publishing(lib: AssetLibrary, campaign_ids: list):
    """V3 legacy campaign publishing (advanced/Studio mode)."""
    default_cid = st.session_state.get("publishing_campaign_id", campaign_ids[-1])
    if default_cid not in campaign_ids:
        default_cid = campaign_ids[-1]
    idx = campaign_ids.index(default_cid)

    selected = st.selectbox("Campaign:", campaign_ids, index=idx, key="pub_legacy_sel")
    st.session_state.publishing_campaign_id = selected

    stats   = lib.get_campaign_stats(selected)
    assets  = lib.get_assets_for_campaign(selected)
    approved = [a for a in assets if a["status"] == "APPROVED"]
    pending  = [a for a in assets if a["status"] not in ("APPROVED", "REJECTED")]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total",    stats["total"])
    m2.metric("Approved", stats["approved"])
    m3.metric("Pending",  stats["pending"])
    m4.metric("Rejected", stats["rejected"])

    if pending:
        st.warning(f"{len(pending)} asset(s) still pending review.")
        if st.button("✅  Open Approval Queue", type="primary", key="pub_leg_approval"):
            st.session_state.approval_campaign_id = selected
            navigate_to("approval")
        return

    if not approved:
        st.info("No approved assets yet for this campaign.")
        return

    for asset in approved:
        meta         = json.loads(asset.get("metadata") or "{}")
        platforms    = json.loads(asset.get("platform_targets") or "[]")
        posting_time = meta.get("posting_time", "")
        desc         = asset.get("asset_description", asset.get("asset_type", ""))
        platform_str = " · ".join(p.replace("_", " ").title() for p in platforms) if platforms else "All platforms"
        time_str     = f" · {posting_time}" if posting_time else ""
        render_html(
            f'<div class="mw-card" style="padding:1rem 1.5rem;margin-bottom:0.5rem;border-left:3px solid #22C55E;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<div style="font-size:14px;font-weight:600;color:#F0EDE8;">{desc}</div>'
            f'<div style="font-size:12px;color:#8A8480;margin-top:2px;">{platform_str}{time_str}</div>'
            f'</div>'
            f'<span class="badge badge-approved">✓ Approved</span>'
            f'</div>'
            f'</div>'
        )

    checklist = _build_checklist(lib, selected, approved)
    st.download_button(
        "⬇  Download Publishing Checklist",
        checklist,
        file_name=f"{selected}_publishing_checklist.md",
        mime="text/markdown",
        type="primary",
        key="pub_leg_dl",
    )


def _build_checklist(lib: AssetLibrary, campaign_id: str, approved: list) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Publishing Checklist — {campaign_id}\n\n",
        f"*Generated by MusicWorks™ V5 — {now}*\n\n",
        f"**{len(approved)} assets approved and ready to publish.**\n\n",
        "> Replace `[STREAMING_LINK]` and `[DEVOTIONAL_LINK]` with live URLs before posting.\n\n",
        "---\n\n",
    ]
    for asset in approved:
        meta         = json.loads(asset.get("metadata") or "{}")
        platforms    = json.loads(asset.get("platform_targets") or "[]")
        desc         = asset.get("asset_description", "")
        posting_time = meta.get("posting_time", "")
        lines.append(f"## {desc}\n\n")
        lines.append(f"- **File:** `{asset.get('file_name', '')}`\n")
        if platforms:
            lines.append(f"- **Platforms:** {', '.join(p.replace('_', ' ').title() for p in platforms)}\n")
        if posting_time:
            lines.append(f"- **Recommended time:** {posting_time}\n")
        lines.append(f"- **Approved:** {(asset.get('approved_at') or '')[:10]}\n\n")
        lines.append("**Steps:**\n")
        for p in (platforms or ["all platforms"]):
            lines.append(f"- [ ] Post to {p.replace('_', ' ').title()}\n")
        lines.append("- [ ] Confirm post is live\n")
        lines.append("- [ ] Record live link\n\n")
    return "".join(lines)
