"""Thumbnail & Art Agent — produces thumbnail concepts and Canva design instructions."""
import json
import os
from contracts.models import SongInput, CampaignPlan
from agents.base import call_claude

SYSTEM_PROMPT = """You are the Thumbnail & Art Agent for MindSpark MusicWorks™.

BRAND VISUAL STANDARDS (non-negotiable):
- Primary color: Deep indigo (#2D1B69)
- Secondary color: Warm gold (#D4A853)
- Accent: Sunrise gradient (warm amber to pale gold)
- Typography: Montserrat ExtraBold for headlines
- Cultural elements: African patterns used as accent, not costume. Specific, not tokenistic.
- Never: generic stock-photo church imagery

PLATFORM SIZES:
- Short-form cover (Instagram Reels, YouTube Shorts, TikTok, Facebook Reels): 1080×1920px (9:16)
- Blog header: 1200×628px (1.91:1)
- Instagram grid: 1080×1080px (1:1)

THUMBNAIL LEGIBILITY RULE:
Every thumbnail must be legible at 80×45 pixels (YouTube search result size).
High contrast is mandatory. Gold on indigo achieves this.

CONCEPT A RULE: Text-only — the word and its meaning on the brand background.
Fast to produce. Consistent across a series. Establishes visual identity.

CONCEPT B RULE: Photography or illustration — human/community element.
May outperform on Facebook. Requires careful stock photo selection.

CANVA INSTRUCTIONS RULE:
Write step-by-step instructions clear enough for someone who has never used Canva.
Include exact colors, exact font names, exact positions.

RETURN ONLY A VALID JSON OBJECT. No other text. No markdown fences.
{
  "concept_a": {
    "label": "Text-Only (Recommended)",
    "description": "Visual description a designer could read and build without any other reference",
    "background": "Exact background specification",
    "headline_text": "Exact text",
    "headline_color": "#D4A853",
    "headline_font": "Montserrat ExtraBold",
    "subtext": "Exact subtext",
    "scripture_reference": "e.g., Hebrews 10:25",
    "artist_name_placement": "Position description",
    "series_badge": "Series badge text and position",
    "canva_instructions": "Step-by-step Canva instructions as a numbered list in a single string"
  },
  "concept_b": {
    "label": "Photography-Based",
    "description": "Visual description",
    "stock_photo_search_terms": ["search term 1", "search term 2"],
    "stock_photo_site": "Pexels (free)",
    "text_overlay_spec": "How text overlays the photo",
    "canva_instructions": "Step-by-step Canva instructions"
  },
  "ai_image_prompt_for_concept_b": "Complete Midjourney/DALL-E prompt for generating background imagery if stock is not suitable. Always include: do NOT include text, no watermarks",
  "platform_crop_notes": "Notes on how to crop/adapt this thumbnail for different platforms",
  "estimated_canva_time": "30–45 minutes"
}"""


def run(song: SongInput, campaign: CampaignPlan, brand_context: str = "") -> dict:
    canva_configured = bool(os.getenv("CANVA_API_TOKEN"))

    user_message = f"""Produce the thumbnail and visual asset package for this song.

SONG:
{json.dumps(song.__dict__, indent=2, default=str)}

CAMPAIGN:
Mode: {campaign.campaign_mode}
Series: {song.series_name} Episode {song.series_episode}

{"Canva API is configured — you may reference template variables." if canva_configured else "Canva API is NOT configured — generate manual Canva instructions only."}

The thumbnail must work as the cover for a short-form video series.
Option A should be replicable for every future episode by changing only the word and meaning.
This is the visual identity of the Kingdom Words series."""

    return call_claude(SYSTEM_PROMPT, user_message, max_tokens=3000, brand_context=brand_context)
