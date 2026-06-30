"""MusicWorks™ V3.2 — Artist Management: per-card editing, create flow, Brand Vault, Distribution."""
import sys
import json
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from datetime import datetime, timezone

from ui.components import page_header, navigate_to, tag_list_html, render_html
from brand_brain.artist_library import list_artists, load_artist, save_artist, create_artist, artist_id_exists, make_slug
from execution.brand_vault import (
    VAULT_TYPES, IMAGE_EXTS, VIDEO_EXTS,
    load_vault_meta, store_vault_asset, delete_vault_asset, vault_asset_count,
)
from execution.distribution_store import (
    SOCIAL_FIELDS, STREAMING_FIELDS, OWNED_FIELDS, PRESS_FIELDS,
    PLATFORM_ICONS, load_distribution, save_distribution, dist_configured_count,
)
from execution.profile_store import load_profile, save_profile


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    if st.session_state.get("creating_artist"):
        _render_create_form()
    elif st.session_state.get("managing_artist_id"):
        brain = load_artist(st.session_state.managing_artist_id)
        if not brain:
            st.error("Artist not found.")
            st.session_state.pop("managing_artist_id", None)
            st.rerun()
        _render_management_view(brain)
    else:
        _render_artist_list()


# ── Artist list ───────────────────────────────────────────────────────────────

def _render_artist_list():
    page_header("Artists", "Your permanent artist library.", "👥")

    col_hdr, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("➕  Add Artist", type="primary", use_container_width=True):
            st.session_state["creating_artist"] = True
            st.rerun()

    artists = list_artists()

    if not artists:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;">
            <div style="font-size:40px; margin-bottom:1rem;">👥</div>
            <div style="font-size:18px; color:#F0EDE8; margin-bottom:0.5rem;">No artists yet</div>
            <div>Click <strong>Add Artist</strong> above to create your first artist profile.</div>
        </div>
        """)
        return

    for info in artists:
        artist_id = info["artist_id"]
        brain = load_artist(artist_id)
        if not brain:
            continue

        vault_count = vault_asset_count(artist_id)
        dist = load_distribution(artist_id)
        dist_count = dist_configured_count(dist)

        is_flagship = artist_id == "fire_and_flow_gospel"
        badge = '<span class="badge badge-live" style="margin-left:8px;font-size:10px;">Flagship</span>' if is_flagship else ""

        render_html(
            f'<div class="mw-card" style="padding:1.25rem 1.5rem; margin-bottom:0.75rem;">'
            f'<div style="font-size:18px; font-weight:800; color:#F0EDE8;">{brain.artist_name}{badge}</div>'
            f'<div style="font-size:13px; color:#9B89D4; margin-top:3px;">{brain.tagline}</div>'
            f'<div style="display:flex; gap:16px; margin-top:8px;">'
            f'<span style="font-size:11px; color:#8A8480;">📸 {vault_count} vault asset{"s" if vault_count != 1 else ""}</span>'
            f'<span style="font-size:11px; color:#8A8480;">🚀 {dist_count} destination{"s" if dist_count != 1 else ""} configured</span>'
            f'</div></div>'
        )

        btn_a, btn_b, btn_c, btn_d = st.columns(4)
        with btn_a:
            if st.button("✏️  Manage Artist", key=f"manage_{artist_id}", type="primary", use_container_width=True):
                st.session_state.managing_artist_id = artist_id
                st.rerun()
        with btn_b:
            if st.button("🎵  New Project", key=f"new_{artist_id}", use_container_width=True):
                st.session_state.wizard_step = 0
                st.session_state.wizard_data = {"artist_id": artist_id, "artist_name": brain.artist_name}
                st.session_state.pop("wizard_campaign_id", None)
                navigate_to("wizard")
        with btn_c:
            if st.button("📦  Campaigns", key=f"camp_{artist_id}", use_container_width=True):
                navigate_to("campaigns")
        with btn_d:
            if st.button("🧠  Brand Brain", key=f"brain_{artist_id}", use_container_width=True):
                st.session_state.brand_brain_artist_id = artist_id
                navigate_to("brand_brain")

        st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)


# ── Create Artist form ────────────────────────────────────────────────────────

def _render_create_form():
    if st.button("← Back to Artists", key="back_from_create"):
        st.session_state.pop("creating_artist", None)
        st.rerun()

    page_header("Add Artist", "Create a new artist profile.", "➕")

    with st.form("create_artist_form", clear_on_submit=False):
        st.markdown("<div class='mw-section-label'>Core Identity</div>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            f_name    = st.text_input("Artist name *", placeholder="e.g. Fire & Flow Gospel")
            f_type    = st.selectbox("Artist type", ["Solo Artist", "Duo", "Group", "Choir", "Ministry"])
            f_genres  = st.text_input("Genres (comma-separated)", placeholder="e.g. Afro-Gospel, Gospel R&B")
        with col_b:
            f_tagline = st.text_input("Tagline", placeholder="One-line identity statement")
            f_heritage = st.text_area("Cultural heritage (one per line)", height=80, placeholder="African\nCaribbean\nTrinidadian")

        f_mission   = st.text_area("Mission statement", height=80)
        f_bio_short = st.text_area("Short bio", height=80)
        f_bio_long  = st.text_area("Long bio (optional)", height=100)

        st.divider()
        st.markdown("<div class='mw-section-label'>Identity & Culture</div>", unsafe_allow_html=True)

        col_c, col_d = st.columns(2)
        with col_c:
            f_pillars   = st.text_area("Cultural pillars (one per line)", height=100)
            f_cities    = st.text_area("Cities of influence (one per line)", height=60)
        with col_d:
            f_audience  = st.text_area("Target audience", height=100)
            f_countries = st.text_area("Countries (one per line)", height=60)

        st.divider()
        st.markdown("<div class='mw-section-label'>Brand & Ministry</div>", unsafe_allow_html=True)

        col_e, col_f = st.columns(2)
        with col_e:
            f_ministry    = st.text_area("Ministry focus", height=80)
            f_voice_tone  = st.text_input("Brand voice / tone (comma-separated)", placeholder="Devotional, Pastoral, Educational")
        with col_f:
            f_visual      = st.text_area("Visual style notes", height=80)
            f_theology    = st.text_area("Theology notes", height=80)

        f_notes = st.text_area("Founder notes (internal only)", height=60)

        submitted = st.form_submit_button("✅  Create Artist", type="primary", use_container_width=True)

    if submitted:
        name = f_name.strip()
        if not name:
            st.error("Artist name is required.")
            return

        slug = make_slug(name)

        if artist_id_exists(slug):
            st.error(f"An artist with the ID '{slug}' already exists. Please use a different name, or manage the existing artist.")
            return

        try:
            brain = create_artist(slug, {
                "artist_name":       name,
                "tagline":           f_tagline.strip(),
                "mission":           f_mission.strip(),
                "bio_short":         f_bio_short.strip(),
                "bio_long":          f_bio_long.strip(),
                "genre":             f_genres,
                "heritage":          f_heritage,
                "brand_voice_tone":  f_voice_tone,
                "theology_notes":    f_theology.strip(),
            })

            save_profile(slug, {
                "cultural_pillars":       [l.strip() for l in f_pillars.splitlines() if l.strip()],
                "cities_of_influence":    [l.strip() for l in f_cities.splitlines() if l.strip()],
                "countries_of_influence": [l.strip() for l in f_countries.splitlines() if l.strip()],
                "target_audience":        f_audience.strip(),
                "ministry_focus":         f_ministry.strip(),
                "visual_style_notes":     f_visual.strip(),
                "notes":                  f_notes.strip(),
            })

            st.session_state.pop("creating_artist", None)
            st.session_state.managing_artist_id = slug
            st.success(f"Artist '{name}' created. Opening profile...")
            st.rerun()

        except Exception as exc:
            st.error(f"Error creating artist: {exc}")


# ── Management view ───────────────────────────────────────────────────────────

def _render_management_view(brain):
    if st.button("← Back to Artists", key="back_to_list"):
        # Clear all card-edit states for this artist
        for k in list(st.session_state.keys()):
            if k.startswith(f"card_ed_") and k.endswith(f"_{brain.artist_id}"):
                del st.session_state[k]
        st.session_state.pop("managing_artist_id", None)
        st.rerun()

    is_flagship = brain.artist_id == "fire_and_flow_gospel"
    badge = " · Flagship Artist" if is_flagship else ""
    render_html(
        f'<div style="margin:1rem 0 1.5rem 0;">'
        f'<div style="font-size:24px; font-weight:800; color:#F0EDE8;">{brain.artist_name}{badge}</div>'
        f'<div style="font-size:14px; color:#9B89D4; margin-top:4px;">{brain.tagline}</div>'
        f'</div>'
    )

    tab_profile, tab_vault, tab_dist = st.tabs(["✏️  Profile", "📸  Brand Vault", "🚀  Distribution"])

    with tab_profile:
        _render_profile_tab(brain)
    with tab_vault:
        _render_vault_tab(brain.artist_id)
    with tab_dist:
        _render_distribution_tab(brain.artist_id, brain.artist_name)


# ── PROFILE TAB ───────────────────────────────────────────────────────────────

def _sec_hdr(title: str, card_key: str, artist_id: str, margin_top: str = "1.5rem"):
    """Render a section label with an inline Edit / Cancel toggle button."""
    state_key = f"card_ed_{card_key}_{artist_id}"
    editing = st.session_state.get(state_key, False)
    col_t, col_b = st.columns([6, 1])
    with col_t:
        st.markdown(
            f"<div class='mw-section-label' style='margin-top:{margin_top};'>{title}</div>",
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(f"<div style='margin-top:{margin_top};'></div>", unsafe_allow_html=True)
        if editing:
            if st.button("✕", key=f"cancel_{card_key}_{artist_id}", use_container_width=True, help="Cancel"):
                st.session_state.pop(state_key, None)
                st.rerun()
        else:
            if st.button("✏️", key=f"edit_{card_key}_{artist_id}", use_container_width=True, help=f"Edit {title}"):
                st.session_state[state_key] = True
                st.rerun()
    return editing


def _save_btn(card_key: str, artist_id: str, label: str = "💾 Save") -> bool:
    col_s, _ = st.columns([1, 3])
    with col_s:
        return st.button(label, key=f"save_{card_key}_{artist_id}", type="primary", use_container_width=True)


def _card_done(card_key: str, artist_id: str, msg: str = "Saved."):
    st.session_state.pop(f"card_ed_{card_key}_{artist_id}", None)
    st.success(msg)
    st.rerun()


def _render_profile_tab(brain):
    profile = load_profile(brain.artist_id)
    aid = brain.artist_id

    # ── Overview (name / tagline) ──────────────────────────────────────────
    editing = _sec_hdr("Artist Identity", "overview", aid, margin_top="0")
    if editing:
        new_name    = st.text_input("Artist name", value=brain.artist_name, key=f"inp_ovname_{aid}")
        new_tagline = st.text_input("Tagline", value=brain.tagline, key=f"inp_ovtag_{aid}")
        if _save_btn("overview", aid):
            brain.artist_name = new_name.strip()
            brain.display_name = new_name.strip()
            brain.tagline = new_tagline.strip()
            save_artist(brain)
            _card_done("overview", aid, f"Artist name updated to '{new_name.strip()}'.")
    else:
        render_html(
            f'<div class="mw-card" style="padding:1rem;">'
            f'<div style="font-size:22px; font-weight:800; color:#F0EDE8;">{brain.artist_name}</div>'
            f'<div style="font-size:13px; color:#9B89D4; margin-top:4px;">{brain.tagline}</div>'
            f'</div>'
        )

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        # MISSION
        editing = _sec_hdr("Mission", "mission", aid)
        if editing:
            new_mission = st.text_area("", value=brain.mission, height=120,
                                       key=f"inp_mission_{aid}", label_visibility="collapsed")
            if _save_btn("mission", aid):
                brain.mission = new_mission.strip()
                save_artist(brain)
                _card_done("mission", aid)
        else:
            render_html(f'<div class="mw-card" style="padding:1rem; font-size:14px; color:#C8C4BE; line-height:1.7;">{brain.mission or "<em style=color:#6A6460>Not set</em>"}</div>')

        # BIOGRAPHY
        editing = _sec_hdr("Biography", "bio", aid)
        if editing:
            new_bio_short = st.text_area("Short bio", value=brain.bio_short or "", height=90, key=f"inp_bios_{aid}")
            new_bio_long  = st.text_area("Long bio", value=brain.bio_long or "", height=130, key=f"inp_biol_{aid}")
            if _save_btn("bio", aid):
                brain.bio_short = new_bio_short.strip()
                brain.bio_long  = new_bio_long.strip()
                save_artist(brain)
                _card_done("bio", aid)
        else:
            txt = brain.bio_short or "<em style='color:#6A6460'>Not set — click ✏️ to add</em>"
            render_html(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#8A8480; line-height:1.6;">{txt}</div>')

        # MINISTRY FOCUS
        editing = _sec_hdr("Ministry Focus", "ministry", aid)
        if editing:
            new_min = st.text_area("", value=profile.get("ministry_focus", ""), height=100,
                                   key=f"inp_min_{aid}", label_visibility="collapsed")
            if _save_btn("ministry", aid):
                save_profile(aid, {**profile, "ministry_focus": new_min.strip()})
                _card_done("ministry", aid)
        else:
            txt = profile.get("ministry_focus") or "<em style='color:#6A6460'>Not set</em>"
            render_html(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#C8C4BE; line-height:1.6;">{txt}</div>')

        # TARGET AUDIENCE
        editing = _sec_hdr("Target Audience", "audience", aid)
        if editing:
            new_aud = st.text_area("", value=profile.get("target_audience", ""), height=80,
                                   key=f"inp_aud_{aid}", label_visibility="collapsed")
            if _save_btn("audience", aid):
                save_profile(aid, {**profile, "target_audience": new_aud.strip()})
                _card_done("audience", aid)
        else:
            txt = profile.get("target_audience") or "<em style='color:#6A6460'>Not set</em>"
            render_html(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#8A8480; line-height:1.6;">{txt}</div>')

    with col_right:
        # GLOBAL IDENTITY
        editing = _sec_hdr("Global Identity", "identity", aid, margin_top="0")
        if editing:
            new_heritage = st.text_area("Heritage (one per line)", value="\n".join(brain.heritage), height=80, key=f"inp_her_{aid}")
            new_genre    = st.text_area("Genres (one per line)", value="\n".join(brain.genre), height=80, key=f"inp_gen_{aid}")
            if _save_btn("identity", aid):
                brain.heritage = [l.strip() for l in new_heritage.splitlines() if l.strip()]
                brain.genre    = [l.strip() for l in new_genre.splitlines() if l.strip()]
                save_artist(brain)
                _card_done("identity", aid)
        else:
            heritage_html = tag_list_html(brain.heritage, "tag tag-indigo") if brain.heritage else "<em style='color:#6A6460'>Not set</em>"
            genre_html    = tag_list_html(brain.genre, "tag tag-gold") if brain.genre else "<em style='color:#6A6460'>Not set</em>"
            render_html(
                f'<div class="mw-card" style="padding:1rem;">'
                f'<div style="margin-bottom:0.75rem;"><div style="font-size:11px; color:#8A8480; margin-bottom:6px;">HERITAGE</div>{heritage_html}</div>'
                f'<div><div style="font-size:11px; color:#8A8480; margin-bottom:6px;">GENRE</div>{genre_html}</div>'
                f'</div>'
            )

        # CULTURAL PILLARS
        editing = _sec_hdr("Cultural Pillars", "pillars", aid)
        if editing:
            new_pillars = st.text_area("One per line", value="\n".join(profile.get("cultural_pillars", [])),
                                       height=120, key=f"inp_pil_{aid}")
            if _save_btn("pillars", aid):
                save_profile(aid, {**profile, "cultural_pillars": [l.strip() for l in new_pillars.splitlines() if l.strip()]})
                _card_done("pillars", aid)
        else:
            pillars = profile.get("cultural_pillars", [])
            if pillars:
                pillars_html = "".join(f'<div style="font-size:12px; color:#C8C4BE; padding:4px 0; border-bottom:1px solid #1E1E1E;">— {p}</div>' for p in pillars)
                render_html(f'<div class="mw-card" style="padding:1rem;">{pillars_html}</div>')
            else:
                render_html('<div class="mw-card" style="padding:1rem;"><em style="color:#6A6460; font-size:12px;">Not set</em></div>')

        # CITIES & COUNTRIES
        editing = _sec_hdr("Cities & Countries", "cities", aid)
        if editing:
            new_cities    = st.text_area("Cities (one per line)", value="\n".join(profile.get("cities_of_influence", [])), height=70, key=f"inp_cit_{aid}")
            new_countries = st.text_area("Countries (one per line)", value="\n".join(profile.get("countries_of_influence", [])), height=70, key=f"inp_cou_{aid}")
            if _save_btn("cities", aid):
                save_profile(aid, {
                    **profile,
                    "cities_of_influence":    [l.strip() for l in new_cities.splitlines() if l.strip()],
                    "countries_of_influence": [l.strip() for l in new_countries.splitlines() if l.strip()],
                })
                _card_done("cities", aid)
        else:
            locs = list(profile.get("cities_of_influence", [])) + list(profile.get("countries_of_influence", []))
            if locs:
                render_html(f'<div class="mw-card" style="padding:1rem;">{tag_list_html(locs, "tag")}</div>')
            else:
                render_html('<div class="mw-card" style="padding:1rem;"><em style="color:#6A6460; font-size:12px;">Not set</em></div>')

    # ── Full-width sections below ──────────────────────────────────────────

    # BRAND VOICE
    editing = _sec_hdr("Brand Voice", "voice", aid)
    if editing:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            new_tone  = st.text_area("Tone (one per line)", value="\n".join(brain.brand_voice.tone), height=90, key=f"inp_tone_{aid}")
            new_style = st.text_area("Style (one per line)", value="\n".join(brain.brand_voice.style), height=80, key=f"inp_sty_{aid}")
        with col_v2:
            new_vocab = st.text_area("Vocabulary (one per line)", value="\n".join(brain.brand_voice.vocabulary), height=80, key=f"inp_voc_{aid}")
            new_av    = st.text_area("Never say (one per line)", value="\n".join(brain.brand_voice.avoid), height=80, key=f"inp_av_{aid}")
        new_scr = st.text_area("Scripture style", value=brain.brand_voice.scripture_style, height=60, key=f"inp_scr_{aid}")
        new_cta = st.text_area("CTA style", value=brain.brand_voice.cta_style, height=60, key=f"inp_cta_{aid}")
        if _save_btn("voice", aid, "💾 Save Brand Voice"):
            brain.brand_voice.tone       = [l.strip() for l in new_tone.splitlines() if l.strip()]
            brain.brand_voice.style      = [l.strip() for l in new_style.splitlines() if l.strip()]
            brain.brand_voice.vocabulary = [l.strip() for l in new_vocab.splitlines() if l.strip()]
            brain.brand_voice.avoid      = [l.strip() for l in new_av.splitlines() if l.strip()]
            brain.brand_voice.scripture_style = new_scr.strip()
            brain.brand_voice.cta_style       = new_cta.strip()
            save_artist(brain)
            _card_done("voice", aid)
    else:
        parts = []
        if brain.brand_voice.tone:
            parts.append(f'<div style="margin-bottom:0.75rem;"><div style="font-size:11px; color:#8A8480; margin-bottom:4px;">TONE</div>{tag_list_html(brain.brand_voice.tone, "tag tag-indigo")}</div>')
        if brain.brand_voice.style:
            parts.append(f'<div style="margin-bottom:0.75rem;"><div style="font-size:11px; color:#8A8480; margin-bottom:4px;">STYLE</div>{tag_list_html(brain.brand_voice.style, "tag")}</div>')
        if brain.brand_voice.vocabulary:
            parts.append(f'<div><div style="font-size:11px; color:#8A8480; margin-bottom:4px;">VOCABULARY</div>{tag_list_html(brain.brand_voice.vocabulary, "tag tag-gold")}</div>')
        if parts:
            render_html(f'<div class="mw-card" style="padding:1rem;">{"".join(parts)}</div>')

    # CREATIVE DNA (visual style)
    editing = _sec_hdr("Visual Style & Creative DNA", "visual", aid)
    if editing:
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            new_vis     = st.text_area("Visual style notes", value=profile.get("visual_style_notes", ""), height=80, key=f"inp_vis_{aid}")
            new_lighting = st.text_area("Lighting (one per line)", value="\n".join(brain.creative_dna.lighting), height=80, key=f"inp_lit_{aid}")
            new_env      = st.text_area("Environment (one per line)", value="\n".join(brain.creative_dna.environment), height=80, key=f"inp_env_{aid}")
        with col_w2:
            new_lens  = st.text_area("Lens style", value=brain.creative_dna.lens_style, height=80, key=f"inp_lens_{aid}")
            new_cam   = st.text_area("Camera movement", value=brain.creative_dna.camera_movement, height=60, key=f"inp_cam_{aid}")
            new_vkeys = st.text_area("Visual keywords (one per line)", value="\n".join(brain.creative_dna.visual_keywords), height=80, key=f"inp_vkeys_{aid}")
        new_avoid_vis = st.text_area("What to avoid (one per line)", value="\n".join(brain.creative_dna.what_to_avoid), height=80, key=f"inp_avv_{aid}")
        if _save_btn("visual", aid, "💾 Save Visual Style"):
            save_profile(aid, {**profile, "visual_style_notes": new_vis.strip()})
            brain.creative_dna.lighting       = [l.strip() for l in new_lighting.splitlines() if l.strip()]
            brain.creative_dna.environment    = [l.strip() for l in new_env.splitlines() if l.strip()]
            brain.creative_dna.lens_style     = new_lens.strip()
            brain.creative_dna.camera_movement = new_cam.strip()
            brain.creative_dna.visual_keywords = [l.strip() for l in new_vkeys.splitlines() if l.strip()]
            brain.creative_dna.what_to_avoid   = [l.strip() for l in new_avoid_vis.splitlines() if l.strip()]
            save_artist(brain)
            _card_done("visual", aid)
    else:
        vis_note = profile.get("visual_style_notes", "")
        content = f'<div style="font-size:13px; color:#C8C4BE; line-height:1.6; margin-bottom:0.75rem;">{vis_note}</div>' if vis_note else ""
        if brain.creative_dna.lighting:
            content += f'<div style="margin-top:0.5rem;"><div style="font-size:11px; color:#8A8480; margin-bottom:4px;">LIGHTING</div>{tag_list_html(brain.creative_dna.lighting, "tag")}</div>'
        if content:
            render_html(f'<div class="mw-card" style="padding:1rem;">{content}</div>')

    # THEOLOGY
    editing = _sec_hdr("Theology", "theology", aid)
    if editing:
        new_stance = st.text_area("Theological stance", value=brain.theological_guardrails.theological_stance, height=80, key=f"inp_stance_{aid}")
        new_scr_acc = st.text_area("Scripture accuracy policy", value=brain.theological_guardrails.scripture_accuracy, height=60, key=f"inp_scracc_{aid}")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            new_req  = st.text_area("Required (one per line)", value="\n".join(brain.theological_guardrails.required), height=100, key=f"inp_req_{aid}")
        with col_t2:
            new_forb = st.text_area("Forbidden (one per line)", value="\n".join(brain.theological_guardrails.forbidden), height=100, key=f"inp_forb_{aid}")
        if _save_btn("theology", aid, "💾 Save Theology"):
            brain.theological_guardrails.theological_stance = new_stance.strip()
            brain.theological_guardrails.scripture_accuracy = new_scr_acc.strip()
            brain.theological_guardrails.required  = [l.strip() for l in new_req.splitlines() if l.strip()]
            brain.theological_guardrails.forbidden = [l.strip() for l in new_forb.splitlines() if l.strip()]
            save_artist(brain)
            _card_done("theology", aid)
    else:
        stance = brain.theological_guardrails.theological_stance
        if stance:
            render_html(f'<div class="mw-card" style="padding:1rem; border-left:3px solid #D4A853; font-size:13px; color:#C8C4BE; line-height:1.6;">{stance}</div>')
        req_html  = "".join(f'<div style="font-size:12px; color:#22C55E; padding:3px 0;">✓ {r}</div>' for r in brain.theological_guardrails.required)
        forb_html = "".join(f'<div style="font-size:12px; color:#EF4444; padding:3px 0;">✗ {r}</div>' for r in brain.theological_guardrails.forbidden)
        if req_html or forb_html:
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                if req_html:
                    render_html(f'<div class="mw-card" style="padding:0.75rem 1rem;"><div style="font-size:11px; color:#8A8480; margin-bottom:6px;">REQUIRED</div>{req_html}</div>')
            with col_t2:
                if forb_html:
                    render_html(f'<div class="mw-card" style="padding:0.75rem 1rem;"><div style="font-size:11px; color:#8A8480; margin-bottom:6px;">FORBIDDEN</div>{forb_html}</div>')

    # BRAND RULES
    editing = _sec_hdr("Brand Rules", "rules", aid)
    if editing:
        new_rules = st.text_area("One per line", value="\n".join(brain.brand_rules), height=150, key=f"inp_rules_{aid}")
        new_prefs = st.text_area("Founder preferences (one per line)", value="\n".join(brain.founder_preferences), height=100, key=f"inp_prefs_{aid}")
        if _save_btn("rules", aid, "💾 Save Rules"):
            brain.brand_rules          = [l.strip() for l in new_rules.splitlines() if l.strip()]
            brain.founder_preferences  = [l.strip() for l in new_prefs.splitlines() if l.strip()]
            save_artist(brain)
            _card_done("rules", aid)
    else:
        rules_html = "".join(f'<div style="font-size:12px; color:#C8C4BE; padding:5px 0; border-bottom:1px solid #1E1E1E;">— {r}</div>' for r in brain.brand_rules)
        if rules_html:
            render_html(f'<div class="mw-card" style="padding:1rem;">{rules_html}</div>')

    # FOUNDER NOTES
    editing = _sec_hdr("Founder Notes", "notes", aid)
    if editing:
        new_notes = st.text_area("", value=profile.get("notes", ""), height=80,
                                 key=f"inp_notes_{aid}", label_visibility="collapsed")
        if _save_btn("notes", aid):
            save_profile(aid, {**profile, "notes": new_notes.strip()})
            _card_done("notes", aid)
    else:
        txt = profile.get("notes", "")
        if txt:
            render_html(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#8A8480; line-height:1.6; font-style:italic;">{txt}</div>')

    st.caption(f"Last saved: {brain.updated_at[:10] if brain.updated_at else 'never'}")


# ── BRAND VAULT TAB ───────────────────────────────────────────────────────────

def _render_vault_tab(artist_id: str):
    meta = load_vault_meta(artist_id)
    assets = meta.get("assets", [])

    st.markdown("<div class='mw-section-label' style='margin-top:0;'>Upload Brand Assets</div>", unsafe_allow_html=True)

    asset_type_labels = [lbl for _, lbl, _ in VAULT_TYPES]
    asset_type_keys   = [key for key, _, _ in VAULT_TYPES]

    col_a, col_b = st.columns([1, 2])
    with col_a:
        sel_label = st.selectbox("Asset type:", asset_type_labels, key=f"vault_type_{artist_id}")
        sel_key   = asset_type_keys[asset_type_labels.index(sel_label)]
    with col_b:
        uploaded = st.file_uploader(
            f"Upload {sel_label}:",
            type=["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "pdf", "svg"],
            accept_multiple_files=True,
            key=f"vault_up_{sel_key}_{artist_id}",
        )

    if uploaded:
        saved = 0
        for f in uploaded:
            try:
                store_vault_asset(artist_id, sel_key, f)
                saved += 1
            except Exception as e:
                st.error(f"Could not save {f.name}: {e}")
        if saved:
            st.success(f"{saved} file(s) added to Brand Vault.")
            st.rerun()

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    if not assets:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:2.5rem; color:#8A8480;">
            <div style="font-size:32px; margin-bottom:0.75rem;">📸</div>
            <div style="font-size:15px; color:#F0EDE8; margin-bottom:0.5rem;">Brand Vault is empty</div>
            <div style="font-size:13px;">Upload artist photos, logos, album covers, and creative references above.</div>
        </div>
        """)
        return

    by_type: dict[str, list] = {}
    for a in assets:
        by_type.setdefault(a.get("asset_type", "misc"), []).append(a)

    type_order = [k for k, _, _ in VAULT_TYPES]

    for asset_type in type_order + [k for k in by_type if k not in type_order]:
        group = by_type.get(asset_type, [])
        if not group:
            continue
        icon  = next((ic  for k, _, ic  in VAULT_TYPES if k == asset_type), "📁")
        label = next((lbl for k, lbl, _ in VAULT_TYPES if k == asset_type), asset_type)
        st.markdown(f"<div class='mw-section-label'>{icon} {label}</div>", unsafe_allow_html=True)

        image_assets = [a for a in group if Path(a["file_name"]).suffix.lower() in IMAGE_EXTS]
        other_assets = [a for a in group if Path(a["file_name"]).suffix.lower() not in IMAGE_EXTS]

        if image_assets:
            img_cols = st.columns(min(len(image_assets), 4))
            for col, asset in zip(img_cols, image_assets):
                path = Path(asset["file_path"])
                with col:
                    if path.exists():
                        st.image(str(path), use_container_width=True)
                    else:
                        render_html(f'<div class="mw-card" style="padding:0.75rem; text-align:center; color:#8A8480;"><div style="font-size:24px;">🖼️</div><div style="font-size:11px;">{asset["file_name"]}</div></div>')
                    size_kb = asset.get("file_size", 0) // 1024
                    st.caption(f"{asset['file_name']} · {size_kb} KB")
                    if st.button("Remove", key=f"del_{asset['asset_id']}", use_container_width=True):
                        delete_vault_asset(artist_id, asset["asset_id"])
                        st.rerun()

        for asset in other_assets:
            path = Path(asset["file_path"])
            suffix = Path(asset["file_name"]).suffix.lower()
            col_info, col_del = st.columns([4, 1])
            with col_info:
                if suffix in VIDEO_EXTS and path.exists():
                    with st.expander(f"▶  {asset['file_name']}", expanded=False):
                        st.video(str(path))
                else:
                    size_kb = asset.get("file_size", 0) // 1024
                    render_html(
                        f'<div class="mw-card" style="padding:0.75rem 1rem; display:flex; align-items:center; gap:10px;">'
                        f'<span style="font-size:20px;">{icon}</span>'
                        f'<div><div style="font-size:13px; color:#F0EDE8;">{asset["file_name"]}</div>'
                        f'<div style="font-size:11px; color:#8A8480;">{label} · {size_kb} KB · {asset.get("uploaded_at","")[:10]}</div></div>'
                        f'</div>'
                    )
            with col_del:
                if st.button("Remove", key=f"del_{asset['asset_id']}", use_container_width=True):
                    delete_vault_asset(artist_id, asset["asset_id"])
                    st.rerun()


# ── DISTRIBUTION TAB ──────────────────────────────────────────────────────────

def _render_distribution_tab(artist_id: str, artist_name: str):
    dist = load_distribution(artist_id)
    count = dist_configured_count(dist)

    if count == 0:
        render_html("""
        <div class="mw-card" style="padding:1.5rem; border-left:3px solid #F59E0B; margin-bottom:1.5rem;">
            <div style="font-size:14px; font-weight:600; color:#F59E0B; margin-bottom:4px;">No publishing destinations configured yet</div>
            <div style="font-size:13px; color:#8A8480;">Fill in the fields below to set up where MusicWorks should direct your publishing workflow.</div>
        </div>
        """)
    else:
        render_html(
            f'<div class="mw-card" style="padding:0.75rem 1rem; border-left:3px solid #22C55E; margin-bottom:1.5rem;">'
            f'<div style="font-size:13px; color:#22C55E; font-weight:600;">{count} publishing destination{"s" if count != 1 else ""} configured</div>'
            f'</div>'
        )

    def _section_form(label: str, fields: dict, section_key: str):
        st.markdown(f"<div class='mw-section-label'>{label}</div>", unsafe_allow_html=True)
        vals = {}
        for key, field_label in fields.items():
            icon = PLATFORM_ICONS.get(key, "•")
            current = dist.get(section_key, {}).get(key, "")
            set_badge = ' <span style="font-size:10px; color:#22C55E;">[saved]</span>' if current else ' <span style="font-size:10px; color:#8A8480;">[not set]</span>'
            placeholder = "https://..." if "url" in key.lower() else ("@handle" if "username" in key.lower() else "")
            vals[key] = st.text_input(
                f"{icon} {field_label}{set_badge}",
                value=current,
                placeholder=placeholder,
                key=f"dist_{section_key}_{key}_{artist_id}",
            )
        return vals

    social_vals  = _section_form("Social Platforms",    SOCIAL_FIELDS,    "social")
    st.divider()
    stream_vals  = _section_form("Streaming Platforms", STREAMING_FIELDS, "streaming")
    st.divider()
    owned_vals   = _section_form("Owned Channels",      OWNED_FIELDS,     "owned")
    st.divider()
    press_vals   = _section_form("Press & Outreach",    PRESS_FIELDS,     "press")
    st.divider()

    col_save, col_note = st.columns([1, 2])
    with col_save:
        if st.button("💾  Save Distribution Setup", type="primary", use_container_width=True, key=f"save_dist_{artist_id}"):
            save_distribution(artist_id, {
                "social":    social_vals,
                "streaming": stream_vals,
                "owned":     owned_vals,
                "press":     press_vals,
            })
            st.success(f"Distribution saved for {artist_name}.")
            st.rerun()
    with col_note:
        render_html(
            '<div style="font-size:12px; color:#6A6460; line-height:1.6; padding-top:0.5rem;">'
            'No live API connections. Saving a URL includes it in your publishing checklist. '
            'Manual posting remains founder-approved.'
            '</div>'
        )
