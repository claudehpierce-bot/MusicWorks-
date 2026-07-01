"""MusicWorks™ V3 — Approval Queue page (integrated)."""
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, status_badge, ASSET_ICONS, TYPE_ORDER, render_html
from execution.asset_library import AssetLibrary


@st.cache_resource
def _get_library():
    return AssetLibrary()


# ── Helper functions ──────────────────────────────────────────────────────────

def _fmt_time(iso: str) -> str:
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d at %H:%M UTC")
    except Exception:
        return iso[:10]


def _render_decision_buttons(asset_id: str, atype: str, meta: dict, lib: AssetLibrary):
    blocked = atype == "press_release" and meta.get("requires_founder_input", False)

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col1:
        if blocked:
            st.button("✓ APPROVE", key=f"appr_{asset_id}", disabled=True,
                      help="Save your personal quote first.")
        else:
            if st.button("✓ APPROVE", key=f"appr_{asset_id}", type="primary"):
                lib.update_status(asset_id, "APPROVED")
                st.success("Approved!")
                st.rerun()

    with col2:
        show_key = f"show_rev_{asset_id}"
        if st.button("↺ REQUEST REVISION", key=f"rev_btn_{asset_id}"):
            st.session_state[show_key] = not st.session_state.get(show_key, False)

        if st.session_state.get(show_key):
            with st.form(key=f"rev_form_{asset_id}"):
                notes = st.text_area(
                    "What needs to change? Be specific:",
                    placeholder="e.g., Move scripture overlay to 0:08. Adjust tone in third paragraph.",
                    height=80,
                )
                if st.form_submit_button("Submit Revision"):
                    if notes.strip():
                        lib.update_status(asset_id, "REVISION_REQUESTED", founder_notes=notes)
                        st.session_state.pop(show_key, None)
                        st.info("Revision requested. Notes saved.")
                        st.rerun()
                    else:
                        st.error("Please describe what needs to change.")

    with col3:
        reject_key = f"show_reject_{asset_id}"
        if st.button("✗ REJECT", key=f"rej_btn_{asset_id}"):
            st.session_state[reject_key] = not st.session_state.get(reject_key, False)

        if st.session_state.get(reject_key):
            with st.form(key=f"rej_form_{asset_id}"):
                reason = st.text_area("Reason (optional):", height=60)
                if st.form_submit_button("Confirm Rejection"):
                    lib.update_status(asset_id, "REJECTED", founder_notes=reason)
                    st.session_state.pop(reject_key, None)
                    st.rerun()


def _render_press_release_quote_form(asset_id: str, lib: AssetLibrary):
    st.warning(
        "**⚠ ACTION REQUIRED BEFORE APPROVAL**\n\n"
        "This press release contains a draft quote. "
        "You must replace it with your own exact words — it will be attributed to you by name."
    )
    with st.form(key=f"quote_form_{asset_id}"):
        st.markdown("**Type your personal quote below:**")
        founder_quote = st.text_area(
            "Your quote:",
            placeholder='"I grew up in church but never knew my own languages had words for what I was living..."',
            height=100,
            label_visibility="collapsed",
        )
        if st.form_submit_button("Save My Quote →"):
            if founder_quote.strip():
                lib.update_press_release_quote(asset_id, founder_quote.strip())
                with sqlite3.connect(lib.db_path) as conn:
                    conn.execute(
                        "UPDATE assets SET metadata=? WHERE asset_id=?",
                        (json.dumps({"requires_founder_input": False, "quote_confirmed": True}), asset_id)
                    )
                    conn.commit()
                st.success("Quote saved. Review and approve.")
                st.rerun()
            else:
                st.error("Please type your quote before saving.")


def _render_video_card(asset: dict):
    file_path = asset.get("file_path", "")
    meta = json.loads(asset.get("metadata") or "{}")

    mp4_path = Path(file_path).parent / (Path(file_path).stem + ".mp4")
    if mp4_path.exists():
        st.video(str(mp4_path))
    else:
        st.info(
            "📋 **V2 — Manual video production required.**\n\n"
            f"Estimated production time: **{meta.get('estimated_production_time', '3–4 hours')}**\n\n"
            "**Steps:**\n"
            "1. Read the storyboard and Veo prompts below\n"
            "2. Open [veo.google.com](https://veo.google.com) and paste each Veo prompt\n"
            "3. Download and assemble clips in CapCut or Canva Video\n"
            "4. Upload the finished MP4 below"
        )

    content = asset.get("preview_text", "")
    if content:
        with st.expander("View storyboard + Veo prompts", expanded=False):
            st.markdown(content[:6000])

    uploaded = st.file_uploader(
        "Upload finished MP4:",
        type=["mp4"],
        key=f"upload_{asset['asset_id']}",
    )
    if uploaded:
        save_dir = Path(file_path).parent
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / uploaded.name
        save_path.write_bytes(uploaded.getbuffer())
        st.success(f"✓ Video saved: {uploaded.name}")


def _render_caption_preview(content: str):
    """Render caption preview with visual separation of parts."""
    if not content:
        return
    lines = content.split("\n")
    in_caption = False
    caption_lines = []
    for line in lines:
        if line.startswith("## Caption"):
            in_caption = True
            continue
        if line.startswith("## ") and in_caption:
            break
        if in_caption and line:
            caption_lines.append(line)

    if caption_lines:
        preview = "\n".join(caption_lines[:8])
        st.markdown(f"""
        <div style="background:#0A0A0A; border:1px solid #242424; border-radius:10px;
                    padding:1rem 1.25rem; font-size:13px; color:#C8C4BE;
                    line-height:1.7; white-space:pre-wrap; font-family:inherit;">{preview}</div>
        """, unsafe_allow_html=True)

    with st.expander("View full caption + hashtags", expanded=False):
        st.markdown(content[:4000])


def _render_asset_card(asset: dict, lib: AssetLibrary):
    asset_id = asset["asset_id"]
    status = asset["status"]
    atype = asset["asset_type"]
    description = asset.get("asset_description", atype)
    meta = json.loads(asset.get("metadata") or "{}")
    icon = ASSET_ICONS.get(atype, "📄")

    STATUS_ICONS = {
        "READY_FOR_REVIEW": "🟡",
        "APPROVED": "🟢",
        "REJECTED": "🔴",
        "REVISION_REQUESTED": "🔵",
    }
    status_icon = STATUS_ICONS.get(status, "⚪")

    with st.expander(
        f"{status_icon}  {icon}  {description}",
        expanded=(status == "READY_FOR_REVIEW")
    ):
        # Press release quote gate
        if atype == "press_release" and meta.get("requires_founder_input") and status == "READY_FOR_REVIEW":
            _render_press_release_quote_form(asset_id, lib)

        # Content preview
        content = asset.get("preview_text", "")
        if atype == "video_package":
            _render_video_card(asset)
        elif atype.startswith("caption_"):
            _render_caption_preview(content)
        elif content:
            max_chars = 4000
            st.markdown(content[:max_chars] + ("..." if len(content) > max_chars else ""))
            if len(content) > max_chars:
                file_path = asset.get("file_path", "")
                if file_path and Path(file_path).exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        full = f.read()
                    st.download_button(
                        "Download full document",
                        full,
                        file_name=asset.get("file_name", "asset.md"),
                        mime="text/markdown",
                        key=f"dl_{asset_id}",
                    )

        # Metadata row
        platforms = json.loads(asset.get("platform_targets") or "[]")
        posting_time = meta.get("posting_time", "")
        cols = st.columns(3)
        if platforms:
            cols[0].caption(f"Platforms: {' · '.join(p.replace('_', ' ') for p in platforms)}")
        if posting_time:
            cols[1].caption(f"Post at: {posting_time}")
        cols[2].caption(f"Revision #{asset.get('revision_count', 0)} of 3 max")

        st.divider()

        # Decision buttons
        if status in ("READY_FOR_REVIEW", "REVISION_REQUESTED"):
            _render_decision_buttons(asset_id, atype, meta, lib)
        elif status == "APPROVED":
            st.success(f"✓ Approved {_fmt_time(asset.get('approved_at', ''))}")
            if asset.get("founder_notes"):
                st.caption(f"Notes: {asset['founder_notes']}")
        elif status == "REJECTED":
            st.error("✗ Rejected")
            if asset.get("founder_notes"):
                st.caption(f"Reason: {asset['founder_notes']}")


# ── V5 one-at-a-time review ───────────────────────────────────────────────────

def _v5_review(artist_id: str, all_jobs: list, gen_dir: Path):
    """V5 Founder Experience: single-asset review with Previous / Next."""
    from execution.production_queue import update_job_status, PHASE_LABELS
    from ui.components import render_html

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

        if meta:
            provider = meta.get("provider_used", "mock")
            is_mock  = meta.get("mock", False)
            mock_tag = ' <span style="background:#F59E0B22;color:#F59E0B;font-size:10px;padding:2px 7px;border-radius:10px;font-weight:600;">MOCK</span>' if is_mock else ""
            render_html(
                f'<div style="font-size:12px;color:#6A6460;margin-bottom:1rem;">'
                f'Provider: <span style="color:#C8C4BE;">{provider}</span>{mock_tag}</div>'
            )

        # Content preview
        out_file = gen_dir / f"{jid}.md"
        if out_file.exists():
            content = out_file.read_text(encoding="utf-8")
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
            ba, bb, bc, bd = st.columns(4)
            with ba:
                if st.button("✓ Approve", key=f"v5a_{jid}", type="primary", use_container_width=True):
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
            render_html(f'<div style="color:#22C55E;font-size:13px;font-weight:600;margin-bottom:0.5rem;">✓ Approved {job.get("approved_at","")[:10]}</div>')
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
    """Drives the V5 one-at-a-time review for V4 production queue jobs."""
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

    # Quick summary stats
    review_n   = sum(1 for j in all_jobs if j.get("status") == "review")
    approved_n = sum(1 for j in all_jobs if j.get("status") == "approved")
    published_n = sum(1 for j in all_jobs if j.get("status") == "published")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("In Review",  review_n)
    m2.metric("Approved",   approved_n)
    m3.metric("Published",  published_n)
    m4.metric("Total Jobs", len(all_jobs))

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

    # ── V5 one-at-a-time review (primary experience) ─────────────────────────
    _render_v5_main_review()

    # ── Legacy V3 campaign assets (Studio mode / advanced) ───────────────────
    try:
        lib = _get_library()
        campaign_ids = lib.get_all_campaign_ids()
    except Exception as e:
        st.error(f"Could not connect to asset database: {e}")
        return

    if not campaign_ids:
        return

    st.divider()
    st.markdown("<div class='mw-section-label'>Legacy Release Assets</div>", unsafe_allow_html=True)

    # ── Release selector ─────────────────────────────────────────────────────
    default_cid = st.session_state.get("approval_campaign_id", campaign_ids[-1])
    if default_cid not in campaign_ids:
        default_cid = campaign_ids[-1]
    idx = campaign_ids.index(default_cid)

    col_sel, col_stats = st.columns([2, 2])
    with col_sel:
        selected_campaign = st.selectbox("Release (legacy):", campaign_ids, index=idx)
        st.session_state.approval_campaign_id = selected_campaign

    stats = lib.get_campaign_stats(selected_campaign)
    with col_stats:
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total", stats["total"])
        s2.metric("Approved", stats["approved"])
        s3.metric("Pending", stats["pending"])
        s4.metric("Rejected", stats["rejected"])

    if stats["all_approved"] and stats["total"] > 0:
        st.success("✓ All assets approved! Ready to publish.")
        col_dl, col_pub = st.columns([1, 1])
        with col_dl:
            from ui.pages.publishing import _build_checklist
            assets_all = lib.get_assets_for_campaign(selected_campaign)
            approved_list = [a for a in assets_all if a["status"] == "APPROVED"]
            checklist = _build_checklist(lib, selected_campaign, approved_list)
            st.download_button(
                "⬇  Download Publishing Checklist",
                checklist,
                file_name=f"{selected_campaign}_checklist.md",
                mime="text/markdown",
            )
        with col_pub:
            if st.button("🚀  Go to Publishing", type="primary"):
                st.session_state.publishing_campaign_id = selected_campaign
                navigate_to("publishing")

    st.divider()

    # ── Asset cards ───────────────────────────────────────────────────────────
    assets = lib.get_assets_for_campaign(selected_campaign)

    if not assets:
        st.info("No assets found for this campaign.")
        return

    assets.sort(key=lambda a: (
        0 if a["status"] == "READY_FOR_REVIEW" else 1,
        TYPE_ORDER.get(a["asset_type"], 99),
    ))

    for asset in assets:
        _render_asset_card(asset, lib)

    # ── Approval log ──────────────────────────────────────────────────────────
    with st.expander("Approval Log (permanent record)", expanded=False):
        log = lib.get_approval_log(selected_campaign)
        if not log:
            st.caption("No decisions recorded yet.")
        else:
            for entry in log:
                decision = entry.get("decision", "")
                desc = entry.get("asset_description", entry.get("asset_id", ""))
                dot = {"APPROVED": "🟢", "REJECTED": "🔴", "REVISION_REQUESTED": "🔵"}.get(decision, "⚪")
                st.markdown(
                    f"{dot} **{decision}** — {desc} — {_fmt_time(entry.get('decision_at', ''))}"
                )
                if entry.get("founder_notes"):
                    st.caption(f"Notes: {entry['founder_notes']}")

    st.caption("Human-led. AI-assisted. Scripture-rooted. Every decision is logged permanently.")


# ── V4 Production Queue Review ────────────────────────────────────────────────

def _render_v4_review_section():
    """Review panel for V4 production queue jobs (in-review and approved)."""
    import json as _json
    from execution.production_queue import list_jobs, update_job_status, STATUS_COLOR, STATUS_LABELS, PHASE_LABELS
    from execution.connectors.publishing_connector import PLATFORM_LABEL, PLATFORM_ICON
    from brand_brain.artist_library import list_artists

    artists = list_artists()
    if not artists:
        return

    render_html('<div class="mw-section-label">Release Assets — Production Queue</div>')

    artist_names = [a["artist_name"] for a in artists]
    artist_ids   = [a["artist_id"]   for a in artists]
    sel_idx  = st.selectbox("Artist:", range(len(artist_names)),
                             format_func=lambda i: artist_names[i], key="ar_v4_artist")
    sel_id   = artist_ids[sel_idx]

    all_jobs = list_jobs(sel_id)
    review_jobs   = [j for j in all_jobs if j.get("status") == "review"]
    approved_jobs = [j for j in all_jobs if j.get("status") == "approved"]
    published_jobs = [j for j in all_jobs if j.get("status") == "published"]

    # Stats
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("In Review",  len(review_jobs))
    m2.metric("Approved",   len(approved_jobs))
    m3.metric("Published",  len(published_jobs))
    m4.metric("Total",      len(all_jobs))

    if review_jobs:
        st.warning(f"{len(review_jobs)} asset(s) waiting for your review.")

    gen_dir = Path(__file__).parent.parent.parent / "data" / "generated" / sel_id

    # Show review jobs first, then approved
    for job in review_jobs + approved_jobs:
        _render_v4_job_review(job, sel_id, gen_dir)

    if not review_jobs and not approved_jobs:
        render_html("""
        <div class="mw-card" style="padding:1.5rem; text-align:center; color:#8A8480; margin-bottom:1rem;">
            <div style="font-size:13px;">No assets in review yet.</div>
            <div style="font-size:12px; margin-top:4px;">Generate content in the Production Queue to populate this section.</div>
        </div>
        """)
        col_btn, _ = st.columns([1, 3])
        with col_btn:
            if st.button("📋  Production Queue →", key="ar_goto_prod"):
                navigate_to("production")


def _render_v4_job_review(job: dict, artist_id: str, gen_dir: Path):
    """Render a single V4 production queue job for review."""
    import json as _json
    from execution.production_queue import update_job_status, PHASE_LABELS, STATUS_COLOR, STATUS_LABELS

    jid    = job["job_id"]
    icon   = job.get("job_icon", "📄")
    label  = job.get("job_label", "")
    phase  = PHASE_LABELS.get(job.get("phase", ""), "")
    status = job.get("status", "pending")
    color  = STATUS_COLOR.get(status, "#6A6460")
    slabel = STATUS_LABELS.get(status, status)

    status_dot = {"review": "🟡", "approved": "🟢", "rejected": "🔴"}.get(status, "⚪")

    with st.expander(f"{status_dot}  {icon}  {label}  ·  {phase}", expanded=(status == "review")):
        # ── Metadata strip ────────────────────────────────────────────────────
        meta_file = gen_dir / f"{jid}_meta.json"
        meta = {}
        if meta_file.exists():
            try:
                meta = _json.loads(meta_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        if meta:
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.caption(f"Connector: {meta.get('connector','')}")
            col_m2.caption(f"Provider: {meta.get('provider_used','mock')}")
            col_m3.caption(f"Worker: {meta.get('worker_used','')}")
            col_m4.caption(f"Time: {meta.get('generation_time_ms',0)}ms")
            if meta.get("mock"):
                render_html('<span style="background:#F59E0B22; color:#F59E0B; font-size:11px; padding:2px 8px; border-radius:12px; font-weight:600;">MOCK OUTPUT</span>')
            if meta.get("prompt_used"):
                with st.expander("Prompt used", expanded=False):
                    st.code(meta["prompt_used"], language=None)

        # ── Content preview ───────────────────────────────────────────────────
        out_file = gen_dir / f"{jid}.md"
        if out_file.exists():
            content = out_file.read_text(encoding="utf-8")
            st.markdown(content[:5000] + ("…" if len(content) > 5000 else ""))

            col_dl, _ = st.columns([1, 4])
            with col_dl:
                st.download_button(
                    "⬇ Download",
                    content.encode("utf-8"),
                    file_name=f"{label.replace(' ','_')}_{jid}.md",
                    mime="text/markdown",
                    key=f"dlv4_{jid}",
                )
        else:
            render_html('<div style="font-size:13px; color:#8A8480; padding:1rem;">No generated content yet.</div>')

        # ── Version history ───────────────────────────────────────────────────
        versions = job.get("versions", [])
        if versions:
            with st.expander(f"Version History ({len(versions)} version(s))", expanded=False):
                for v in reversed(versions):
                    st.caption(f"v{v.get('version','')} — {v.get('at','')[:16]}")

        st.divider()

        # ── Decision buttons ──────────────────────────────────────────────────
        if status == "review":
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                if st.button("✓ Approve", key=f"v4appr_{jid}", type="primary", use_container_width=True):
                    update_job_status(artist_id, jid, "approved")
                    st.success("Approved — asset moves to Publishing Queue.")
                    st.rerun()
            with col_b:
                if st.button("↺ Re-render", key=f"v4rr_{jid}", use_container_width=True):
                    update_job_status(artist_id, jid, "pending")
                    st.info("Reset to Pending. Return to Production Queue to regenerate.")
                    st.rerun()
            with col_c:
                rev_key = f"v4rev_show_{jid}"
                if st.button("✏ Request Revision", key=f"v4rev_btn_{jid}", use_container_width=True):
                    st.session_state[rev_key] = not st.session_state.get(rev_key, False)
                if st.session_state.get(rev_key):
                    with st.form(f"v4rev_form_{jid}"):
                        notes = st.text_area("What needs to change?", height=80)
                        if st.form_submit_button("Submit"):
                            if notes.strip():
                                from execution.production_queue import get_job, save_job
                                j = get_job(artist_id, jid)
                                if j:
                                    j["notes"] = notes.strip()
                                    save_job(j)
                                update_job_status(artist_id, jid, "pending")
                                st.session_state.pop(rev_key, None)
                                st.rerun()
            with col_d:
                if st.button("✗ Reject", key=f"v4rej_{jid}", use_container_width=True):
                    update_job_status(artist_id, jid, "rejected")
                    st.rerun()

        elif status == "approved":
            render_html(f'<div style="color:#22C55E; font-size:13px; font-weight:600;">✓ Approved — {job.get("approved_at","")[:10]}</div>')
            col_pub, col_rev = st.columns([1, 1])
            with col_pub:
                if st.button("🚀  Add to Publishing Queue", key=f"v4pub_{jid}", type="primary", use_container_width=True):
                    navigate_to("publishing")
            with col_rev:
                if st.button("↺ Re-render", key=f"v4rr2_{jid}", use_container_width=True):
                    update_job_status(artist_id, jid, "pending")
                    st.info("Reset to Pending.")
                    st.rerun()
