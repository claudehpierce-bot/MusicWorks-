"""MusicWorks™ V4 — ElevenLabs worker: voice narration for devotional content."""
import os
from .base_worker import BaseWorker, WorkerResult


class ElevenLabsWorker(BaseWorker):
    key         = "elevenlabs"
    name        = "ElevenLabs"
    description = "Voice narration: devotional audio guides, podcast intros, spoken scripture"
    icon        = "🔊"
    color       = "#F59E0B"
    provider_url = "https://elevenlabs.io"
    supported_types = ["behind_scenes", "church_outreach"]

    @property
    def available(self) -> bool:
        return bool(os.environ.get("ELEVENLABS_API_KEY"))

    def estimate_time(self, job: dict) -> str:
        return "~1 min" if self.available else "Not configured — add ELEVENLABS_API_KEY"

    def generate(self, job: dict, brand_context: str = "") -> WorkerResult:
        title = job.get("song_title", "the song")
        script = (
            f"[HLANGANA DEVOTIONAL AUDIO GUIDE]\n\n"
            f"This is a narrated companion to the song {title} by Fire & Flow Gospel.\n\n"
            "The word is HLANGANA. Pronounced: hla-NGA-na.\n"
            "It comes from the Zulu language and means: to gather together. To become one.\n\n"
            "Open your Bible to Hebrews, chapter ten, verse twenty-five.\n\n"
            "\"Do not give up meeting together, as some are in the habit of doing, "
            "but encouraging one another — and all the more as you see the Day approaching.\"\n\n"
            "The African Church did not need a Greek lexicon to understand this verse.\n"
            "They had HLANGANA. They lived it.\n\n"
            "This week's reflection: Where are you being called to gather? "
            "Who are you called to arrive alongside?\n\n"
            "Pray this prayer with me now...\n"
        )
        instructions = (
            "# ElevenLabs Audio Brief\n\n"
            f"**Job:** {job.get('job_label', 'Voice narration')}\n"
            f"**Song:** {title}\n\n"
            "## Voice Settings\n\n"
            "- **Voice style:** Warm, pastoral, conversational. Caribbean English with gentle authority.\n"
            "- **Pacing:** Slow and deliberate. Breathing room between thoughts.\n"
            "- **Stability:** High — consistent tone throughout.\n"
            "- **Similarity boost:** Medium — natural, not over-produced.\n\n"
            "## Script\n\n"
            f"{script}\n\n"
            "## Production Steps\n\n"
            "1. Open [elevenlabs.io](https://elevenlabs.io)\n"
            "2. Select or clone the artist voice (upload voice sample from Brand Vault)\n"
            "3. Paste the script above\n"
            "4. Apply settings above\n"
            "5. Generate and review — re-generate any lines that need adjustment\n"
            "6. Export as MP3 and upload to Brand Vault as 'Audio Guide'\n"
        )
        return WorkerResult(
            success=True, output_text=instructions, mock=not self.available,
            metadata={"script_words": len(script.split())}
        )
