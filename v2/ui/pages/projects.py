"""MusicWorks™ V3 — Projects page."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, navigate_to, countdown_days, render_html
from execution.asset_library import AssetLibrary

SONGS_DIR = Path(__file__).parent.parent.parent / "data" / "songs"


@st.cache_resource
def _get_library():
    return AssetLibrary()


def _load_songs() -> list[dict]:
    if not SONGS_DIR.exists():
        return []
    songs = []
    for f in sorted(SONGS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            data["_file"] = str(f)
            songs.append(data)
        except Exception:
            pass
    return songs


def render():
    page_header("Projects", "Every song is a project. Every project is a mission.", "🎵")

    col_title, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("➕  New Project", type="primary", use_container_width=True):
            st.session_state.wizard_step = 0
            st.session_state.wizard_data = {}
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("wizard")

    songs = _load_songs()

    if not songs:
        render_html("""
        <div class="mw-card" style="text-align:center; padding:3rem; color:#8A8480;">
            <div style="font-size:40px; margin-bottom:1rem;">🎵</div>
            <div style="font-size:18px; color:#F0EDE8; margin-bottom:0.5rem;">No projects yet</div>
            <div>Click New Project to start your first campaign.</div>
        </div>
        """)
        return

    st.markdown(f"<div class='mw-section-label'>{len(songs)} project(s)</div>", unsafe_allow_html=True)

    try:
        lib = _get_library()
        all_campaigns = lib.get_all_campaign_ids()
    except Exception:
        lib = None
        all_campaigns = []

    for song in reversed(songs):
        _render_project_card(song, lib, all_campaigns)


def _render_project_card(song: dict, lib, all_campaigns: list):
    title = song.get("title", "Untitled")
    artist = song.get("artist_name", "")
    album = song.get("album_title", "")
    release = song.get("release_date", "")
    scripture = song.get("scripture_primary", "")
    themes = song.get("themes", [])
    genre = song.get("genre", [])
    song_id = song.get("song_id", "")

    days = countdown_days(release) if release else None
    if days is not None:
        if days > 0:
            countdown_html = f'<span style="font-size:13px; color:#FF6B2B; font-weight:600;">{days}d to launch</span>'
        elif days == 0:
            countdown_html = '<span class="badge badge-live">Launch Day!</span>'
        else:
            countdown_html = '<span class="badge badge-approved">Released</span>'
    else:
        countdown_html = ""

    # Find related campaigns
    related = [c for c in all_campaigns if title.lower().replace(" ", "-") in c.lower() or
               (song_id and song_id[:8] in c)] if all_campaigns else []

    campaign_stats = None
    if related and lib:
        try:
            campaign_stats = lib.get_campaign_stats(related[0])
        except Exception:
            pass

    has_campaign = bool(related)

    with st.expander(f"**{title}** · {artist} · {album}", expanded=False):
        col_a, col_b = st.columns([1.5, 1])

        with col_a:
            render_html(f"""
            <div style="margin-bottom:1rem;">
                <div style="font-size:22px; font-weight:800; color:#F0EDE8; letter-spacing:-0.5px; margin-bottom:4px;">
                    {title}
                </div>
                <div style="font-size:13px; color:#9B89D4; margin-bottom:2px;">{artist}</div>
                <div style="font-size:13px; color:#8A8480;">{album} · {release} {countdown_html}</div>
            </div>
            """)

            if scripture:
                st.markdown(f'<div class="mw-card" style="padding:0.75rem 1rem; border-left:3px solid #D4A853; font-size:13px; color:#D4A853;">{scripture}</div>', unsafe_allow_html=True)

            if themes:
                from ui.components import tag_list_html
                st.markdown(f'<div style="margin-top:0.75rem;">{tag_list_html(themes, "tag tag-gold")}</div>', unsafe_allow_html=True)

        with col_b:
            if campaign_stats:
                total = campaign_stats["total"]
                approved = campaign_stats["approved"]
                pct = (approved / total * 100) if total > 0 else 0
                render_html(f"""
                <div class="mw-card" style="padding:1rem;">
                    <div class="mw-section-label">Campaign Status</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin:0.75rem 0;">
                        <div style="background:rgba(34,197,94,0.08); border-radius:8px; padding:0.5rem;">
                            <div style="font-size:18px; font-weight:700; color:#22C55E;">{approved}</div>
                            <div style="font-size:10px; color:#8A8480;">Approved</div>
                        </div>
                        <div style="background:rgba(245,158,11,0.08); border-radius:8px; padding:0.5rem;">
                            <div style="font-size:18px; font-weight:700; color:#F59E0B;">{campaign_stats["pending"]}</div>
                            <div style="font-size:10px; color:#8A8480;">Pending</div>
                        </div>
                    </div>
                </div>
                """)
            else:
                render_html("""
                <div class="mw-card" style="padding:1rem; text-align:center; color:#8A8480;">
                    <div style="font-size:24px; margin-bottom:4px;">📦</div>
                    <div style="font-size:12px;">No campaign built yet</div>
                </div>
                """)

        # Action buttons
        st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        with b1:
            if has_campaign and lib:
                if st.button("✅  Approval Queue", key=f"proj_approve_{song_id}", use_container_width=True, type="primary"):
                    st.session_state.approval_campaign_id = related[0]
                    navigate_to("approval")
            else:
                if st.button("🚀  Build Campaign", key=f"proj_build_{song_id}", use_container_width=True, type="primary"):
                    st.session_state.wizard_step = 5
                    st.session_state.wizard_data = dict(song)
                    st.session_state.wizard_data["song_file"] = song.get("_file", "")
                    st.session_state.wizard_data["mode"] = "blitz"
                    st.session_state.pop("wizard_campaign_id", None)
                    navigate_to("wizard")
        with b2:
            if has_campaign:
                if st.button("📊  Analytics", key=f"proj_analytics_{song_id}", use_container_width=True):
                    navigate_to("analytics")
        with b3:
            if has_campaign:
                if st.button("🚀  Publishing", key=f"proj_pub_{song_id}", use_container_width=True):
                    if related:
                        st.session_state.publishing_campaign_id = related[0]
                    navigate_to("publishing")
