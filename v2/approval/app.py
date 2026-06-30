"""MusicWorks™ Approval Queue — Streamlit web app."""
import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

# Allow imports from the v2 root when run via `streamlit run approval/app.py`
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.asset_library import AssetLibrary

st.set_page_config(
    page_title="MusicWorks™ Approval Queue",
    page_icon="🎵",
    layout="wide",
)

# ── Helper functions (defined before use) ────────────────────────────────────

def fmt_time(iso: str) -> str:
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d at %H:%M UTC")
    except Exception:
        return iso[:10]


def render_decision_buttons(asset_id: str, atype: str, meta: dict, lib: AssetLibrary):
    blocked = atype == "press_release" and meta.get("requires_founder_input", False)

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col1:
        if blocked:
            st.button("✓ APPROVE", key=f"approve_{asset_id}", disabled=True,
                      help="Save your personal quote first.")
        else:
            if st.button("✓ APPROVE", key=f"approve_{asset_id}", type="primary"):
                lib.update_status(asset_id, "APPROVED")
                st.success("Approved!")
                st.rerun()

    with col2:
        show_key = f"show_revise_{asset_id}"
        if st.button("↺ REQUEST REVISION", key=f"revise_btn_{asset_id}"):
            st.session_state[show_key] = not st.session_state.get(show_key, False)

        if st.session_state.get(show_key):
            with st.form(key=f"revision_form_{asset_id}"):
                notes = st.text_area(
                    "What needs to change? Be specific:",
                    placeholder="e.g., Move scripture overlay to 0:08. Add pronunciation guide before meaning reveal.",
                    height=80,
                )
                if st.form_submit_button("Submit Revision Request"):
                    if notes.strip():
                        lib.update_status(asset_id, "REVISION_REQUESTED", founder_notes=notes)
                        st.session_state.pop(show_key, None)
                        st.info("Revision requested. Notes saved to approval log.")
                        st.rerun()
                    else:
                        st.error("Please describe what needs to change.")

    with col3:
        reject_key = f"show_reject_{asset_id}"
        if st.button("✗ REJECT", key=f"reject_btn_{asset_id}"):
            st.session_state[reject_key] = not st.session_state.get(reject_key, False)

        if st.session_state.get(reject_key):
            with st.form(key=f"reject_form_{asset_id}"):
                reason = st.text_area("Reason (optional):", height=60)
                if st.form_submit_button("Confirm Rejection"):
                    lib.update_status(asset_id, "REJECTED", founder_notes=reason)
                    st.session_state.pop(reject_key, None)
                    st.rerun()


def render_press_release_quote_form(asset_id: str, lib: AssetLibrary):
    st.warning(
        "**⚠ ACTION REQUIRED BEFORE APPROVAL**\n\n"
        "This press release contains a draft quote written by the agent. "
        "You must replace it with your own exact words. "
        "This quote will be attributed to you by name."
    )
    with st.form(key=f"quote_form_{asset_id}"):
        st.markdown("**Type your personal quote below:**")
        founder_quote = st.text_area(
            "Your quote:",
            placeholder='e.g., "I grew up in church but never knew my own languages had words for what I was living..."',
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
                st.success("Quote saved. Now review the document and approve.")
                st.rerun()
            else:
                st.error("Please type your quote before saving.")


def render_video_card(asset: dict):
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
            "3. Download the generated clips\n"
            "4. Assemble in CapCut or Canva Video\n"
            "5. Upload the finished MP4 below\n"
        )

    content = asset.get("preview_text", "")
    if content:
        with st.expander("View storyboard + Veo prompts", expanded=False):
            st.markdown(content[:6000])

    uploaded = st.file_uploader(
        "Upload finished MP4 (once produced)",
        type=["mp4"],
        key=f"upload_{asset['asset_id']}",
    )
    if uploaded:
        save_dir = Path(file_path).parent
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / uploaded.name
        save_path.write_bytes(uploaded.getbuffer())
        st.success(f"✓ Video saved: {uploaded.name}")
        st.info("You can now approve this asset.")


def render_asset_card(asset: dict, lib: AssetLibrary):
    asset_id = asset["asset_id"]
    status = asset["status"]
    atype = asset["asset_type"]
    description = asset.get("asset_description", atype)
    meta = json.loads(asset.get("metadata") or "{}")

    STATUS_ICONS = {
        "READY_FOR_REVIEW": "🟡",
        "APPROVED": "🟢",
        "REJECTED": "🔴",
        "REVISION_REQUESTED": "🔵",
    }
    icon = STATUS_ICONS.get(status, "⚪")

    with st.expander(f"{icon}  {description}", expanded=(status == "READY_FOR_REVIEW")):

        # Press release quote gate
        if atype == "press_release" and meta.get("requires_founder_input") and status == "READY_FOR_REVIEW":
            render_press_release_quote_form(asset_id, lib)

        # Content preview
        if atype == "video_package":
            render_video_card(asset)
        else:
            content = asset.get("preview_text", "")
            if content:
                # Show first 4000 chars; offer download for longer docs
                st.markdown(content[:4000] + ("..." if len(content) > 4000 else ""))
                if len(content) > 4000:
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
            render_decision_buttons(asset_id, atype, meta, lib)
        elif status == "APPROVED":
            st.success(f"✓ Approved {fmt_time(asset.get('approved_at', ''))}")
            if asset.get("founder_notes"):
                st.caption(f"Notes: {asset['founder_notes']}")
        elif status == "REJECTED":
            st.error("✗ Rejected")
            if asset.get("founder_notes"):
                st.caption(f"Reason: {asset['founder_notes']}")
        elif status == "REVISION_REQUESTED":
            st.info("↺ Revision requested")
            if asset.get("founder_notes"):
                st.caption(f"Revision notes: {asset['founder_notes']}")


def generate_checklist(lib: AssetLibrary, campaign_id: str) -> str:
    assets = lib.get_assets_for_campaign(campaign_id)
    approved = [a for a in assets if a["status"] == "APPROVED"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Publishing Checklist — {campaign_id}\n\n",
        f"*Generated by MusicWorks™ V2 — {now}*\n\n",
        f"**{len(approved)} assets approved and ready to publish.**\n\n",
        "> Replace `[STREAMING_LINK]` and `[DEVOTIONAL_LINK]` with live URLs before posting.\n\n",
        "---\n\n",
    ]

    for asset in approved:
        meta = json.loads(asset.get("metadata") or "{}")
        platforms = json.loads(asset.get("platform_targets") or "[]")
        lines.append(f"## {asset['asset_description']}\n\n")
        lines.append(f"- **File:** `{asset.get('file_name', '')}`\n")
        lines.append(f"- **Path:** `{asset.get('file_path', '')}`\n")
        if platforms:
            lines.append(f"- **Platforms:** {', '.join(p.replace('_', ' ').title() for p in platforms)}\n")
        posting_time = meta.get("posting_time", "")
        if posting_time:
            lines.append(f"- **Recommended time:** {posting_time}\n")
        lines.append(f"- **Approved:** {asset.get('approved_at', '')[:10]}\n\n")
        lines.append("**Publishing steps:**\n")
        for p in (platforms or ["all platforms"]):
            lines.append(f"- [ ] Post to {p.replace('_', ' ').title()}\n")
        lines.append("- [ ] Add pinned/first comment\n")
        lines.append("- [ ] Confirm post is live\n")
        lines.append("- [ ] Record confirmation\n\n")

    return "".join(lines)


# ── App initialisation ────────────────────────────────────────────────────────

@st.cache_resource
def get_library():
    return AssetLibrary()


library = get_library()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎵 MusicWorks™")
    st.markdown("*Approval Queue — V2*")
    st.divider()

    campaign_ids = library.get_all_campaign_ids()

    if not campaign_ids:
        st.warning("No campaigns found.")
        st.code("python main.py")
        st.info("Run the command above to generate your first campaign.")
        st.stop()

    selected_campaign = st.selectbox("Select campaign:", campaign_ids)
    st.divider()

    stats = library.get_campaign_stats(selected_campaign)
    c1, c2 = st.columns(2)
    c1.metric("Total", stats["total"])
    c2.metric("Approved", stats["approved"])
    c3, c4 = st.columns(2)
    c3.metric("Pending", stats["pending"])
    c4.metric("Rejected", stats["rejected"])

    if stats["all_approved"] and stats["total"] > 0:
        st.success("✓ All assets approved!")
        st.divider()
        checklist = generate_checklist(library, selected_campaign)
        st.download_button(
            "⬇ Download Publishing Checklist",
            checklist,
            file_name=f"{selected_campaign}_checklist.md",
            mime="text/markdown",
        )

    st.divider()
    st.caption(f"DB: {Path(library.db_path).name}")

# ── Main area ─────────────────────────────────────────────────────────────────

st.title(f"Campaign: {selected_campaign}")
st.caption("Nothing publishes until you press APPROVE. Every decision is logged permanently.")

assets = library.get_assets_for_campaign(selected_campaign)

if not assets:
    st.info("No assets found for this campaign.")
    st.stop()

# Sort: pending first, then by asset type
TYPE_ORDER = {
    "video_package": 0,
    "caption_instagram": 1,
    "caption_tiktok": 2,
    "caption_youtube": 3,
    "caption_facebook": 4,
    "blog_post": 5,
    "press_release": 6,
    "church_blurb": 7,
    "thumbnail_concept": 8,
}
assets.sort(key=lambda a: (
    0 if a["status"] == "READY_FOR_REVIEW" else 1,
    TYPE_ORDER.get(a["asset_type"], 99),
))

for asset in assets:
    render_asset_card(asset, library)

# ── Approval log ──────────────────────────────────────────────────────────────
with st.expander("Approval Log (permanent record)", expanded=False):
    log = library.get_approval_log(selected_campaign)
    if not log:
        st.caption("No decisions recorded yet.")
    else:
        for entry in log:
            decision_icon = {"APPROVED": "🟢", "REJECTED": "🔴", "REVISION_REQUESTED": "🔵"}.get(entry["decision"], "⚪")
            st.markdown(
                f"{decision_icon} **{entry['decision']}** — {entry.get('asset_description', entry['asset_id'])} "
                f"— {fmt_time(entry['decision_at'])}"
            )
            if entry.get("founder_notes"):
                st.caption(f"Notes: {entry['founder_notes']}")
