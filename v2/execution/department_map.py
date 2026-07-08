"""MusicWorks™ V7 — Department attribution for the Creative Boardroom.

Maps each production_queue job_type to the department that ACTUALLY produces
it today. This is deliberately NOT the same as JOB_TYPE_META's `worker` field:
instagram_reel/tiktok/youtube_short/facebook_reel/reaction are nominally
"hedra" (Artist Presence) job types, but the current wizard build path fills
them with caption TEXT from the Growth & Discovery pipeline (social_media_agent)
-- no Artist Relations agent exists yet (see the V7 Constitution, Article XIII).
Attributing them to Artist Relations here would be exactly the "fake success"
the Constitution forbids. Attribution follows the real content source, not the
job type's nominal worker.
"""
from execution.production_queue import list_jobs

DEPARTMENTS = ["art", "film", "artist_relations", "growth"]

DEPARTMENT_META = {
    "art":              {"label": "Art Department",       "icon": "🎨"},
    "film":             {"label": "Film Department",      "icon": "🎬"},
    "artist_relations": {"label": "Artist Relations",     "icon": "🎤"},
    "growth":           {"label": "Growth & Discovery",   "icon": "📈"},
}

JOB_TYPE_DEPARTMENT = {
    # Film Department — cinematic / long-form video
    "music_video": "film", "trailer": "film", "lyric_visualizer": "film",
    "cinematic_scenes": "film", "worship_background": "film",
    "youtube_video": "film", "rumble_video": "film", "spotify_canvas": "film",

    # Artist Relations — human-voice video. None of these are populated by
    # the current wizard build (no real agent exists yet) -- left mapped here
    # so the department shows an honest zero rather than being silently omitted.
    "artist_welcome": "artist_relations", "devotional": "artist_relations",
    "scripture_reflection": "artist_relations", "countdown": "artist_relations",
    "behind_scenes": "artist_relations", "x_video": "artist_relations",

    # Growth & Discovery — captions (today's real source for these 5 job_types,
    # despite their nominal "hedra" worker classification), written assets, and
    # the full growth/SEO/discovery catalog
    "instagram_reel": "growth", "tiktok": "growth", "youtube_short": "growth",
    "facebook_reel": "growth", "reaction": "growth",
    "blog": "growth", "email": "growth", "press_release": "growth",
    "church_outreach": "growth", "post_launch": "growth",
    "website_copy": "growth", "artist_story": "growth", "behind_song_article": "growth",
    "seo_title": "growth", "seo_description": "growth", "seo_keywords": "growth",
    "hashtag_set": "growth", "playlist_pitch": "growth", "playlist_target_notes": "growth",
    "genre_positioning": "growth", "similar_artist_notes": "growth", "discovery_copy": "growth",
    "artist_bio_short": "growth", "artist_bio_long": "growth",
    "x_post": "growth", "threads_post": "growth", "rumble_description": "growth",
    "community_post": "growth",

    # Art Department — graphics
    "quote_card": "art", "story_slides": "art", "thumbnail_set": "art",
    "countdown_graphic": "art", "release_announcement_graphic": "art", "campaign_poster": "art",
}


def department_status(artist_id: str, campaign_id: str) -> list[dict]:
    """Real, honest per-department status for a campaign -- no fabricated
    ratings or quality judgments (none exist yet; see the Constitution,
    Article XIII). Just what actually got made, and whether it's still
    in progress or ready to look at."""
    jobs = list_jobs(artist_id, campaign_id=campaign_id)

    counts = {d: {"total": 0, "unresolved": 0} for d in DEPARTMENTS}
    for job in jobs:
        dept = JOB_TYPE_DEPARTMENT.get(job.get("job_type"))
        if not dept:
            continue
        counts[dept]["total"] += 1
        if job.get("status") in ("pending", "queued", "generating"):
            counts[dept]["unresolved"] += 1

    result = []
    for dept in DEPARTMENTS:
        meta = DEPARTMENT_META[dept]
        total = counts[dept]["total"]
        unresolved = counts[dept]["unresolved"]
        if total == 0:
            status = "Not part of this campaign yet"
        elif unresolved > 0:
            status = "Still in progress"
        else:
            status = f"{total} piece{'s' if total != 1 else ''} ready for your review"
        result.append({
            "key": dept, "label": meta["label"], "icon": meta["icon"],
            "count": total, "status": status,
        })
    return result
