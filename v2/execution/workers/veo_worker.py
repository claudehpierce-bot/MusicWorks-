"""MusicWorks™ V4 — Veo worker: AI video generation (storyboard + prompt output)."""
import os
from .base_worker import BaseWorker, WorkerResult

_VIDEO_JOB_TYPES = [
    "instagram_reel", "tiktok", "youtube_short",
    "facebook_reel", "x_video", "rumble_video",
    "spotify_canvas", "reaction",
]

_SCENE_TEMPLATES: dict[str, list[str]] = {
    "instagram_reel": [
        "SCENE 1 (0:00–0:03): Extreme close-up of hands — clasped, then slowly opening upward. Deep indigo atmosphere. Gold rim light from background. No faces visible. Text overlay fades in: 'HLANGANA'",
        "SCENE 2 (0:03–0:08): Wide shot — sunrise breaking over an open African courtyard. Silhouettes of people moving toward the light. Amapiano percussion begins. Slow zoom toward the gathering.",
        "SCENE 3 (0:08–0:15): Medium shots — individual faces in warm golden morning light. Eyes closed. Lips moving in song. Diverse representation of African and Caribbean diaspora. No choreography — authentic.",
        "SCENE 4 (0:15–0:22): Wide establishing — full congregation gathered outdoors, arms raised. Camera pulls back slowly to reveal the scale of the gathering. God rays through trees.",
        "SCENE 5 (0:22–0:28): Text card: 'Do not give up meeting together — Hebrews 10:25'. Gold text on deep indigo. Scripture fades to streaming link.",
        "SCENE 6 (0:28–0:30): Final frame — Bonfire logo mark. Song title and artist name.",
    ],
    "tiktok": [
        "SCENE 1 (0:00–0:02): Hook — text appears instantly: 'This Zulu word unlocks Hebrews 10:25'. Pronunciation shown: hla-NGA-na. Warm indigo background.",
        "SCENE 2 (0:02–0:08): Meaning reveal — word splits to show full definition in motion type. 'HLANGANA = To gather together — to become one'. Sound: Amapiano gospel pulse begins.",
        "SCENE 3 (0:08–0:18): Visual — African courtyard gathering. Sunrise. Community worship. Quick cuts timed to beat. Energy builds.",
        "SCENE 4 (0:18–0:25): Scripture drop — Hebrews 10:25 in full. 'The African Church knew this word long before the English Bible arrived.' Text animates in.",
        "SCENE 5 (0:25–0:30): CTA — 'Stream HLANGANA. Link in bio.' Logo end card.",
    ],
    "spotify_canvas": [
        "SCENE 1 (0:00–0:02): Abstract — warm gold particles rising from dark indigo. No text.",
        "SCENE 2 (0:02–0:05): Aerial view — African courtyard from above. People gathering from all directions. Slow motion.",
        "SCENE 3 (0:05–0:08): Return to particles — looping subtly. Continuous motion. Minimal. Mood-driven.",
    ],
    "youtube_short": [
        "SCENE 1 (0:00–0:03): Title card — 'What does HLANGANA mean?' White text on deep indigo. Instant hook.",
        "SCENE 2 (0:03–0:10): Word study — animated text teaching the pronunciation and meaning. Cultural context shown in subtitle.",
        "SCENE 3 (0:10–0:30): Music video highlights — 4-5 quick cuts of gathering imagery. Warm light, community, movement.",
        "SCENE 4 (0:30–0:45): Scripture — Hebrews 10:25 with the word meaning overlay. Pastoral moment.",
        "SCENE 5 (0:45–0:60): CTA — 'Full song streaming now. Devotional guide free. Links in description.' End card with logo.",
    ],
}


class VeoWorker(BaseWorker):
    key         = "veo"
    name        = "Veo"
    description = "AI video generation: Reels, Shorts, TikTok, Canvas, reaction clips"
    icon        = "🎥"
    color       = "#FF6B2B"
    provider_url = "https://labs.google/veo"
    supported_types = _VIDEO_JOB_TYPES

    @property
    def available(self) -> bool:
        return bool(os.environ.get("GOOGLE_VEO_API_KEY"))

    def estimate_time(self, job: dict) -> str:
        return "~3 min per scene" if self.available else "Manual — use Veo.google.com"

    def generate(self, job: dict, brand_context: str = "") -> WorkerResult:
        jtype = job.get("job_type", "instagram_reel")
        scenes = _SCENE_TEMPLATES.get(jtype, _SCENE_TEMPLATES["instagram_reel"])

        storyboard = f"# Veo Production Brief: {job.get('job_label', jtype)}\n\n"
        storyboard += f"**Song:** {job.get('song_title', '')}\n"
        storyboard += f"**Phase:** {job.get('phase', 'launch')}\n"
        storyboard += f"**Platform:** {job.get('platform', '')}\n\n"
        storyboard += "## Storyboard + Veo Prompts\n\n"
        for i, scene in enumerate(scenes, 1):
            storyboard += f"### Scene {i}\n{scene}\n\n"
            veo_prompt = _build_veo_prompt(scene, job)
            storyboard += f"**Veo prompt:**\n```\n{veo_prompt}\n```\n\n"
        storyboard += "---\n\n## Production Instructions\n\n"
        storyboard += "1. Open [veo.google.com](https://veo.google.com)\n"
        storyboard += "2. Generate each scene using the Veo prompt above\n"
        storyboard += "3. Download all clips\n"
        storyboard += "4. Assemble in CapCut or Canva Video using scene order above\n"
        storyboard += "5. Add music track: HLANGANA (master audio)\n"
        storyboard += "6. Export at platform-appropriate resolution and upload to Brand Vault\n\n"
        storyboard += f"**Estimated assembly time:** {self.estimate_time(job)}\n"

        return WorkerResult(
            success=True,
            output_text=storyboard,
            mock=not self.available,
            metadata={"scenes": len(scenes), "platform": job.get("platform", "")},
        )

    def build_prompt(self, job: dict, brand_context: str = "") -> str:
        return _build_veo_prompt("Gathering scene — African diaspora worship — warm golden light", job)


def _build_veo_prompt(scene_desc: str, job: dict) -> str:
    base = (
        "Cinematic gospel music video scene. "
        "Setting: authentic Southern African outdoor courtyard or gathering space. "
        "Lighting: warm golden hour, god rays, no artificial studio light. "
        "Color palette: deep indigo and warm gold. "
        "People: African and Caribbean diaspora — authentic, not stock. Natural movement. No choreography. "
        "Atmosphere: communal worship, belonging, warmth. "
        "Camera: slow push-in, steady, cinematic depth of field. "
        "NO identifiable faces in close-up. "
        f"Scene: {scene_desc[:200]}"
    )
    return base
