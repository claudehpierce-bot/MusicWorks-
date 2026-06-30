"""MusicWorks™ V3 — Publishing page."""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, render_html
from execution.asset_library import AssetLibrary


@st.cache_resource
def _get_library():
    return AssetLibrary()


def render():
    page_header("Publishing", "Review approved assets and publish your campaign.", "🚀")

    try:
        lib = _get_library()
        campaign_ids = lib.get_all_campaign_ids()
    except Exception as e:
        st.error(f"Could not load campaigns: {e}")
        return

    if not campaign_ids:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;">
            <div style="font-size:40px; margin-bottom:1rem;">🚀</div>
            <div style="font-size:18px; color:#F0EDE8; margin-bottom:0.5rem;">Nothing to publish yet</div>
            <div>Build and approve a campaign first.</div>
        </div>
        """)
        return

    # Campaign selector
    default_cid = st.session_state.get("publishing_campaign_id", campaign_ids[-1])
    if default_cid not in campaign_ids:
        default_cid = campaign_ids[-1]
    idx = campaign_ids.index(default_cid)

    selected = st.selectbox("Select campaign:", campaign_ids, index=idx)
    st.session_state.publishing_campaign_id = selected

    stats = lib.get_campaign_stats(selected)
    assets = lib.get_assets_for_campaign(selected)
    approved = [a for a in assets if a["status"] == "APPROVED"]
    pending = [a for a in assets if a["status"] != "APPROVED" and a["status"] != "REJECTED"]

    # ── Status row ────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Assets", stats["total"])
    m2.metric("Approved", stats["approved"])
    m3.metric("Pending", stats["pending"])
    m4.metric("Rejected", stats["rejected"])

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    if pending:
        st.warning(f"**{len(pending)} asset(s) still pending review.** Approve all assets before publishing.")
        if st.button("✅  Open Approval Queue", type="primary"):
            st.session_state.approval_campaign_id = selected
            navigate_to("approval")
        st.divider()

    if not approved:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:2rem; color:#8A8480;">
            No approved assets yet. Visit the Approval Queue to review and approve your campaign assets.
        </div>
        """)
        return

    # ── Publishing checklist ──────────────────────────────────────────────────
    st.markdown("<div class='mw-section-label'>Ready to Publish</div>", unsafe_allow_html=True)

    for asset in approved:
        meta = json.loads(asset.get("metadata") or "{}")
        platforms = json.loads(asset.get("platform_targets") or "[]")
        posting_time = meta.get("posting_time", "")
        desc = asset.get("asset_description", asset.get("asset_type", ""))

        platform_str = " · ".join(p.replace("_", " ").title() for p in platforms) if platforms else "All platforms"
        time_str = f" · {posting_time}" if posting_time else ""

        render_html(f"""
        <div class="mw-card" style="padding:1rem 1.5rem; margin-bottom:0.5rem;
                    border-left:3px solid #22C55E;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:14px; font-weight:600; color:#F0EDE8;">{desc}</div>
                    <div style="font-size:12px; color:#8A8480; margin-top:2px;">
                        {platform_str}{time_str}
                    </div>
                </div>
                <span class="badge badge-approved">✓ Approved</span>
            </div>
        </div>
        """)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    if stats["all_approved"] and stats["total"] > 0:
        st.success(f"✓ All {stats['total']} assets approved. Your campaign is ready to publish.")

    # ── Download checklist ────────────────────────────────────────────────────
    checklist = _build_checklist(lib, selected, approved)
    st.download_button(
        "⬇  Download Publishing Checklist",
        checklist,
        file_name=f"{selected}_publishing_checklist.md",
        mime="text/markdown",
        type="primary",
    )

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    st.info("""
    **Publishing reminder:** Replace `[STREAMING_LINK]` and `[DEVOTIONAL_LINK]` with live URLs before posting.
    Confirm the streaming link is live on all platforms before sharing social captions.
    """)


def _build_checklist(lib: AssetLibrary, campaign_id: str, approved: list) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Publishing Checklist — {campaign_id}\n\n",
        f"*Generated by MusicWorks™ V3 — {now}*\n\n",
        f"**{len(approved)} assets approved and ready to publish.**\n\n",
        "> Replace `[STREAMING_LINK]` and `[DEVOTIONAL_LINK]` with live URLs before posting.\n\n",
        "---\n\n",
    ]
    for asset in approved:
        meta = json.loads(asset.get("metadata") or "{}")
        platforms = json.loads(asset.get("platform_targets") or "[]")
        desc = asset.get("asset_description", "")
        lines.append(f"## {desc}\n\n")
        lines.append(f"- **File:** `{asset.get('file_name', '')}`\n")
        if platforms:
            lines.append(f"- **Platforms:** {', '.join(p.replace('_', ' ').title() for p in platforms)}\n")
        posting_time = meta.get("posting_time", "")
        if posting_time:
            lines.append(f"- **Recommended time:** {posting_time}\n")
        lines.append(f"- **Approved:** {(asset.get('approved_at') or '')[:10]}\n\n")
        lines.append("**Steps:**\n")
        for p in (platforms or ["all platforms"]):
            lines.append(f"- [ ] Post to {p.replace('_', ' ').title()}\n")
        lines.append("- [ ] Confirm post is live\n")
        lines.append("- [ ] Record live link\n\n")
    return "".join(lines)
