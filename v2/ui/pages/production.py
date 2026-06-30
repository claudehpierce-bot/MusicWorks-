"""MusicWorks™ V4 — Production Queue: create, manage, and generate all media jobs."""
import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, render_html
from brand_brain.artist_library import list_artists, load_artist
from execution.production_queue import (
    JOB_TYPES, JOB_TYPE_META, STATUS_COLOR, STATUS_LABELS, PHASE_LABELS, PHASES,
    list_jobs, create_job, update_job_status, delete_job, queue_stats, save_job,
)
from execution.media_calendar import generate_calendar
from execution.distrokid_store import list_releases, upsert_release, get_release
from execution.workers import get_worker


def render():
    page_header("Production Queue", "Every deliverable. Every platform. Every phase.", "📋")

    artists = list_artists()
    if not artists:
        render_html('<div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;"><div style="font-size:36px; margin-bottom:1rem;">📋</div><div>Create an artist first.</div></div>')
        return

    artist_names = [a["artist_name"] for a in artists]
    artist_ids   = [a["artist_id"]   for a in artists]
    sel_idx  = st.selectbox("Artist:", range(len(artist_names)),
                             format_func=lambda i: artist_names[i], key="pq_artist")
    sel_id   = artist_ids[sel_idx]
    sel_name = artist_names[sel_idx]

    tab_new, tab_queue, tab_generate = st.tabs(["📋  Register Release", "⚙️  Production Queue", "🤖  Generate Content"])

    # ── TAB 1: Register Release (DistroKid metadata) ─────────────────────────
    with tab_new:
        render_html('<div class="mw-section-label">Register a Release</div>')
        st.caption("Enter your song's release information. MusicWorks uses this to anchor every campaign job.")

        releases = list_releases(sel_id)
        song_options = ["+ New Release"] + [f"{r['song_title']} ({r['release_date']})" for r in releases]
        sel_song = st.selectbox("Song:", song_options, key="pq_song_sel")

        existing: dict = {}
        song_id_prefill = ""
        if sel_song != "+ New Release" and releases:
            idx = song_options.index(sel_song) - 1
            existing = releases[idx]
            song_id_prefill = existing.get("song_id", "")

        with st.form("release_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                song_title    = st.text_input("Song title *", value=existing.get("song_title", ""), placeholder="e.g. HLANGANA")
                release_date  = st.date_input("Release date *", value=_parse_date(existing.get("release_date")))
                streaming_url = st.text_input("Streaming URL (Linktree / smartlink)", value=existing.get("streaming_url", ""), placeholder="https://")
                spotify_url   = st.text_input("Spotify URL", value=existing.get("spotify_url", ""), placeholder="https://open.spotify.com/...")
                apple_url     = st.text_input("Apple Music URL", value=existing.get("apple_music_url", ""), placeholder="https://music.apple.com/...")
            with col_b:
                pre_save_link = st.text_input("Pre-save link", value=existing.get("pre_save_link", ""), placeholder="https://")
                upc           = st.text_input("UPC", value=existing.get("upc", ""))
                isrc          = st.text_input("ISRC (optional)", value=existing.get("isrc", ""))
                store_url     = st.text_input("DistroKid Store URL", value=existing.get("store_url", ""), placeholder="https://distrokid.com/...")
                album_url     = st.text_input("Album URL", value=existing.get("album_url", ""), placeholder="https://")
                campaign_mode = st.selectbox("Campaign mode", ["blitz", "standard", "slow"],
                                             help="Blitz = all phases; Standard = pre + launch + post; Slow = launch only")

            saved = st.form_submit_button("💾  Save Release & Build Calendar", type="primary")

        if saved:
            if not song_title.strip():
                st.error("Song title is required.")
            else:
                from brand_brain.artist_library import make_slug
                sid = song_id_prefill or make_slug(song_title)
                upsert_release(sel_id, sid, {
                    "song_title":     song_title.strip(),
                    "release_date":   str(release_date),
                    "pre_save_link":  pre_save_link.strip(),
                    "streaming_url":  streaming_url.strip(),
                    "spotify_url":    spotify_url.strip(),
                    "apple_music_url": apple_url.strip(),
                    "upc":            upc.strip(),
                    "isrc":           isrc.strip(),
                    "store_url":      store_url.strip(),
                    "album_url":      album_url.strip(),
                    "status":         "upcoming",
                })
                jobs = generate_calendar(
                    artist_id=sel_id,
                    song_id=sid,
                    song_title=song_title.strip(),
                    release_date_str=str(release_date),
                    campaign_mode=campaign_mode,
                )
                st.success(f"Release registered. {len(jobs)} production jobs created in the queue.")
                st.rerun()

    # ── TAB 2: Production Queue ───────────────────────────────────────────────
    with tab_queue:
        stats = queue_stats(sel_id)
        all_jobs = list_jobs(sel_id)

        # Stats row
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Total",      stats.get("total", 0))
        m2.metric("Pending",    stats.get("pending", 0))
        m3.metric("Generating", stats.get("generating", 0))
        m4.metric("In Review",  stats.get("review", 0))
        m5.metric("Approved",   stats.get("approved", 0))
        m6.metric("Published",  stats.get("published", 0))

        if not all_jobs:
            render_html('<div class="mw-card" style="text-align:center; padding:2rem; color:#8A8480; margin-top:1rem;">No jobs yet. Register a release above to generate your production queue.</div>')
        else:
            # Filters
            col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
            with col_f1:
                phase_filter = st.selectbox("Phase:", ["All"] + [PHASE_LABELS[p] for p in PHASES], key="pq_phase")
            with col_f2:
                status_filter = st.selectbox("Status:", ["All"] + [l for _, l, _ in [
                    ("pending","Pending",""), ("queued","Queued",""), ("generating","Generating",""),
                    ("review","In Review",""), ("approved","Approved",""), ("published","Published",""), ("rejected","Rejected","")
                ]], key="pq_status")
            with col_f3:
                worker_filter = st.selectbox("Worker:", ["All", "Claude", "Veo", "Hedra", "ElevenLabs", "Canva"], key="pq_worker")

            phase_rev   = {v: k for k, v in PHASE_LABELS.items()}
            status_rev  = {"Pending":"pending","Queued":"queued","Generating":"generating",
                           "In Review":"review","Approved":"approved","Published":"published","Rejected":"rejected"}
            worker_rev  = {"Claude":"claude","Veo":"veo","Hedra":"hedra","ElevenLabs":"elevenlabs","Canva":"canva"}

            filtered = [j for j in all_jobs
                if (phase_filter == "All" or j.get("phase") == phase_rev.get(phase_filter))
                and (status_filter == "All" or j.get("status") == status_rev.get(status_filter))
                and (worker_filter == "All" or j.get("worker") == worker_rev.get(worker_filter))
            ]
            st.caption(f"Showing {len(filtered)} of {len(all_jobs)} jobs")

            for job in filtered:
                _render_job_card(job, sel_id)

        # Manual job creation
        st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
        with st.expander("+ Add a Single Job Manually", expanded=False):
            _render_manual_job_form(sel_id, list_releases(sel_id))

    # ── TAB 3: Generate Content ───────────────────────────────────────────────
    with tab_generate:
        render_html('<div class="mw-section-label">Generate Content</div>')
        st.caption("Select a pending job and let the AI worker generate the content brief or text.")

        pending_jobs = [j for j in list_jobs(sel_id) if j.get("status") in ("pending", "queued")]
        if not pending_jobs:
            render_html('<div class="mw-card" style="padding:1.5rem; text-align:center; color:#8A8480;">No pending jobs. Register a release or add jobs manually.</div>')
        else:
            job_labels = [f"{j['job_icon']}  {j['job_label']} ({PHASE_LABELS.get(j.get('phase',''),'')}) — {j.get('scheduled_date','')[:10]}" for j in pending_jobs]
            sel_job_idx = st.selectbox("Select job to generate:", range(len(pending_jobs)),
                                        format_func=lambda i: job_labels[i], key="gen_job_sel")
            sel_job = pending_jobs[sel_job_idx]

            worker_key = sel_job.get("worker", "claude")
            worker = get_worker(worker_key)

            if worker:
                col_info, col_act = st.columns([3, 1])
                with col_info:
                    render_html(f"""
                    <div class="mw-card" style="padding:1rem;">
                        <div style="font-size:13px; color:#8A8480; margin-bottom:6px;">Worker assigned</div>
                        <div style="font-size:22px;">{worker.icon}  <span style="font-size:16px; font-weight:700; color:#F0EDE8;">{worker.name}</span></div>
                        <div style="font-size:12px; color:#C8C4BE; margin-top:4px;">{worker.description}</div>
                        <div style="font-size:12px; color:#8A8480; margin-top:6px;">Estimated time: {worker.estimate_time(sel_job)}</div>
                        <div style="margin-top:8px;">{worker.status_pill()}</div>
                    </div>
                    """)
                with col_act:
                    extra_notes = st.text_area("Additional notes:", height=100, key=f"gen_notes_{sel_job['job_id']}")

            st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)

            if st.button("🤖  Generate", type="primary", key=f"gen_btn_{sel_job['job_id']}"):
                if not worker:
                    st.error("No worker configured for this job type.")
                else:
                    brain = load_artist(sel_id)
                    brand_ctx = _build_brand_context(brain)
                    if extra_notes:
                        sel_job = dict(sel_job)
                        sel_job["notes"] = extra_notes

                    with st.spinner(f"{worker.icon} {worker.name} generating…"):
                        result = worker.generate(sel_job, brand_context=brand_ctx)

                    if result.success:
                        # Save output text
                        out_dir = Path(__file__).parent.parent.parent / "data" / "generated" / sel_id
                        out_dir.mkdir(parents=True, exist_ok=True)
                        out_file = out_dir / f"{sel_job['job_id']}.md"
                        out_file.write_text(result.output_text, encoding="utf-8")

                        update_job_status(sel_id, sel_job["job_id"], "review")
                        mock_badge = " (mock)" if result.mock else ""
                        st.success(f"Generated{mock_badge}. Job moved to Review.")
                        st.markdown("---")
                        st.markdown(result.output_text)
                        if result.metadata:
                            st.caption(str(result.metadata))
                    else:
                        st.error(f"Generation failed: {result.error}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _render_job_card(job: dict, artist_id: str):
    jid    = job["job_id"]
    icon   = job.get("job_icon", "📄")
    label  = job.get("job_label", "")
    phase  = PHASE_LABELS.get(job.get("phase", ""), "")
    status = job.get("status", "pending")
    color  = STATUS_COLOR.get(status, "#6A6460")
    slabel = STATUS_LABELS.get(status, status)
    sd     = (job.get("scheduled_date") or "")[:10]
    worker = job.get("worker", "")

    with st.expander(f"{icon}  {label}  ·  {phase}  ·  {sd}", expanded=False):
        col_a, col_b, col_c = st.columns([2, 2, 1])
        with col_a:
            st.caption(f"Status: {slabel}  ·  Worker: {worker.title()}  ·  Priority: {job.get('priority','')}")
        with col_b:
            if job.get("notes"):
                st.caption(f"Notes: {job['notes']}")
        with col_c:
            render_html(f'<span style="color:{color}; font-size:12px; font-weight:700;">● {slabel}</span>')

        # Status controls
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            if status == "pending" and st.button("Queue →", key=f"jq_{jid}", use_container_width=True):
                update_job_status(artist_id, jid, "queued")
                st.rerun()
        with col_s2:
            if status in ("pending","queued") and st.button("Skip to Review →", key=f"jr_{jid}", use_container_width=True):
                update_job_status(artist_id, jid, "review")
                st.rerun()
        with col_s3:
            if status == "review" and st.button("✓ Approve", key=f"ja_{jid}", use_container_width=True, type="primary"):
                update_job_status(artist_id, jid, "approved")
                st.rerun()
        with col_s4:
            if st.button("🗑 Delete", key=f"jdel_{jid}", use_container_width=True):
                delete_job(artist_id, jid)
                st.rerun()

        # Generated content
        out_file = Path(__file__).parent.parent.parent / "data" / "generated" / artist_id / f"{jid}.md"
        if out_file.exists():
            with st.expander("View generated content", expanded=False):
                st.markdown(out_file.read_text(encoding="utf-8")[:4000])
            col_dl, _ = st.columns([1, 3])
            with col_dl:
                st.download_button("⬇ Download",
                                   out_file.read_bytes(),
                                   file_name=f"{jid}_{label.replace(' ','_')}.md",
                                   key=f"dl_{jid}")


def _render_manual_job_form(artist_id: str, releases: list):
    with st.form("manual_job_form"):
        job_type_labels = [f"{icon}  {lbl}" for key, lbl, icon, *_ in JOB_TYPES]
        job_type_keys   = [key for key, *_ in JOB_TYPES]
        sel_type_label  = st.selectbox("Job type:", job_type_labels)
        sel_type_key    = job_type_keys[job_type_labels.index(sel_type_label)]

        if releases:
            rel_options = [f"{r['song_title']} ({r['release_date']})" for r in releases]
            rel_idx = st.selectbox("Song (optional):", ["None"] + rel_options)
            sel_rel = releases[rel_idx - 1] if rel_idx != "None" and isinstance(rel_idx, int) else None
        else:
            sel_rel = None
        phase  = st.selectbox("Phase:", list(PHASE_LABELS.keys()), format_func=lambda k: PHASE_LABELS[k])
        sched  = st.date_input("Scheduled date:")
        notes  = st.text_area("Notes:", height=60)
        prio   = st.slider("Priority:", 1, 10, 5)
        submitted = st.form_submit_button("Create Job", type="primary")

    if submitted:
        create_job(
            artist_id=artist_id,
            job_type=sel_type_key,
            song_id=sel_rel.get("song_id", "") if sel_rel else "",
            song_title=sel_rel.get("song_title", "") if sel_rel else "",
            release_date=sel_rel.get("release_date", "") if sel_rel else "",
            phase=phase,
            scheduled_date=str(sched),
            notes=notes,
            priority=prio,
        )
        st.success("Job created.")
        st.rerun()


def _build_brand_context(brain) -> str:
    if not brain:
        return ""
    parts = [
        f"Artist: {brain.artist_name}",
        f"Mission: {brain.mission}",
        f"Tagline: {brain.tagline}",
        f"Heritage: {', '.join(brain.heritage)}",
        f"Genre: {', '.join(brain.genre)}",
        f"Tone: {', '.join(brain.brand_voice.tone[:3])}",
        f"Avoid: {', '.join(brain.brand_voice.avoid[:3])}",
        f"Theology: {brain.theological_guardrails.theological_stance[:200]}",
    ]
    return "\n".join(parts)


def _parse_date(s: str | None):
    from datetime import date
    if not s:
        return date.today()
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except Exception:
        return date.today()
