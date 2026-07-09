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

# Bridges this module's 4 Boardroom-display keys to
# execution/brief_dependencies.py's 5 REGEN_GROUPS keys, which is where
# Phase 2's cross-department reviews actually attach (review granularity
# matches the 5 real content agents, not the 4-department display grouping —
# see brief_dependencies.py's own docstring for why). "growth" absorbs 3
# regen groups here for the same reason it absorbs 3 agents' job_types above.
DEPARTMENT_REGEN_GROUPS = {
    "art":              ["artwork"],
    "film":              ["video"],
    "artist_relations": [],
    "growth":            ["captions", "written", "growth"],
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


def department_rating(artist_id: str, campaign_id: str, department: str) -> dict | None:
    """Real cross-department review rating for a Boardroom row (V7 Phase 2),
    aggregated across whichever of this department's underlying regen groups
    have been reviewed so far. Minimum-wins, not an average -- if any part
    of a department's work needs attention, the Boardroom surfaces that,
    not a blurred-together score. Returns None (never a fabricated rating)
    if nothing has been reviewed for this department yet."""
    from execution import review_store

    groups = DEPARTMENT_REGEN_GROUPS.get(department, [])
    if not groups:
        return None

    all_reviews = review_store.get_reviews(artist_id, campaign_id)
    relevant = [r for r in all_reviews.values() if r["target"] in groups]
    if not relevant:
        return None

    worst = min(relevant, key=lambda r: r["rating"])
    return {"rating": worst["rating"], "verdict": worst["verdict"], "reviewer": worst["reviewer"]}


def department_status(artist_id: str, campaign_id: str) -> list[dict]:
    """Real, honest per-department status for a campaign. Includes a real
    cross-department rating where Phase 2 review data exists for it;
    `rating`/`verdict` are None rather than fabricated when it doesn't
    (e.g. Artist Relations, or before the first review has run)."""
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
        rating_info = department_rating(artist_id, campaign_id, dept) if total > 0 else None
        result.append({
            "key": dept, "label": meta["label"], "icon": meta["icon"],
            "count": total, "status": status,
            "rating": rating_info["rating"] if rating_info else None,
            "verdict": rating_info["verdict"] if rating_info else None,
        })
    return result
