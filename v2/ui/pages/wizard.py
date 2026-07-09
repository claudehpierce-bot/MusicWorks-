"""MusicWorks™ V5 — Media Campaign Wizard (7-step integrated flow).

Steps: Artist -> Creative Master -> Details & Lyrics -> Artwork ->
Release Info -> Analysis -> Launch. Every step feeds the Creative Master
(the uploaded song) so nothing downstream is guessed at random.
"""
import sys
import json
import re
import uuid
import time
from collections import OrderedDict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import navigate_to, page_header, render_html
from brand_brain.artist_library import list_artists, load_artist, save_artist
from brand_brain.models import ArtistBrain

SONGS_DIR = Path(__file__).parent.parent.parent / "data" / "songs"
ARTISTS_DIR = Path(__file__).parent.parent.parent / "data" / "artists"
DRAFT_PATH = Path(__file__).parent.parent.parent / "data" / "drafts" / "wizard_draft.json"
SONGS_DIR.mkdir(parents=True, exist_ok=True)
ARTISTS_DIR.mkdir(parents=True, exist_ok=True)

STEPS = ["Artist", "Creative Master", "Details & Lyrics", "Artwork", "Release Info", "Analysis", "Launch"]

# Campaign mode: display label → internal key
CAMPAIGN_MODE_LABELS = OrderedDict([
    ("Full Launch",       "blitz"),
    ("Standard Rollout",  "standard"),
    ("Growth Campaign",   "growth"),
    ("Ministry Outreach", "ministry_push"),
    ("Chart Push",        "chart_push"),
])
CAMPAIGN_MODE_DESCS = {
    "Full Launch":       "All platforms, all asset types. Maximum release-day impact.",
    "Standard Rollout":  "Core social + blog assets for a steady, sustainable rollout.",
    "Growth Campaign":   "Optimized for building streams and reach over 2–4 weeks.",
    "Ministry Outreach": "Church bulletin, devotional blog, and pastoral email focus.",
    "Chart Push":        "Radio-ready press kit and streaming platform priority.",
}
_MODE_TO_LABEL = {v: k for k, v in CAMPAIGN_MODE_LABELS.items()}


def _init():
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 0
    if "wizard_data" not in st.session_state:
        st.session_state.wizard_data = {}


def _go(step: int):
    st.session_state.wizard_step = step
    st.rerun()


def _progress_header():
    current = st.session_state.wizard_step
    items = ""
    for i, label in enumerate(STEPS):
        if i < current:
            bg = "#22C55E"; dot = "✓"; tc = "#22C55E"; fw = "500"; nc = "#fff"
            shadow = ""
        elif i == current:
            bg = "#FF6B2B"; dot = str(i + 1); tc = "#F0EDE8"; fw = "700"; nc = "#fff"
            shadow = "box-shadow:0 0 14px rgba(255,107,43,0.45);"
        else:
            bg = "#242424"; dot = str(i + 1); tc = "#6A6460"; fw = "400"; nc = "#6A6460"
            shadow = ""
        connector = (
            f'<div style="flex:1;height:2px;background:{"#22C55E" if i < current else "#242424"};'
            f'margin:0 6px;align-self:center;border-radius:1px;"></div>'
            if i < len(STEPS) - 1 else ""
        )
        items += (
            f'<div style="display:flex;align-items:center;">'
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:5px;">'
            f'<div style="width:36px;height:36px;border-radius:50%;background:{bg};color:{nc};'
            f'font-size:14px;font-weight:700;display:flex;align-items:center;justify-content:center;'
            f'flex-shrink:0;{shadow}">{dot}</div>'
            f'<div style="font-size:10px;color:{tc};font-weight:{fw};white-space:nowrap;">{label}</div>'
            f'</div>{connector}</div>'
        )
    st.markdown(
        f'<div class="mw-card" style="padding:1.25rem 1.75rem;margin-bottom:1.75rem;">'
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;">{items}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Draft helpers ─────────────────────────────────────────────────────────────

def _save_draft(d: dict, step: int):
    DRAFT_PATH.parent.mkdir(parents=True, exist_ok=True)
    safe = {k: v for k, v in d.items() if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
    safe["_draft_step"] = step
    DRAFT_PATH.write_text(json.dumps(safe, indent=2, default=str), encoding="utf-8")


def _load_draft() -> dict | None:
    if DRAFT_PATH.exists():
        try:
            return json.loads(DRAFT_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _clear_draft():
    if DRAFT_PATH.exists():
        try:
            DRAFT_PATH.unlink()
        except Exception:
            pass


# ── STEP 0: ARTIST ────────────────────────────────────────────────────────────

def _step_artist():
    st.markdown("### Step 1 — Choose Artist")

    artists = list_artists()

    if not artists:
        st.info("No artists found. Create your first artist below.")
        _create_artist_form()
        return

    # Only one artist — skip the dropdown, show card directly
    if len(artists) == 1:
        selected = artists[0]
        brain = load_artist(selected["artist_id"])
        if brain:
            render_html(f"""
            <div class="mw-card" style="padding:1rem; border-left:3px solid #D4A853; margin:0.5rem 0 1.25rem 0;">
            <div style="font-size:14px; font-weight:600; color:#F0EDE8;">{brain.artist_name}</div>
            <div style="font-size:12px; color:#9B89D4; margin-bottom:0.5rem;">{brain.tagline}</div>
            <div style="font-size:12px; color:#8A8480;">{brain.mission[:120]}...</div>
            </div>
            """)
            if brain.genre:
                from ui.components import tag_list_html
                st.markdown(tag_list_html(brain.genre, "tag tag-gold"), unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:0.75rem;'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("Continue with this artist →", type="primary", use_container_width=True):
                st.session_state.wizard_data["artist_id"] = selected["artist_id"]
                st.session_state.wizard_data["artist_name"] = selected["artist_name"]
                _go(1)
        with col2:
            if st.button("+ Add Another Artist", use_container_width=True):
                st.session_state["_show_create_artist"] = True
                st.rerun()

        if st.session_state.get("_show_create_artist"):
            st.markdown("---")
            _create_artist_form()
        return

    # Multiple artists — show dropdown
    st.caption("Select an existing artist or create a new one.")
    options = [a["artist_name"] for a in artists] + ["+ Create New Artist"]
    choice = st.selectbox("Artist:", options)

    if choice == "+ Create New Artist":
        st.markdown("---")
        _create_artist_form()
    else:
        idx = options.index(choice)
        selected = artists[idx]
        brain = load_artist(selected["artist_id"])
        if brain:
            render_html(f"""
            <div class="mw-card" style="padding:1rem; border-left:3px solid #D4A853; margin:0.5rem 0 1rem 0;">
            <div style="font-size:14px; font-weight:600; color:#F0EDE8;">{brain.artist_name}</div>
            <div style="font-size:12px; color:#9B89D4; margin-bottom:0.5rem;">{brain.tagline}</div>
            <div style="font-size:12px; color:#8A8480;">{brain.mission[:120]}...</div>
            </div>
            """)
            if brain.genre:
                from ui.components import tag_list_html
                st.markdown(tag_list_html(brain.genre, "tag tag-gold"), unsafe_allow_html=True)
        if st.button("Continue with this artist →", type="primary"):
            st.session_state.wizard_data["artist_id"] = selected["artist_id"]
            st.session_state.wizard_data["artist_name"] = selected["artist_name"]
            _go(1)


def _create_artist_form():
    new_name = st.text_input("Artist name:", placeholder="e.g. Fire & Flow Gospel")
    new_id = st.text_input(
        "Artist ID (no spaces):",
        value=re.sub(r"[^a-z0-9_]", "_", new_name.lower().strip()) if new_name else "",
        placeholder="e.g. fire_and_flow_gospel",
    )
    new_tagline = st.text_input("Tagline:", placeholder="One sentence describing this artist")
    new_mission = st.text_area("Mission:", height=80)

    if st.button("Create Artist & Continue →", type="primary"):
        if not new_name or not new_id:
            st.error("Artist name and ID are required.")
        elif load_artist(new_id) is not None:
            st.error(f"Artist ID '{new_id}' already exists.")
        else:
            brain = ArtistBrain(
                artist_id=new_id, artist_name=new_name, display_name=new_name,
                tagline=new_tagline, mission=new_mission, bio_short="", bio_long="",
            )
            save_artist(brain)
            st.session_state.wizard_data["artist_id"] = new_id
            st.session_state.wizard_data["artist_name"] = new_name
            st.session_state.pop("_show_create_artist", None)
            _go(1)


# ── STEP 1: CREATIVE MASTER ───────────────────────────────────────────────────

@st.cache_data(show_spinner="Analyzing your Creative Master...")
def _cached_analyze(file_bytes: bytes, filename: str) -> dict:
    from execution.audio_analysis import analyze_audio
    return analyze_audio(file_bytes, filename).to_dict()


def _step_creative_master():
    d = st.session_state.wizard_data
    st.markdown("### Step 2 — Upload Creative Master")
    st.caption(f"Artist: **{d.get('artist_name', '')}**")
    st.caption(
        "Upload the finished song. MusicWorks analyzes it immediately — this becomes "
        "the foundation of every media asset in your campaign."
    )

    col_a, col_b = st.columns(2)
    analysis = None
    file_bytes = None

    with col_a:
        audio_file = st.file_uploader("Creative Master (WAV, MP3, or FLAC) *", type=["wav", "mp3", "flac"])
        if audio_file:
            file_bytes = audio_file.getvalue()
            analysis = _cached_analyze(file_bytes, audio_file.name)
            st.audio(audio_file)
            st.caption(f"✓ {audio_file.name}  ·  {audio_file.size // 1024} KB")
        elif d.get("audio_file_name") and d.get("audio_analysis"):
            analysis = d["audio_analysis"]
            st.caption(f"✓ On file: **{d['audio_file_name']}**  — upload a new file to replace it.")
        elif d.get("audio_file_name"):
            st.caption(f"✓ On file: **{d['audio_file_name']}**  — upload a new file to replace it.")

        mix_type = st.radio(
            "File type:",
            ["Working Mix", "Master"],
            index=0 if d.get("mix_type", "Working Mix") == "Working Mix" else 1,
            horizontal=True,
            help="Working Mix = in-progress version for review. Master = final production-ready file.",
        )

    with col_b:
        if analysis and analysis.get("energy_curve"):
            st.caption("⚡ Waveform (energy over time) — AI-assisted estimate")
            st.line_chart(analysis["energy_curve"])
        if analysis and analysis.get("degraded") and analysis.get("degraded_reason"):
            st.info(analysis["degraded_reason"])

        default_dur = (analysis or {}).get("duration_seconds") or d.get("duration_seconds") or 0
        duration = st.number_input(
            "Duration (seconds):",
            min_value=0,
            value=int(default_dur),
            step=1,
            help="Auto-detected from your upload — AI-assisted estimate, edit if needed.",
        )
        default_bpm = (analysis or {}).get("tempo_bpm") or d.get("bpm") or 0
        bpm = st.number_input(
            "BPM (optional):",
            min_value=0,
            value=int(default_bpm),
            step=1,
            help="Estimated from the waveform — AI-assisted estimate, edit if needed.",
        )
        key = st.text_input("Key (optional):", value=d.get("key") or "", placeholder="e.g. G Major")

        mood_tags = (analysis or {}).get("mood_tags")
        if mood_tags:
            from ui.components import tag_list_html
            st.caption("Detected mood — AI-assisted estimate")
            st.markdown(tag_list_html(mood_tags, "tag tag-gold"), unsafe_allow_html=True)

    render_html("""
    <div class="mw-card" style="padding:0.75rem 1rem; border-left:3px solid #F59E0B; margin-top:0.5rem;">
    <div style="font-size:12px; color:#F59E0B; font-weight:600; margin-bottom:2px;">Audio QC gate</div>
    <div style="font-size:12px; color:#8A8480;">Upload the working mix now. You'll confirm QC sign-off in the Analysis step before the campaign builds.</div>
    </div>
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            _go(0)
    with col2:
        if st.button("Continue →", type="primary"):
            if not audio_file and not d.get("audio_file_name"):
                st.error("Please upload your Creative Master to continue.")
            else:
                artist_id = d.get("artist_id", "")
                audio_path = d.get("audio_file_path", "")
                if audio_file:
                    save_dir = ARTISTS_DIR / artist_id / "audio"
                    save_dir.mkdir(parents=True, exist_ok=True)
                    dest = save_dir / audio_file.name
                    dest.write_bytes(file_bytes)
                    audio_path = str(dest)
                d.update({
                    "audio_file_path": audio_path,
                    "audio_file_name": audio_file.name if audio_file else d.get("audio_file_name", ""),
                    "mix_type": mix_type,
                    "duration_seconds": duration or None,
                    "bpm": bpm or None,
                    "key": key or None,
                    "audio_analysis": analysis or d.get("audio_analysis") or {},
                })
                _save_draft(d, 2)
                _go(2)


# ── STEP 2: DETAILS & LYRICS ──────────────────────────────────────────────────

def _step_details_lyrics():
    from datetime import date as _date
    d = st.session_state.wizard_data

    if st.session_state.get("_details_error"):
        st.error(st.session_state.pop("_details_error"))

    st.markdown("### Step 3 — Song Details & Lyrics")
    st.caption(f"Artist: **{d.get('artist_name', '')}**  ·  File: **{d.get('audio_file_name', '')}**")

    col_a, col_b = st.columns(2)
    with col_a:
        song_title = st.text_input("Song title *", value=d.get("title", ""), placeholder="e.g. HLANGANA")
        title_meaning = st.text_input(
            "Title meaning / translation:",
            value=d.get("title_meaning", ""),
            placeholder="e.g. Gather Together",
        )
        title_language = st.text_input(
            "Title language:",
            value=d.get("title_language", ""),
            placeholder="e.g. Zulu, Amapiano, Shona",
        )
    with col_b:
        release_date = st.date_input(
            "Release date *",
            value=_date.fromisoformat(d["release_date"]) if d.get("release_date") else _date.today(),
        )
        album_title = st.text_input("Album title *", value=d.get("album_title", ""),
                                     placeholder="e.g. Becoming Vol. 1")

    cultural_notes = st.text_area(
        "Cultural / pronunciation notes:",
        value=d.get("cultural_notes", "") or "",
        height=60,
        placeholder="Pronunciation guide, cultural context, or anything the AI should know about this song's language or cultural roots…",
    )

    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mw-section-label'>Lyrics</div>", unsafe_allow_html=True)
    st.caption("MusicWorks extracts lyrics to sync captions, lyric videos, and quote cards to what the song actually says.")

    lyrics_text = d.get("lyrics_text", "") or ""
    tab_paste, tab_upload = st.tabs(["Paste Lyrics", "Upload File"])
    with tab_paste:
        lyrics_text = st.text_area("Paste lyrics:", value=lyrics_text, height=180,
                                    placeholder="Paste the full lyrics here…")
    with tab_upload:
        lyrics_file = st.file_uploader("Lyrics file (.txt, .docx, .pdf):", type=["txt", "docx", "pdf"], key="lyrics_upload")
        if lyrics_file:
            from execution.lyrics_extraction import extract_lyrics
            extracted, err = extract_lyrics(lyrics_file)
            if err:
                st.error(err)
            else:
                lyrics_text = extracted
                st.success(f"✓ Extracted {len(extracted.splitlines())} lines from {lyrics_file.name}")
                st.text_area("Extracted lyrics preview:", value=lyrics_text, height=160, disabled=True)

    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mw-section-label'>Scripture Foundation</div>", unsafe_allow_html=True)
    scripture_primary = st.text_input(
        "Primary scripture *",
        value=d.get("scripture_primary", ""),
        placeholder="e.g. Hebrews 10:25",
    )
    scripture_text = st.text_area(
        "Scripture text *",
        value=d.get("scripture_primary_text", ""),
        height=80,
        placeholder="Paste the full verse text here…",
    )
    scripture_supporting = st.text_input(
        "Supporting scriptures:",
        value=", ".join(d.get("scripture_supporting", [])),
        placeholder="e.g. Acts 2:42, Psalm 122:1  (separate multiple with commas)",
    )

    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mw-section-label'>Song Identity</div>", unsafe_allow_html=True)
    col_c, col_d = st.columns(2)
    with col_c:
        themes_raw = st.text_input(
            "Themes *",
            value=", ".join(d.get("themes", [])),
            placeholder="e.g. Community, Identity, Gathering",
        )
        genre_raw = st.text_input(
            "Genre *",
            value=", ".join(d.get("genre", [])),
            placeholder="e.g. Afro-Gospel, Amapiano Gospel",
        )
    with col_d:
        default_mood = d.get("mood") or (d.get("audio_analysis") or {}).get("mood_tags", [])
        mood_raw = st.text_input(
            "Mood:",
            value=", ".join(default_mood),
            placeholder="e.g. Devotional, Communal, Hopeful",
            help="Pre-filled from your Creative Master's detected mood — edit freely.",
        )

    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mw-section-label'>Campaign Strategy</div>", unsafe_allow_html=True)
    st.caption("How should MusicWorks build this campaign?")

    current_internal = d.get("mode", "blitz")
    current_label = _MODE_TO_LABEL.get(current_internal, "Full Launch")
    mode_labels = list(CAMPAIGN_MODE_LABELS.keys())
    default_idx = mode_labels.index(current_label) if current_label in mode_labels else 0

    selected_label = st.selectbox("Campaign strategy:", mode_labels, index=default_idx)
    st.caption(CAMPAIGN_MODE_DESCS[selected_label])
    campaign_mode = CAMPAIGN_MODE_LABELS[selected_label]

    internal_notes = st.text_area(
        "Internal notes (not included in campaign assets):",
        value=d.get("internal_notes", "") or "",
        height=60,
        placeholder="Team notes, production context, anything for your own reference…",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            _go(1)
    with col2:
        if st.button("Continue →", type="primary"):
            missing = []
            if not song_title.strip():
                missing.append("Song title")
            if not album_title.strip():
                missing.append("Album title")
            if not scripture_primary.strip():
                missing.append("Primary scripture")
            if not scripture_text.strip():
                missing.append("Scripture text")
            if not themes_raw.strip():
                missing.append("Themes")
            if not genre_raw.strip():
                missing.append("Genre")
            if missing:
                st.session_state["_details_error"] = f"Required fields missing: {', '.join(missing)}"
                st.rerun()
            else:
                slug = re.sub(r"[^a-z0-9-]", "-", song_title.strip().lower())
                artist_id = d.get("artist_id", "unknown")
                song_id = d.get("song_id") or f"{artist_id[:8].replace('_', '-')}-{slug}-{uuid.uuid4().hex[:4]}"
                d.update({
                    "song_id": song_id,
                    "title": song_title.strip(),
                    "title_meaning": title_meaning.strip(),
                    "title_language": title_language.strip(),
                    "album_title": album_title.strip(),
                    "release_date": str(release_date),
                    "cultural_notes": cultural_notes.strip() or None,
                    "lyrics_text": lyrics_text.strip() or None,
                    "scripture_primary": scripture_primary.strip(),
                    "scripture_primary_text": scripture_text.strip(),
                    "scripture_supporting": [s.strip() for s in scripture_supporting.split(",") if s.strip()],
                    "themes": [t.strip() for t in themes_raw.split(",") if t.strip()],
                    "genre": [g.strip() for g in genre_raw.split(",") if g.strip()],
                    "mood": [m.strip() for m in mood_raw.split(",") if m.strip()],
                    "mode": campaign_mode,
                    "internal_notes": internal_notes.strip(),
                })
                _save_draft(d, 3)
                _go(3)


# ── STEP 3: ARTWORK ───────────────────────────────────────────────────────────

def _step_artwork():
    d = st.session_state.wizard_data
    st.markdown("### Step 4 — Upload Artwork")
    st.caption("Upload visual assets. Album cover is required to continue.")

    artist_id = d.get("artist_id", "unknown")
    ref_dir = ARTISTS_DIR / artist_id / "references"
    art_dir = ARTISTS_DIR / artist_id / "artwork"
    ref_dir.mkdir(parents=True, exist_ok=True)
    art_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = {}

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div style="font-size:12px; color:#D4A853; font-weight:600; margin-bottom:4px;">ALBUM COVER *</div>', unsafe_allow_html=True)
        album_cover = st.file_uploader("Album cover (JPG/PNG)", type=["jpg", "jpeg", "png"], key="album_cover")
        if album_cover:
            dest = art_dir / album_cover.name
            dest.write_bytes(album_cover.read())
            saved_paths["artwork_file_path"] = str(dest)
            st.image(str(dest), width=200)
        elif d.get("artwork_file_path"):
            st.caption(f"✓ Cover on file: {Path(d['artwork_file_path']).name}")
            saved_paths["artwork_file_path"] = d["artwork_file_path"]

    with col_b:
        st.markdown('<div style="font-size:12px; color:#8A8480; font-weight:600; margin-bottom:4px;">ARTIST PHOTOS</div>', unsafe_allow_html=True)
        artist_photos = st.file_uploader("Artist / promo photos:", type=["jpg", "jpeg", "png"],
                                          accept_multiple_files=True, key="artist_photos")
        photo_paths = list(d.get("artist_photo_paths") or [])
        for f in (artist_photos or []):
            dest = ref_dir / f"artist_{f.name}"
            dest.write_bytes(f.read())
            photo_paths.append(str(dest))
        if photo_paths:
            st.success(f"✓ {len(photo_paths)} photo(s) ready")
        saved_paths["artist_photo_paths"] = photo_paths

    st.markdown("---")
    st.markdown('<div style="font-size:12px; color:#8A8480; font-weight:600; margin-bottom:4px;">CREATIVE DNA REFERENCES</div>', unsafe_allow_html=True)
    st.caption("Mood boards, lighting references, location photos — up to 5 images.")
    dna_files = st.file_uploader("Reference images:", type=["jpg", "jpeg", "png"],
                                  accept_multiple_files=True, key="dna_refs")
    dna_paths = list(d.get("creative_dna_reference_paths") or [])
    for f in (dna_files or [])[:5]:
        dest = ref_dir / f"dna_{f.name}"
        dest.write_bytes(f.read())
        dna_paths.append(str(dest))
    if dna_paths:
        st.success(f"✓ {len(dna_paths)} reference image(s) ready")
    saved_paths["creative_dna_reference_paths"] = dna_paths

    col_c, col_d = st.columns(2)
    with col_c:
        logos = st.file_uploader("Brand logos (PNG preferred):", type=["png", "svg", "jpg"],
                                  accept_multiple_files=True, key="logos")
        logo_paths = list(d.get("logo_paths") or [])
        for f in (logos or []):
            dest = ref_dir / f"logo_{f.name}"
            dest.write_bytes(f.read())
            logo_paths.append(str(dest))
        if logo_paths:
            st.success(f"✓ {len(logo_paths)} logo(s) ready")
        saved_paths["logo_paths"] = logo_paths

    with col_d:
        st.markdown(
            f'<div style="font-size:11px; color:#6A6460; margin-top:0.5rem; line-height:1.5;">'
            f'Typography, reference videos, and additional creative assets can be added to the Brand Brain directly.<br>'
            f'All assets are stored in <code>data/artists/{artist_id}/</code></div>',
            unsafe_allow_html=True,
        )

    d.update(saved_paths)
    has_cover = bool(saved_paths.get("artwork_file_path"))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            _go(2)
    with col2:
        if not has_cover:
            st.caption("Upload an album cover to continue.")
        if st.button("Continue to Release Info →", type="primary", disabled=not has_cover):
            _go(4)


# ── STEP 4: RELEASE INFO ──────────────────────────────────────────────────────

def _step_release_info():
    from datetime import date as _date
    d = st.session_state.wizard_data

    st.markdown("### Step 5 — DistroKid Release Information")
    st.caption(f"**{d.get('title', '')}** · {d.get('artist_name', '')}")
    st.caption(
        "MusicWorks doesn't distribute your music — DistroKid does. These details anchor "
        "your media campaign to the actual release so every link points to the right place."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        release_date = st.date_input(
            "Release date *",
            value=_date.fromisoformat(d["release_date"]) if d.get("release_date") else _date.today(),
            key="ri_release_date",
        )
        isrc = st.text_input("ISRC:", value=d.get("isrc", "") or "", placeholder="e.g. QZK5X2412345")
        upc = st.text_input("UPC:", value=d.get("upc", "") or "", placeholder="e.g. 850012345678")
    with col_b:
        streaming_url = st.text_input(
            "Streaming URL (DistroKid smart link):",
            value=d.get("streaming_url", "") or "",
            placeholder="https://distrokid.com/hyperfollow/...",
        )
        album_url = st.text_input("Album URL:", value=d.get("album_url", "") or "", placeholder="https://...")
        presave_url = st.text_input("Pre-save URL:", value=d.get("presave_url", "") or "", placeholder="https://...")

    render_html("""
    <div class="mw-card" style="padding:0.75rem 1rem; border-left:3px solid #9B89D4; margin-top:0.5rem;">
    <div style="font-size:12px; color:#9B89D4; font-weight:600; margin-bottom:2px;">Campaign anchor</div>
    <div style="font-size:12px; color:#8A8480;">Every link MusicWorks generates — captions, bios, thumbnails — points back here.</div>
    </div>
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            _go(3)
    with col2:
        if st.button("Continue →", type="primary"):
            d.update({
                "release_date": str(release_date),
                "isrc": isrc.strip() or None,
                "upc": upc.strip() or None,
                "streaming_url": streaming_url.strip() or None,
                "album_url": album_url.strip() or None,
                "presave_url": presave_url.strip() or None,
            })
            try:
                from execution.distrokid_store import upsert_release
                upsert_release(d.get("artist_id", ""), d.get("song_id", ""), {
                    "song_title": d.get("title", ""),
                    "release_date": d.get("release_date", ""),
                    "isrc": d.get("isrc"),
                    "upc": d.get("upc"),
                    "streaming_url": d.get("streaming_url"),
                    "album_url": d.get("album_url"),
                    "pre_save_link": d.get("presave_url"),
                    "status": "upcoming",
                })
            except Exception as e:
                st.warning(f"Could not save to DistroKid release records: {e}")
            _save_draft(d, 5)
            _go(5)


# ── STEP 5: ANALYSIS ──────────────────────────────────────────────────────────

def _step_analysis():
    d = st.session_state.wizard_data
    st.markdown("### Step 6 — Creative Analysis")
    st.caption(f"**{d.get('artist_name', '')}** · **{d.get('title', '')}** · {d.get('album_title', '')}")

    brand = load_artist(d.get("artist_id", ""))
    artist_id = d.get("artist_id", "")

    analysis = d.get("audio_analysis") or {}
    hooks = analysis.get("hook_timestamps") or []
    duration = d.get("duration_seconds") or analysis.get("duration_seconds")
    mode = d.get("mode", "blitz")

    from execution.audio_analysis import suggest_deliverables
    suggestions = suggest_deliverables(len(hooks), duration, mode)

    st.markdown("<div class='mw-section-label'>Creative Analysis Complete</div>", unsafe_allow_html=True)
    st.caption("Creative analysis estimate — based on your Creative Master's waveform. Edit anything in earlier steps and these numbers update.")

    dur_val = duration or 0
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Song Length", f"{dur_val // 60}:{dur_val % 60:02d}")
    m2.metric("Detected Hooks", suggestions["detected_hooks"])
    m3.metric("Mood", ", ".join(analysis.get("mood_tags") or d.get("mood") or ["—"]))
    m4.metric("Energy", (analysis.get("energy_level") or "—").title())

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    d1, d2, d3, d4, d5, d6 = st.columns(6)
    d1.metric("Shorts", suggestions["suggested_shorts"])
    d2.metric("Reels", suggestions["suggested_reels"])
    d3.metric("Quote Cards", suggestions["suggested_quote_cards"])
    d4.metric("Blog Articles", suggestions["suggested_blog_articles"])
    d5.metric("Devotionals", suggestions["suggested_devotionals"])
    d6.metric("Video Concepts", suggestions["suggested_video_concepts"])

    render_html(f"""
    <div class="mw-card" style="padding:1rem 1.5rem; margin-top:0.75rem; border-left:3px solid #22C55E;">
    <div style="font-size:12px; color:#8A8480;">Estimated Campaign Assets</div>
    <div style="font-size:28px; font-weight:800; color:#F0EDE8;">{suggestions['estimated_total_assets']}</div>
    </div>
    """)

    if analysis.get("degraded") and analysis.get("degraded_reason"):
        st.info(analysis["degraded_reason"])

    st.divider()

    # Brand Vault + Distribution checks
    try:
        from execution.brand_vault import vault_has_visuals
        from execution.distribution_store import load_distribution, dist_configured_count
        _has_visuals  = vault_has_visuals(artist_id)
        _dist         = load_distribution(artist_id)
        _dist_ok      = dist_configured_count(_dist) > 0
    except Exception:
        _has_visuals = False
        _dist_ok     = False

    checks = [
        ("Song title",                  bool(d.get("title")),                         True),
        ("Album title",                 bool(d.get("album_title")),                   True),
        ("Artist selected",             bool(d.get("artist_id")),                     True),
        ("Primary scripture",           bool(d.get("scripture_primary")),             True),
        ("Themes",                      bool(d.get("themes")),                        True),
        ("Brand Brain found",           brand is not None,                            False),
        ("Audio file uploaded",         bool(d.get("audio_file_path")),              False),
        ("Lyrics added",                bool(d.get("lyrics_text")),                   False),
        ("Album cover uploaded",        bool(d.get("artwork_file_path")),             False),
        ("Creative DNA references",     bool(d.get("creative_dna_reference_paths")),  False),
        ("Brand Vault — visual assets", _has_visuals,                                 False),
        ("Distribution configured",     _dist_ok,                                     False),
    ]

    errors = [(label, req) for label, ok, req in checks if not ok and req]
    warnings = [(label, req) for label, ok, req in checks if not ok and not req]

    if not _has_visuals:
        st.info(
            "MusicWorks can build this campaign, but **visual generation will be weaker** until "
            "artist photos, logos, and Creative DNA references are uploaded in the Brand Vault. "
            "Go to Artists → Brand Vault to add them."
        )

    rows_html = ""
    for label, ok, required in checks:
        icon = "✓" if ok else ("✗" if required else "⚠")
        color = "#22C55E" if ok else ("#EF4444" if required else "#F59E0B")
        note = "" if ok else (" (required)" if required else " (recommended)")
        rows_html += (
            f'<div style="display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1px solid #1E1E1E;">'
            f'<span style="color:{color}; font-size:14px; min-width:16px;">{icon}</span>'
            f'<span style="font-size:13px; color:#C8C4BE;">{label}</span>'
            f'<span style="font-size:11px; color:#6A6460;">{note}</span></div>'
        )
    st.markdown(f'<div class="mw-card" style="padding:1rem 1.5rem;">{rows_html}</div>', unsafe_allow_html=True)

    if errors:
        st.error(f"Cannot proceed — go back and complete: {', '.join(l for l, _ in errors)}")
    if warnings:
        st.warning(f"Recommended before launch: {', '.join(l for l, _ in warnings)}")

    st.divider()
    st.markdown("**Hard Gate Confirmation**")
    st.caption("Both must be confirmed before the campaign builds.")
    theology_ok = st.checkbox("✓ I confirm this song has passed Theology Review — lyrics are scripturally sound and align with the artist's theological guardrails.")
    audio_ok = st.checkbox("✓ I confirm this song has passed Audio QC — the file is clean, at correct level, and production-ready.")

    can_proceed = not errors and theology_ok and audio_ok

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            _go(4)
    with col2:
        if not can_proceed:
            reasons = []
            if errors:
                reasons.append("fix required items above")
            if not theology_ok:
                reasons.append("confirm Theology Review")
            if not audio_ok:
                reasons.append("confirm Audio QC")
            if reasons:
                st.caption(f"To unlock: {' · '.join(reasons)}")
        if st.button("Launch Media Factory™ →", type="primary", disabled=not can_proceed):
            if _save_song_json(d, brand, theology_ok, audio_ok):
                _clear_draft()
                _go(6)


# ── STEP 6: LAUNCH ────────────────────────────────────────────────────────────

def _step_launch():
    d = st.session_state.wizard_data

    if st.session_state.get("wizard_campaign_id"):
        _render_campaign_ready(d)
        return

    title = d.get("title", "Your Song")
    artist = d.get("artist_name", "")
    mode_internal = d.get("mode", "blitz")
    mode_label = _MODE_TO_LABEL.get(mode_internal, "Full Launch")

    st.markdown("### Step 7 — Launch Media Factory™")

    render_html(f"""
    <div class="mw-card" style="padding:1.5rem; border-left:3px solid #FF6B2B; margin-bottom:1rem;">
    <div style="font-size:16px; font-weight:700; color:#F0EDE8; margin-bottom:4px;">{title}</div>
    <div style="font-size:13px; color:#9B89D4; margin-bottom:0.25rem;">{artist}</div>
    <div style="font-size:12px; color:#8A8480;">Strategy: <span style="color:#D4A853; font-weight:600;">{mode_label}</span></div>
    </div>
    """)

    render_html("""
    <div class="mw-card" style="padding:1rem 1.5rem; margin-bottom:1.5rem;">
    <div style="font-size:11px; color:#8A8480; font-weight:600; letter-spacing:0.6px; text-transform:uppercase; margin-bottom:0.75rem;">What MusicWorks will generate</div>
    <div style="font-size:13px; color:#C8C4BE; line-height:1.8;">
    Social captions (Instagram, TikTok, YouTube, Facebook) · Video storyboard · Blog post · Press release · Church outreach blurb · Thumbnail concepts
    </div>
    </div>
    """)

    song_file = d.get("song_file", "")
    if not song_file or not Path(song_file).exists():
        st.error("Song file not found. Please go back and complete the Analysis step.")
        if st.button("← Back to Analysis"):
            _go(5)
        return

    try:
        from config import ANTHROPIC_API_KEY, MOCK_MODE as CFG_MOCK
        has_key = bool(ANTHROPIC_API_KEY)
        default_mock = CFG_MOCK or not has_key
    except ImportError:
        has_key = False
        default_mock = True

    if not has_key:
        st.info("✨ Your campaign is being prepared. This preview uses sample content — connect your Creative Engines in Settings any time for a fully generated campaign.")

    # Mock mode lives in an expander — launch button is the hero action
    with st.expander("⚙ Advanced options", expanded=False):
        st.checkbox(
            "Use sample content (preview without generating real assets)",
            value=default_mock,
            key="wizard_mock_override",
            help="Turn this on to preview your campaign structure before connecting your Creative Engines.",
        )
    if "wizard_mock_override" not in st.session_state:
        st.session_state.wizard_mock_override = default_mock

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("← Back"):
            _go(5)
    with col2:
        if st.button("🚀  LAUNCH MEDIA FACTORY", type="primary", use_container_width=True):
            campaign_id = _run_campaign_build(d, st.session_state.wizard_mock_override)
            if campaign_id:
                st.session_state.wizard_campaign_id = campaign_id
                st.balloons()
                st.rerun()


# ── Internals: song save + campaign run ───────────────────────────────────────

def _save_song_json(d: dict, brand, theology_ok: bool, audio_ok: bool) -> bool:
    """Save the song JSON and store the path in wizard_data. Returns True on success."""
    try:
        artist_id = d.get("artist_id", "")
        analysis = d.get("audio_analysis") or {}
        song_data = {
            "song_id": d.get("song_id", f"{artist_id}-{uuid.uuid4().hex[:6]}"),
            "artist_id": artist_id,
            "title": d.get("title", ""),
            "title_meaning": d.get("title_meaning", ""),
            "title_language": d.get("title_language", ""),
            "artist_name": d.get("artist_name", ""),
            "album_title": d.get("album_title", ""),
            "album_id": re.sub(r"[^a-z0-9-]", "-", d.get("album_title", "").lower()),
            "release_date": d.get("release_date", ""),
            "duration_seconds": d.get("duration_seconds"),
            "bpm": d.get("bpm"),
            "key": d.get("key"),
            "genre": d.get("genre", []),
            "mood": d.get("mood", []),
            "scripture_primary": d.get("scripture_primary", ""),
            "scripture_primary_text": d.get("scripture_primary_text", ""),
            "scripture_supporting": d.get("scripture_supporting", []),
            "themes": d.get("themes", []),
            "theology_approved": theology_ok,
            "audio_qc_approved": audio_ok,
            "audio_file_path": d.get("audio_file_path", ""),
            "artwork_file_path": d.get("artwork_file_path", ""),
            "creative_dna_reference_paths": d.get("creative_dna_reference_paths", []),
            "artist_photo_paths": d.get("artist_photo_paths", []),
            "logo_paths": d.get("logo_paths", []),
            "cultural_notes": d.get("cultural_notes"),
            "content_advisory": "none",
            "brand_color_primary": (
                brand.creative_dna.color_palette.get("primary", "#2D1B69").split(" ")[0]
                if brand else "#2D1B69"
            ),
            "brand_color_secondary": (
                brand.creative_dna.color_palette.get("secondary", "#D4A853").split(" ")[0]
                if brand else "#D4A853"
            ),
            "target_geography": brand.audience.get("geography_priority", []) if brand else [],
            "target_audience_age": "18-45",
            "target_faith_background": "Christian — all denominations",
            "isrc": d.get("isrc"),
            "lyrics_text": d.get("lyrics_text"),
            "tempo_estimate": analysis.get("tempo_bpm"),
            "mood_estimate": analysis.get("mood_tags", []),
            "energy_level_estimate": analysis.get("energy_level"),
            "hook_timestamps": analysis.get("hook_timestamps", []),
            "structure_segments": analysis.get("structure_segments", []),
            "audio_analysis_source": analysis.get("source"),
            "_internal_notes": d.get("internal_notes", ""),
        }
        song_data = {k: v for k, v in song_data.items() if v is not None}

        slug = re.sub(r"[^a-z0-9-]", "-", d.get("title", "song").lower())
        song_path = SONGS_DIR / f"{slug}.json"
        song_path.write_text(json.dumps(song_data, indent=2, ensure_ascii=False), encoding="utf-8")
        d["song_file"] = str(song_path)
        return True
    except Exception as e:
        st.error(f"Could not save song file: {e}")
        return False


# Translates the orchestrator's internal, technical printer output into
# department-framed lines a founder should actually see. Anything that
# doesn't match a known real stage is not shown -- we never relay raw
# agent/worker/queue language to the founder (V7 Constitution, Article IX),
# and we never invent a stage that didn't really run (Article XIII).
_BUILD_STAGE_MESSAGES = [
    ("Brand Brain loaded",               "🧠", "Creative Director", "Your artist identity is understood."),
    ("No Brand Brain found",             "🧠", "Creative Director", "Proceeding without a full artist profile."),
    ("Social Media Agent running",       "📈", "Growth & Discovery", "Drafting your platform captions..."),
    ("caption assets stored",            "📈", "Growth & Discovery", "Captions ready."),
    ("Blog & Press Agent running",       "📈", "Growth & Discovery", "Writing your press release and blog..."),
    ("written assets stored",            "📈", "Growth & Discovery", "Written package ready."),
    ("Video Production Agent running",   "🎬", "Film Department", "Planning your cinematic sequence..."),
    ("video package assets stored",      "🎬", "Film Department", "Storyboard ready."),
    ("Thumbnail & Art Agent running",    "🎨", "Art Department", "Exploring visual concepts..."),
    ("thumbnail assets stored",          "🎨", "Art Department", "Campaign artwork ready."),
    ("Growth & Discovery Agent running", "📈", "Growth & Discovery", "Building your SEO & discovery strategy..."),
    ("growth & discovery assets stored", "📈", "Growth & Discovery", "SEO package complete."),
    ("Syncing assets to Production Queue", "🚀", "Campaign Operations", "Preparing your Media Blitz..."),
    ("job(s) added to Asset Review",     "🚀", "Campaign Operations", "Awaiting your review."),
]


def _translate_build_message(raw_msg: str) -> str | None:
    for substr, icon, dept, phrase in _BUILD_STAGE_MESSAGES:
        if substr in raw_msg:
            return f"{icon} {dept}: {phrase}"
    return None


def _run_campaign_build(d: dict, mock_mode: bool) -> str | None:
    """Run the full campaign build, narrated as your creative team at work.
    Returns campaign_id or None."""
    from contracts.models import SongInput

    with st.status("Assembling your Creative Team...", expanded=True) as status:
        try:
            status.write("🧠 Creative Director: reviewing your artist identity...")
            from brand_brain.brain_loader import load_context
            brand_context = "" if mock_mode else load_context(d.get("artist_id", ""))
            if mock_mode:
                time.sleep(0.5)
            status.write("✓ Artist identity understood")

            status.write("🧠 Creative Director: reading your song...")
            song_data = json.loads(Path(d["song_file"]).read_text(encoding="utf-8"))
            song = SongInput.from_dict(song_data)
            if mock_mode:
                time.sleep(0.4)
            status.write(f"✓ Song understood: {song.title}")

            status.write("🧠 Creative Director: studying the lyrics and scripture...")
            if mock_mode:
                time.sleep(0.4)
            status.write(f"✓ Scripture identified: {song.scripture_primary}")

            status.write("🧠 Creative Director: preparing your Creative Brief...")
            mode = d.get("mode", "blitz")
            if mock_mode:
                from agents.mock_data import get_campaign_plan, get_campaign_brief
                time.sleep(0.6)
                plan = get_campaign_plan(song, mode)
                brief_fields = get_campaign_brief(song, mode)
            else:
                import agents.campaign_agent as campaign_agent
                plan, brief_fields = campaign_agent.run(song, mode, brand_context=brand_context)
            status.write(f"✓ Creative Brief ready: {plan.campaign_name}")

            from execution import campaign_store
            media_campaign = campaign_store.create_campaign(
                artist_id=song.artist_id,
                song_id=song.song_id,
                song_title=song.title,
                campaign_name=plan.campaign_name,
                campaign_mode=mode,
                song_file_path=d.get("song_file", ""),
            )
            campaign_store.update_campaign_status(song.artist_id, media_campaign["campaign_id"], "building")

            from execution import brief_store
            brief_store.create_brief(song.artist_id, media_campaign["campaign_id"], brief_fields)

            status.write("🚀 Campaign Operations: mapping your campaign calendar...")
            if mock_mode:
                time.sleep(0.3)
            status.write(f"✓ {len(plan.content_calendar)} calendar entries planned")

            status.write("🚀 Campaign Operations: assembling your creative team...")
            from execution.asset_library import AssetLibrary
            from execution.orchestrator import RenderOrchestrator

            library = AssetLibrary()
            orchestrator = RenderOrchestrator(library, mock_mode=mock_mode)
            if mock_mode:
                time.sleep(0.3)
            status.write("✓ Your creative team is in place")

            seen_lines = set()
            def _printer(msg):
                translated = _translate_build_message(msg)
                if translated and translated not in seen_lines:
                    seen_lines.add(translated)
                    status.write(translated)

            assets = orchestrator.run_campaign(song, plan, printer=_printer, brief=brief_fields)
            status.write(f"✓ {len(assets)} campaign assets ready")

            campaign_store.update_campaign_status(song.artist_id, media_campaign["campaign_id"], "review")
            st.session_state.wizard_media_campaign_id = media_campaign["campaign_id"]

            status.write("🚀 Campaign Operations: opening the Boardroom...")
            status.update(label="✅ Your Creative Team Has Finished!", state="complete")
            return plan.campaign_id

        except Exception as e:
            status.update(label=f"✗ Build failed: {e}", state="error")
            st.error(f"Campaign build failed: {e}")
            return None


_OPERATIONS_STATUS_COPY = {
    "draft":                  "Preparing to begin.",
    "building":               "Still assembling the team.",
    "review":                 "Awaiting your review.",
    "approved":               "Assets approved — add your release links to continue.",
    "waiting_for_distrokid":  "Waiting on your DistroKid release links.",
    "ready_to_launch":        "Ready when you are.",
    "live_blitz":             "Your Media Blitz is live.",
    "paused":                 "Paused.",
    "completed":              "Campaign completed.",
    "relaunch_ready":         "Ready to relaunch or extend.",
}


def _render_campaign_ready(d: dict):
    campaign_id = st.session_state.wizard_campaign_id
    artist_id = d.get("artist_id", "")
    media_campaign_id = st.session_state.get("wizard_media_campaign_id", "")

    render_html(f"""
    <div style="background:linear-gradient(135deg, #0A2A1A, #0D3D20);
                border:1px solid rgba(34,197,94,0.3); border-radius:16px;
                padding:2rem; text-align:center; margin-bottom:1.5rem;">
    <div style="font-size:44px; margin-bottom:0.6rem;">✅</div>
    <div style="font-size:22px; font-weight:800; color:#F0EDE8; margin-bottom:0.4rem;">Your Creative Team Has Finished</div>
    <div style="font-size:13px; color:#8A8480;">Step into the Boardroom below to see what they built.</div>
    </div>
    """)

    # ── The Creative Boardroom — real, honest department status ────────────────
    if artist_id and media_campaign_id:
        from execution import campaign_store
        from execution.department_map import department_status

        media_campaign = campaign_store.get_campaign(artist_id, media_campaign_id)
        dept_rows = department_status(artist_id, media_campaign_id)

        rows_html = (
            '<div style="display:flex;align-items:center;justify-content:space-between;'
            'padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.14);">'
            '<span style="font-family:Georgia,serif;font-size:15px;color:#F0EDE8;">You<span style="display:block;'
            'font-size:10px;letter-spacing:0.08em;text-transform:uppercase;color:#D4A853;margin-top:2px;">'
            'Executive Producer</span></span><span style="font-size:13px;color:#C8BEEA;">Presiding</span></div>'
        )

        cd_name = media_campaign.get("campaign_name", "") if media_campaign else ""
        rows_html += (
            '<div style="display:flex;align-items:center;justify-content:space-between;'
            'padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.14);">'
            '<span style="font-family:Georgia,serif;font-size:15px;color:#F0EDE8;">🧠 Creative Director</span>'
            f'<span style="font-size:13px;color:#C8BEEA;">Creative Brief ready — {cd_name}</span></div>'
        )

        for dept in dept_rows:
            if dept.get("rating"):
                stars = "★" * dept["rating"] + "☆" * (5 - dept["rating"])
                note = dept.get("verdict") or dept["status"]
                note_html = f'<span style="font-family:ui-monospace,monospace;color:#D4A853;letter-spacing:0.06em;">{stars}</span> <span style="font-size:12px;color:#C8BEEA;">{note}</span>'
            else:
                note_html = f'<span style="font-size:13px;color:#C8BEEA;">{dept["status"]}</span>'
            rows_html += (
                '<div style="display:flex;align-items:center;justify-content:space-between;'
                'padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.14);gap:1rem;">'
                f'<span style="font-family:Georgia,serif;font-size:15px;color:#F0EDE8;white-space:nowrap;">{dept["icon"]} {dept["label"]}</span>'
                f'<span style="text-align:right;">{note_html}</span></div>'
            )

        ops_status = media_campaign.get("status", "review") if media_campaign else "review"
        ops_copy = _OPERATIONS_STATUS_COPY.get(ops_status, ops_status.replace("_", " ").title())
        rows_html += (
            '<div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;">'
            '<span style="font-family:Georgia,serif;font-size:15px;color:#F0EDE8;">🚀 Campaign Operations</span>'
            f'<span style="font-size:13px;color:#C8BEEA;">{ops_copy}</span></div>'
        )

        render_html(f"""
        <div style="background:linear-gradient(160deg, #2D1B69, #120B29);
                    border-radius:14px; padding:1.5rem 1.75rem; margin-bottom:1.5rem;">
        <div style="font-size:11px; letter-spacing:0.14em; text-transform:uppercase;
                    color:#B7A9E6; margin-bottom:0.5rem;">The Creative Boardroom</div>
        {rows_html}
        </div>
        """)

    st.caption(
        "Next: approve these assets, then release your music through DistroKid. "
        "Once you have your release links, the Media Blitz Control Center lets you "
        "schedule and launch the media campaign."
    )

    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    with col_a:
        if st.button("✅  Open Approval Queue", type="primary", use_container_width=True):
            st.session_state.approval_campaign_id = campaign_id
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("approval")
    with col_b:
        if st.button("📄  View Creative Brief", use_container_width=True):
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("creative_brief")
    with col_c:
        if st.button("🎯  Media Blitz Control Center", use_container_width=True):
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("media_blitz")
    with col_d:
        if st.button("📦  View All Campaigns", use_container_width=True):
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("campaigns")
    with col_e:
        if st.button("➕  New Project", use_container_width=True):
            st.session_state.wizard_step = 0
            st.session_state.wizard_data = {}
            st.session_state.pop("wizard_campaign_id", None)
            st.rerun()

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    st.caption("Human-led. AI-assisted. Scripture-rooted. Nothing publishes until you approve it.")


# ── Main entry point ──────────────────────────────────────────────────────────

def render():
    _init()
    page_header("Media Campaign Wizard", "One song. One campaign. Complete.", "🎵")
    _progress_header()

    step = st.session_state.wizard_step

    # Offer draft resume when entering a fresh wizard
    if step == 0 and not st.session_state.wizard_data:
        draft = _load_draft()
        if draft and draft.get("title"):
            st.info(
                f"📝 You have an unfinished draft: **{draft.get('title', 'Untitled')}** "
                f"— {draft.get('artist_name', '')}"
            )
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Resume Draft →", type="primary"):
                    st.session_state.wizard_data = draft
                    st.session_state.wizard_step = draft.get("_draft_step", 1)
                    st.rerun()
            with c2:
                if st.button("Start Fresh"):
                    _clear_draft()
                    st.rerun()
            st.divider()

    dispatch = [
        _step_artist,           # 0
        _step_creative_master,  # 1
        _step_details_lyrics,   # 2
        _step_artwork,          # 3
        _step_release_info,     # 4
        _step_analysis,         # 5
        _step_launch,           # 6
    ]

    if 0 <= step < len(dispatch):
        dispatch[step]()
    else:
        st.session_state.wizard_step = 0
        st.rerun()
