"""MusicWorks™ V5 — Media Library (Creator Mode)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import navigate_to, render_html


_TYPE_FILTERS = {
    "All Assets":  None,
    "Writing":     {"blog", "email", "press_release", "church_outreach", "post_launch", "reaction"},
    "Video":       {"instagram_reel", "tiktok", "youtube_short", "facebook_reel", "x_video",
                    "rumble_video", "spotify_canvas", "behind_scenes"},
    "Image":       {"thumbnail_set", "quote_card", "story_slides", "countdown"},
    "Audio":       {"voice_over", "audio_preview"},
}


def render():
    render_html("""
    <div style="margin-bottom:1.5rem;">
        <h1 style="margin:0 0 4px 0;">📚 Media Library</h1>
        <p style="color:#8A8480;font-size:15px;margin:0;">
            Your approved and published assets — ready to download and share.
        </p>
    </div>
    """)

    try:
        from brand_brain.artist_library import list_artists
        from execution.production_queue import list_jobs
    except Exception as e:
        st.error(f"Could not load library: {e}")
        return

    artists = list_artists()
    if not artists:
        render_html("""
        <div class="mw-card" style="text-align:center;padding:3rem;color:#8A8480;">
            <div style="font-size:40px;margin-bottom:1rem;">👥</div>
            <div style="font-size:18px;color:#F0EDE8;margin-bottom:0.5rem;">No artists yet</div>
            <div style="font-size:13px;">Create an artist profile and generate content first.</div>
        </div>
        """)
        if st.button("👥 Add Artist", type="primary", key="ml_add_artist"):
            navigate_to("artists")
        return

    names = [a["artist_name"] for a in artists]
    ids   = [a["artist_id"]   for a in artists]
    sel   = st.selectbox("Artist:", range(len(names)), format_func=lambda i: names[i], key="ml_artist")
    sel_id = ids[sel]

    all_jobs    = list_jobs(sel_id)
    approved    = [j for j in all_jobs if j.get("status") in ("approved", "published")]
    gen_dir     = Path(__file__).parent.parent.parent / "data" / "generated" / sel_id

    if not approved:
        render_html("""
        <div class="mw-card" style="text-align:center;padding:3rem;color:#8A8480;">
            <div style="font-size:40px;margin-bottom:1rem;">📭</div>
            <div style="font-size:18px;color:#F0EDE8;margin-bottom:0.5rem;">No approved assets yet</div>
            <div style="font-size:13px;">Complete a release to see your assets here.</div>
        </div>
        """)
        if st.button("🚀 Start a Release", type="primary", key="ml_start_release"):
            navigate_to("wizard")
        return

    published   = [j for j in approved if j.get("status") == "published"]
    unpublished = [j for j in approved if j.get("status") != "published"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Approved",    len(approved))
    m2.metric("Published",         len(published))
    m3.metric("Ready to Publish",  len(unpublished))

    # Type filter
    filter_choice = st.selectbox("Filter by Type:", list(_TYPE_FILTERS.keys()), key="ml_type_filter")
    filter_types  = _TYPE_FILTERS[filter_choice]

    if filter_types is not None:
        display_jobs = [j for j in approved if j.get("phase", "") in filter_types]
    else:
        display_jobs = approved

    if not display_jobs:
        st.info(f"No assets in '{filter_choice}' category yet.")
        return

    st.markdown(f"<div class='mw-section-label'>{filter_choice} — {len(display_jobs)} asset(s)</div>", unsafe_allow_html=True)

    for job in display_jobs:
        label  = job.get("job_label", "Asset")
        icon   = job.get("job_icon",  "📄")
        status = job.get("status",    "approved")
        jid    = job["job_id"]
        phase  = job.get("phase", "")

        status_badge = "🔵 Published" if status == "published" else "✅ Approved"
        out_file     = gen_dir / f"{jid}.md"

        with st.expander(f"{icon} {label}  ·  {status_badge}", expanded=False):
            # Metadata row
            mc1, mc2, mc3 = st.columns(3)
            mc1.caption(f"Type: {phase.replace('_',' ').title()}")
            mc2.caption(f"Status: {status.title()}")
            approved_at = job.get("approved_at", "")
            mc3.caption(f"Approved: {approved_at[:10] if approved_at else '—'}")

            if out_file.exists():
                content = out_file.read_text(encoding="utf-8")

                # Content preview
                st.markdown(
                    f'<div style="background:#080810;border:1px solid #1E1E1E;border-radius:10px;'
                    f'padding:1rem 1.25rem;font-size:13px;color:#C8C4BE;line-height:1.7;'
                    f'max-height:280px;overflow-y:auto;white-space:pre-wrap;margin-bottom:0.75rem;">'
                    f'{content[:2000]}{"…" if len(content) > 2000 else ""}</div>',
                    unsafe_allow_html=True
                )

                dl_col, pub_col = st.columns([1, 1])
                with dl_col:
                    st.download_button(
                        "⬇ Download",
                        content.encode("utf-8"),
                        file_name=f"{label.replace(' ','_')}_{jid}.md",
                        mime="text/markdown",
                        key=f"ml_dl_{jid}",
                    )
                with pub_col:
                    if status != "published":
                        if st.button("🚀 Publish This", key=f"ml_pub_{jid}", use_container_width=True, type="primary"):
                            navigate_to("publishing")
            else:
                st.caption("Content file not found — asset may still be generating.")

    render_html("""
    <div style="margin-top:2rem;text-align:center;padding:1.25rem;border-top:1px solid #1E1E1E;">
        <div style="font-size:12px;color:#6A6460;">
            Human-led. AI-assisted. Scripture-rooted.
        </div>
    </div>
    """)
