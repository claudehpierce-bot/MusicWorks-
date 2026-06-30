"""MusicWorks™ V4.2 — Provider Registry: single source of truth for all AI providers.

Adding a new provider requires only:
  1. A new Provider entry in PROVIDERS
  2. An env var for its API key
  3. Capability tags
  Everything else (routing, UI, fallback) works automatically.
"""
from dataclasses import dataclass, field

@dataclass
class Provider:
    key:             str
    name:            str
    category:        str
    env_var:         str
    icon:            str
    color:           str
    description:     str
    capabilities:    list
    requires_api_key: bool = True   # False = subscription-only tool (no API)
    provider_url:    str = ""
    mock_available:  bool = True


PROVIDERS: list[Provider] = [

    # ── AI Writing ─────────────────────────────────────────────────────────────
    Provider("claude", "Claude", "AI Writing", "ANTHROPIC_API_KEY", "🧠", "#D4A853",
             "Long-form content: blog posts, emails, press releases, captions, church outreach",
             ["blog", "email", "captions", "press_release", "church_outreach",
              "lyric_commentary", "storytelling", "short_caption"],
             provider_url="https://claude.ai"),

    Provider("perplexity", "Perplexity", "Research", "PERPLEXITY_API_KEY", "🔍", "#20B2AA",
             "AI-powered research: trend analysis, scripture context, gospel discovery, fact checking",
             ["research", "trend_analysis", "fact_checking", "gospel_context", "artist_research"],
             provider_url="https://perplexity.ai"),

    # ── Video Generation ───────────────────────────────────────────────────────
    Provider("veo", "Google Veo", "Video Generation", "GOOGLE_VEO_API_KEY", "🎥", "#FF6B2B",
             "Cinematic AI video: Reels, Shorts, TikTok, music video scenes, Canvas",
             ["cinematic_video", "music_video", "commercial", "reel", "short_video"],
             provider_url="https://deepmind.google/technologies/veo"),

    Provider("hedra", "Hedra", "Video Generation", "HEDRA_API_KEY", "🎙️", "#9B89D4",
             "AI talking-head avatar: devotional content, presenter clips, lip-sync without camera",
             ["avatar", "lip_sync", "presenter", "devotional_video"],
             provider_url="https://www.hedra.com"),

    Provider("heygen", "HeyGen", "Video Generation", "HEYGEN_API_KEY", "🧑‍💻", "#6366F1",
             "AI avatar studio: multi-language presenter, ministry, and corporate video",
             ["avatar", "lip_sync", "presenter", "multi_language", "ministry_video"],
             provider_url="https://heygen.com"),

    # ── Image Generation ───────────────────────────────────────────────────────
    Provider("leonardo", "Leonardo AI", "Image Generation", "LEONARDO_API_KEY", "🎨", "#FF9500",
             "Hero artwork, album covers, character art, branding, illustration",
             ["character_art", "branding", "album_cover", "illustration", "hero_artwork"],
             provider_url="https://leonardo.ai"),

    Provider("google_imagen", "Google Imagen", "Image Generation", "GOOGLE_AI_API_KEY", "🔵", "#4285F4",
             "Photorealistic imagery: lifestyle photography, marketing assets, product shots",
             ["photorealism", "lifestyle", "marketing", "product", "environmental"],
             provider_url="https://ai.google.dev"),

    Provider("canva", "Canva", "Image Generation", "CANVA_API_KEY", "🖼️", "#22C55E",
             "Branded design briefs: quote cards, thumbnails, story slides, countdown graphics",
             ["quote_card", "thumbnail", "story_slide", "countdown", "branding", "template"],
             provider_url="https://canva.com"),

    # ── Video Editing ──────────────────────────────────────────────────────────
    Provider("capcut", "CapCut", "Video Editing", "CAPCUT_API_KEY", "✂️", "#FF4D6A",
             "Short-form video editing: Reels assembly, TikTok, auto-captions, transitions",
             ["short_form_editing", "reels", "tiktok_edit", "auto_caption", "transitions"],
             requires_api_key=False,
             provider_url="https://capcut.com"),

    Provider("vizard", "Vizard", "Video Editing", "VIZARD_API_KEY", "📐", "#7C3AED",
             "Video repurposing: clip extraction from long-form, auto-captioning, social clips",
             ["video_repurposing", "clip_extraction", "auto_caption", "social_clips"],
             requires_api_key=False,
             provider_url="https://vizard.ai"),

    Provider("pictory", "Pictory", "Video Editing", "PICTORY_API_KEY", "🎞️", "#EC4899",
             "Long-form repurposing: article to video, blog to reel, slideshow creation",
             ["long_form_repurposing", "article_to_video", "blog_to_reel", "slideshow"],
             requires_api_key=False,
             provider_url="https://pictory.ai"),

    # ── Voice ─────────────────────────────────────────────────────────────────
    Provider("elevenlabs", "ElevenLabs", "Voice", "ELEVENLABS_API_KEY", "🔊", "#F59E0B",
             "Voice narration: devotional audio, podcast intros, spoken scripture, voice cloning",
             ["voice_clone", "narration", "podcast", "scripture", "devotional_audio"],
             provider_url="https://elevenlabs.io"),

    # ── Publishing ────────────────────────────────────────────────────────────
    Provider("youtube",    "YouTube",    "Publishing", "YOUTUBE_API_KEY",    "▶️", "#FF0000",
             "Video publishing, YouTube Shorts, channel management",
             ["video_publish", "shorts", "community_post"],
             provider_url="https://studio.youtube.com"),

    Provider("instagram",  "Instagram",  "Publishing", "INSTAGRAM_API_KEY",  "📸", "#E1306C",
             "Reels, posts, Stories, carousel",
             ["reel_publish", "post_publish", "story"],
             provider_url="https://instagram.com"),

    Provider("facebook",   "Facebook",   "Publishing", "FACEBOOK_API_KEY",   "👥", "#1877F2",
             "Facebook Reels, long-form posts, page management",
             ["reel_publish", "post_publish", "page_manage"],
             provider_url="https://facebook.com"),

    Provider("tiktok",     "TikTok",     "Publishing", "TIKTOK_API_KEY",     "🎵", "#69C9D0",
             "TikTok video uploads, trending audio integration",
             ["video_publish", "trending"],
             provider_url="https://tiktok.com"),

    Provider("x",          "X",          "Publishing", "X_API_KEY",          "✖️", "#F0EDE8",
             "Posts, threads, video, X Spaces promotion",
             ["post_publish", "video_publish", "thread_publish"],
             provider_url="https://x.com"),

    Provider("threads",    "Threads",    "Publishing", "THREADS_API_KEY",    "🧵", "#C8C4BE",
             "Meta Threads text and media posts",
             ["post_publish"],
             provider_url="https://threads.net"),

    Provider("rumble",     "Rumble",     "Publishing", "RUMBLE_API_KEY",     "🔴", "#85C742",
             "Rumble video platform uploads",
             ["video_publish"],
             provider_url="https://rumble.com"),

    Provider("mailchimp",  "Mailchimp",  "Publishing", "MAILCHIMP_API_KEY",  "📧", "#FFE01B",
             "Email newsletter campaigns, release announcements",
             ["email_publish", "newsletter", "subscriber_blast"],
             provider_url="https://mailchimp.com"),

    Provider("beehiiv",    "Beehiiv",    "Publishing", "BEEHIIV_API_KEY",    "🐝", "#F8A100",
             "Beehiiv newsletter publishing and subscriber growth",
             ["email_publish", "newsletter", "subscriber_growth"],
             provider_url="https://beehiiv.com"),

    # ── Distribution ─────────────────────────────────────────────────────────
    Provider("distrokid", "DistroKid", "Distribution", "", "🎵", "#8B5CF6",
             "Music distribution — metadata display only, no automation",
             ["distribution", "streaming_metadata"],
             requires_api_key=False,
             mock_available=False,
             provider_url="https://distrokid.com"),
]

# ── Lookup helpers ─────────────────────────────────────────────────────────────

PROVIDER_MAP: dict[str, Provider] = {p.key: p for p in PROVIDERS}

CATEGORIES: list[str] = list(dict.fromkeys(p.category for p in PROVIDERS))


def get_provider(key: str) -> Provider | None:
    return PROVIDER_MAP.get(key)


def list_by_category(category: str) -> list[Provider]:
    return [p for p in PROVIDERS if p.category == category]


def providers_for_capability(capability: str) -> list[Provider]:
    return [p for p in PROVIDERS if capability in p.capabilities]


def is_api_key_set(key: str) -> bool:
    """True if the provider's env var or st.secrets entry is configured."""
    import os
    p = PROVIDER_MAP.get(key)
    if not p or not p.env_var:
        return False
    try:
        import streamlit as st
        if hasattr(st, "secrets") and p.env_var in st.secrets:
            return bool(st.secrets[p.env_var])
    except Exception:
        pass
    return bool(os.environ.get(p.env_var, ""))
