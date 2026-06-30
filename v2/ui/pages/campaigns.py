"""MusicWorks™ V3 — Campaigns page."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, progress_bar_html, render_html
from execution.asset_library import AssetLibrary


@st.cache_resource
def _get_library():
    return AssetLibrary()


def render():
    page_header("Campaigns", "All campaigns built with MusicWorks™.", "📦")

    try:
        lib = _get_library()
        campaign_ids = lib.get_all_campaign_ids()
    except Exception as e:
        st.error(f"Could not load campaigns: {e}")
        return

    col_title, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("➕  New Campaign", type="primary", use_container_width=True):
            st.session_state.wizard_step = 0
            st.session_state.wizard_data = {}
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("wizard")

    if not campaign_ids:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;">
            <div style="font-size:40px; margin-bottom:1rem;">📦</div>
            <div style="font-size:18px; color:#F0EDE8; margin-bottom:0.5rem;">No campaigns yet</div>
            <div>Run your first campaign to see it here.</div>
        </div>
        """)
        return

    # ── Aggregate stats row ───────────────────────────────────────────────────
    total_assets = 0
    total_approved = 0
    for cid in campaign_ids:
        s = lib.get_campaign_stats(cid)
        total_assets += s["total"]
        total_approved += s["approved"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Campaigns", len(campaign_ids))
    m2.metric("Total Assets", total_assets)
    m3.metric("Approved", total_approved)
    pending = total_assets - total_approved
    m4.metric("Pending Review", pending)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mw-section-label'>All Campaigns</div>", unsafe_allow_html=True)

    # ── Campaign cards ────────────────────────────────────────────────────────
    for cid in reversed(campaign_ids):
        stats = lib.get_campaign_stats(cid)
        total = stats["total"]
        approved = stats["approved"]
        pending_c = stats["pending"]
        rejected = stats["rejected"]
        pct = (approved / total * 100) if total > 0 else 0
        all_ok = stats["all_approved"] and total > 0

        status_html = (
            '<span class="badge badge-approved">✓ All Approved</span>'
            if all_ok
            else f'<span class="badge badge-pending">● {pending_c} pending</span>'
        )

        render_html(f"""
        <div class="mw-card" style="padding:1.25rem 1.5rem; margin-bottom:0.75rem;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div style="flex:1; min-width:200px;">
        <div style="font-size:16px; font-weight:700; color:#F0EDE8; margin-bottom:4px;">{cid}</div>
        <div style="display:flex; gap:12px; flex-wrap:wrap; margin-top:6px;">
        <span style="font-size:12px; color:#22C55E;">{approved} approved</span>
        <span style="font-size:12px; color:#F59E0B;">{pending_c} pending</span>
        <span style="font-size:12px; color:#EF4444;">{rejected} rejected</span>
        </div>
        {progress_bar_html(pct)}
        </div>
        <div style="display:flex; align-items:center; gap:8px;">{status_html}</div>
        </div>
        </div>
        """)

        btn_a, btn_b, _ = st.columns([1, 1, 3])
        with btn_a:
            if st.button("✅  Approval Queue", key=f"camp_approve_{cid}", use_container_width=True, type="primary"):
                st.session_state.approval_campaign_id = cid
                navigate_to("approval")
        with btn_b:
            if st.button("🚀  Publishing", key=f"camp_publish_{cid}", use_container_width=True):
                st.session_state.publishing_campaign_id = cid
                navigate_to("publishing")
