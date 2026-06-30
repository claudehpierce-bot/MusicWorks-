"""MusicWorks™ V3.1 — Artist Management page (Profile + Brand Vault + Distribution)."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from datetime import datetime, timezone

from ui.components import page_header, navigate_to, tag_list_html, render_html
from brand_brain.artist_library import list_artists, load_artist, save_artist
from execution.brand_vault import (
    VAULT_TYPES, IMAGE_EXTS, VIDEO_EXTS,
    load_vault_meta, store_vault_asset, delete_vault_asset,
)
from execution.distribution_store import (
    SOCIAL_FIELDS, STREAMING_FIELDS, OWNED_FIELDS, PRESS_FIELDS,
    PLATFORM_ICONS, load_distribution, save_distribution, dist_configured_count,
)
from execution.profile_store import load_profile, save_profile


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    managing_id = st.session_state.get("managing_artist_id")

    if managing_id:
        brain = load_artist(managing_id)
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

        from execution.brand_vault import vault_asset_count
        from execution.distribution_store import dist_configured_count, load_distribution
        vault_count = vault_asset_count(artist_id)
        dist = load_distribution(artist_id)
        dist_count = dist_configured_count(dist)

        is_flagship = artist_id == "fire_and_flow_gospel"
        badge = '<span class="badge badge-live" style="margin-left:8px;font-size:10px;">Flagship</span>' if is_flagship else ""

        render_html(
            f'<div class="mw-card" style="padding:1.25rem 1.5rem; margin-bottom:0.75rem;">'
            f'<div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">'
            f'<div style="flex:1;">'
            f'<div style="font-size:18px; font-weight:800; color:#F0EDE8;">{brain.artist_name}{badge}</div>'
            f'<div style="font-size:13px; color:#9B89D4; margin-top:3px;">{brain.tagline}</div>'
            f'<div style="display:flex; gap:16px; margin-top:8px;">'
            f'<span style="font-size:11px; color:#8A8480;">📸 {vault_count} vault asset{"s" if vault_count != 1 else ""}</span>'
            f'<span style="font-size:11px; color:#8A8480;">🚀 {dist_count} destination{"s" if dist_count != 1 else ""} configured</span>'
            f'</div></div></div></div>'
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


# ── Management view (Profile + Brand Vault + Distribution) ────────────────────

def _render_management_view(brain):
    if st.button("← Back to Artists", key="back_to_list"):
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

def _render_profile_tab(brain):
    edit_key = f"editing_profile_{brain.artist_id}"
    editing = st.session_state.get(edit_key, False)

    if editing:
        _render_profile_editor(brain, edit_key)
    else:
        _render_profile_view(brain, edit_key)


def _render_profile_view(brain, edit_key):
    col_hdr, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("✏️  Edit Profile", key="btn_edit_profile", type="primary", use_container_width=True):
            st.session_state[edit_key] = True
            st.rerun()

    profile = load_profile(brain.artist_id)

    col_a, col_b = st.columns([1.4, 1])
    with col_a:
        st.markdown("<div class='mw-section-label'>Mission</div>", unsafe_allow_html=True)
        render_html(f'<div class="mw-card" style="padding:1rem; font-size:14px; color:#C8C4BE; line-height:1.7;">{brain.mission}</div>')

        if brain.bio_short:
            st.markdown("<div class='mw-section-label' style='margin-top:1rem;'>Biography</div>", unsafe_allow_html=True)
            render_html(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#8A8480; line-height:1.6;">{brain.bio_short}</div>')

        if profile.get("ministry_focus"):
            st.markdown("<div class='mw-section-label' style='margin-top:1rem;'>Ministry Focus</div>", unsafe_allow_html=True)
            render_html(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#C8C4BE; line-height:1.6;">{profile["ministry_focus"]}</div>')

        if profile.get("target_audience"):
            st.markdown("<div class='mw-section-label' style='margin-top:1rem;'>Target Audience</div>", unsafe_allow_html=True)
            render_html(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#8A8480; line-height:1.6;">{profile["target_audience"]}</div>')

    with col_b:
        st.markdown("<div class='mw-section-label'>Global Identity</div>", unsafe_allow_html=True)
        heritage_html = tag_list_html(brain.heritage, "tag tag-indigo")
        genre_html = tag_list_html(brain.genre, "tag tag-gold")
        render_html(
            f'<div class="mw-card" style="padding:1rem;">'
            f'<div style="margin-bottom:0.75rem;"><div style="font-size:11px; color:#8A8480; margin-bottom:6px;">HERITAGE</div>{heritage_html}</div>'
            f'<div><div style="font-size:11px; color:#8A8480; margin-bottom:6px;">GENRE</div>{genre_html}</div>'
            f'</div>'
        )

        if profile.get("cultural_pillars"):
            st.markdown("<div class='mw-section-label' style='margin-top:1rem;'>Cultural Pillars</div>", unsafe_allow_html=True)
            pillars_html = "".join(
                f'<div style="font-size:12px; color:#C8C4BE; padding:4px 0; border-bottom:1px solid #1E1E1E;">— {p}</div>'
                for p in profile["cultural_pillars"]
            )
            render_html(f'<div class="mw-card" style="padding:1rem;">{pillars_html}</div>')

        if profile.get("cities_of_influence") or profile.get("countries_of_influence"):
            locs = list(profile.get("cities_of_influence", [])) + list(profile.get("countries_of_influence", []))
            locs_html = tag_list_html(locs, "tag")
            st.markdown("<div class='mw-section-label' style='margin-top:1rem;'>Cities & Countries</div>", unsafe_allow_html=True)
            render_html(f'<div class="mw-card" style="padding:1rem;">{locs_html}</div>')

    # Creative DNA / Visual style
    if profile.get("visual_style_notes"):
        st.markdown("<div class='mw-section-label' style='margin-top:1.5rem;'>Visual Style</div>", unsafe_allow_html=True)
        render_html(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#C8C4BE; line-height:1.6;">{profile["visual_style_notes"]}</div>')

    if profile.get("notes"):
        st.markdown("<div class='mw-section-label' style='margin-top:1rem;'>Founder Notes</div>", unsafe_allow_html=True)
        render_html(f'<div class="mw-card" style="padding:1rem; font-size:13px; color:#8A8480; line-height:1.6; font-style:italic;">{profile["notes"]}</div>')

    if brain.brand_rules:
        rules_html = "".join(
            f'<div style="font-size:12px; color:#C8C4BE; padding:5px 0; border-bottom:1px solid #1E1E1E;">— {r}</div>'
            for r in brain.brand_rules[:6]
        )
        st.markdown("<div class='mw-section-label' style='margin-top:1.5rem;'>Brand Rules</div>", unsafe_allow_html=True)
        render_html(f'<div class="mw-card" style="padding:1rem;">{rules_html}</div>')

    st.caption(f"Last updated: {brain.updated_at[:10] if brain.updated_at else 'never'}")


def _render_profile_editor(brain, edit_key):
    profile = load_profile(brain.artist_id)

    col_hdr, col_cancel = st.columns([3, 1])
    with col_cancel:
        if st.button("Cancel", key="cancel_edit", use_container_width=True):
            st.session_state[edit_key] = False
            st.rerun()

    st.markdown("<div class='mw-section-label'>Core Identity</div>", unsafe_allow_html=True)

    new_name       = st.text_input("Artist name", value=brain.artist_name, key="ed_name")
    new_tagline    = st.text_input("Tagline", value=brain.tagline, key="ed_tagline")
    new_mission    = st.text_area("Mission statement", value=brain.mission, height=120, key="ed_mission")
    new_bio_short  = st.text_area("Short bio", value=brain.bio_short or "", height=100, key="ed_bio_short")
    new_bio_long   = st.text_area("Long bio", value=brain.bio_long or "", height=150, key="ed_bio_long")

    st.divider()
    st.markdown("<div class='mw-section-label'>Global Identity</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        new_heritage = st.text_area(
            "Heritage (one per line)",
            value="\n".join(brain.heritage),
            height=120, key="ed_heritage",
        )
        new_genre = st.text_area(
            "Genres (one per line)",
            value="\n".join(brain.genre),
            height=100, key="ed_genre",
        )
    with col_b:
        new_pillars = st.text_area(
            "Cultural pillars (one per line)",
            value="\n".join(profile.get("cultural_pillars", [])),
            height=120, key="ed_pillars",
        )
        new_cities = st.text_area(
            "Cities of influence (one per line)",
            value="\n".join(profile.get("cities_of_influence", [])),
            height=60, key="ed_cities",
        )
        new_countries = st.text_area(
            "Countries of influence (one per line)",
            value="\n".join(profile.get("countries_of_influence", [])),
            height=60, key="ed_countries",
        )

    st.divider()
    st.markdown("<div class='mw-section-label'>Audience & Ministry</div>", unsafe_allow_html=True)

    col_c, col_d = st.columns(2)
    with col_c:
        new_audience = st.text_area(
            "Target audience",
            value=profile.get("target_audience", ""),
            height=100, key="ed_audience",
        )
    with col_d:
        new_ministry = st.text_area(
            "Ministry focus",
            value=profile.get("ministry_focus", ""),
            height=100, key="ed_ministry",
        )

    st.divider()
    st.markdown("<div class='mw-section-label'>Brand Voice & Visual Style</div>", unsafe_allow_html=True)

    col_e, col_f = st.columns(2)
    with col_e:
        current_tone = ", ".join(brain.brand_voice.tone) if brain.brand_voice.tone else ""
        new_tone = st.text_input("Brand voice / tone (comma-separated)", value=current_tone, key="ed_tone")
    with col_f:
        new_visual = st.text_area(
            "Visual style notes",
            value=profile.get("visual_style_notes", ""),
            height=80, key="ed_visual",
        )

    new_notes = st.text_area(
        "Founder notes (internal only)",
        value=profile.get("notes", ""),
        height=80, key="ed_notes",
    )

    st.divider()

    if st.button("💾  Save Changes", type="primary", use_container_width=True, key="btn_save_profile"):
        # Update ArtistBrain
        brain.artist_name    = new_name.strip()
        brain.display_name   = new_name.strip()
        brain.tagline        = new_tagline.strip()
        brain.mission        = new_mission.strip()
        brain.bio_short      = new_bio_short.strip()
        brain.bio_long       = new_bio_long.strip()
        brain.heritage       = [l.strip() for l in new_heritage.splitlines() if l.strip()]
        brain.genre          = [l.strip() for l in new_genre.splitlines() if l.strip()]

        if new_tone.strip():
            brain.brand_voice.tone = [t.strip() for t in new_tone.split(",") if t.strip()]

        save_artist(brain)

        # Update extended profile
        ext = {
            "cultural_pillars":       [l.strip() for l in new_pillars.splitlines() if l.strip()],
            "cities_of_influence":    [l.strip() for l in new_cities.splitlines() if l.strip()],
            "countries_of_influence": [l.strip() for l in new_countries.splitlines() if l.strip()],
            "target_audience":        new_audience.strip(),
            "ministry_focus":         new_ministry.strip(),
            "visual_style_notes":     new_visual.strip(),
            "notes":                  new_notes.strip(),
        }
        save_profile(brain.artist_id, ext)

        st.session_state[edit_key] = False
        st.success(f"Profile saved for {brain.artist_name}.")
        st.rerun()


# ── BRAND VAULT TAB ───────────────────────────────────────────────────────────

def _render_vault_tab(artist_id: str):
    meta = load_vault_meta(artist_id)
    assets = meta.get("assets", [])

    st.markdown("<div class='mw-section-label'>Upload Brand Assets</div>", unsafe_allow_html=True)

    asset_type_options = [lbl for _, lbl, _ in VAULT_TYPES]
    asset_type_keys    = [key for key, _, _ in VAULT_TYPES]

    col_a, col_b = st.columns([1, 2])
    with col_a:
        selected_label = st.selectbox("Asset type:", asset_type_options, key="vault_type_sel")
        selected_key = asset_type_keys[asset_type_options.index(selected_label)]

    with col_b:
        uploaded = st.file_uploader(
            f"Upload {selected_label}:",
            type=["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "pdf", "svg"],
            accept_multiple_files=True,
            key=f"vault_upload_{selected_key}",
        )

    if uploaded:
        saved_count = 0
        for f in uploaded:
            try:
                store_vault_asset(artist_id, selected_key, f)
                saved_count += 1
            except Exception as e:
                st.error(f"Could not save {f.name}: {e}")
        if saved_count:
            st.success(f"{saved_count} file(s) added to Brand Vault.")
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

    # Group assets by type
    by_type: dict[str, list] = {}
    for a in assets:
        by_type.setdefault(a.get("asset_type", "misc"), []).append(a)

    type_order = [k for k, _, _ in VAULT_TYPES]

    for asset_type in type_order + [k for k in by_type if k not in type_order]:
        group = by_type.get(asset_type, [])
        if not group:
            continue

        icon = next((ic for k, _, ic in VAULT_TYPES if k == asset_type), "📁")
        label = next((lbl for k, lbl, _ in VAULT_TYPES if k == asset_type), asset_type)
        st.markdown(f"<div class='mw-section-label'>{icon} {label}</div>", unsafe_allow_html=True)

        # Images: show as grid; others: show as file cards
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
            set_badge = ' <span style="font-size:10px; color:#22C55E; font-weight:600;">[saved]</span>' if current else ' <span style="font-size:10px; color:#8A8480;">[not set]</span>'
            placeholder = "https://..." if "url" in key.lower() else ("@handle" if "username" in key.lower() else "")
            vals[key] = st.text_input(
                f"{icon} {field_label}{set_badge}",
                value=current,
                placeholder=placeholder,
                key=f"dist_{section_key}_{key}",
                label_visibility="visible",
            )
        return vals

    with st.container():
        social_vals   = _section_form("Social Platforms",   SOCIAL_FIELDS,    "social")
        st.divider()
        stream_vals   = _section_form("Streaming Platforms", STREAMING_FIELDS, "streaming")
        st.divider()
        owned_vals    = _section_form("Owned Channels",     OWNED_FIELDS,     "owned")
        st.divider()
        press_vals    = _section_form("Press & Outreach",   PRESS_FIELDS,     "press")

        st.divider()

        col_save, col_note = st.columns([1, 2])
        with col_save:
            if st.button("💾  Save Distribution Setup", type="primary", use_container_width=True, key="save_dist"):
                data = {
                    "social":    social_vals,
                    "streaming": stream_vals,
                    "owned":     owned_vals,
                    "press":     press_vals,
                }
                save_distribution(artist_id, data)
                st.success(f"Distribution setup saved for {artist_name}.")
                st.rerun()
        with col_note:
            render_html(
                '<div style="font-size:12px; color:#6A6460; line-height:1.6; padding-top:0.5rem;">'
                'Saving a URL here means MusicWorks will include it in your publishing checklist. '
                'No live API connections are made. Manual posting remains founder-approved.'
                '</div>'
            )
