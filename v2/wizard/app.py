"""
MusicWorks™ New Project Wizard
Multi-step entry point for every new campaign.
Produces a SongInput JSON file ready for main.py to consume.
No API calls are made here — this is data collection only.
"""
import json
import sys
import re
import uuid
from pathlib import Path
from datetime import date

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from brand_brain.artist_library import list_artists, load_artist, save_artist
from brand_brain.models import ArtistBrain

st.set_page_config(
    page_title="MusicWorks™ New Project Wizard",
    page_icon="🎵",
    layout="centered",
)

SONGS_DIR = Path(__file__).parent.parent / "data" / "songs"
ARTISTS_DIR = Path(__file__).parent.parent / "data" / "artists"
SONGS_DIR.mkdir(parents=True, exist_ok=True)
ARTISTS_DIR.mkdir(parents=True, exist_ok=True)

STEPS = ["Artist", "Song Upload", "Project Info", "Reference Assets", "Validate & Launch"]

# ── Session state init ────────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 0
if "wizard_data" not in st.session_state:
    st.session_state.wizard_data = {}


def go_to(step: int):
    st.session_state.step = step
    st.rerun()


# ── Step progress header ──────────────────────────────────────────────────────
st.markdown("## MusicWorks™ New Project Wizard")
st.caption("Build every campaign from here. One song at a time.")

cols = st.columns(len(STEPS))
for i, (col, label) in enumerate(zip(cols, STEPS)):
    if i < st.session_state.step:
        col.markdown(f"✅ **{label}**")
    elif i == st.session_state.step:
        col.markdown(f"**▶ {label}**")
    else:
        col.markdown(f"<span style='color:#888'>{label}</span>", unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 0: ARTIST
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.step == 0:
    st.subheader("Step 1 — Choose Artist")

    artists = list_artists()
    artist_options = [f"{a['artist_name']} ({a['artist_id']})" for a in artists]
    artist_options_with_new = artist_options + ["+ Create New Artist"]

    choice = st.selectbox("Select an artist:", artist_options_with_new)

    if choice == "+ Create New Artist":
        st.markdown("---")
        st.markdown("**Create New Artist**")
        new_name = st.text_input("Artist name:", placeholder="e.g. Fire & Flow Gospel")
        new_id = st.text_input(
            "Artist ID (no spaces, use underscores):",
            value=re.sub(r"[^a-z0-9_]", "_", new_name.lower().strip()) if new_name else "",
            placeholder="e.g. fire_and_flow_gospel",
        )
        new_tagline = st.text_input("Tagline:", placeholder="One sentence describing this artist")
        new_mission = st.text_area("Mission statement:", height=80)

        if st.button("Create Artist & Continue", type="primary"):
            if not new_name or not new_id:
                st.error("Artist name and ID are required.")
            elif load_artist(new_id) is not None:
                st.error(f"An artist with ID '{new_id}' already exists.")
            else:
                brain = ArtistBrain(
                    artist_id=new_id,
                    artist_name=new_name,
                    display_name=new_name,
                    tagline=new_tagline,
                    mission=new_mission,
                    bio_short="",
                    bio_long="",
                )
                save_artist(brain)
                st.session_state.wizard_data["artist_id"] = new_id
                st.session_state.wizard_data["artist_name"] = new_name
                st.success(f"Artist '{new_name}' created.")
                go_to(1)
    else:
        if st.button("Continue with this artist", type="primary", disabled=not artists):
            selected = artists[artist_options.index(choice)]
            st.session_state.wizard_data["artist_id"] = selected["artist_id"]
            st.session_state.wizard_data["artist_name"] = selected["artist_name"]
            go_to(1)

        if not artists:
            st.info("No artists found. Create your first artist above.")

        if artists:
            chosen_id = artists[artist_options.index(choice)]["artist_id"] if choice != "+ Create New Artist" else None
            if chosen_id:
                brain = load_artist(chosen_id)
                if brain:
                    with st.expander("Brand Brain preview", expanded=False):
                        st.markdown(f"**Mission:** {brain.mission}")
                        st.markdown(f"**Genre:** {', '.join(brain.genre)}")
                        st.markdown(f"**Heritage:** {', '.join(brain.heritage)}")
                        if brain.brand_rules:
                            st.markdown("**Brand rules:**")
                            for r in brain.brand_rules[:4]:
                                st.caption(f"- {r}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: SONG UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.step == 1:
    st.subheader("Step 2 — Upload Song")
    st.caption(f"Artist: **{st.session_state.wizard_data.get('artist_name', '')}**")

    audio_file = st.file_uploader("Upload song file (MP3 or WAV):", type=["mp3", "wav"])
    duration = st.number_input("Duration (seconds):", min_value=0, value=0, step=1)
    bpm = st.number_input("BPM (optional):", min_value=0, value=0, step=1)
    key = st.text_input("Key (optional):", placeholder="e.g. G Major")
    isrc = st.text_input("ISRC code (optional):", placeholder="e.g. US-XXX-26-00001")
    track_number = st.number_input("Track number on album (optional):", min_value=0, value=0, step=1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            go_to(0)
    with col2:
        if st.button("Continue", type="primary"):
            artist_id = st.session_state.wizard_data.get("artist_id", "")
            audio_path = ""
            if audio_file:
                save_dir = ARTISTS_DIR / artist_id / "audio"
                save_dir.mkdir(parents=True, exist_ok=True)
                dest = save_dir / audio_file.name
                dest.write_bytes(audio_file.read())
                audio_path = str(dest)
                st.session_state.wizard_data["audio_file_name"] = audio_file.name

            st.session_state.wizard_data.update({
                "audio_file_path": audio_path,
                "duration_seconds": duration or None,
                "bpm": bpm or None,
                "key": key or None,
                "isrc": isrc or None,
                "track_number": track_number or None,
            })
            go_to(2)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: PROJECT INFORMATION
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.step == 2:
    st.subheader("Step 3 — Project Information")
    st.caption(f"Artist: **{st.session_state.wizard_data.get('artist_name', '')}**")

    col_a, col_b = st.columns(2)
    with col_a:
        song_title = st.text_input("Song title *", placeholder="e.g. HLANGANA")
        title_meaning = st.text_input("Title meaning (if non-English):", placeholder="e.g. Gather Together")
        title_language = st.text_input("Title language:", placeholder="e.g. Zulu")
    with col_b:
        album_title = st.text_input("Album title *", placeholder="e.g. Becoming Vol. 1")
        release_date = st.date_input("Release date *", value=date.today())
        track_number_display = st.session_state.wizard_data.get("track_number") or ""

    scripture_primary = st.text_input("Primary scripture *", placeholder="e.g. Hebrews 10:25")
    scripture_text = st.text_area("Full scripture text *", height=80,
        placeholder="e.g. not giving up meeting together, as some are in the habit of doing...")
    scripture_supporting = st.text_input("Supporting scriptures (comma-separated):",
        placeholder="e.g. Acts 2:42, Psalm 122:1")

    themes_raw = st.text_input("Themes (comma-separated) *",
        placeholder="e.g. Community, Church, African Identity")
    genre_raw = st.text_input("Genre (comma-separated) *",
        placeholder="e.g. Afro-Gospel, Amapiano Gospel")
    mood_raw = st.text_input("Mood (comma-separated):",
        placeholder="e.g. Devotional, Communal, Hopeful")

    st.markdown("---")
    series_name = st.text_input("Series name (if part of a series):", placeholder="e.g. Kingdom Words")
    series_episode = st.number_input("Episode number:", min_value=0, value=0, step=1)
    cultural_notes = st.text_area("Cultural notes (pronunciation, context):", height=60)
    internal_notes = st.text_area("Internal notes (not used in campaign assets):", height=60)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            go_to(1)
    with col2:
        if st.button("Continue", type="primary"):
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
                st.error(f"Required fields missing: {', '.join(missing)}")
            else:
                slug = re.sub(r"[^a-z0-9-]", "-", song_title.strip().lower())
                artist_id = st.session_state.wizard_data.get("artist_id", "unknown")
                song_id = f"{artist_id[:8].replace('_', '-')}-{slug}-{uuid.uuid4().hex[:4]}"

                st.session_state.wizard_data.update({
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
                })
                go_to(3)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: REFERENCE ASSETS
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.step == 3:
    st.subheader("Step 4 — Reference Assets")
    st.caption("Upload visual assets. All are optional but improve campaign quality.")

    artist_id = st.session_state.wizard_data.get("artist_id", "unknown")
    ref_dir = ARTISTS_DIR / artist_id / "references"
    art_dir = ARTISTS_DIR / artist_id / "artwork"
    ref_dir.mkdir(parents=True, exist_ok=True)
    art_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = {}

    album_cover = st.file_uploader("Album cover (JPG/PNG) — required for launch:", type=["jpg", "jpeg", "png"])
    if album_cover:
        dest = art_dir / album_cover.name
        dest.write_bytes(album_cover.read())
        saved_paths["artwork_file_path"] = str(dest)
        st.success(f"Saved: {album_cover.name}")

    st.markdown("---")
    st.markdown("**Creative DNA Reference Images** — mood, lighting, color, environment")
    dna_files = st.file_uploader(
        "Upload reference images (up to 5):",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="dna_refs",
    )
    dna_paths = []
    for f in (dna_files or [])[:5]:
        dest = ref_dir / f"dna_{f.name}"
        dest.write_bytes(f.read())
        dna_paths.append(str(dest))
    if dna_paths:
        st.success(f"Saved {len(dna_paths)} reference image(s)")

    st.markdown("---")
    st.markdown("**Artist Photos / Promo Photos**")
    artist_photos = st.file_uploader(
        "Upload artist photos:",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="artist_photos",
    )
    photo_paths = []
    for f in (artist_photos or []):
        dest = ref_dir / f"artist_{f.name}"
        dest.write_bytes(f.read())
        photo_paths.append(str(dest))
    if photo_paths:
        st.success(f"Saved {len(photo_paths)} artist photo(s)")

    st.markdown("---")
    st.markdown("**Brand Logos**")
    logos = st.file_uploader(
        "Upload logo files (PNG with transparency preferred):",
        type=["png", "svg", "jpg"],
        accept_multiple_files=True,
        key="logos",
    )
    logo_paths = []
    for f in (logos or []):
        dest = ref_dir / f"logo_{f.name}"
        dest.write_bytes(f.read())
        logo_paths.append(str(dest))
    if logo_paths:
        st.success(f"Saved {len(logo_paths)} logo file(s)")

    saved_paths["creative_dna_reference_paths"] = dna_paths
    saved_paths["artist_photo_paths"] = photo_paths
    saved_paths["logo_paths"] = logo_paths
    st.session_state.wizard_data.update(saved_paths)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            go_to(2)
    with col2:
        if st.button("Continue to Validation", type="primary"):
            go_to(4)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: VALIDATE & LAUNCH
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.step == 4:
    d = st.session_state.wizard_data
    st.subheader("Step 5 — Validate & Launch")
    st.caption(f"Artist: **{d.get('artist_name', '')}** | Song: **{d.get('title', '')}**")

    # Validation checks
    warnings = []
    errors = []

    if not d.get("audio_file_path"):
        warnings.append("No audio file uploaded — you will need to reference it manually.")
    if not d.get("artwork_file_path"):
        warnings.append("No album cover uploaded — required before campaign launches.")
    if not d.get("creative_dna_reference_paths"):
        warnings.append("No Creative DNA reference images — agents will use Brand Brain defaults.")
    if not d.get("artist_id"):
        errors.append("No artist selected.")
    if not d.get("title"):
        errors.append("Song title is missing.")
    if not d.get("scripture_primary"):
        errors.append("Primary scripture is missing.")

    brand = load_artist(d.get("artist_id", ""))
    if brand is None:
        warnings.append(f"No Brand Brain found for artist_id='{d.get('artist_id')}' — campaign will run without brand context.")
    else:
        st.success(f"Brand Brain found: {brand.artist_name}")

    for err in errors:
        st.error(f"ERROR: {err}")
    for warn in warnings:
        st.warning(f"WARNING: {warn}")

    st.divider()

    # Hard gate confirmation
    st.markdown("**Hard Gate Confirmation**")
    st.caption("Both gates must be confirmed before any campaign can run.")
    theology_ok = st.checkbox(
        "I confirm this song has passed Theology Review — lyrics are scripturally sound and align with the artist's theological guardrails."
    )
    audio_ok = st.checkbox(
        "I confirm this song has passed Audio QC — the master file is clean, at correct level, and production-ready."
    )

    st.divider()

    # Campaign mode
    mode = st.selectbox("Campaign mode:", ["blitz", "standard", "growth", "ministry_push", "chart_push"])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            go_to(3)
    with col2:
        can_save = not errors and theology_ok and audio_ok
        if st.button("Save Song & Get Launch Command", type="primary", disabled=not can_save):
            # Build the SongInput dict
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
                "theology_approved": True,
                "audio_qc_approved": True,
                "audio_file_path": d.get("audio_file_path", ""),
                "artwork_file_path": d.get("artwork_file_path", ""),
                "creative_dna_reference_paths": d.get("creative_dna_reference_paths", []),
                "artist_photo_paths": d.get("artist_photo_paths", []),
                "logo_paths": d.get("logo_paths", []),
                "series_name": d.get("series_name"),
                "series_episode": d.get("series_episode"),
                "cultural_notes": d.get("cultural_notes"),
                "content_advisory": "none",
                "brand_color_primary": brand.creative_dna.color_palette.get("primary", "#2D1B69").split(" ")[0] if brand else "#2D1B69",
                "brand_color_secondary": brand.creative_dna.color_palette.get("secondary", "#D4A853").split(" ")[0] if brand else "#D4A853",
                "target_geography": brand.audience.get("geography_priority", []) if brand else [],
                "target_audience_age": "18-45",
                "target_faith_background": "Christian -- all denominations",
                "_internal_notes": d.get("internal_notes", ""),
            }

            # Remove None values
            song_data = {k: v for k, v in song_data.items() if v is not None}

            # Save to disk
            song_filename = re.sub(r"[^a-z0-9-]", "-", d.get("title", "song").lower()) + ".json"
            song_path = SONGS_DIR / song_filename
            song_path.write_text(
                json.dumps(song_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            st.session_state.wizard_data["song_file"] = str(song_path)
            st.session_state.wizard_data["mode"] = mode

            st.success(f"Song file saved: data/songs/{song_filename}")

    # Show launch command if song was saved
    if st.session_state.wizard_data.get("song_file"):
        song_file_rel = Path(st.session_state.wizard_data["song_file"]).name
        mode_val = st.session_state.wizard_data.get("mode", "blitz")

        st.divider()
        st.markdown("### Ready to launch")
        st.markdown("Run this command from the `v2/` directory:")
        st.code(f'python main.py --song data/songs/{song_file_rel} --mode {mode_val}', language="bash")
        st.markdown("Then open the Approval Queue:")
        st.code("python -m streamlit run approval/app.py", language="bash")

        with st.expander("View generated song JSON", expanded=False):
            song_path = st.session_state.wizard_data["song_file"]
            st.json(json.loads(Path(song_path).read_text(encoding="utf-8")))

        if st.button("Start a new project"):
            st.session_state.step = 0
            st.session_state.wizard_data = {}
            st.rerun()
