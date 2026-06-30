"""MusicWorks™ V4.3 — Platform Profiles: editable publishing guidance per platform.

Policies are NOT hardcoded. Defaults are seeded on first access and then
stored as editable JSON in data/platform_profiles/{key}.json.
Founders can update any field as platform policies evolve.

MusicWorks does NOT guarantee compliance. This is operational guidance only.
"""
from .compliance_store import load_profile, save_profile

# ── Default profiles ──────────────────────────────────────────────────────────
# Stored in code only as seed data. Once saved to JSON, the JSON is authoritative.

_DEFAULTS: dict[str, dict] = {

    "youtube": {
        "key":   "youtube",
        "name":  "YouTube",
        "icon":  "▶️",
        "color": "#FF0000",
        "media_types": ["video", "shorts", "community_post", "thumbnail"],
        "video_lengths": {
            "long_form":    "Up to 12 hours",
            "shorts":       "Under 60 seconds",
            "optimal_reel": "7–15 seconds for highest retention",
        },
        "image_sizes": {
            "thumbnail":         "1280×720 px (16:9)",
            "channel_art":       "2560×1440 px",
            "profile_photo":     "800×800 px",
        },
        "caption_length": {"max": 5000, "recommended": 200, "unit": "characters"},
        "hashtag_guidance": "3–5 hashtags in description. First 3 appear under the title.",
        "ai_notes": (
            "Disclose AI-generated content in the video description when content is "
            "realistic and could mislead viewers. Use 'This video contains AI-generated imagery.' "
            "YouTube has an AI disclosure requirement for realistic altered content."
        ),
        "music_notes": (
            "Use YouTube Audio Library, licensed music, or original compositions. "
            "Copyrighted music will trigger Content ID. Monetization may be affected."
        ),
        "best_practices": [
            "Custom thumbnail with bold text and close-up face (if available) lifts CTR",
            "First 30 seconds must hook — algorithm rewards completion rate",
            "Chapters improve navigation and search discoverability",
            "End screen + cards boost session time",
            "Upload SRT captions for accessibility and SEO",
        ],
        "last_updated": "2026-06-30",
        "reference_links": [
            "https://support.google.com/youtube/answer/6162278",
            "https://support.google.com/youtube/answer/9440436",
        ],
    },

    "instagram": {
        "key":   "instagram",
        "name":  "Instagram",
        "icon":  "📸",
        "color": "#E1306C",
        "media_types": ["reel", "post", "story", "carousel"],
        "video_lengths": {
            "reels":      "15–90 seconds",
            "feed_video": "Up to 60 seconds",
            "stories":    "Up to 60 seconds per clip",
        },
        "image_sizes": {
            "feed_square":    "1080×1080 px (1:1)",
            "feed_portrait":  "1080×1350 px (4:5)",
            "story_reel":     "1080×1920 px (9:16)",
            "thumbnail":      "1080×1080 px",
        },
        "caption_length": {"max": 2200, "recommended": 125, "unit": "characters"},
        "hashtag_guidance": "5–10 hashtags on feed posts. 3–5 on Reels. Place in caption or first comment.",
        "ai_notes": (
            "Instagram (Meta) requires labeling 'Made with AI' for realistic AI-generated images and videos. "
            "Use Creator Studio or app settings to add AI labels. Policy evolving — check Meta guidance regularly."
        ),
        "music_notes": (
            "Use licensed music from the Instagram Music Library or cleared original compositions. "
            "Unlicensed music may result in muted audio or content removal."
        ),
        "best_practices": [
            "Reels with trending audio get algorithmic boost",
            "Optimal Reel length: 7–15 seconds for highest play-through rate",
            "First frame must be visually compelling — no black intro frames",
            "Add on-screen text for silent viewers",
            "Post at audience peak hours (check Instagram Insights)",
        ],
        "last_updated": "2026-06-30",
        "reference_links": [
            "https://help.instagram.com/303828544168782",
        ],
    },

    "facebook": {
        "key":   "facebook",
        "name":  "Facebook",
        "icon":  "👥",
        "color": "#1877F2",
        "media_types": ["reel", "post", "story", "video"],
        "video_lengths": {
            "reels":      "15–90 seconds",
            "long_form":  "Up to 4 hours",
            "stories":    "Up to 20 seconds per clip",
        },
        "image_sizes": {
            "feed":       "1200×630 px (1.91:1)",
            "square":     "1080×1080 px",
            "story_reel": "1080×1920 px (9:16)",
        },
        "caption_length": {"max": 63206, "recommended": 80, "unit": "characters"},
        "hashtag_guidance": "1–3 hashtags. Facebook hashtags have limited discovery impact compared to Instagram.",
        "ai_notes": (
            "Meta requires disclosure of AI-generated content that could mislead users. "
            "Label realistic AI content in post descriptions."
        ),
        "music_notes": (
            "Use Facebook Sound Collection or licensed music. "
            "Copyrighted music will be flagged by Rights Manager."
        ),
        "best_practices": [
            "Native Facebook video (uploaded directly) performs better than links",
            "Square and vertical formats outperform landscape on mobile",
            "Reels receive priority distribution in the algorithm",
            "Caption the first few lines — long posts get truncated",
        ],
        "last_updated": "2026-06-30",
        "reference_links": [
            "https://www.facebook.com/business/help/",
        ],
    },

    "tiktok": {
        "key":   "tiktok",
        "name":  "TikTok",
        "icon":  "🎵",
        "color": "#69C9D0",
        "media_types": ["video", "story", "photo_mode"],
        "video_lengths": {
            "default":  "15 seconds to 10 minutes",
            "optimal":  "15–60 seconds",
            "sweet_spot": "21–34 seconds for highest completion",
        },
        "image_sizes": {
            "video":      "1080×1920 px (9:16)",
            "cover":      "1080×1920 px",
        },
        "caption_length": {"max": 2200, "recommended": 150, "unit": "characters"},
        "hashtag_guidance": "3–5 hashtags. Mix niche (#gospelrap) with broad (#gospel). Use trending sounds.",
        "ai_notes": (
            "TikTok requires creators to label AI-generated content using Creator Tools. "
            "Go to Post → AI-Generated Content toggle. Failing to label may result in removal. "
            "Realistic AI faces must be disclosed — AI AIGC label required."
        ),
        "music_notes": (
            "Use TikTok's Commercial Music Library for monetizable content. "
            "Original sound performs well. Trending audio boosts discoverability. "
            "Personal accounts have broader music access than Creator/Business accounts."
        ),
        "best_practices": [
            "Hook in first 1–2 seconds — TikTok algorithm rewards watch-through",
            "On-screen text captions improve completion rate",
            "Trending audio dramatically boosts reach",
            "Post consistently — 1–3 times per day recommended for growth",
            "Engage with comments within first hour of posting",
        ],
        "last_updated": "2026-06-30",
        "reference_links": [
            "https://www.tiktok.com/creators/creator-portal/",
        ],
    },

    "x": {
        "key":   "x",
        "name":  "X",
        "icon":  "✖️",
        "color": "#F0EDE8",
        "media_types": ["post", "video", "image", "thread"],
        "video_lengths": {
            "standard": "Up to 2 minutes 20 seconds",
            "premium":  "Up to 3 hours (Premium subscribers)",
            "optimal":  "Under 30 seconds",
        },
        "image_sizes": {
            "post_image": "1200×675 px (16:9)",
            "profile":    "400×400 px",
            "banner":     "1500×500 px",
        },
        "caption_length": {"max": 280, "recommended": 200, "unit": "characters (standard)"},
        "hashtag_guidance": "1–2 hashtags maximum. Overuse reduces reach on X.",
        "ai_notes": (
            "X does not currently mandate AI labels but best practice is to disclose "
            "AI-generated images and videos in the post text."
        ),
        "music_notes": "No dedicated music library. Use original music or ensure licensing for any included audio.",
        "best_practices": [
            "Short, punchy captions perform best",
            "Video autoplay drives engagement — no caption needed for hook",
            "Thread structure works well for devotional storytelling",
            "Post during trending conversations for discovery",
        ],
        "last_updated": "2026-06-30",
        "reference_links": [
            "https://help.twitter.com/en/using-x/x-videos",
        ],
    },

    "threads": {
        "key":   "threads",
        "name":  "Threads",
        "icon":  "🧵",
        "color": "#C8C4BE",
        "media_types": ["post", "image", "video"],
        "video_lengths": {
            "standard": "Up to 5 minutes",
        },
        "image_sizes": {
            "post": "1080×1080 px (recommended)",
        },
        "caption_length": {"max": 500, "recommended": 200, "unit": "characters"},
        "hashtag_guidance": "Threads does not use hashtags for discovery. Focus on text content quality.",
        "ai_notes": (
            "Meta AI disclosure policy applies to Threads. "
            "Label realistic AI-generated images and videos."
        ),
        "music_notes": "No music library. Post audio is attached as video audio only.",
        "best_practices": [
            "Conversational, authentic tone works best on Threads",
            "Short devotional thoughts and questions drive engagement",
            "Cross-post from Instagram Reels for reach",
            "Community interaction is the primary growth lever",
        ],
        "last_updated": "2026-06-30",
        "reference_links": [
            "https://help.instagram.com/179980294969769",
        ],
    },

    "rumble": {
        "key":   "rumble",
        "name":  "Rumble",
        "icon":  "🔴",
        "color": "#85C742",
        "media_types": ["video"],
        "video_lengths": {
            "standard": "No hard limit",
        },
        "image_sizes": {
            "thumbnail": "1280×720 px (16:9)",
        },
        "caption_length": {"max": 5000, "recommended": 300, "unit": "characters"},
        "hashtag_guidance": "Use descriptive tags in the video tag field. No hashtag convention.",
        "ai_notes": "Rumble has no formal AI disclosure requirement. Disclose voluntarily in description.",
        "music_notes": "Use original or licensed music. No built-in music library.",
        "best_practices": [
            "Upload original video (not repurposed YouTube content) for better ranking",
            "Fill all metadata fields — title, description, tags, category",
            "Gospel and faith content is a growing category on Rumble",
        ],
        "last_updated": "2026-06-30",
        "reference_links": [
            "https://rumble.com/help",
        ],
    },

    "website": {
        "key":   "website",
        "name":  "Website / Blog",
        "icon":  "🌐",
        "color": "#6A6460",
        "media_types": ["blog_post", "video_embed", "image", "audio"],
        "video_lengths": {"standard": "No limit — host via YouTube or Vimeo embed"},
        "image_sizes": {
            "hero":     "1920×1080 px",
            "featured": "1200×630 px",
            "inline":   "800×600 px",
        },
        "caption_length": {"max": 0, "recommended": 0, "unit": "no limit — long-form recommended"},
        "hashtag_guidance": "Not applicable. Use SEO keywords in headings and meta descriptions instead.",
        "ai_notes": "Disclose AI assistance in the author note or at the end of the article.",
        "music_notes": "Embedded audio players should use properly licensed music.",
        "best_practices": [
            "Long-form blog posts (1500–3000 words) rank better in search",
            "Embed Reels and YouTube videos for time-on-page",
            "Include devotional guide PDF as a lead magnet",
            "Add structured data for articles and music for rich results",
        ],
        "last_updated": "2026-06-30",
        "reference_links": [],
    },

    "newsletter": {
        "key":   "newsletter",
        "name":  "Newsletter",
        "icon":  "📧",
        "color": "#FFE01B",
        "media_types": ["email", "text", "image"],
        "video_lengths": {"note": "Video does not auto-play in email — use animated GIF or thumbnail link to video"},
        "image_sizes": {
            "header":    "600×200 px",
            "inline":    "600×400 px",
            "thumbnail": "300×200 px",
        },
        "caption_length": {"max": 0, "recommended": 0, "unit": "no hard limit — keep subject line under 50 chars"},
        "hashtag_guidance": "Not applicable for email.",
        "ai_notes": "Disclose AI assistance in a footer note if used for content creation.",
        "music_notes": "Link to streaming platforms instead of embedding audio.",
        "best_practices": [
            "Subject line is everything — A/B test if possible",
            "Preview text (preheader) is the second most-read element",
            "Mobile-first layout — 600px max width",
            "Single clear CTA per email",
            "Send on Tuesdays or Thursdays, 9–11 AM local time",
        ],
        "last_updated": "2026-06-30",
        "reference_links": [],
    },
}

PLATFORM_KEYS  = list(_DEFAULTS.keys())
PLATFORM_NAMES = {k: v["name"] for k, v in _DEFAULTS.items()}
PLATFORM_ICONS = {k: v["icon"] for k, v in _DEFAULTS.items()}


# ── Access helpers ─────────────────────────────────────────────────────────────

def get_profile(platform_key: str) -> dict:
    """Return stored profile or fall back to default."""
    stored = load_profile(platform_key)
    if stored:
        return stored
    # Seed the default to disk on first access
    default = _DEFAULTS.get(platform_key, {})
    if default:
        save_profile(platform_key, default)
    return default


def update_profile(platform_key: str, updates: dict) -> None:
    """Merge updates into the existing profile and save."""
    profile = get_profile(platform_key)
    profile.update(updates)
    from datetime import date
    profile["last_updated"] = str(date.today())
    save_profile(platform_key, profile)


def list_platform_profiles() -> list[dict]:
    return [get_profile(k) for k in PLATFORM_KEYS]
