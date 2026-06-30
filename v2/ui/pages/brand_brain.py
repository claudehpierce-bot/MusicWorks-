"""MusicWorks™ V3 — Brand Brain page."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, tag_list_html, render_html
from brand_brain.artist_library import list_artists, load_artist


def render():
    page_header("Brand Brain", "The permanent memory of every artist.", "🧠")

    artists = list_artists()
    if not artists:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;">
            <div style="font-size:40px; margin-bottom:1rem;">🧠</div>
            <div style="font-size:18px; color:#F0EDE8; margin-bottom:0.5rem;">No artists yet</div>
            <div>Create an artist to activate the Brand Brain.</div>
        </div>
        """)
        return

    artist_names = [a["artist_name"] for a in artists]
    artist_ids = [a["artist_id"] for a in artists]

    default_id = st.session_state.get("brand_brain_artist_id", artist_ids[0])
    if default_id in artist_ids:
        default_idx = artist_ids.index(default_id)
    else:
        default_idx = 0

    selected_idx = st.selectbox("Artist:", range(len(artist_names)),
                                 format_func=lambda i: artist_names[i],
                                 index=default_idx)
    selected_id = artist_ids[selected_idx]
    brain = load_artist(selected_id)

    if not brain:
        st.error("Could not load artist brain.")
        return

    render_html(f"""
    <div style="background:linear-gradient(135deg, #1A0F42, #2D1B69);
                border:1px solid rgba(212,168,83,0.2); border-radius:16px;
                padding:2rem; margin:1rem 0 2rem 0;">
        <div style="font-size:24px; font-weight:800; color:#F0EDE8; margin-bottom:4px;">
            {brain.display_name}
        </div>
        <div style="font-size:14px; color:#9B89D4; margin-bottom:0.75rem;">{brain.tagline}</div>
        <div style="font-size:13px; color:#8A8480;">{brain.mission[:120]}...</div>
    </div>
    """)

    tab1, tab2, tab3, tab4 = st.tabs(["Brand Voice", "Creative DNA", "Theology", "Rules & Preferences"])

    with tab1:
        voice = brain.brand_voice
        col_a, col_b = st.columns(2)

        with col_a:
            _section("Tone", tag_list_html(voice.tone, "tag tag-indigo"))
            _section("Style", tag_list_html(voice.style, "tag"))
            _section("Brand Vocabulary", tag_list_html(voice.vocabulary, "tag tag-gold"))

        with col_b:
            _section("Scripture Style", f'<p style="font-size:13px; color:#C8C4BE;">{voice.scripture_style}</p>')
            _section("CTA Style", f'<p style="font-size:13px; color:#C8C4BE;">{voice.cta_style}</p>')
            if voice.avoid:
                avoid_html = "".join(f'<div style="font-size:12px; color:#EF4444; padding:3px 0;">✗ {a}</div>' for a in voice.avoid)
                _section("Never Say", avoid_html)

        if voice.platform_voice:
            st.markdown("<div class='mw-section-label' style='margin-top:1.5rem;'>Platform Voice</div>", unsafe_allow_html=True)
            for platform, note in voice.platform_voice.items():
                render_html(f"""
                <div class="mw-card" style="padding:0.75rem 1rem; margin-bottom:0.5rem;
                            border-left:3px solid #2D1B69;">
                    <div style="font-size:11px; color:#9B89D4; text-transform:uppercase;
                                letter-spacing:0.5px; margin-bottom:4px;">{platform.title()}</div>
                    <div style="font-size:13px; color:#C8C4BE;">{note}</div>
                </div>
                """)

    with tab2:
        dna = brain.creative_dna
        col_c, col_d = st.columns(2)

        with col_c:
            # Color palette
            palette = dna.color_palette
            swatches = ""
            color_map = {
                "primary": ("#2D1B69", "Primary"),
                "secondary": ("#D4A853", "Secondary"),
                "accent": ("#FF6B2B", "Accent"),
                "background_warm": ("#1A0F42", "Background"),
            }
            for key, (fallback, label) in color_map.items():
                raw = palette.get(key, fallback)
                hex_color = raw.split(" ")[0] if raw else fallback
                swatches += f'<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;"><div class="color-swatch" style="background:{hex_color};"></div><span style="font-size:13px; color:#C8C4BE;">{label} — {hex_color}</span></div>'
            _section("Color Palette", swatches)

            _section("Lighting", tag_list_html(dna.lighting, "tag"))
            _section("Environment", tag_list_html(dna.environment, "tag"))

        with col_d:
            _section("Lens Style", f'<p style="font-size:13px; color:#C8C4BE;">{dna.lens_style}</p>')
            _section("Camera Movement", f'<p style="font-size:13px; color:#C8C4BE;">{dna.camera_movement}</p>')
            _section("Composition", f'<p style="font-size:13px; color:#C8C4BE;">{dna.composition}</p>')
            _section("Visual Keywords", tag_list_html(dna.visual_keywords, "tag"))
            _section("Rendering Keywords", tag_list_html(dna.rendering_keywords, "tag tag-fire"))

        if dna.what_to_avoid:
            avoid_html = "".join(f'<div style="font-size:12px; color:#EF4444; padding:4px 0; border-bottom:1px solid #1E1E1E;">✗ {a}</div>' for a in dna.what_to_avoid)
            _section("Never Use (Visual)", avoid_html)

    with tab3:
        theo = brain.theological_guardrails
        st.markdown(f'<div class="mw-card" style="padding:1rem; border-left:3px solid #D4A853; font-size:14px; color:#C8C4BE; margin-bottom:1rem;">{theo.theological_stance}</div>', unsafe_allow_html=True)

        col_e, col_f = st.columns(2)
        with col_e:
            if theo.required:
                req_html = "".join(f'<div style="font-size:13px; color:#22C55E; padding:5px 0; border-bottom:1px solid #1E1E1E;">✓ {r}</div>' for r in theo.required)
                _section("Always Required", req_html)
        with col_f:
            if theo.forbidden:
                forb_html = "".join(f'<div style="font-size:13px; color:#EF4444; padding:5px 0; border-bottom:1px solid #1E1E1E;">✗ {r}</div>' for r in theo.forbidden)
                _section("Forbidden", forb_html)

        _section("Scripture Accuracy", f'<p style="font-size:13px; color:#C8C4BE;">{theo.scripture_accuracy}</p>')

    with tab4:
        col_g, col_h = st.columns(2)
        with col_g:
            if brain.brand_rules:
                rules_html = "".join(f'<div style="font-size:13px; color:#C8C4BE; padding:6px 0; border-bottom:1px solid #1E1E1E;">— {r}</div>' for r in brain.brand_rules)
                _section("Brand Rules (non-negotiable)", rules_html)
        with col_h:
            if brain.founder_preferences:
                prefs_html = "".join(f'<div style="font-size:13px; color:#C8C4BE; padding:6px 0; border-bottom:1px solid #1E1E1E;">• {p}</div>' for p in brain.founder_preferences)
                _section("Founder Preferences", prefs_html)

        if brain.future_notes:
            notes_html = "".join(f'<div style="font-size:13px; color:#8A8480; padding:5px 0; border-bottom:1px solid #1E1E1E;">→ {n}</div>' for n in brain.future_notes)
            _section("Future Notes", notes_html)

    st.caption(f"Last updated: {brain.updated_at[:10] if brain.updated_at else 'unknown'}")

    # ── Sources & Status ──────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mw-section-label'>Brand Brain Sources & Status</div>", unsafe_allow_html=True)

    from execution.brand_vault import load_vault_meta, vault_asset_count, vault_has_visuals
    from execution.distribution_store import load_distribution, dist_configured_count
    from execution.profile_store import load_profile

    vault_meta   = load_vault_meta(selected_id)
    vault_count  = vault_asset_count(selected_id)
    has_visuals  = vault_has_visuals(selected_id)
    dist         = load_distribution(selected_id)
    dist_count   = dist_configured_count(dist)
    profile      = load_profile(selected_id)
    profile_updated = profile.get("updated_at", "")[:10] or "not set"

    def _src_row(icon, label, value, status_color, status_label):
        return (
            f'<div style="display:flex; align-items:center; gap:12px; padding:8px 0; border-bottom:1px solid #1E1E1E;">'
            f'<span style="font-size:18px; min-width:24px;">{icon}</span>'
            f'<div style="flex:1;">'
            f'<div style="font-size:13px; color:#F0EDE8; font-weight:500;">{label}</div>'
            f'<div style="font-size:11px; color:#8A8480;">{value}</div>'
            f'</div>'
            f'<span style="font-size:11px; color:{status_color}; font-weight:600;">{status_label}</span>'
            f'</div>'
        )

    rows = (
        _src_row("📄", "Artist Profile",   f"data/artists/{selected_id}.json · last saved: {brain.updated_at[:10] if brain.updated_at else '?'}",  "#22C55E", "Loaded") +
        _src_row("🗂️", "Extended Profile", f"data/artists/{selected_id}_profile.json · updated: {profile_updated}", "#22C55E" if profile.get("cultural_pillars") else "#F59E0B", "Active" if profile.get("cultural_pillars") else "Minimal") +
        _src_row("📸", "Brand Vault",      f"{vault_count} asset(s) uploaded — {'visuals present' if has_visuals else 'no visuals yet'}", "#22C55E" if has_visuals else "#F59E0B", "Ready" if has_visuals else "Needs assets") +
        _src_row("🚀", "Distribution",     f"{dist_count} destination(s) configured",  "#22C55E" if dist_count > 0 else "#F59E0B", "Configured" if dist_count > 0 else "Not set") +
        _src_row("🧠", "Creative DNA",     "Loaded from artist JSON — visual keywords, palette, lighting", "#22C55E", "Active")
    )
    render_html(f'<div class="mw-card" style="padding:0.5rem 1.5rem;">{rows}</div>')


def _section(title: str, content_html: str):
    render_html(f"""
    <div class="mw-card" style="padding:1rem; margin-bottom:0.75rem;">
        <div style="font-size:11px; color:#8A8480; font-weight:600; letter-spacing:0.8px;
                    text-transform:uppercase; margin-bottom:0.75rem;">{title}</div>
        {content_html}
    </div>
    """)
