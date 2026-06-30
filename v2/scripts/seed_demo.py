"""
scripts/seed_demo.py — Seed the MusicWorks™ demo database.

Creates the full Fire & Flow Gospel / HLANGANA blitz campaign:
  - Ensures artist + song JSON files exist on disk
  - Inserts 10 demo assets into SQLite (all READY_FOR_REVIEW)
  - Press release quote locked until founder enters their own words

Safe to call multiple times — skips if campaign already seeded.

Usage (from v2/ directory):
    python scripts/seed_demo.py
"""

import sys
import json
from pathlib import Path

V2_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(V2_DIR))

ARTIST_ID   = "fire_and_flow_gospel"
SONG_ID     = "fire-flow-hlangana-001"
CAMPAIGN_ID = "hlangana-blitz-launch-001"
RELEASE_DATE = "2026-07-03"


def seed_demo(silent: bool = False) -> bool:
    """
    Seed Fire & Flow Gospel demo data.
    Returns True if seeded, False if campaign already exists.
    """
    from execution.asset_library import AssetLibrary
    lib = AssetLibrary()

    if CAMPAIGN_ID in lib.get_all_campaign_ids():
        if not silent:
            print(f"Demo already seeded (campaign {CAMPAIGN_ID} exists). Nothing to do.")
        return False

    if not silent:
        print("Seeding Fire & Flow Gospel / HLANGANA demo data...")

    _ensure_data_files()
    _seed_extended_profile()
    _seed_assets(lib, silent)

    if not silent:
        stats = lib.get_campaign_stats(CAMPAIGN_ID)
        print(f"[ok] Seeded {stats['total']} assets for campaign: {CAMPAIGN_ID}")
        print(f"     {stats['approved']} approved | {stats['pending']} pending review")
    return True


def _ensure_data_files():
    """Write artist + song JSON if not already on disk (repo normally has them)."""
    artists_dir = V2_DIR / "data" / "artists"
    artists_dir.mkdir(parents=True, exist_ok=True)
    artist_path = artists_dir / f"{ARTIST_ID}.json"
    if not artist_path.exists():
        artist_path.write_text(
            json.dumps(_ARTIST_DATA, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    songs_dir = V2_DIR / "data" / "songs"
    songs_dir.mkdir(parents=True, exist_ok=True)
    song_path = songs_dir / "hlangana.json"
    if not song_path.exists():
        song_path.write_text(
            json.dumps(_SONG_DATA, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def _seed_extended_profile():
    """Seed Fire & Flow Gospel extended profile (cultural pillars, cities, etc.)."""
    from execution.profile_store import load_profile, save_profile
    profile = load_profile(ARTIST_ID)
    if profile.get("cultural_pillars"):
        return  # Already set

    save_profile(ARTIST_ID, {
        "cultural_pillars": [
            "Gospel mission — every lyric points to Christ",
            "Urban confidence — rap skill and lyrical depth as prophetic proclamation",
            "Youth movement — next generation of African and Caribbean believers",
            "Afro-Caribbean-American identity — the lens for all creative decisions",
            "Kingdom Words — recovering African and global language theology",
            "Diaspora bridge — music for those living between cultures",
        ],
        "cities_of_influence": [
            "New York City",
            "London",
            "Lagos",
            "Port of Spain",
            "Johannesburg",
            "Accra",
        ],
        "countries_of_influence": [
            "USA",
            "UK",
            "Nigeria",
            "Ghana",
            "Trinidad and Tobago",
            "South Africa",
            "Jamaica",
            "Barbados",
        ],
        "target_audience": (
            "Christian youth and young adults in the African and Caribbean diaspora, ages 18-35. "
            "Culturally bilingual — fluent in their heritage and in their adopted country. "
            "Faithful but not religious. Gospel-hungry but genre-curious. "
            "Looking for music that sounds like them AND sounds like God."
        ),
        "ministry_focus": (
            "Discipleship through music. "
            "Kingdom Words teaching series — recovering African and global language theology for the Church. "
            "Church community building through gathering-centered songs. "
            "Pastoral partnerships for devotional guide distribution."
        ),
        "visual_style_notes": (
            "Deep indigo and warm gold. Authentic African and Caribbean settings — never generic stock. "
            "Warm, communal, rooted in place. Festival energy (Fire persona) and intimate devotional (Flow persona). "
            "Urban confidence meets gospel mission. Both aesthetics live in the same brand."
        ),
        "notes": (
            "Rap skill and lyrical depth are central — not just worship melody but prophetic proclamation. "
            "The Afro-Caribbean-American identity is the lens through which all creative decisions flow. "
            "Africa, Trinidad & Tobago, and New York City are all present in the sound and the visual world. "
            "Never sanitize the culture for a mainstream Christian market."
        ),
    })


def _seed_assets(lib, silent: bool):
    from agents.mock_data import (
        SOCIAL_MEDIA_OUTPUT,
        BLOG_PRESS_OUTPUT,
        VIDEO_PRODUCTION_OUTPUT,
        THUMBNAIL_OUTPUT,
    )

    ig = SOCIAL_MEDIA_OUTPUT["instagram"]
    tk = SOCIAL_MEDIA_OUTPUT["tiktok"]
    yt = SOCIAL_MEDIA_OUTPUT["youtube"]
    fb = SOCIAL_MEDIA_OUTPUT["facebook"]
    bp = BLOG_PRESS_OUTPUT["blog_post"]
    pr = BLOG_PRESS_OUTPUT["press_release"]
    cb = BLOG_PRESS_OUTPUT["church_blurb"]
    vp = VIDEO_PRODUCTION_OUTPUT
    th = THUMBNAIL_OUTPUT

    # 1 — Instagram caption
    _store(lib, "caption_instagram", "Instagram Reels caption — HLANGANA launch",
        f"{ig['caption']}\n\n{' '.join(ig['hashtags'])}\n\n"
        f"📌 Pinned comment:\n{ig['pinned_comment']}\n\n"
        f"⏰ Recommended post time: {ig['posting_time_recommendation']}\n"
        f"Rationale: {ig['posting_time_rationale']}",
        "caption_instagram.txt", ["instagram"])

    # 2 — TikTok caption
    _store(lib, "caption_tiktok", "TikTok caption — HLANGANA launch",
        f"{tk['caption']}\n\n{' '.join(tk['hashtags'])}\n\n"
        f"💬 First comment:\n{tk['first_comment']}\n\n"
        f"⏰ Recommended post time: {tk['posting_time_recommendation']}\n"
        f"Rationale: {tk['posting_time_rationale']}",
        "caption_tiktok.txt", ["tiktok"])

    # 3 — YouTube caption
    _store(lib, "caption_youtube", "YouTube Shorts title + description — HLANGANA launch",
        f"TITLE:\n{yt['title']}\n\nDESCRIPTION:\n{yt['description']}\n\n"
        f"{' '.join(yt['hashtags'])}\n\n"
        f"⏰ Recommended post time: {yt['posting_time_recommendation']}\n"
        f"Rationale: {yt['posting_time_rationale']}",
        "caption_youtube.txt", ["youtube"])

    # 4 — Facebook caption
    _store(lib, "caption_facebook", "Facebook Reels caption — HLANGANA launch",
        f"{fb['caption']}\n\n{' '.join(fb['hashtags'])}\n\n"
        f"⏰ Recommended post time: {fb['posting_time_recommendation']}\n"
        f"Rationale: {fb['posting_time_rationale']}",
        "caption_facebook.txt", ["facebook"])

    # 5 — Blog post
    _store(lib, "blog_post",
        f"Blog post — {bp['title']}",
        f"# {bp['title']}\n\n*{bp['meta_description']}*\n\n---\n\n{bp['content']}",
        "blog_post.md", ["website"])

    # 6 — Press release (quote locked — requires founder input)
    pr_content = _format_press_release(pr)
    lib.store_text_asset(
        CAMPAIGN_ID, SONG_ID, "press_release",
        "Press release — HLANGANA / Becoming Vol. 1 launch",
        pr_content,
        "press_release.md",
        platform_targets=["media_outreach"],
        requires_founder_input=True,
    )

    # 7 — Church blurb
    _store(lib, "church_blurb", "Church outreach blurb — pastoral email",
        cb["content"], "church_blurb.txt", ["church_outreach"])

    # 8 — Video storyboard + Veo prompts
    shots = "\n\n".join(
        f"**{s['timecode']} — {s['label']}**\n"
        f"Visual: {s['visual']}\n"
        f"Audio: {s['audio']}\n"
        f"On-screen text: {s['on_screen_text']}"
        + (f"\nNotes: {s['notes']}" if s.get("notes") else "")
        for s in vp["storyboard"]
    )
    veo = "\n\n".join(
        f"**Clip {c['clip_number']} — {c['label']}** ({c['timecode_in_video']}, {c['duration_seconds']}s)\n"
        f"Prompt: {c['veo_prompt']}\n"
        f"Style notes: {c['style_notes']}"
        for c in vp["veo_job_plan"]
    )
    _store(lib, "video_package",
        "Video storyboard + Veo prompts — HLANGANA Kingdom Word Short #001",
        f"# HLANGANA — Video Production Package\n\n"
        f"**Concept:** {vp['concept_statement']}\n\n"
        f"---\n\n## Storyboard\n\n{shots}\n\n"
        f"---\n\n## Veo Clip Prompts\n\n{veo}\n\n"
        f"---\n\n## Production Notes\n\n{vp['production_notes_human']}\n\n"
        f"**Estimated production time:** {vp['estimated_production_time']}",
        "video_storyboard.md",
        ["instagram_reels", "youtube_shorts", "tiktok", "facebook_reels"])

    # 9 — Thumbnail concept A
    ta = th["concept_a"]
    _store(lib, "thumbnail_concept",
        f"Thumbnail concept A — {ta['label']}",
        f"# Thumbnail Concept A — {ta['label']}\n\n"
        f"**Description:** {ta['description']}\n\n"
        f"**Background:** {ta['background']}\n"
        f"**Headline:** {ta['headline_text']} ({ta['headline_color']}, {ta['headline_font']})\n"
        f"**Subtext:** {ta['subtext']} ({ta['subtext_color']})\n"
        f"**Scripture reference:** {ta['scripture_reference']}\n"
        f"**Series badge:** {ta['series_badge']}\n"
        f"**Artist credit:** {ta['artist_name_placement']}\n\n"
        f"---\n\n## Canva Instructions\n\n{ta['canva_instructions']}\n\n"
        f"**Estimated time:** {th['estimated_canva_time']}\n\n"
        f"---\n\n## Crop Notes\n\n{th['platform_crop_notes']}",
        "thumbnail_concept_a.md",
        ["instagram", "youtube", "tiktok", "facebook"])

    # 10 — Thumbnail concept B
    tb = th["concept_b"]
    stock_terms = "\n".join(f"- {t}" for t in tb["stock_photo_search_terms"])
    _store(lib, "thumbnail_concept",
        f"Thumbnail concept B — {tb['label']}",
        f"# Thumbnail Concept B — {tb['label']}\n\n"
        f"**Description:** {tb['description']}\n\n"
        f"**Text overlay spec:** {tb['text_overlay_spec']}\n\n"
        f"**AI image prompt:**\n> {th['ai_image_prompt_for_concept_b']}\n\n"
        f"**Stock photo search terms:**\n{stock_terms}\n\n"
        f"**Stock photo site:** {tb['stock_photo_site']}\n\n"
        f"---\n\n## Canva Instructions\n\n{tb['canva_instructions']}\n\n"
        f"**Estimated time:** {th['estimated_canva_time']}",
        "thumbnail_concept_b.md",
        ["instagram", "youtube", "tiktok", "facebook"])

    if not silent:
        print("  Assets seeded:")
        for label in [
            "caption_instagram", "caption_tiktok", "caption_youtube", "caption_facebook",
            "blog_post", "press_release [quote locked]", "church_blurb",
            "video_package", "thumbnail_concept A", "thumbnail_concept B",
        ]:
            print(f"    [ok] {label}")


def _store(lib, asset_type, description, content, file_name, platforms):
    lib.store_text_asset(
        CAMPAIGN_ID, SONG_ID, asset_type, description, content,
        file_name, platform_targets=platforms,
    )


def _format_press_release(pr: dict) -> str:
    return (
        f"# {pr['headline']}\n\n"
        f"**{pr['dateline']}** — {pr['body']}\n\n"
        f"**⚠ DRAFT QUOTE — REPLACE WITH YOUR OWN WORDS:**\n"
        f"> {pr['founder_quote_draft']}\n\n"
        f"---\n\n"
        f"**About Fire & Flow Gospel**\n{pr['boilerplate_fire_and_flow']}\n\n"
        f"**About MindSpark MusicWorks™**\n{pr['boilerplate_musicworks']}\n\n"
        f"**Media Contact**\n{pr['contact_placeholder']}\n"
    )


# ── Minimal fallback data (used only if JSON files are absent from the repo) ──

_ARTIST_DATA = {
    "artist_id": "fire_and_flow_gospel",
    "artist_name": "Fire & Flow Gospel",
    "display_name": "Fire & Flow Gospel",
    "tagline": "The sound of the African and Caribbean diaspora encountering the living God.",
    "mission": "To create gospel music that bridges African and Caribbean cultural languages with scripture.",
    "bio_short": "Independent Afro-Gospel / Amapiano Gospel artist. Debut album: Becoming Vol. 1 (July 2026).",
    "genre": ["Afro-Gospel", "Amapiano Gospel", "Sgija Gospel", "Afrobeats Gospel"],
    "heritage": ["Trinidadian", "African Diaspora"],
    "team_members": [],
    "creative_dna": {
        "lighting": ["Warm golden tones — sunrise and early morning preferred"],
        "color_palette": {
            "primary": "#2D1B69 (deep indigo)",
            "secondary": "#D4A853 (warm gold)",
            "avoid": "Cold blues, grey tones, neon",
        },
        "architecture": ["Authentic Southern African courtyard"],
        "typography": ["Montserrat ExtraBold for headlines"],
        "motion": ["Slow, deliberate camera movement"],
    },
    "brand_voice": {
        "tone": ["devotional", "culturally rooted", "clear"],
        "avoid": ["hype language", "generic Christian phrases"],
    },
    "theological_guardrails": {
        "required": ["scripture anchor in every asset"],
        "prohibited": ["prosperity gospel framing"],
    },
    "campaign_history": [],
    "created_at": "2026-06-01T00:00:00+00:00",
    "updated_at": "2026-06-01T00:00:00+00:00",
}

_SONG_DATA = {
    "song_id": "fire-flow-hlangana-001",
    "artist_id": "fire_and_flow_gospel",
    "title": "HLANGANA",
    "title_meaning": "Gather Together",
    "title_language": "Zulu",
    "artist_name": "Fire & Flow Gospel",
    "album_title": "Becoming Vol. 1",
    "album_id": "becoming-vol-1",
    "release_date": RELEASE_DATE,
    "duration_seconds": 247,
    "bpm": 94,
    "key": "G Major",
    "genre": ["Afro-Gospel", "Amapiano Gospel"],
    "mood": ["Devotional", "Communal", "Hopeful"],
    "scripture_primary": "Hebrews 10:25",
    "scripture_primary_text": (
        "not giving up meeting together, as some are in the habit of doing, "
        "but encouraging one another—and all the more as you see the Day approaching."
    ),
    "scripture_supporting": ["Acts 2:42", "Psalm 122:1"],
    "themes": ["Community", "Church", "Gathering", "African Identity", "Discipleship"],
    "lyrics_approved": True,
    "theology_approved": True,
    "audio_qc_approved": True,
    "isrc": "US-XXX-26-00003",
    "content_advisory": "none",
    "series_name": "Kingdom Words",
    "series_episode": 1,
    "cultural_notes": "HLANGANA is a Zulu word. Pronunciation: H-La-Nga-Na. Active, intentional meaning — deliberate gathering.",
    "brand_color_primary": "#2D1B69",
    "brand_color_secondary": "#D4A853",
    "target_geography": ["US", "UK", "Nigeria", "Ghana", "South Africa", "Caribbean"],
    "target_audience_age": "18-45",
    "target_faith_background": "Christian — all denominations",
}


if __name__ == "__main__":
    seeded = seed_demo(silent=False)
    if not seeded:
        print("Run complete — nothing to seed.")
