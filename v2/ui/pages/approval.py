"""MusicWorks™ V5 — Asset Review (single one-at-a-time review flow)."""
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, render_html


# ── Helper functions ──────────────────────────────────────────────────────────

def _fmt_time(iso: str) -> str:
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d at %H:%M UTC")
    except Exception:
        return iso[:10]


def _founder_quote_pending(content: str) -> bool:
    """Press releases ship with a bracketed placeholder that must be replaced
    with the founder's own words before the asset can be approved."""
    return "[FOUNDER QUOTE" in content


def _save_founder_quote(out_file: Path, quote: str):
    content = out_file.read_text(encoding="utf-8")
    updated = re.sub(r"\[FOUNDER QUOTE[^\]]*\]", quote, content)
    out_file.write_text(updated, encoding="utf-8")


# ── V5 one-at-a-time review ───────────────────────────────────────────────────

def _v5_review(artist_id: str, all_jobs: list, gen_dir: Path):
    """Single-asset review with Previous / Next — the only Asset Review flow."""
    from execution.production_queue import update_job_status, PHASE_LABELS

    FILTER_OPTIONS = {
        "all":       ("All Assets",  lambda j: j.get("status") in ("review", "approved")),
        "review":    ("Review Now",  lambda j: j.get("status") == "review"),
        "approved":  ("Approved",    lambda j: j.get("status") == "approved"),
        "published": ("Published",   lambda j: j.get("status") == "published"),
    }

    active_filter = st.session_state.get("v5_filter", "all")

    # Count per filter
    counts = {}
    for key, (label, pred) in FILTER_OPTIONS.items():
        counts[key] = sum(1 for j in all_jobs if pred(j))

    filtered = [j for j in all_jobs if FILTER_OPTIONS[active_filter][1](j)]
    total    = len(filtered)

    if total == 0:
        review_count = counts.get("review", 0)
        render_html(f"""
        <div class="mw-asset-preview" style="text-align:center; padding:3rem; color:#8A8480;">
            <div style="font-size:48px; margin-bottom:1rem;">{'✅' if review_count == 0 else '📭'}</div>
            <div style="font-size:18px; color:#F0EDE8; margin-bottom:0.5rem;">
                {'All assets reviewed!' if review_count == 0 else 'Nothing in this filter'}
            </div>
            <div style="font-size:13px;">
                {'Ready to head to Publishing.' if review_count == 0 else 'Switch filter to see other assets.'}
            </div>
        </div>
        """)
        if review_count == 0 and counts.get("approved", 0) > 0:
            if st.button("🚀 Go to Publishing", type="primary", key="v5_goto_pub"):
                navigate_to("publishing")
        return

    if "v5_review_idx" not in st.session_state:
        st.session_state.v5_review_idx = 0
    # Find first "review" status job if filter is "all"
    if active_filter == "all" and st.session_state.get("_v5_auto_focus", True):
        first_review = next((i for i, j in enumerate(filtered) if j.get("status") == "review"), None)
        if first_review is not None:
            st.session_state.v5_review_idx = first_review
        st.session_state._v5_auto_focus = False

    idx = max(0, min(st.session_state.v5_review_idx, total - 1))
    job = filtered[idx]

    # ── Layout: filter column + asset column ──────────────────────────────────
    left, right = st.columns([2, 5], gap="medium")

    with left:
        # Filter tabs
        filter_html = '<div class="mw-filter-list">'
        for key, (label, pred) in FILTER_OPTIONS.items():
            active_cls = "mw-filter-item-active" if key == active_filter else ""
            cnt        = counts[key]
            filter_html += (
                f'<div class="mw-filter-item {active_cls}">'
                f'<span>{label}</span>'
                f'<span class="mw-filter-count">{cnt}</span>'
                f'</div>'
            )
        filter_html += "</div>"
        render_html(filter_html)

        # Filter buttons
        for key, (label, _) in FILTER_OPTIONS.items():
            btn_type = "primary" if key == active_filter else "secondary"
            if st.button(label, key=f"v5_f_{key}", use_container_width=True, type=btn_type):
                st.session_state.v5_filter = key
                st.session_state.v5_review_idx = 0
                st.rerun()

        # Asset list (clickable)
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        render_html('<div style="font-size:10px;color:#6A6460;font-weight:600;letter-spacing:0.6px;text-transform:uppercase;margin-bottom:0.4rem;">Assets</div>')
        for i, j in enumerate(filtered):
            s       = j.get("status", "")
            dot     = {"review": "🟡", "approved": "🟢", "rejected": "🔴", "published": "🔵"}.get(s, "⚪")
            lbl     = j.get("job_label", "Asset")
            is_cur  = (i == idx)
            border  = "border-left:3px solid #FF6B2B;" if is_cur else "border-left:3px solid transparent;"
            bg      = "background:rgba(255,107,43,0.07);" if is_cur else ""
            render_html(
                f'<div style="padding:6px 10px;border-radius:6px;font-size:12px;'
                f'color:{"#F0EDE8" if is_cur else "#8A8480"};margin-bottom:2px;{border}{bg}">'
                f'{dot} {lbl[:28]}</div>'
            )
            if st.button(f"Select", key=f"v5_sel_{i}_{j['job_id']}", use_container_width=True):
                st.session_state.v5_review_idx = i
                st.rerun()

    with right:
        # Progress label
        jid    = job["job_id"]
        icon   = job.get("job_icon", "📄")
        label  = job.get("job_label", "")
        phase  = PHASE_LABELS.get(job.get("phase", ""), "")
        status = job.get("status", "pending")

        STATUS_COLORS = {"review": "#F59E0B", "approved": "#22C55E", "rejected": "#EF4444", "published": "#3B82F6"}
        STATUS_ICONS  = {"review": "🟡", "approved": "🟢", "rejected": "🔴", "published": "🔵"}
        s_color = STATUS_COLORS.get(status, "#8A8480")
        s_icon  = STATUS_ICONS.get(status, "⚪")

        render_html(
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">'
            f'<div style="font-size:13px;color:#8A8480;">Asset {idx + 1} of {total}</div>'
            f'<span style="background:{s_color}22;color:{s_color};font-size:11px;font-weight:600;'
            f'padding:3px 10px;border-radius:20px;border:1px solid {s_color}44;">'
            f'{s_icon} {status.title()}</span>'
            f'</div>'
        )

        # ── Alternatives (V7 Constitution, Amendment I) ─────────────────────────
        # Regeneration never touches an existing job -- it creates a linked
        # alternative instead. Surface that link both directions: an asset
        # with alternatives pointing at it, and an asset that IS one.
        from execution.production_queue import get_job as _get_job

        alt_target_id = job.get("alternative_of", "")
        alt_target = _get_job(artist_id, alt_target_id) if alt_target_id else None
        alternatives_of_this = [j for j in all_jobs if j.get("alternative_of") == jid]

        if alternatives_of_this:
            st.info(f"🔄 {len(alternatives_of_this)} new alternative(s) available for this asset — regenerated from your Live Creative Brief.")
            for alt in alternatives_of_this:
                if st.button(f"Compare with alternative ({alt.get('status','review')})", key=f"v5_gotoalt_{jid}_{alt['job_id']}", use_container_width=True):
                    match = next((i for i, j in enumerate(filtered) if j["job_id"] == alt["job_id"]), None)
                    if match is not None:
                        st.session_state.v5_review_idx = match
                    else:
                        st.session_state.v5_filter = "all"
                        st.session_state.v5_review_idx = 0
                    st.rerun()

        if alt_target:
            target_file = gen_dir / f"{alt_target_id}.md"
            target_content = target_file.read_text(encoding="utf-8") if target_file.exists() else "(no content)"
            st.markdown(f"**🔄 New alternative** — comparing against your current **{alt_target.get('status','').title()}** version:")
            with st.expander(f"Current ({alt_target.get('status','').title()}) — {alt_target.get('job_label','')}", expanded=False):
                st.markdown(
                    f'<div style="font-size:12px;color:#8A8480;white-space:pre-wrap;max-height:220px;overflow-y:auto;">{target_content[:2000]}</div>',
                    unsafe_allow_html=True,
                )
            st.caption("New Alternative ⬇")

        render_html(
            f'<div class="mw-asset-preview">'
            f'<div style="font-size:11px;color:#8A8480;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:0.4rem;">{phase}</div>'
            f'<div style="font-size:22px;font-weight:700;color:#F0EDE8;margin-bottom:1.25rem;">{icon} {label}</div>'
        )

        # Connector meta
        meta_file = gen_dir / f"{jid}_meta.json"
        meta      = {}
        if meta_file.exists():
            try:
                import json as _j
                meta = _j.loads(meta_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Provider/mock detail is Studio Mode operator info -- founders should
        # never see provider or worker language (V7 Constitution, Article IX).
        if meta and st.session_state.get("studio_mode"):
            provider = meta.get("provider_used", "mock")
            is_mock  = meta.get("mock", False)
            mock_tag = ' <span style="background:#F59E0B22;color:#F59E0B;font-size:10px;padding:2px 7px;border-radius:10px;font-weight:600;">MOCK</span>' if is_mock else ""
            render_html(
                f'<div style="font-size:12px;color:#6A6460;margin-bottom:1rem;">'
                f'Provider: <span style="color:#C8C4BE;">{provider}</span>{mock_tag}</div>'
            )

        # Video assets: preview the rendered clip, or offer manual upload when none exists
        is_video_job = job.get("worker") in ("veo", "hedra")
        mp4_path = gen_dir / f"{jid}.mp4"
        if is_video_job:
            if mp4_path.exists():
                st.video(str(mp4_path))
            else:
                st.info(
                    "📋 **Manual video production required.**\n\n"
                    "**Steps:**\n"
                    "1. Read the storyboard and prompts below\n"
                    "2. Generate the clips with the assigned provider (Veo / Hedra)\n"
                    "3. Assemble the final cut in your editor of choice\n"
                    "4. Upload the finished MP4 below"
                )
                uploaded = st.file_uploader("Upload finished MP4:", type=["mp4"], key=f"v5_upload_{jid}")
                if uploaded:
                    gen_dir.mkdir(parents=True, exist_ok=True)
                    mp4_path.write_bytes(uploaded.getbuffer())
                    st.success(f"✓ Video saved: {uploaded.name}")
                    st.rerun()

        # Content preview
        out_file = gen_dir / f"{jid}.md"
        quote_pending = False
        if out_file.exists():
            content = out_file.read_text(encoding="utf-8")

            if job.get("job_type") == "press_release" and _founder_quote_pending(content):
                quote_pending = True
                st.warning(
                    "**⚠ ACTION REQUIRED BEFORE APPROVAL**\n\n"
                    "This press release contains a draft quote placeholder. "
                    "You must replace it with your own exact words — it will be attributed to you by name."
                )
                with st.form(key=f"v5_quote_form_{jid}"):
                    st.markdown("**Type your personal quote below:**")
                    founder_quote = st.text_area(
                        "Your quote:",
                        placeholder='"I grew up in church but never knew my own languages had words for what I was living..."',
                        height=100,
                        label_visibility="collapsed",
                    )
                    if st.form_submit_button("Save My Quote →"):
                        if founder_quote.strip():
                            _save_founder_quote(out_file, founder_quote.strip())
                            st.success("Quote saved. Review and approve.")
                            st.rerun()
                        else:
                            st.error("Please type your quote before saving.")

            st.markdown(
                f'<div style="background:#080810;border:1px solid #1E1E1E;border-radius:10px;'
                f'padding:1.25rem 1.5rem;font-size:13px;color:#C8C4BE;line-height:1.7;'
                f'max-height:320px;overflow-y:auto;white-space:pre-wrap;font-family:inherit;">'
                f'{content[:3000]}{"…" if len(content) > 3000 else ""}</div>',
                unsafe_allow_html=True
            )
            render_html("</div>")  # close mw-asset-preview

            # Version history
            versions = job.get("versions", [])
            if versions:
                with st.expander(f"Version History ({len(versions)})", expanded=False):
                    for v in reversed(versions):
                        st.caption(f"v{v.get('version','')} — {v.get('at','')[:16]}")
        else:
            render_html(
                '<div style="font-size:13px;color:#8A8480;padding:1.5rem 0;">No content generated yet.</div>'
                '</div>'  # close mw-asset-preview
            )

        # ── Action buttons ────────────────────────────────────────────────────
        if status == "review":
            st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

            # Approving an alternative whose target already went somewhere
            # meaningful (approved/scheduled/published) requires an explicit,
            # separate confirmation -- it is never automatic (Amendment I,
            # Principle 7). The target is retired to "superseded", never deleted.
            needs_supersede_confirm = bool(alt_target) and alt_target.get("status") in ("approved", "scheduled", "published")
            confirm_key = f"v5_supersede_confirm_{jid}"

            if needs_supersede_confirm and st.session_state.get(confirm_key):
                st.warning(
                    f"Approving this will retire your previously {alt_target.get('status')} version — "
                    "it's kept as history, not deleted."
                )
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("Yes, Replace It", key=f"v5a_confirm_{jid}", type="primary", use_container_width=True):
                        update_job_status(artist_id, jid, "approved")
                        update_job_status(artist_id, alt_target_id, "superseded")
                        # The live content for this group just genuinely
                        # changed -- this is the actual trigger for a
                        # re-review, not the regeneration that created the
                        # alternative (V7 Phase 2 design).
                        from execution.brief_dependencies import job_type_to_regen_group
                        target_group = job_type_to_regen_group(job.get("job_type"))
                        campaign_id = job.get("campaign_id", "")
                        if target_group and campaign_id:
                            from execution.asset_library import AssetLibrary
                            from execution.orchestrator import RenderOrchestrator
                            try:
                                from config import ANTHROPIC_API_KEY
                                mock_mode = not bool(ANTHROPIC_API_KEY)
                            except ImportError:
                                mock_mode = True
                            orchestrator = RenderOrchestrator(AssetLibrary(), mock_mode=mock_mode)
                            orchestrator.review_group(artist_id, campaign_id, target_group, printer=lambda *a: None)
                        st.session_state.pop(confirm_key, None)
                        st.session_state.v5_review_idx = min(idx + 1, total - 1)
                        st.success("Approved — previous version retired, not deleted.")
                        st.rerun()
                with cc2:
                    if st.button("Cancel", key=f"v5a_cancel_{jid}", use_container_width=True):
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
                st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

            ba, bb, bc, bd = st.columns(4)
            with ba:
                if quote_pending:
                    st.button("✓ Approve", key=f"v5a_{jid}", disabled=True,
                              help="Save your personal quote first.", use_container_width=True)
                elif needs_supersede_confirm:
                    if st.button("✓ Approve (Replaces Current)", key=f"v5a_{jid}", type="primary", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()
                elif st.button("✓ Approve", key=f"v5a_{jid}", type="primary", use_container_width=True):
                    update_job_status(artist_id, jid, "approved")
                    st.session_state.v5_review_idx = min(idx + 1, total - 1)
                    st.success("Approved!")
                    st.rerun()
            with bb:
                if st.button("↺ Re-render", key=f"v5r_{jid}", use_container_width=True):
                    update_job_status(artist_id, jid, "pending")
                    st.info("Reset to Pending. Go to Production Queue to regenerate.")
                    st.rerun()
            with bc:
                rev_key = f"v5rev_{jid}"
                if st.button("✏ Revise", key=f"v5rv_btn_{jid}", use_container_width=True):
                    st.session_state[rev_key] = not st.session_state.get(rev_key, False)
                if st.session_state.get(rev_key):
                    with st.form(f"v5rv_form_{jid}"):
                        notes = st.text_area("What needs to change?", height=80)
                        if st.form_submit_button("Submit Revision"):
                            if notes.strip():
                                from execution.production_queue import get_job, save_job
                                j = get_job(artist_id, jid)
                                if j:
                                    j["notes"] = notes.strip()
                                    save_job(j)
                                update_job_status(artist_id, jid, "pending")
                                st.session_state.pop(rev_key, None)
                                st.rerun()
            with bd:
                if st.button("✗ Reject", key=f"v5rej_{jid}", use_container_width=True):
                    update_job_status(artist_id, jid, "rejected")
                    st.rerun()

            # Download
            if out_file.exists():
                st.download_button(
                    "⬇ Download",
                    out_file.read_bytes(),
                    file_name=f"{label.replace(' ','_')}_{jid}.md",
                    mime="text/markdown",
                    key=f"v5dl_{jid}",
                )

        elif status == "approved":
            render_html(f'<div style="color:#22C55E;font-size:13px;font-weight:600;margin-bottom:0.5rem;">✓ Approved {_fmt_time(job.get("approved_at",""))}</div>')
            pub_col, rer_col = st.columns([1, 1])
            with pub_col:
                if st.button("🚀 Add to Publishing Queue", key=f"v5pub_{jid}", type="primary", use_container_width=True):
                    navigate_to("publishing")
            with rer_col:
                if st.button("↺ Re-render", key=f"v5rr2_{jid}", use_container_width=True):
                    update_job_status(artist_id, jid, "pending")
                    st.info("Reset to Pending.")
                    st.rerun()
            if out_file.exists():
                st.download_button(
                    "⬇ Download",
                    out_file.read_bytes(),
                    file_name=f"{label.replace(' ','_')}_{jid}.md",
                    mime="text/markdown",
                    key=f"v5dl2_{jid}",
                )

        # ── Previous / Next navigation ────────────────────────────────────────
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        pn1, pn2, pn3 = st.columns([1, 3, 1])
        with pn1:
            if idx > 0:
                if st.button("← Previous", key="v5_prev", use_container_width=True):
                    st.session_state.v5_review_idx = idx - 1
                    st.rerun()
        with pn2:
            # dots indicator
            dots = ""
            for di in range(total):
                if di == idx:
                    dots += '<span style="font-size:14px;color:#FF6B2B;">●</span> '
                elif di < total:
                    dots += '<span style="font-size:10px;color:#333;">●</span> '
            render_html(f'<div style="text-align:center;padding:6px 0;">{dots}</div>')
        with pn3:
            if idx < total - 1:
                if st.button("Next →", key="v5_next", use_container_width=True):
                    st.session_state.v5_review_idx = idx + 1
                    st.rerun()
            elif total > 0 and counts.get("approved", 0) > 0:
                if st.button("🚀 Publish", key="v5_pub_end", type="primary", use_container_width=True):
                    navigate_to("publishing")


def _render_v5_main_review():
    """Drives the single one-at-a-time Asset Review flow for production queue jobs."""
    from execution.production_queue import list_jobs
    from brand_brain.artist_library import list_artists

    artists = list_artists()
    if not artists:
        render_html("""
        <div class="mw-card" style="text-align:center;padding:2rem;color:#8A8480;">
            <div style="font-size:16px;color:#F0EDE8;margin-bottom:0.5rem;">No artists yet</div>
            <div style="font-size:13px;">Create an artist profile first, then run the Production Queue.</div>
        </div>
        """)
        if st.button("👥  Add Artist", type="primary", key="v5_add_artist"):
            navigate_to("artists")
        return

    # Artist selector
    names = [a["artist_name"] for a in artists]
    ids   = [a["artist_id"]   for a in artists]
    sel   = st.selectbox("Artist:", range(len(names)),
                         format_func=lambda i: names[i], key="v5_artist_sel")
    sel_id = ids[sel]

    all_jobs = list_jobs(sel_id)
    gen_dir  = Path(__file__).parent.parent.parent / "data" / "generated" / sel_id

    # Quick summary stats — same source Home's snapshot and Results use,
    # so the numbers never disagree between pages.
    from execution.production_queue import queue_stats
    stats = queue_stats(sel_id)
    review_n    = stats.get("review", 0)
    approved_n  = stats.get("approved", 0)
    published_n = stats.get("published", 0)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("In Review",  review_n)
    m2.metric("Approved",   approved_n)
    m3.metric("Published",  published_n)
    m4.metric("Total Jobs", stats.get("total", 0))

    if review_n > 0:
        st.warning(f"{review_n} asset(s) waiting for your review.")

    actionable = [j for j in all_jobs if j.get("status") in ("review", "approved")]
    if not actionable:
        render_html("""
        <div class="mw-card" style="text-align:center;padding:2rem;color:#8A8480;margin-top:0.5rem;">
            <div style="font-size:16px;color:#F0EDE8;margin-bottom:0.5rem;">No assets in review yet</div>
            <div style="font-size:13px;">Generate content in the Production Queue to populate this section.</div>
        </div>
        """)
        if st.button("📋  Go to Production Queue", type="primary", key="v5_goto_prod"):
            navigate_to("production")
        return

    _v5_review(sel_id, all_jobs, gen_dir)


# ── Main render ───────────────────────────────────────────────────────────────

def render():
    page_header("Asset Review", "Nothing publishes until you approve it.", "✅")
    _render_v5_main_review()
    st.caption("Human-led. AI-assisted. Scripture-rooted. Every decision is logged permanently.")
