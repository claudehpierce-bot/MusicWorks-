"""MusicWorks™ V7 Phase 1 — the Creative Brief's dependency graph.

Constitutional Amendment I, Principle 4: departments must explicitly declare
which Brief fields they consume, as data, not as regeneration logic scattered
through the app. This module is the ONE place that mapping lives. Adding a
6th department later (e.g. once Artist Relations gets a real agent) means
adding one entry to REGEN_GROUPS and updating this table — nothing else in
the codebase should need to change.

Regeneration granularity matches the 5 content agents 1:1, not the 4
Boardroom departments (execution/department_map.py) — "growth" alone spans
3 different agents and 28 job_types; collapsing to department level would
force an unrelated field edit to re-run all of them. See brief_store.py's
BRIEF_FIELDS for the full field list this maps.
"""

REGEN_GROUPS = {
    "captions": {"agent": "social_media_agent",    "label": "Platform Captions",     "icon": "📱"},
    "written":  {"agent": "blog_press_agent",       "label": "Blog & Press",          "icon": "✍️"},
    "video":    {"agent": "video_production_agent", "label": "Storyboard & Trailer",  "icon": "🎬"},
    "artwork":  {"agent": "thumbnail_agent",        "label": "Artwork & Thumbnails",  "icon": "🎨"},
    "growth":   {"agent": "growth_content_agent",   "label": "Growth & SEO Package",  "icon": "📈"},
}

# Curated by hand, not inferred — a founder should be able to predict what
# regenerating will touch. campaign_duration/publishing_priority map to
# nothing here: they're Campaign Operations' scheduling concerns, not
# creative-regeneration triggers (see brief_store.py's field comment).
BRIEF_FIELD_REGEN_GROUPS = {
    # Foundational — touches the whole campaign's identity.
    "campaign_theme":       ["captions", "written", "video", "artwork", "growth"],
    "scripture_emphasis":   ["captions", "written", "video", "growth"],

    # Naming / message — text-forward departments plus whatever displays it.
    "campaign_title":       ["written", "artwork", "growth", "captions"],
    "core_message":         ["captions", "written", "video", "growth"],
    "call_to_action":       ["captions", "written", "growth"],
    "tagline":               ["artwork", "captions", "growth"],

    # Audience / strategy — copy and discovery, not visuals.
    "target_audience":      ["captions", "written", "growth"],
    "campaign_goals":       ["written", "growth"],
    "artist_narrative":     ["written", "growth"],
    "platform_strategy":    ["captions", "growth"],

    # Tone / atmosphere — visual and cinematic departments.
    "emotion":               ["captions", "video", "artwork"],
    "mood":                   ["video", "artwork"],
    "story":                  ["video", "written"],

    # Pure visual direction — artwork only, occasionally video's palette.
    "visual_direction":     ["artwork", "video"],
    "colour_direction":     ["artwork"],

    # Discovery / SEO — growth only.
    "keywords":               ["growth"],
    "seo":                     ["growth"],
    "hashtags":               ["captions", "growth"],
    "playlist_direction":   ["growth"],

    # Operational — Campaign Operations, never a regeneration trigger.
    "campaign_duration":    [],
    "publishing_priority":  [],
}


def affected_groups(changed_fields: list[str]) -> list[str]:
    """The union of regen groups touched by a set of changed Brief fields,
    in REGEN_GROUPS' stable order."""
    touched = set()
    for field in changed_fields:
        touched.update(BRIEF_FIELD_REGEN_GROUPS.get(field, []))
    return [g for g in REGEN_GROUPS if g in touched]
