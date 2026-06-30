"""MusicWorks™ V3.2 — Brand Brain page (fully editable)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, tag_list_html, render_html
from brand_brain.artist_library import list_artists, load_artist, save_artist


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
    artist_ids   = [a["artist_id"]   for a in artists]

    default_id = st.session_state.get("brand_brain_artist_id", artist_ids[0])
    default_idx = artist_ids.index(default_id) if default_id in artist_ids else 0

    sel_idx = st.selectbox("Artist:", range(len(artist_names)),
                           format_func=lambda i: artist_names[i], index=default_idx)
    sel_id  = artist_ids[sel_idx]
    brain   = load_artist(sel_id)

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

    # ── TAB 1: Brand Voice ────────────────────────────────────────────────────
    with tab1:
        _tab_edit_bar("Brand Voice", "bb_voice", sel_id)
        if st.session_state.get(f"bb_voice_{sel_id}"):
            with st.form(f"form_voice_{sel_id}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    new_tone  = st.text_area("Tone (one per line)", value="\n".join(brain.brand_voice.tone), height=100)
                    new_style = st.text_area("Style (one per line)", value="\n".join(brain.brand_voice.style), height=80)
                    new_vocab = st.text_area("Vocabulary (one per line)", value="\n".join(brain.brand_voice.vocabulary), height=80)
                with col_b:
                    new_avoid = st.text_area("Never say (one per line)", value="\n".join(brain.brand_voice.avoid), height=80)
                    new_scr   = st.text_area("Scripture style", value=brain.brand_voice.scripture_style, height=80)
                    new_cta   = st.text_area("CTA style", value=brain.brand_voice.cta_style, height=60)
                st.markdown("<div class='mw-section-label'>Platform Voice</div>", unsafe_allow_html=True)
                pv = brain.brand_voice.platform_voice or {}
                pv_ig = st.text_area("Instagram", value=pv.get("instagram", ""), height=60)
                pv_tk = st.text_area("TikTok",    value=pv.get("tiktok", ""),    height=60)
                pv_yt = st.text_area("YouTube",   value=pv.get("youtube", ""),   height=60)
                pv_fb = st.text_area("Facebook",  value=pv.get("facebook", ""),  height=60)
                pv_em = st.text_area("Email",     value=pv.get("email", ""),     height=60)
                saved = st.form_submit_button("💾 Save Brand Voice", type="primary")
            if saved:
                b = load_artist(sel_id)
                b.brand_voice.tone       = [l.strip() for l in new_tone.splitlines()  if l.strip()]
                b.brand_voice.style      = [l.strip() for l in new_style.splitlines() if l.strip()]
                b.brand_voice.vocabulary = [l.strip() for l in new_vocab.splitlines() if l.strip()]
                b.brand_voice.avoid      = [l.strip() for l in new_avoid.splitlines() if l.strip()]
                b.brand_voice.scripture_style = new_scr.strip()
                b.brand_voice.cta_style       = new_cta.strip()
                b.brand_voice.platform_voice  = {k: v.strip() for k, v in {
                    "instagram": pv_ig, "tiktok": pv_tk, "youtube": pv_yt,
                    "facebook": pv_fb, "email": pv_em,
                }.items() if v.strip()}
                save_artist(b)
                st.session_state.pop(f"bb_voice_{sel_id}", None)
                st.success("Brand Voice saved.")
                st.rerun()
        else:
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
                    <div class="mw-card" style="padding:0.75rem 1rem; margin-bottom:0.5rem; border-left:3px solid #2D1B69;">
                        <div style="font-size:11px; color:#9B89D4; text-transform:uppercase; margin-bottom:4px;">{platform.title()}</div>
                        <div style="font-size:13px; color:#C8C4BE;">{note}</div>
                    </div>
                    """)

    # ── TAB 2: Creative DNA ───────────────────────────────────────────────────
    with tab2:
        _tab_edit_bar("Creative DNA", "bb_dna", sel_id)
        if st.session_state.get(f"bb_dna_{sel_id}"):
            with st.form(f"form_dna_{sel_id}"):
                col_c, col_d = st.columns(2)
                with col_c:
                    new_lighting  = st.text_area("Lighting (one per line)",     value="\n".join(brain.creative_dna.lighting), height=90)
                    new_env       = st.text_area("Environment (one per line)",  value="\n".join(brain.creative_dna.environment), height=80)
                    new_vkeys     = st.text_area("Visual keywords (one per line)", value="\n".join(brain.creative_dna.visual_keywords), height=80)
                    new_rkeys     = st.text_area("Rendering keywords (one per line)", value="\n".join(brain.creative_dna.rendering_keywords), height=80)
                with col_d:
                    new_lens      = st.text_area("Lens style",       value=brain.creative_dna.lens_style,      height=70)
                    new_cam       = st.text_area("Camera movement",  value=brain.creative_dna.camera_movement, height=60)
                    new_comp      = st.text_area("Composition",      value=brain.creative_dna.composition,     height=60)
                    new_avoid_dna = st.text_area("What to avoid (one per line)", value="\n".join(brain.creative_dna.what_to_avoid), height=80)
                st.markdown("<div class='mw-section-label'>Performance & Event Style</div>", unsafe_allow_html=True)
                new_festival = st.text_area("Festival style", value=brain.creative_dna.festival_style, height=60)
                new_church   = st.text_area("Church style",   value=brain.creative_dna.church_style,   height=60)
                new_perf     = st.text_area("Performance style", value=brain.creative_dna.performance_style, height=60)
                saved = st.form_submit_button("💾 Save Creative DNA", type="primary")
            if saved:
                b = load_artist(sel_id)
                b.creative_dna.lighting          = [l.strip() for l in new_lighting.splitlines()  if l.strip()]
                b.creative_dna.environment       = [l.strip() for l in new_env.splitlines()       if l.strip()]
                b.creative_dna.visual_keywords   = [l.strip() for l in new_vkeys.splitlines()     if l.strip()]
                b.creative_dna.rendering_keywords = [l.strip() for l in new_rkeys.splitlines()    if l.strip()]
                b.creative_dna.lens_style        = new_lens.strip()
                b.creative_dna.camera_movement   = new_cam.strip()
                b.creative_dna.composition       = new_comp.strip()
                b.creative_dna.what_to_avoid     = [l.strip() for l in new_avoid_dna.splitlines() if l.strip()]
                b.creative_dna.festival_style    = new_festival.strip()
                b.creative_dna.church_style      = new_church.strip()
                b.creative_dna.performance_style = new_perf.strip()
                save_artist(b)
                st.session_state.pop(f"bb_dna_{sel_id}", None)
                st.success("Creative DNA saved.")
                st.rerun()
        else:
            dna = brain.creative_dna
            col_c, col_d = st.columns(2)
            with col_c:
                palette = dna.color_palette
                swatches = ""
                color_map = {
                    "primary":          ("#2D1B69", "Primary"),
                    "secondary":        ("#D4A853", "Secondary"),
                    "accent":           ("#FF6B2B", "Accent"),
                    "background_warm":  ("#1A0F42", "Background"),
                }
                for ckey, (fallback, clabel) in color_map.items():
                    raw = palette.get(ckey, fallback)
                    hex_color = raw.split(" ")[0] if raw else fallback
                    swatches += f'<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;"><div class="color-swatch" style="background:{hex_color};"></div><span style="font-size:13px; color:#C8C4BE;">{clabel} — {hex_color}</span></div>'
                _section("Color Palette", swatches)
                _section("Lighting",    tag_list_html(dna.lighting, "tag"))
                _section("Environment", tag_list_html(dna.environment, "tag"))
            with col_d:
                _section("Lens Style",      f'<p style="font-size:13px; color:#C8C4BE;">{dna.lens_style}</p>')
                _section("Camera Movement", f'<p style="font-size:13px; color:#C8C4BE;">{dna.camera_movement}</p>')
                _section("Composition",     f'<p style="font-size:13px; color:#C8C4BE;">{dna.composition}</p>')
                _section("Visual Keywords",    tag_list_html(dna.visual_keywords, "tag"))
                _section("Rendering Keywords", tag_list_html(dna.rendering_keywords, "tag tag-fire"))
            if dna.what_to_avoid:
                avoid_html = "".join(f'<div style="font-size:12px; color:#EF4444; padding:4px 0; border-bottom:1px solid #1E1E1E;">✗ {a}</div>' for a in dna.what_to_avoid)
                _section("Never Use (Visual)", avoid_html)

    # ── TAB 3: Theology ───────────────────────────────────────────────────────
    with tab3:
        _tab_edit_bar("Theology", "bb_theo", sel_id)
        if st.session_state.get(f"bb_theo_{sel_id}"):
            with st.form(f"form_theo_{sel_id}"):
                new_stance  = st.text_area("Theological stance", value=brain.theological_guardrails.theological_stance, height=80)
                new_scr_acc = st.text_area("Scripture accuracy policy", value=brain.theological_guardrails.scripture_accuracy, height=70)
                col_e, col_f = st.columns(2)
                with col_e:
                    new_req  = st.text_area("Required (one per line)", value="\n".join(brain.theological_guardrails.required), height=120)
                with col_f:
                    new_forb = st.text_area("Forbidden (one per line)", value="\n".join(brain.theological_guardrails.forbidden), height=120)
                saved = st.form_submit_button("💾 Save Theology", type="primary")
            if saved:
                b = load_artist(sel_id)
                b.theological_guardrails.theological_stance = new_stance.strip()
                b.theological_guardrails.scripture_accuracy = new_scr_acc.strip()
                b.theological_guardrails.required  = [l.strip() for l in new_req.splitlines()  if l.strip()]
                b.theological_guardrails.forbidden = [l.strip() for l in new_forb.splitlines() if l.strip()]
                save_artist(b)
                st.session_state.pop(f"bb_theo_{sel_id}", None)
                st.success("Theology saved.")
                st.rerun()
        else:
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

    # ── TAB 4: Rules & Preferences ────────────────────────────────────────────
    with tab4:
        _tab_edit_bar("Rules & Preferences", "bb_rules", sel_id)
        if st.session_state.get(f"bb_rules_{sel_id}"):
            with st.form(f"form_rules_{sel_id}"):
                new_rules = st.text_area("Brand rules (one per line)",        value="\n".join(brain.brand_rules),          height=150)
                new_prefs = st.text_area("Founder preferences (one per line)", value="\n".join(brain.founder_preferences), height=120)
                new_fnotes = st.text_area("Future notes (one per line)",       value="\n".join(brain.future_notes),        height=100)
                saved = st.form_submit_button("💾 Save Rules", type="primary")
            if saved:
                b = load_artist(sel_id)
                b.brand_rules         = [l.strip() for l in new_rules.splitlines()  if l.strip()]
                b.founder_preferences = [l.strip() for l in new_prefs.splitlines()  if l.strip()]
                b.future_notes        = [l.strip() for l in new_fnotes.splitlines() if l.strip()]
                save_artist(b)
                st.session_state.pop(f"bb_rules_{sel_id}", None)
                st.success("Rules & Preferences saved.")
                st.rerun()
        else:
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

    from execution.brand_vault import vault_asset_count, vault_has_visuals
    from execution.distribution_store import load_distribution, dist_configured_count
    from execution.profile_store import load_profile

    vault_count = vault_asset_count(sel_id)
    has_visuals = vault_has_visuals(sel_id)
    dist        = load_distribution(sel_id)
    dist_count  = dist_configured_count(dist)
    profile     = load_profile(sel_id)
    p_updated   = profile.get("updated_at", "")[:10] or "not set"

    def _src_row(icon, label, value, status_color, status_label):
        return (
            f'<div style="display:flex; align-items:center; gap:12px; padding:8px 0; border-bottom:1px solid #1E1E1E;">'
            f'<span style="font-size:18px; min-width:24px;">{icon}</span>'
            f'<div style="flex:1;"><div style="font-size:13px; color:#F0EDE8; font-weight:500;">{label}</div>'
            f'<div style="font-size:11px; color:#8A8480;">{value}</div></div>'
            f'<span style="font-size:11px; color:{status_color}; font-weight:600;">{status_label}</span>'
            f'</div>'
        )

    rows = (
        _src_row("📄", "Artist Profile",   f"data/artists/{sel_id}.json · last saved: {brain.updated_at[:10] if brain.updated_at else '?'}", "#22C55E", "Loaded") +
        _src_row("🗂️", "Extended Profile", f"data/profiles/{sel_id}.json · updated: {p_updated}", "#22C55E" if profile.get("cultural_pillars") else "#F59E0B", "Active" if profile.get("cultural_pillars") else "Minimal") +
        _src_row("📸", "Brand Vault",      f"{vault_count} asset(s) — {'visuals present' if has_visuals else 'no visuals yet'}", "#22C55E" if has_visuals else "#F59E0B", "Ready" if has_visuals else "Needs assets") +
        _src_row("🚀", "Distribution",     f"{dist_count} destination(s) configured", "#22C55E" if dist_count > 0 else "#F59E0B", "Configured" if dist_count > 0 else "Not set") +
        _src_row("🧠", "Creative DNA",     "Loaded from artist JSON — visual keywords, palette, lighting", "#22C55E", "Active")
    )
    render_html(f'<div class="mw-card" style="padding:0.5rem 1.5rem;">{rows}</div>')

    col_go, _ = st.columns([1, 3])
    with col_go:
        if st.button("✏️  Edit in Artist Profile", use_container_width=True):
            st.session_state.managing_artist_id = sel_id
            navigate_to("artists")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tab_edit_bar(tab_label: str, state_key: str, artist_id: str):
    """Render an Edit / Cancel button row at the top of a Brand Brain tab."""
    full_key = f"{state_key}_{artist_id}"
    editing  = st.session_state.get(full_key, False)
    col_lbl, col_btn = st.columns([4, 1])
    with col_lbl:
        st.markdown(f"<div style='font-size:12px; color:#8A8480; margin-top:4px;'>{'Editing ' + tab_label if editing else tab_label + ' (read-only — click Edit to change)'}</div>", unsafe_allow_html=True)
    with col_btn:
        if editing:
            if st.button("✕ Cancel", key=f"cancel_{state_key}_{artist_id}", use_container_width=True):
                st.session_state.pop(full_key, None)
                st.rerun()
        else:
            if st.button(f"✏️ Edit", key=f"edit_{state_key}_{artist_id}", use_container_width=True):
                st.session_state[full_key] = True
                st.rerun()
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)


def _section(title: str, content_html: str):
    render_html(f"""
    <div class="mw-card" style="padding:1rem; margin-bottom:0.75rem;">
        <div style="font-size:11px; color:#8A8480; font-weight:600; letter-spacing:0.8px;
                    text-transform:uppercase; margin-bottom:0.75rem;">{title}</div>
        {content_html}
    </div>
    """)
