"""MusicWorks™ V5.4 — Veo worker: Hero Worker #1, Cinematic Video.

Long-form storytelling: official music videos, trailers, visualizers,
cinematic scenes, worship backgrounds. When GOOGLE_VEO_API_KEY is present,
calls the real Google Veo API (via the google-genai SDK) and saves the
rendered clip to data/generated/{artist_id}/{job_id}.mp4 — Asset Review
picks it up automatically. Without a key, returns a storyboard + prompt
brief for manual production, same as before.
"""
import os
import time
from pathlib import Path
from .base_worker import BaseWorker, WorkerResult

_VIDEO_JOB_TYPES = [
    "music_video", "trailer", "lyric_visualizer", "cinematic_scenes",
    "worship_background", "youtube_video", "rumble_video", "spotify_canvas",
]

GEN_DIR = Path(__file__).parent.parent.parent / "data" / "generated"

_SCENE_TEMPLATES: dict[str, list[str]] = {
    "music_video": [
        "SCENE 1 (0:00–0:03): Extreme close-up of hands — clasped, then slowly opening upward. Deep indigo atmosphere. Gold rim light from background. No faces visible. Text overlay fades in: song title.",
        "SCENE 2 (0:03–0:08): Wide shot — sunrise breaking over an open African courtyard. Silhouettes of people moving toward the light. Amapiano percussion begins. Slow zoom toward the gathering.",
        "SCENE 3 (0:08–0:15): Medium shots — individual faces in warm golden morning light. Eyes closed. Lips moving in song. Diverse representation of African and Caribbean diaspora. No choreography — authentic.",
        "SCENE 4 (0:15–0:22): Wide establishing — full congregation gathered outdoors, arms raised. Camera pulls back slowly to reveal the scale of the gathering. God rays through trees.",
        "SCENE 5 (0:22–0:28): Text card — primary scripture reference on gold text, deep indigo background. Scripture fades to streaming link.",
        "SCENE 6 (0:28–0:30): Final frame — brand logo mark. Song title and artist name.",
    ],
    "trailer": [
        "SCENE 1 (0:00–0:02): Black frame, sound only — a single sustained vocal note rises. Text fades in: 'Something is coming.'",
        "SCENE 2 (0:02–0:06): Rapid flash-cuts — fragments of the full music video (gathering, sunrise, close-up hands) cut on the beat. High energy, quick pacing.",
        "SCENE 3 (0:06–0:10): Slow-motion hero shot — the artist or community silhouetted against the light. Title card and release date animate in.",
    ],
    "lyric_visualizer": [
        "SCENE 1 (0:00–0:02): Abstract — warm gold particles rising from dark indigo. No text yet.",
        "SCENE 2 (0:02–0:20): Lyric text syncs to vocal timing — each line fades in/out in rhythm with the song, kinetic typography, gold on indigo.",
        "SCENE 3 (looping): Particles continue in a slow, seamless loop behind the lyrics — minimal, mood-driven, never distracts from the words.",
    ],
    "cinematic_scenes": [
        "SCENE A: Aerial establishing shot — African courtyard or coastal Caribbean vista at golden hour, slow drone push-in.",
        "SCENE B: Macro detail — hands on an instrument, fabric texture, candle flame — tactile, warm-lit inserts for B-roll.",
        "SCENE C: Community in motion — walking toward a gathering point, unposed, documentary-style camera work.",
        "SCENE D: Quiet devotional moment — a single figure in prayer or reflection, soft focus background.",
    ],
    "worship_background": [
        "LOOP 1 (seamless, 0:00–0:15): Slow aerial drift over clouds at dawn, warm gold light breaking through — no cuts, ambient motion only.",
        "LOOP 2 (seamless, 0:00–0:15): Gentle particle/light rays drifting across a deep indigo gradient — designed to run behind live worship without pulling focus.",
        "LOOP 3 (seamless, 0:00–0:15): Slow-motion water or fabric movement in gold and indigo tones — meditative, non-narrative.",
    ],
    "youtube_video": [
        "SCENE 1 (0:00–0:05): Title card — the song's meaning as a question. White text on deep indigo. Instant hook.",
        "SCENE 2 (0:05–0:25): Word study — animated text teaching the pronunciation and meaning. Cultural context shown in subtitle.",
        "SCENE 3 (0:25–1:30): Extended music video footage — full narrative arc of gathering imagery, warm light, community, movement.",
        "SCENE 4 (1:30–2:00): Scripture — primary reference with the word meaning overlay. Pastoral moment.",
        "SCENE 5 (2:00–2:30): CTA — streaming and devotional guide links. End card with logo.",
    ],
    "rumble_video": [
        "SCENE 1 (0:00–0:10): Full-length narrative open — same as YouTube long-form: title card, hook, cultural context.",
        "SCENE 2 (0:10–2:30): Complete music video content assembled for a long-form platform audience, no time cuts.",
    ],
    "spotify_canvas": [
        "SCENE 1 (0:00–0:02): Abstract — warm gold particles rising from dark indigo. No text.",
        "SCENE 2 (0:02–0:05): Aerial view — African courtyard from above. People gathering from all directions. Slow motion.",
        "SCENE 3 (0:05–0:08): Return to particles — looping subtly. Continuous motion. Minimal. Mood-driven.",
    ],
}


class VeoWorker(BaseWorker):
    key         = "veo"
    name        = "Veo"
    description = "Cinematic AI video: music videos, trailers, visualizers, worship backgrounds"
    icon        = "🎬"
    color       = "#FF6B2B"
    provider_url = "https://labs.google/veo"
    supported_types = _VIDEO_JOB_TYPES

    @property
    def available(self) -> bool:
        return bool(os.environ.get("GOOGLE_VEO_API_KEY"))

    def estimate_time(self, job: dict) -> str:
        return "~2-6 min per clip" if self.available else "Manual — use Veo.google.com"

    def generate(self, job: dict, brand_context: str = "") -> WorkerResult:
        if not self.available:
            return self._mock(job)
        return self._live(job, brand_context)

    # ── Mock / manual-production path ───────────────────────────────────────

    def _mock(self, job: dict) -> WorkerResult:
        jtype = job.get("job_type", "music_video")
        scenes = _SCENE_TEMPLATES.get(jtype, _SCENE_TEMPLATES["cinematic_scenes"])

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
        storyboard += "5. Add the Creative Master audio track\n"
        storyboard += "6. Export at platform-appropriate resolution and upload to Brand Vault\n\n"
        storyboard += f"**Estimated assembly time:** {self.estimate_time(job)}\n"

        return WorkerResult(
            success=True,
            output_text=storyboard,
            mock=True,
            metadata={"scenes": len(scenes), "platform": job.get("platform", "")},
        )

    # ── Live Google Veo API path ─────────────────────────────────────────────

    def _live(self, job: dict, brand_context: str) -> WorkerResult:
        try:
            from google import genai

            jtype = job.get("job_type", "music_video")
            scenes = _SCENE_TEMPLATES.get(jtype, _SCENE_TEMPLATES["cinematic_scenes"])
            prompt = _build_veo_prompt(scenes[0], job, brand_context)

            client = genai.Client(api_key=os.environ["GOOGLE_VEO_API_KEY"])
            operation = client.models.generate_videos(
                model="veo-3.0-generate-001",
                prompt=prompt,
            )

            poll_seconds = 10
            max_wait_seconds = 600
            waited = 0
            while not operation.done and waited < max_wait_seconds:
                time.sleep(poll_seconds)
                waited += poll_seconds
                operation = client.operations.get(operation)

            if not operation.done:
                return WorkerResult(success=False, error="Veo generation timed out after 10 minutes.")

            generated = operation.response.generated_videos
            if not generated:
                return WorkerResult(success=False, error="Veo returned no video output.")

            artist_id = job.get("artist_id", "")
            job_id = job.get("job_id", "")
            out_dir = GEN_DIR / artist_id
            out_dir.mkdir(parents=True, exist_ok=True)
            mp4_path = out_dir / f"{job_id}.mp4"

            client.files.download(file=generated[0].video)
            generated[0].video.save(str(mp4_path))

            summary = (
                f"# Veo Cinematic Video: {job.get('job_label', jtype)}\n\n"
                f"**Song:** {job.get('song_title', '')}\n"
                f"**Rendered via:** Google Veo (veo-3.0-generate-001)\n"
                f"**Prompt used:**\n```\n{prompt}\n```\n"
            )

            return WorkerResult(
                success=True,
                output_text=summary,
                output_files=[str(mp4_path)],
                prompt_used=prompt,
                mock=False,
                metadata={"model": "veo-3.0-generate-001", "wait_seconds": waited},
            )
        except Exception as e:
            return WorkerResult(success=False, error=str(e))

    def build_prompt(self, job: dict, brand_context: str = "") -> str:
        jtype = job.get("job_type", "music_video")
        scenes = _SCENE_TEMPLATES.get(jtype, _SCENE_TEMPLATES["cinematic_scenes"])
        return _build_veo_prompt(scenes[0], job, brand_context)


def _build_veo_prompt(scene_desc: str, job: dict, brand_context: str = "") -> str:
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
    if brand_context:
        base += f"\nBrand context: {brand_context[:300]}"
    return base
