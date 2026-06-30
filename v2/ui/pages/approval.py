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


# ── Main render ───────────────────────────────────────────────────────────────

def render():
    page_header("Approval Queue", "Nothing publishes until you approve it.", "✅")

    try:
        lib = _get_library()
        campaign_ids = lib.get_all_campaign_ids()
    except Exception as e:
        st.error(f"Could not connect to asset database: {e}")
        return

    if not campaign_ids:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;">
            <div style="font-size:40px; margin-bottom:1rem;">✅</div>
            <div style="font-size:18px; color:#F0EDE8; margin-bottom:0.5rem;">No campaigns yet</div>
            <div>Build your first campaign to see assets here.</div>
        </div>
        """)
        if st.button("➕  New Project", type="primary"):
            st.session_state.wizard_step = 0
            st.session_state.wizard_data = {}
            navigate_to("wizard")
        return

    # ── Campaign selector ─────────────────────────────────────────────────────
    default_cid = st.session_state.get("approval_campaign_id", campaign_ids[-1])
    if default_cid not in campaign_ids:
        default_cid = campaign_ids[-1]
    idx = campaign_ids.index(default_cid)

    col_sel, col_stats = st.columns([2, 2])
    with col_sel:
        selected_campaign = st.selectbox("Campaign:", campaign_ids, index=idx)
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
