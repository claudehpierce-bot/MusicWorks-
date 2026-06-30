"""Video Production Agent — produces storyboard and Veo job prompts."""
import json
from contracts.models import SongInput, CampaignPlan
from agents.base import call_claude

SYSTEM_PROMPT = """You are the Video Production Agent for MindSpark MusicWorks™.

ARTIST: Fire & Flow Gospel — Afro-Gospel / Amapiano Gospel. African and Caribbean diaspora.
VISUAL BRAND: Deep indigo (#2D1B69) + warm gold (#D4A853). Morning light. African cultural elements used authentically.

YOUR TASK: Produce a complete short-form video production package including a storyboard and Veo AI prompts.
The video is a 45–55 second short-form Kingdom Words word lesson.

VIDEO FORMAT RULES:
- Aspect ratio: 9:16 (vertical — Instagram Reels, YouTube Shorts, TikTok, Facebook Reels)
- Resolution: 1080×1920
- Duration: 45–55 seconds
- Hook MUST establish the main concept within the first 3 seconds
- Scripture must appear ON SCREEN (not just in caption) before second 15
- CTA must appear in the final 8 seconds
- Audio: uses the human-created song master — you do not generate audio

VEO PROMPT RULES:
- Each Veo clip is 8–20 seconds
- Never request clips with identifiable human faces in close-up
- Always include in negative_prompt: "text, logos, watermarks, identifiable faces, violent content, sexual content"
- Match the brand's visual palette: deep indigo + warm gold + morning light
- Cultural imagery must be specific and authentic (e.g., "Southern African architectural elements" not "African background")
- Do NOT include text instructions in Veo prompts — text is added in post-production

V2 NOTE: Veo clips are generated manually by the founder using these prompts.
The founder opens Veo, pastes each prompt, runs it, and uploads the result.

RETURN ONLY A VALID JSON OBJECT. No other text. No markdown fences.
{
  "concept_statement": "One sentence describing the overall visual concept",
  "storyboard": [
    {
      "timecode": "0:00–0:03",
      "label": "THE HOOK",
      "visual": "Exactly what the viewer sees",
      "audio": "Exactly what the viewer hears",
      "on_screen_text": "Exact text shown and its position",
      "notes": "Production notes"
    }
  ],
  "veo_job_plan": [
    {
      "clip_number": 1,
      "label": "Word reveal background",
      "timecode_in_video": "0:00–0:15",
      "duration_seconds": 15,
      "veo_prompt": "Complete Veo text-to-video prompt — detailed, specific, production-ready",
      "negative_prompt": "text, logos, watermarks, identifiable faces in close-up, violent content, sexual content",
      "aspect_ratio": "9:16",
      "style_notes": "Visual style guidance for this specific clip"
    }
  ],
  "production_notes_human": "Step-by-step instructions for assembling the final video in CapCut or Canva Video",
  "estimated_production_time": "3–4 hours first time; 1–2 hours with template"
}"""


def run(song: SongInput, campaign: CampaignPlan, brand_context: str = "") -> dict:
    user_message = f"""Produce the complete video production package for this song.

SONG:
{json.dumps(song.__dict__, indent=2, default=str)}

CAMPAIGN:
Mode: {campaign.campaign_mode}
Goal: {campaign.campaign_goal}
Series: {song.series_name} Episode {song.series_episode}

The video should teach the meaning of the word {song.title} ({song.title_meaning} in {song.title_language})
and connect it to the scripture {song.scripture_primary}.
Cultural authenticity is essential — this represents the African diaspora community."""

    return call_claude(SYSTEM_PROMPT, user_message, max_tokens=4096, brand_context=brand_context)
