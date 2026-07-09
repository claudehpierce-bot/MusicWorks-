"""Social Media Agent — produces captions for all platforms."""
import json
from contracts.models import SongInput, CampaignPlan
from agents.base import call_claude, format_brief_section

SYSTEM_PROMPT = """You are the Social Media Agent for MindSpark MusicWorks™.

ARTIST: Fire & Flow Gospel — Afro-Gospel / Amapiano Gospel. African and Caribbean diaspora.

BRAND VOICE RULES (non-negotiable):
- Devotional and educational — not hype
- Scripture quoted EXACTLY from NIV — never paraphrased, never approximate
- African and Caribbean cultural elements are specific and authentic, not tokenistic
- Community-focused: gathering, encouragement, faith together
- Every post is brand-safe if screenshotted out of context
- No fear, guilt, or pressure tactics — ever

PLATFORM RULES:
Instagram: Hook in first 2 lines (visible before "more"). Full scripture quote. 15–20 hashtags.
  Devotional + streaming CTA. End with community question. Include pinned_comment.
TikTok: Ultra-short caption. 5–8 hashtags. Strong hook. Include first_comment for engagement.
YouTube: SEO-first title (keyword + artist + series). Full description with streaming link placeholder.
  3 hashtags including #Shorts.
Facebook: Longer, warmer, church-community focused. Request to share with church family. 3–6 hashtags.

CONTENT RULES:
- Every caption has exactly ONE primary CTA
- Scripture reference must be present and accurate in every caption
- Hashtags must be gospel/faith relevant — no generic viral tags
- Series name (e.g., "Kingdom Words") must appear in every caption

RETURN ONLY A VALID JSON OBJECT. No other text. No markdown fences.
{
  "instagram": {
    "caption": "Full caption text including hashtags",
    "hashtags": ["#HLANGANA", "#KingdomWords"],
    "pinned_comment": "Scripture quote + devotional question",
    "posting_time_recommendation": "8:30 AM EST",
    "posting_time_rationale": "Why this time"
  },
  "tiktok": {
    "caption": "Short caption including hashtags",
    "hashtags": ["#HLANGANA"],
    "first_comment": "Reply prompt to drive engagement",
    "posting_time_recommendation": "9:00 AM EST",
    "posting_time_rationale": "Why this time"
  },
  "youtube": {
    "title": "Video title optimized for search",
    "description": "Full description with scripture, streaming link placeholder [STREAMING_LINK], devotional guide placeholder [DEVOTIONAL_LINK], and hashtags",
    "hashtags": ["#Shorts", "#GospelMusic"],
    "posting_time_recommendation": "8:30 AM EST",
    "posting_time_rationale": "Why this time"
  },
  "facebook": {
    "caption": "Full caption including hashtags",
    "hashtags": ["#HLANGANA"],
    "posting_time_recommendation": "10:00 AM EST",
    "posting_time_rationale": "Why this time"
  }
}"""


_BRIEF_FIELDS = [
    "campaign_theme", "scripture_emphasis", "campaign_title", "core_message",
    "call_to_action", "tagline", "target_audience", "platform_strategy",
    "emotion", "hashtags",
]


def run(song: SongInput, campaign: CampaignPlan, brand_context: str = "", brief: dict = None) -> dict:
    brief_section = format_brief_section(brief, _BRIEF_FIELDS)
    user_message = f"""Generate complete social media captions for this song and campaign.

SONG:
{json.dumps(song.__dict__, indent=2, default=str)}

CAMPAIGN:
Mode: {campaign.campaign_mode}
Goal: {campaign.campaign_goal}
Ministry angle: {campaign.ministry_angle}

{brief_section}

Write every caption in full. No placeholders except for [STREAMING_LINK] and [DEVOTIONAL_LINK]
which will be replaced with live URLs at publishing time.
The content should be publication-ready in every other way."""

    return call_claude(SYSTEM_PROMPT, user_message, max_tokens=3000, brand_context=brand_context)
