"""MusicWorks™ V7 Phase 3 — Brand Brain Evolution: honest campaign history.

Completes infrastructure that already existed in this codebase but was never
wired up: brand_brain/models.py's CampaignMemory and
brand_brain/artist_library.py's add_campaign_memory() were built in an
earlier sprint, and brand_brain/brain_loader.py already renders
campaign_history into every agent's prompt context — but nothing in the app
ever actually called add_campaign_memory. This module is that real trigger.

Every field is sourced from data that genuinely exists (campaign_store,
brief_store, review_store, production_queue) or left honestly empty —
never fabricated to simulate "learning" from what may be a single
completed campaign. best_platform in particular stays empty: there is no
real analytics/audience pipeline in this product yet, and claiming a "best"
platform without real performance data would be exactly the fake success
the Constitution forbids.
"""
from execution import campaign_store, brief_store, review_store, production_queue
from execution.review_dependencies import REVIEWER_LABELS

_APPROVED_STATUSES = ("approved", "scheduled", "published")
_CAPTION_JOB_TYPES = ("instagram_reel", "tiktok", "youtube_short", "facebook_reel")


def record_completion(artist_id: str, campaign_id: str) -> bool:
    """Called when a campaign completes (Campaign Operations' Stop action in
    ui/pages/media_blitz.py). Builds a CampaignMemory from real data and
    appends it to the artist's Brand Brain — every future campaign's agents
    see it automatically via brand_brain.brain_loader.load_context(), no
    per-agent wiring needed (Principle 8: future departments consume it
    naturally)."""
    from brand_brain.artist_library import add_campaign_memory

    campaign = campaign_store.get_campaign(artist_id, campaign_id)
    if not campaign:
        return False

    brief_version = brief_store.get_current(artist_id, campaign_id)
    brief_fields = brief_version["fields"] if brief_version else {}

    reviews = review_store.get_reviews(artist_id, campaign_id)
    jobs = production_queue.list_jobs(artist_id, campaign_id=campaign_id)

    # The actual creative concepts used, straight from the Brief that shipped —
    # not a guess at what "worked," just what this campaign actually was.
    winning_hooks = [v for v in [
        brief_fields.get("campaign_theme"),
        brief_fields.get("tagline"),
        brief_fields.get("core_message"),
    ] if v]

    # What the founder actually approved -- a real signal (they chose to
    # publish it), not a fabricated performance metric.
    winning_thumbnails = [
        j["job_label"] for j in jobs
        if j.get("job_type") == "thumbnail_set" and j.get("status") in _APPROVED_STATUSES
    ]
    winning_captions = [
        j["job_label"] for j in jobs
        if j.get("job_type") in _CAPTION_JOB_TYPES and j.get("status") in _APPROVED_STATUSES
    ]

    # Every real review verdict that flagged something -- not every review,
    # only the ones that weren't a perfect match.
    imperfect_reviews = [r for r in reviews.values() if r["rating"] < 5]
    lessons_learned = [
        f"{REVIEWER_LABELS.get(r['reviewer'], r['reviewer'])} on {r['target']}: {r['verdict']}"
        for r in imperfect_reviews
    ]

    # How much the founder actually asked for changes before approving --
    # a real count from the alternative_of lineage, not an opinion.
    revision_count = sum(1 for j in jobs if j.get("alternative_of"))
    founder_revisions = (
        [f"{revision_count} asset(s) needed at least one regeneration before approval"]
        if revision_count else []
    )

    # Mechanically derived from the lowest ratings, not a new fabricated
    # opinion -- the same real verdicts, reframed forward-looking.
    recommendations = [
        f"Next time: address — {r['verdict']}" for r in reviews.values() if r["rating"] <= 3
    ]

    memory = {
        "campaign_id":        campaign_id,
        "song_title":         campaign.get("song_title", ""),
        "date":               campaign.get("completed_at") or campaign.get("updated_at", ""),
        "mode":               campaign.get("campaign_mode", ""),
        "winning_hooks":      winning_hooks,
        "winning_thumbnails": winning_thumbnails,
        "winning_captions":   winning_captions,
        "best_platform":      "",
        "lessons_learned":    lessons_learned,
        "founder_revisions":  founder_revisions,
        "recommendations":    recommendations,
    }
    return add_campaign_memory(artist_id, memory)
