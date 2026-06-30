"""MusicWorks™ V3 — New Project Wizard (6-step integrated flow)."""
import sys
import json
import re
import uuid
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import navigate_to, page_header, render_html
from brand_brain.artist_library import list_artists, load_artist, save_artist
from brand_brain.models import ArtistBrain

SONGS_DIR = Path(__file__).parent.parent.parent / "data" / "songs"
ARTISTS_DIR = Path(__file__).parent.parent.parent / "data" / "artists"
SONGS_DIR.mkdir(parents=True, exist_ok=True)
ARTISTS_DIR.mkdir(parents=True, exist_ok=True)

STEPS = ["Artist", "Song", "Details", "Assets", "Validate", "Build"]


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
            color = "#22C55E"; dot = "✓"; text_color = "#22C55E"; txt_w = "400"
        elif i == current:
            color = "#FF6B2B"; dot = str(i + 1); text_color = "#F0EDE8"; txt_w = "600"
        else:
            color = "#333"; dot = str(i + 1); text_color = "#6A6460"; txt_w = "400"
        num_color = "#fff" if i <= current else "#6A6460"
        connector = (
            f'<div style="flex:1;height:1px;background:{"#22C55E" if i < current else "#242424"};margin:0 4px;align-self:center;"></div>'
            if i < len(STEPS) - 1 else ""
        )
        items += (
            f'<div style="display:flex;align-items:center;">'
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px;">'
            f'<div style="width:28px;height:28px;border-radius:50%;background:{color};color:{num_color};font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{dot}</div>'
            f'<div style="font-size:10px;color:{text_color};font-weight:{txt_w};white-space:nowrap;">{label}</div>'
            f'</div>{connector}</div>'
        )
    st.markdown(
        f'<div class="mw-card" style="padding:1.25rem 1.5rem;margin-bottom:1.5rem;"><div style="display:flex;align-items:flex-start;justify-content:space-between;">{items}</div></div>',
        unsafe_allow_html=True,
    )


# ── STEP 0: ARTIST ────────────────────────────────────────────────────────────

def _step_artist():
    st.markdown("### Step 1 — Choose Artist")
    st.caption("Select an existing artist or create a new one.")

    artists = list_artists()
    options = [f"{a['artist_name']}" for a in artists] + ["+ Create New Artist"]

    choice = st.selectbox("Artist:", options)

    if choice == "+ Create New Artist":
        st.markdown("---")
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
                _go(1)
    else:
        if artists:
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
        else:
            st.info("No artists found. Create your first artist above.")


# ── STEP 1: SONG ─────────────────────────────────────────────────────────────

def _step_song():
    d = st.session_state.wizard_data
    st.markdown(f"### Step 2 — Upload Song")
    st.caption(f"Artist: **{d.get('artist_name', '')}**")

    col_a, col_b = st.columns(2)
    with col_a:
        audio_file = st.file_uploader("Song file (MP3 or WAV):", type=["mp3", "wav"])
        if audio_file:
            st.caption(f"✓ {audio_file.name} ({audio_file.size // 1024} KB)")

        mix_type = st.radio("File type:", ["Working Mix", "Master"], horizontal=True)

    with col_b:
        duration = st.number_input("Duration (seconds):", min_value=0, value=0, step=1)
        bpm = st.number_input("BPM (optional):", min_value=0, value=0, step=1)
        key = st.text_input("Key (optional):", placeholder="e.g. G Major")
        isrc = st.text_input("ISRC (optional):", placeholder="e.g. US-XXX-26-00001")
        track_number = st.number_input("Track number:", min_value=0, value=0, step=1)

    render_html("""
    <div class="mw-card" style="padding:0.75rem 1rem; border-left:3px solid #F59E0B; margin-top:0.5rem;">
        <div style="font-size:12px; color:#F59E0B; font-weight:600; margin-bottom:2px;">Audio QC gate</div>
        <div style="font-size:12px; color:#8A8480;">
            Upload the working mix now to track progress. You'll confirm QC approval in Step 5.
        </div>
    </div>
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            _go(0)
    with col2:
        if st.button("Continue →", type="primary"):
            artist_id = d.get("artist_id", "")
            audio_path = ""
            if audio_file:
                save_dir = ARTISTS_DIR / artist_id / "audio"
                save_dir.mkdir(parents=True, exist_ok=True)
                dest = save_dir / audio_file.name
                dest.write_bytes(audio_file.read())
                audio_path = str(dest)
            d.update({
                "audio_file_path": audio_path,
                "audio_file_name": audio_file.name if audio_file else "",
                "mix_type": mix_type,
                "duration_seconds": duration or None,
                "bpm": bpm or None,
                "key": key or None,
                "isrc": isrc or None,
                "track_number": track_number or None,
            })
            _go(2)


# ── STEP 2: PROJECT DETAILS ───────────────────────────────────────────────────

def _step_details():
    from datetime import date
    d = st.session_state.wizard_data
    st.markdown("### Step 3 — Project Details")
    st.caption(f"Artist: **{d.get('artist_name', '')}**")

    col_a, col_b = st.columns(2)
    with col_a:
        song_title = st.text_input("Song title *", value=d.get("title", ""), placeholder="e.g. HLANGANA")
        title_meaning = st.text_input("Title meaning (if non-English):", value=d.get("title_meaning", ""), placeholder="e.g. Gather Together")
        title_language = st.text_input("Title language:", value=d.get("title_language", ""), placeholder="e.g. Zulu")
        album_title = st.text_input("Album title *", value=d.get("album_title", ""), placeholder="e.g. Becoming Vol. 1")
    with col_b:
        release_date = st.date_input("Release date *",
                                     value=date.fromisoformat(d["release_date"]) if d.get("release_date") else date.today())
        series_name = st.text_input("Series name:", value=d.get("series_name", "") or "", placeholder="e.g. Kingdom Words")
        series_episode = st.number_input("Episode #:", min_value=0, value=d.get("series_episode", 0) or 0, step=1)

    scripture_primary = st.text_input("Primary scripture *", value=d.get("scripture_primary", ""), placeholder="e.g. Hebrews 10:25")
    scripture_text = st.text_area("Scripture text *", value=d.get("scripture_primary_text", ""), height=80,
                                   placeholder="Paste the full verse text here...")
    scripture_supporting = st.text_input("Supporting scriptures (comma-separated):",
                                          value=", ".join(d.get("scripture_supporting", [])),
                                          placeholder="e.g. Acts 2:42, Psalm 122:1")

    col_c, col_d = st.columns(2)
    with col_c:
        themes_raw = st.text_input("Themes *", value=", ".join(d.get("themes", [])),
                                    placeholder="e.g. Community, Identity, Gathering")
        genre_raw = st.text_input("Genre *", value=", ".join(d.get("genre", [])),
                                   placeholder="e.g. Afro-Gospel, Amapiano Gospel")
    with col_d:
        mood_raw = st.text_input("Mood:", value=", ".join(d.get("mood", [])),
                                  placeholder="e.g. Devotional, Communal, Hopeful")
        campaign_mode = st.selectbox("Campaign mode:", ["blitz", "standard", "growth", "ministry_push", "chart_push"],
                                      index=["blitz", "standard", "growth", "ministry_push", "chart_push"].index(d.get("mode", "blitz")))

    cultural_notes = st.text_area("Cultural notes (pronunciation, context):",
                                   value=d.get("cultural_notes", "") or "", height=60)
    internal_notes = st.text_area("Internal notes (not used in campaign assets):",
                                   value=d.get("internal_notes", "") or "", height=60)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            _go(1)
    with col2:
        if st.button("Continue →", type="primary"):
            missing = []
            if not song_title.strip(): missing.append("Song title")
            if not album_title.strip(): missing.append("Album title")
            if not scripture_primary.strip(): missing.append("Primary scripture")
            if not scripture_text.strip(): missing.append("Scripture text")
            if not themes_raw.strip(): missing.append("Themes")
            if not genre_raw.strip(): missing.append("Genre")
            if missing:
                st.error(f"Required fields missing: {', '.join(missing)}")
                return

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
                "scripture_primary": scripture_primary.strip(),
                "scripture_primary_text": scripture_text.strip(),
                "scripture_supporting": [s.strip() for s in scripture_supporting.split(",") if s.strip()],
                "themes": [t.strip() for t in themes_raw.split(",") if t.strip()],
                "genre": [g.strip() for g in genre_raw.split(",") if g.strip()],
                "mood": [m.strip() for m in mood_raw.split(",") if m.strip()],
                "series_name": series_name.strip() or None,
                "series_episode": series_episode or None,
                "cultural_notes": cultural_notes.strip() or None,
                "internal_notes": internal_notes.strip(),
                "mode": campaign_mode,
            })
            _go(3)


# ── STEP 3: ASSETS ────────────────────────────────────────────────────────────

def _step_assets():
    d = st.session_state.wizard_data
    st.markdown("### Step 4 — Upload Assets")
    st.caption("Upload visual assets. Album cover is required before launch.")

    artist_id = d.get("artist_id", "unknown")
    ref_dir = ARTISTS_DIR / artist_id / "references"
    art_dir = ARTISTS_DIR / artist_id / "artwork"
    ref_dir.mkdir(parents=True, exist_ok=True)
    art_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = {}

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div style="font-size:12px; color:#D4A853; font-weight:600; margin-bottom:4px;">ALBUM COVER</div>', unsafe_allow_html=True)
        album_cover = st.file_uploader("Album cover (JPG/PNG) *", type=["jpg", "jpeg", "png"], key="album_cover")
        if album_cover:
            dest = art_dir / album_cover.name
            dest.write_bytes(album_cover.read())
            saved_paths["artwork_file_path"] = str(dest)
            st.image(str(dest), width=200)

    with col_b:
        st.markdown('<div style="font-size:12px; color:#8A8480; font-weight:600; margin-bottom:4px;">ARTIST PHOTOS</div>', unsafe_allow_html=True)
        artist_photos = st.file_uploader("Artist / promo photos:", type=["jpg", "jpeg", "png"],
                                          accept_multiple_files=True, key="artist_photos")
        photo_paths = []
        for f in (artist_photos or []):
            dest = ref_dir / f"artist_{f.name}"
            dest.write_bytes(f.read())
            photo_paths.append(str(dest))
        if photo_paths:
            st.success(f"✓ {len(photo_paths)} photo(s) saved")
        saved_paths["artist_photo_paths"] = photo_paths

    st.markdown("---")
    st.markdown('<div style="font-size:12px; color:#8A8480; font-weight:600; margin-bottom:4px;">CREATIVE DNA REFERENCE PACK</div>', unsafe_allow_html=True)
    st.caption("Mood boards, lighting references, location photos — up to 5 images.")
    dna_files = st.file_uploader("Reference images:", type=["jpg", "jpeg", "png"],
                                  accept_multiple_files=True, key="dna_refs")
    dna_paths = []
    for f in (dna_files or [])[:5]:
        dest = ref_dir / f"dna_{f.name}"
        dest.write_bytes(f.read())
        dna_paths.append(str(dest))
    if dna_paths:
        st.success(f"✓ {len(dna_paths)} reference image(s) saved")
    saved_paths["creative_dna_reference_paths"] = dna_paths

    col_c, col_d = st.columns(2)
    with col_c:
        logos = st.file_uploader("Brand logos (PNG preferred):", type=["png", "svg", "jpg"],
                                  accept_multiple_files=True, key="logos")
        logo_paths = []
        for f in (logos or []):
            dest = ref_dir / f"logo_{f.name}"
            dest.write_bytes(f.read())
            logo_paths.append(str(dest))
        if logo_paths:
            st.success(f"✓ {len(logo_paths)} logo(s) saved")
        saved_paths["logo_paths"] = logo_paths

    with col_d:
        st.markdown('<div style="font-size:11px; color:#6A6460; margin-top:0.5rem; line-height:1.5;">'
                    'Typography, reference videos, and additional creative assets can be added to the Brand Brain directly.<br>'
                    'All assets are stored in <code>data/artists/{artist_id}/</code></div>', unsafe_allow_html=True)

    d.update(saved_paths)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            _go(2)
    with col2:
        if st.button("Continue to Validation →", type="primary"):
            _go(4)


# ── STEP 4: VALIDATE ─────────────────────────────────────────────────────────

def _step_validate():
    d = st.session_state.wizard_data
    st.markdown("### Step 5 — Validate")
    st.caption(f"**{d.get('artist_name', '')}** · **{d.get('title', '')}** · {d.get('album_title', '')}")

    brand = load_artist(d.get("artist_id", ""))

    # Validation checks
    checks = [
        ("Song title", bool(d.get("title")), True),
        ("Album title", bool(d.get("album_title")), True),
        ("Artist selected", bool(d.get("artist_id")), True),
        ("Primary scripture", bool(d.get("scripture_primary")), True),
        ("Themes", bool(d.get("themes")), True),
        ("Brand Brain found", brand is not None, False),
        ("Audio file uploaded", bool(d.get("audio_file_path")), False),
        ("Album cover uploaded", bool(d.get("artwork_file_path")), False),
        ("Creative DNA references", bool(d.get("creative_dna_reference_paths")), False),
    ]

    errors = [(label, required) for label, ok, required in checks if not ok and required]
    warnings = [(label, required) for label, ok, required in checks if not ok and not required]

    rows_html = ""
    for label, ok, required in checks:
        icon = "✓" if ok else ("✗" if required else "⚠")
        color = "#22C55E" if ok else ("#EF4444" if required else "#F59E0B")
        note = "" if ok else (" (required)" if required else " (recommended)")
        rows_html += f'<div style="display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1px solid #1E1E1E;"><span style="color:{color}; font-size:14px; min-width:16px;">{icon}</span><span style="font-size:13px; color:#C8C4BE;">{label}</span><span style="font-size:11px; color:#6A6460;">{note}</span></div>'

    st.markdown(f'<div class="mw-card" style="padding:1rem 1.5rem;">{rows_html}</div>', unsafe_allow_html=True)

    if errors:
        st.error(f"Cannot proceed: {', '.join(l for l, _ in errors)} required.")
    if warnings:
        st.warning(f"Recommended before launch: {', '.join(l for l, _ in warnings)}")

    st.divider()

    st.markdown("**Hard Gate Confirmation**")
    st.caption("Both must be confirmed before any campaign can run.")
    theology_ok = st.checkbox("✓ I confirm this song has passed Theology Review — lyrics are scripturally sound and align with the artist's theological guardrails.")
    audio_ok = st.checkbox("✓ I confirm this song has passed Audio QC — the file is clean, at correct level, and production-ready.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            _go(3)
    with col2:
        can_proceed = not errors and theology_ok and audio_ok
        if st.button("Save & Proceed to Build →", type="primary", disabled=not can_proceed):
            if _save_song_json(d, brand, theology_ok, audio_ok):
                _go(5)


def _save_song_json(d: dict, brand, theology_ok: bool, audio_ok: bool) -> bool:
    """Save the song JSON and store the path in wizard_data. Returns True on success."""
    try:
        artist_id = d.get("artist_id", "")
        song_data = {
            "song_id": d.get("song_id", f"{artist_id}-{uuid.uuid4().hex[:6]}"),
            "artist_id": artist_id,
            "title": d.get("title", ""),
            "title_meaning": d.get("title_meaning", ""),
            "title_language": d.get("title_language", ""),
            "artist_name": d.get("artist_name", ""),
            "album_title": d.get("album_title", ""),
            "album_id": re.sub(r"[^a-z0-9-]", "-", d.get("album_title", "").lower()),
            "track_number": d.get("track_number"),
            "release_date": d.get("release_date", ""),
            "duration_seconds": d.get("duration_seconds"),
            "bpm": d.get("bpm"),
            "key": d.get("key"),
            "isrc": d.get("isrc"),
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
            "series_name": d.get("series_name"),
            "series_episode": d.get("series_episode"),
            "cultural_notes": d.get("cultural_notes"),
            "content_advisory": "none",
            "brand_color_primary": (brand.creative_dna.color_palette.get("primary", "#2D1B69").split(" ")[0]
                                    if brand else "#2D1B69"),
            "brand_color_secondary": (brand.creative_dna.color_palette.get("secondary", "#D4A853").split(" ")[0]
                                      if brand else "#D4A853"),
            "target_geography": brand.audience.get("geography_priority", []) if brand else [],
            "target_audience_age": "18-45",
            "target_faith_background": "Christian — all denominations",
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


# ── STEP 5: BUILD CAMPAIGN ────────────────────────────────────────────────────

def _step_build():
    d = st.session_state.wizard_data

    # If already built, show success state
    if st.session_state.get("wizard_campaign_id"):
        _render_campaign_ready(d)
        return

    title = d.get("title", "Your Song")
    artist = d.get("artist_name", "")
    mode = d.get("mode", "blitz")

    st.markdown("### Step 6 — Build Campaign")
    render_html(f"""
    <div class="mw-card" style="padding:1.5rem; border-left:3px solid #FF6B2B; margin-bottom:1.5rem;">
        <div style="font-size:16px; font-weight:700; color:#F0EDE8; margin-bottom:4px;">{title}</div>
        <div style="font-size:13px; color:#9B89D4; margin-bottom:0.25rem;">{artist}</div>
        <div style="font-size:12px; color:#8A8480;">
            Campaign mode: <span style="color:#D4A853; font-weight:600; text-transform:uppercase;">{mode}</span>
        </div>
    </div>
    """)

    # Check song file
    song_file = d.get("song_file", "")
    if not song_file or not Path(song_file).exists():
        st.error("Song file not found. Please go back and complete validation.")
        if st.button("← Back to Validation"):
            _go(4)
        return

    # API key check
    try:
        from config import ANTHROPIC_API_KEY, MOCK_MODE as CFG_MOCK
        has_key = bool(ANTHROPIC_API_KEY)
        default_mock = CFG_MOCK or not has_key
    except ImportError:
        has_key = False
        default_mock = True

    if not has_key:
        st.warning("No Anthropic API key found — running in Mock Mode. Assets will use sample data.")

    mock_mode = st.checkbox(
        "Use Mock Mode (sample data — no API calls)",
        value=default_mock,
        help="Enable this if you don't have an API key set up yet."
    )

    render_html("""
    <div class="mw-card" style="padding:1rem 1.5rem; margin:1rem 0;">
        <div style="font-size:11px; color:#8A8480; font-weight:600; letter-spacing:0.6px;
                    text-transform:uppercase; margin-bottom:0.75rem;">What happens next</div>
        <div style="font-size:13px; color:#C8C4BE; line-height:1.8;">
            MusicWorks will automatically generate all campaign assets:<br>
            Social media captions · Video storyboard · Blog post · Press release · Church outreach · Thumbnail concepts
        </div>
    </div>
    """)

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("← Back"):
            _go(4)
    with col2:
        if st.button("🚀  BUILD CAMPAIGN", type="primary", use_container_width=True):
            campaign_id = _run_campaign_build(d, mock_mode)
            if campaign_id:
                st.session_state.wizard_campaign_id = campaign_id
                st.rerun()


def _run_campaign_build(d: dict, mock_mode: bool) -> str | None:
    """Run the full campaign build with animated progress. Returns campaign_id or None."""
    from contracts.models import SongInput

    with st.status("Building your campaign...", expanded=True) as status:
        try:
            # Step 1: Brand Brain
            status.write("⏳ Loading Brand Brain...")
            from brand_brain.brain_loader import load_context
            brand_context = "" if mock_mode else load_context(d.get("artist_id", ""))
            if mock_mode:
                time.sleep(0.5)
            status.write("✓ Brand Brain loaded")

            # Step 2: Creative DNA
            status.write("⏳ Loading Creative DNA...")
            if mock_mode:
                time.sleep(0.4)
            status.write("✓ Creative DNA ready")

            # Step 3: Read Song
            status.write("⏳ Reading Song...")
            song_data = json.loads(Path(d["song_file"]).read_text(encoding="utf-8"))
            song = SongInput.from_dict(song_data)
            if mock_mode:
                time.sleep(0.4)
            status.write(f'✓ Song loaded: {song.title}')

            # Step 4: Lyrics / scripture context
            status.write("⏳ Reading Lyrics & Scripture...")
            if mock_mode:
                time.sleep(0.4)
            status.write(f"✓ Scripture: {song.scripture_primary}")

            # Step 5: Campaign Plan
            status.write("⏳ Building Campaign Plan...")
            mode = d.get("mode", "blitz")
            if mock_mode:
                from agents.mock_data import get_campaign_plan
                time.sleep(0.6)
                plan = get_campaign_plan(song, mode)
            else:
                import agents.campaign_agent as campaign_agent
                plan = campaign_agent.run(song, mode, brand_context=brand_context)
            status.write(f"✓ Campaign plan ready: {plan.campaign_name}")

            # Step 6: Generate Assets
            status.write("⏳ Generating Assets...")
            from execution.asset_library import AssetLibrary
            from execution.orchestrator import RenderOrchestrator

            library = AssetLibrary()
            orchestrator = RenderOrchestrator(library, mock_mode=mock_mode)

            log_lines = []
            def _printer(msg):
                log_lines.append(msg)
                if len(log_lines) % 2 == 0:
                    status.write(f"   ↳ {msg}")

            assets = orchestrator.run_campaign(song, plan, printer=_printer)
            status.write(f"✓ {len(assets)} assets generated")

            status.update(label="✅ Campaign Ready!", state="complete")
            return plan.campaign_id

        except Exception as e:
            status.update(label=f"✗ Build failed: {e}", state="error")
            st.error(f"Campaign build failed: {e}")
            return None


def _render_campaign_ready(d: dict):
    campaign_id = st.session_state.wizard_campaign_id

    render_html(f"""
    <div style="background:linear-gradient(135deg, #0A2A1A, #0D3D20);
                border:1px solid rgba(34,197,94,0.3); border-radius:16px;
                padding:2.5rem; text-align:center; margin-bottom:2rem;">
        <div style="font-size:48px; margin-bottom:0.75rem;">✅</div>
        <div style="font-size:24px; font-weight:800; color:#F0EDE8; margin-bottom:0.5rem;">
            Campaign Ready!
        </div>
        <div style="font-size:14px; color:#22C55E; margin-bottom:0.5rem;">{campaign_id}</div>
        <div style="font-size:13px; color:#8A8480;">
            All assets have been generated and are waiting for your review.
        </div>
    </div>
    """)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅  Open Approval Queue", type="primary", use_container_width=True):
            st.session_state.approval_campaign_id = campaign_id
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("approval")
    with col_b:
        if st.button("📦  View All Campaigns", use_container_width=True):
            st.session_state.pop("wizard_campaign_id", None)
            navigate_to("campaigns")
    with col_c:
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

    page_header("New Project Wizard", "One song. One campaign. Complete.", "🎵")
    _progress_header()

    step = st.session_state.wizard_step

    if step == 0:
        _step_artist()
    elif step == 1:
        _step_song()
    elif step == 2:
        _step_details()
    elif step == 3:
        _step_assets()
    elif step == 4:
        _step_validate()
    elif step == 5:
        _step_build()
    else:
        st.session_state.wizard_step = 0
        st.rerun()
