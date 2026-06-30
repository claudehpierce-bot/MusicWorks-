"""MusicWorks™ V4 — Hedra worker: AI avatar video (behind-the-scenes, devotional talking head)."""
import os
from .base_worker import BaseWorker, WorkerResult


class HedraWorker(BaseWorker):
    key         = "hedra"
    name        = "Hedra"
    description = "AI avatar: talking-head devotional content without full video production"
    icon        = "🎙️"
    color       = "#9B89D4"
    provider_url = "https://www.hedra.com"
    supported_types = ["behind_scenes", "reaction"]

    @property
    def available(self) -> bool:
        return bool(os.environ.get("HEDRA_API_KEY"))

    def estimate_time(self, job: dict) -> str:
        return "~2 min" if self.available else "Not configured — add HEDRA_API_KEY"

    def generate(self, job: dict, brand_context: str = "") -> WorkerResult:
        jtype = job.get("job_type", "behind_scenes")
        script = self._build_script(jtype, job)
        instructions = (
            f"# Hedra Production Brief: {job.get('job_label', jtype)}\n\n"
            f"**Song:** {job.get('song_title', '')}\n"
            f"**Phase:** {job.get('phase', 'launch')}\n\n"
            "## Script\n\n"
            f"{script}\n\n"
            "## Hedra Setup Instructions\n\n"
            "1. Open [hedra.com](https://www.hedra.com)\n"
            "2. Upload your artist photo or approved avatar image from the Brand Vault\n"
            "3. Paste the script above into Hedra's audio/text input\n"
            "4. Select voice matching: warm, pastoral, Afro-Caribbean English\n"
            "5. Generate and preview the avatar video\n"
            "6. Download MP4 and upload to Brand Vault as 'Behind the Scenes'\n\n"
            "**Note:** Hedra avatar replaces manual camera requirement for devotional content. "
            "Use the artist's approved profile photo — not an AI-generated face.\n"
        )
        return WorkerResult(
            success=True, output_text=instructions, mock=not self.available,
            metadata={"script_words": len(script.split())}
        )

    def _build_script(self, jtype: str, job: dict) -> str:
        title = job.get("song_title", "the song")
        if jtype == "behind_scenes":
            return (
                f"I want to tell you why I wrote {title}.\n\n"
                "It started with a word I found in a Zulu dictionary at 2 AM.\n"
                "HLANGANA. To gather. To become one.\n\n"
                "I read Hebrews 10:25 again with that word in mind, and everything changed.\n"
                "The writer wasn't asking us to attend church. He was asking us to *arrive* — "
                "to show up fully, from wherever we had come from, and recognize each other as the same people.\n\n"
                "That's what this song is about. That's what the African and Caribbean Church has always known.\n\n"
                f"Stream {title} now. The link is in my bio.\n"
                "And the devotional guide is free — because community should never be paywalled."
            )
        return (
            f"Thank you. Truly.\n\n"
            f"{title} has been out for [X] days, and the messages I've received have left me speechless.\n\n"
            "You're gathering. You're playing it in small groups. You're sharing it with your pastors.\n"
            "That's exactly what it was made for.\n\n"
            "If you haven't listened yet, the link is in my bio. The devotional guide is still free.\n"
            "Come and gather."
        )
