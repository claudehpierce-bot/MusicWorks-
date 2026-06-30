"""MusicWorks™ V3 — Artist Library page."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, tag_list_html, render_html
from brand_brain.artist_library import list_artists, load_artist


def render():
    page_header("Artists", "Your permanent artist library.", "👥")

    artists = list_artists()

    col_title, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("➕  Add Artist", type="primary", use_container_width=True):
            st.session_state.wizard_step = 0
            st.session_state.wizard_data = {}
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("wizard")

    if not artists:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;">
            <div style="font-size:40px; margin-bottom:1rem;">👥</div>
            <div style="font-size:18px; color:#F0EDE8; margin-bottom:0.5rem;">No artists yet</div>
            <div>Create your first artist to get started.</div>
        </div>
        """)
        return

    for info in artists:
        artist_id = info["artist_id"]
        brain = load_artist(artist_id)
        if not brain:
            continue
        _render_artist_card(brain)


def _render_artist_card(brain):
    is_flagship = brain.artist_id == "fire_and_flow_gospel"
    badge = '<span class="badge badge-live" style="margin-left:8px;">Flagship Artist</span>' if is_flagship else ""

    with st.expander(f"**{brain.artist_name}** — {brain.tagline[:60]}...", expanded=is_flagship):
        # ── Header row ────────────────────────────────────────────────────────
        render_html(f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-start;
                    flex-wrap:wrap; gap:1rem; margin-bottom:1.5rem;">
            <div>
                <div style="font-size:22px; font-weight:800; color:#F0EDE8; letter-spacing:-0.5px;">
                    {brain.artist_name} {badge}
                </div>
                <div style="font-size:14px; color:#9B89D4; margin-top:4px;">{brain.tagline}</div>
            </div>
        </div>
        """)

        # ── Two-column: Bio + Mission | Identity ──────────────────────────────
        col_a, col_b = st.columns([1.4, 1])

        with col_a:
            st.markdown("<div class='mw-section-label'>Mission</div>", unsafe_allow_html=True)
            st.markdown(f'<div class="mw-card" style="padding:1rem; font-size:14px; color:#C8C4BE; line-height:1.7;">{brain.mission}</div>', unsafe_allow_html=True)

            if brain.bio_short:
                st.markdown("<div class='mw-section-label' style='margin-top:1rem;'>Biography</div>", unsafe_allow_html=True)
                st.markdown(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#8A8480; line-height:1.6;">{brain.bio_short}</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown("<div class='mw-section-label'>Global Identity</div>", unsafe_allow_html=True)
            heritage_html = tag_list_html(brain.heritage, "tag tag-indigo")
            genre_html = tag_list_html(brain.genre, "tag tag-gold")
            render_html(f"""
            <div class="mw-card" style="padding:1rem;">
                <div style="margin-bottom:0.75rem;">
                    <div style="font-size:11px; color:#8A8480; margin-bottom:6px;">HERITAGE</div>
                    {heritage_html}
                </div>
                <div>
                    <div style="font-size:11px; color:#8A8480; margin-bottom:6px;">GENRE</div>
                    {genre_html}
                </div>
            </div>
            """)

            # Platform handles
            if brain.platform_handles:
                handles_html = ""
                for platform, handle in brain.platform_handles.items():
                    handles_html += f'<div style="font-size:12px; color:#8A8480; padding:3px 0;"><span style="color:#F0EDE8; text-transform:capitalize;">{platform}:</span> {handle}</div>'
                render_html(f"""
                <div class="mw-card" style="padding:1rem; margin-top:1rem;">
                    <div style="font-size:11px; color:#8A8480; margin-bottom:8px;">PLATFORMS</div>
                    {handles_html}
                </div>
                """)

        # ── Creative DNA ──────────────────────────────────────────────────────
        dna = brain.creative_dna
        st.markdown("<div class='mw-section-label' style='margin-top:1.5rem;'>Creative DNA</div>", unsafe_allow_html=True)

        col_c, col_d = st.columns(2)
        with col_c:
            # Color palette
            palette = dna.color_palette
            if palette:
                swatches = ""
                color_map = {
                    "primary": ("#2D1B69", "Primary"),
                    "secondary": ("#D4A853", "Secondary"),
                    "accent": ("#FF6B2B", "Accent"),
                }
                for key, (fallback, label) in color_map.items():
                    raw = palette.get(key, fallback)
                    hex_color = raw.split(" ")[0] if raw else fallback
                    swatches += f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;"><div class="color-swatch" style="background:{hex_color};"></div><span style="font-size:12px; color:#C8C4BE;">{label} — {hex_color}</span></div>'

                render_html(f"""
                <div class="mw-card" style="padding:1rem;">
                    <div style="font-size:11px; color:#8A8480; margin-bottom:10px;">COLOR PALETTE</div>
                    {swatches}
                </div>
                """)

        with col_d:
            # Visual keywords
            if dna.visual_keywords:
                kw_html = tag_list_html(dna.visual_keywords[:10], "tag")
                render_html(f"""
                <div class="mw-card" style="padding:1rem;">
                    <div style="font-size:11px; color:#8A8480; margin-bottom:10px;">VISUAL KEYWORDS</div>
                    {kw_html}
                </div>
                """)
            if dna.emotion:
                em_html = tag_list_html(dna.emotion, "tag tag-fire")
                render_html(f"""
                <div class="mw-card" style="padding:1rem; margin-top:0.75rem;">
                    <div style="font-size:11px; color:#8A8480; margin-bottom:10px;">EMOTION + ENERGY</div>
                    {em_html}
                </div>
                """)

        # ── Brand Rules (condensed) ────────────────────────────────────────────
        if brain.brand_rules:
            rules_html = "".join(
                f'<div style="font-size:12px; color:#C8C4BE; padding:5px 0; border-bottom:1px solid #1E1E1E;">— {r}</div>'
                for r in brain.brand_rules[:5]
            )
            render_html(f"""
            <div class="mw-card" style="padding:1rem; margin-top:1rem;">
                <div style="font-size:11px; color:#8A8480; margin-bottom:10px;">BRAND RULES (non-negotiable)</div>
                {rules_html}
                {'<div style="font-size:11px; color:#6A6460; padding-top:6px;">...and ' + str(len(brain.brand_rules) - 5) + ' more</div>' if len(brain.brand_rules) > 5 else ''}
            </div>
            """)

        # ── Discography ────────────────────────────────────────────────────────
        if brain.discography:
            albums_html = ""
            for album in brain.discography:
                status_cls = "badge-approved" if album.get("status") == "released" else "badge-pending"
                status_lbl = album.get("status", "draft").title()
                albums_html += f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding:8px 0; border-bottom:1px solid #1E1E1E;">
                    <div>
                        <div style="font-size:13px; color:#F0EDE8; font-weight:500;">{album.get("title", "")}</div>
                        <div style="font-size:11px; color:#8A8480;">{album.get("release_date", "")} · {len(album.get("tracks", []))} tracks</div>
                    </div>
                    <span class="badge {status_cls}">{status_lbl}</span>
                </div>
                """
            render_html(f"""
            <div class="mw-card" style="padding:1rem; margin-top:1rem;">
                <div style="font-size:11px; color:#8A8480; margin-bottom:10px;">DISCOGRAPHY</div>
                {albums_html}
            </div>
            """)

        # ── Campaign history count ────────────────────────────────────────────
        if brain.campaign_history:
            st.caption(f"{len(brain.campaign_history)} campaign(s) in history.")

        # ── Action buttons ────────────────────────────────────────────────────
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        btn1, btn2, btn3 = st.columns(3)
        with btn1:
            if st.button("🎵  New Project", key=f"artist_new_{brain.artist_id}", use_container_width=True, type="primary"):
                st.session_state.wizard_step = 0
                st.session_state.wizard_data = {"artist_id": brain.artist_id, "artist_name": brain.artist_name}
                st.session_state.pop("wizard_campaign_id", None)
                navigate_to("wizard")
        with btn2:
            if st.button("📦  View Campaigns", key=f"artist_campaigns_{brain.artist_id}", use_container_width=True):
                navigate_to("campaigns")
        with btn3:
            if st.button("🧠  Brand Brain", key=f"artist_brain_{brain.artist_id}", use_container_width=True):
                st.session_state.brand_brain_artist_id = brain.artist_id
                navigate_to("brand_brain")
