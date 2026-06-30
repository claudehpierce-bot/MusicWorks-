"""MusicWorks™ V3.2 — Creative Studio: Brand Vault + Creative Departments preview."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html
from brand_brain.artist_library import list_artists, load_artist
from execution.brand_vault import (
    VAULT_TYPES, IMAGE_EXTS, VIDEO_EXTS,
    load_vault_meta, store_vault_asset, delete_vault_asset, vault_asset_count,
)


_DEPARTMENTS = [
    {
        "icon": "✨",
        "name": "Spiritual Exploration",
        "desc": "Deep-dive theology sessions. Give the Studio a scripture, theme, or question — it maps the theological landscape, finds connecting passages, and surfaces creative angles that honor the text.",
        "examples": ["'What does Hebrews 10:25 say about community?' → full theological map", "Scripture-to-song concept briefs", "Theme development from one verse to a full album arc"],
    },
    {
        "icon": "🎵",
        "name": "Musical Brainstorm",
        "desc": "Production and sound direction. Describe a feeling, a season, a scripture — the Studio returns genre directions, BPM ranges, instrumentation notes, and Afro-Gospel reference tracks.",
        "examples": ["'What would HLANGANA sound like as Sgija gospel?' → full production direction", "Arrangement concepts for diaspora worship contexts", "Tempo and key recommendations by campaign mode"],
    },
    {
        "icon": "🔤",
        "name": "Kingdom Words Naming",
        "desc": "Research and validate new Kingdom Words series entries. Provide a concept or biblical theme — the Studio searches African, Caribbean, and global languages for words that unlock the scripture.",
        "examples": ["'Find a word in Yoruba for covenant' → research brief + pronunciation", "Episode concept development for the Kingdom Words series", "Cultural context validation for diaspora audiences"],
    },
    {
        "icon": "🎨",
        "name": "Visual Concepts",
        "desc": "Campaign visual direction briefs. The Studio translates a song's theology into specific scene descriptions, color stories, lighting guides, and photography directions — all rooted in Creative DNA.",
        "examples": ["'Visual concept for a song about community in exile' → full scene brief", "Color story development per campaign mode", "Shot list ideas for manual videography"],
    },
    {
        "icon": "🤖",
        "name": "AI Prompt Generation",
        "desc": "Production-ready Veo, Imagen, and Canva prompts. The Studio takes your creative concept and outputs optimized prompts for every AI tool in the MusicWorks pipeline.",
        "examples": ["Veo prompts optimized for Fire & Flow gospel atmosphere", "Canva design briefs with exact dimensions and style notes", "Imagen prompts for thumbnail concept generation"],
    },
]


def render():
    page_header("Creative Studio™", "Brand Vault · Creative assets · AI-assisted production.", "🎬")

    artists = list_artists()

    # ── BRAND VAULT ──────────────────────────────────────────────────────────
    render_html("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.5rem;">
        <div style="font-size:28px;">📸</div>
        <div>
            <div style="font-size:20px; font-weight:800; color:#F0EDE8;">Brand Vault</div>
            <div style="font-size:13px; color:#8A8480;">Upload and manage artist photos, logos, album covers, and creative references.</div>
        </div>
    </div>
    """)

    if not artists:
        render_html("""
        <div class="mw-card" style="padding:2rem; text-align:center; color:#8A8480; margin-bottom:2rem;">
            <div style="font-size:32px; margin-bottom:0.75rem;">👥</div>
            <div>Create an artist first to use the Brand Vault.</div>
        </div>
        """)
    else:
        artist_names = [a["artist_name"] for a in artists]
        artist_ids   = [a["artist_id"]   for a in artists]

        sel_idx = st.selectbox(
            "Select artist:",
            range(len(artist_names)),
            format_func=lambda i: artist_names[i],
            key="studio_artist_sel",
        )
        sel_id = artist_ids[sel_idx]

        vault_count = vault_asset_count(sel_id)
        st.caption(f"{vault_count} asset(s) in vault for {artist_names[sel_idx]}")

        _render_vault(sel_id)

    st.divider()

    # ── AI CREATIVE DEPARTMENTS (coming soon) ─────────────────────────────────
    render_html("""
    <div style="background:linear-gradient(135deg, #0D0D0D, #1A0F42);
                border:1px solid rgba(212,168,83,0.3); border-radius:16px;
                padding:2rem; text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:30px; margin-bottom:0.75rem;">🤖</div>
        <div style="font-size:20px; font-weight:800; color:#F0EDE8; margin-bottom:0.5rem;">
            AI Creative Departments
        </div>
        <div style="font-size:14px; color:#9B89D4; margin-bottom:0.5rem;">
            Five AI-assisted creative departments. One unified creative workspace.
        </div>
        <div style="font-size:13px; color:#8A8480; margin-bottom:1.25rem;">
            Available as an add-on module in V3
        </div>
        <span class="badge badge-revision" style="font-size:12px; padding:4px 12px;">Coming in V3</span>
    </div>
    """)

    st.markdown("<div class='mw-section-label'>Five Creative Departments</div>", unsafe_allow_html=True)

    for dept in _DEPARTMENTS:
        with st.expander(f"{dept['icon']}  {dept['name']}", expanded=False):
            render_html(f'<div style="font-size:14px; color:#C8C4BE; line-height:1.7; margin-bottom:1rem;">{dept["desc"]}</div>')
            st.markdown("<div style='font-size:11px; color:#8A8480; font-weight:600; letter-spacing:0.6px; text-transform:uppercase; margin-bottom:0.5rem;'>Examples</div>", unsafe_allow_html=True)
            for ex in dept["examples"]:
                render_html(f'<div style="font-size:12px; color:#D4A853; padding:4px 0; border-left:2px solid #D4A853; padding-left:10px; margin-bottom:4px;">{ex}</div>')


def _render_vault(artist_id: str):
    meta   = load_vault_meta(artist_id)
    assets = meta.get("assets", [])

    st.markdown("<div class='mw-section-label' style='margin-top:1rem;'>Upload Asset</div>", unsafe_allow_html=True)

    asset_type_labels = [lbl for _, lbl, _ in VAULT_TYPES]
    asset_type_keys   = [key for key, _, _ in VAULT_TYPES]

    col_a, col_b = st.columns([1, 2])
    with col_a:
        sel_label = st.selectbox("Asset type:", asset_type_labels, key=f"sv_type_{artist_id}")
        sel_key   = asset_type_keys[asset_type_labels.index(sel_label)]
    with col_b:
        uploaded = st.file_uploader(
            f"Upload {sel_label}:",
            type=["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "pdf", "svg"],
            accept_multiple_files=True,
            key=f"sv_up_{sel_key}_{artist_id}",
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
            st.success(f"{saved} file(s) added.")
            st.rerun()

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    if not assets:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:2rem; color:#8A8480;">
            <div style="font-size:32px; margin-bottom:0.5rem;">📁</div>
            <div style="font-size:14px; color:#F0EDE8; margin-bottom:0.25rem;">No assets yet</div>
            <div style="font-size:12px;">Upload photos, logos, album covers, and references above.</div>
        </div>
        """)
        return

    # Group by type
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
        st.markdown(f"<div class='mw-section-label'>{icon} {label} ({len(group)})</div>", unsafe_allow_html=True)

        image_assets = [a for a in group if Path(a["file_name"]).suffix.lower() in IMAGE_EXTS]
        other_assets = [a for a in group if Path(a["file_name"]).suffix.lower() not in IMAGE_EXTS]

        if image_assets:
            img_cols = st.columns(min(len(image_assets), 4))
            for col, asset in zip(img_cols, image_assets):
                path = Path(asset["file_path"])
                with col:
                    if path.exists():
                        st.image(str(path), use_container_width=True)
                    size_kb = asset.get("file_size", 0) // 1024
                    st.caption(f"{asset['file_name']} · {size_kb} KB")
                    if st.button("🗑️ Remove", key=f"svdel_{asset['asset_id']}", use_container_width=True):
                        from execution.brand_vault import delete_vault_asset
                        delete_vault_asset(artist_id, asset["asset_id"])
                        st.rerun()

        for asset in other_assets:
            path   = Path(asset["file_path"])
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
                        f'<div style="font-size:11px; color:#8A8480;">{label} · {size_kb} KB</div></div>'
                        f'</div>'
                    )
            with col_del:
                if st.button("🗑️", key=f"svdel_{asset['asset_id']}", use_container_width=True):
                    from execution.brand_vault import delete_vault_asset
                    delete_vault_asset(artist_id, asset["asset_id"])
                    st.rerun()
