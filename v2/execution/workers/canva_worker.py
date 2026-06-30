"""MusicWorks™ V4 — Canva worker: design briefs for static assets."""
import os
from .base_worker import BaseWorker, WorkerResult

_DESIGN_JOB_TYPES = ["quote_card", "story_slides", "thumbnail_set", "countdown"]

_SPECS: dict[str, dict] = {
    "quote_card": {
        "size": "1080 x 1080 px (square)",
        "format": "PNG or JPG",
        "tool": "Canva (desktop or web)",
        "elements": ["Background: deep indigo #2D1B69", "Quote text: white Montserrat ExtraBold, large", "Artist name: gold #D4A853 Montserrat Light", "Logo mark bottom-right: Bonfire icon"],
    },
    "story_slides": {
        "size": "1080 x 1920 px (9:16 vertical)",
        "format": "PNG sequence or MP4 for motion",
        "tool": "Canva Mobile or Desktop",
        "elements": ["Full-bleed background: African courtyard image from Brand Vault or indigo gradient", "Headline: 48pt white Montserrat ExtraBold", "Subtext: 28pt light gray Montserrat", "CTA strip at bottom: gold bar with white text", "Swipe-up prompt: 'Stream now' with arrow"],
    },
    "thumbnail_set": {
        "size": "1280 x 720 px (16:9) + 1080 x 1080 (square version)",
        "format": "PNG",
        "tool": "Canva Desktop",
        "elements": ["Background: deep indigo gradient or scene image", "Title: HLANGANA — Montserrat ExtraBold, large gold", "Subtitle: Fire & Flow Gospel — white, smaller", "Hebrews 10:25 reference in bottom corner", "Option A (text-only): word + meaning; Option B (image): scene + word overlay"],
    },
    "countdown": {
        "size": "1080 x 1920 px story + 1080 x 1080 post",
        "format": "Animated GIF or MP4 (3–5 sec loop)",
        "tool": "Canva (animated templates)",
        "elements": ["Large countdown number: centered, Montserrat ExtraBold, white", "Label: 'Days until HLANGANA' — gold", "Background: slow indigo particle animation or courtyard image", "Date stamp: release date in corner", "Logo: bottom center"],
    },
}

_MOCK_BRIEFS: dict[str, str] = {
    "quote_card": """\
## Canva Design Brief: Quote Card

**Dimensions:** 1080 x 1080 px (square)

**Quote to use:**
> "Do not give up meeting together... and all the more as you see the Day approaching."
> — Hebrews 10:25 (NIV)

**Design spec:**
- Background: solid deep indigo #2D1B69 or gradient to #1A0F42
- Quote text: white Montserrat ExtraBold, 52pt, centered, max 2 lines
- Scripture reference: gold #D4A853, 24pt Montserrat Light, below quote
- Decorative element: thin gold horizontal rule above and below text
- Artist name: bottom center, white Montserrat Light 20pt
- Bonfire logo mark: bottom-right, small

**Mood:** Devotional. Still. Weighty. Not hype.

**Canva template suggestion:** Minimalist dark quote card → replace fonts and colors to match spec.
""",

    "story_slides": """\
## Canva Design Brief: Story Slides (4-slide sequence)

**Dimensions:** 1080 x 1920 px (9:16)

**Slide 1 — Hook:**
- Background: African courtyard image (upload from Brand Vault) with dark overlay
- Text: "A word you need to know" — 60pt white Montserrat ExtraBold, centered
- Gold line accent below text

**Slide 2 — Word:**
- Background: deep indigo gradient
- Large word: "HLANGANA" — 80pt gold Montserrat ExtraBold, centered
- Pronunciation: "hla-NGA-na" — white italic, 36pt
- Meaning: "To gather together" — white light, 40pt

**Slide 3 — Scripture:**
- Background: same as slide 1 (different image crop)
- Hebrews 10:25 in full — white Montserrat, 32pt
- Scripture reference in gold

**Slide 4 — CTA:**
- Background: deep indigo
- "Stream now": gold pill button style
- Song title + artist name
- Logo mark bottom center
""",

    "thumbnail_set": """\
## Canva Design Brief: Thumbnail Set

**Dimensions:** 1280 x 720 px (YouTube/blog) + 1080 x 1080 (Square)

**Option A — Text-only (recommended for Kingdom Words series):**
- Background: deep indigo #2D1B69
- Word: "HLANGANA" — Montserrat ExtraBold, 100pt, gold #D4A853, centered
- Meaning: "Gather Together" — white, 48pt, below
- Scripture: "Hebrews 10:25" — gray, 32pt
- Artist name: bottom left, white 24pt
- Logo: bottom right

**Option B — Image + text:**
- Background: African courtyard photo (warm golden light), dark overlay (60% opacity)
- Same text layout as Option A
- Word appears to "rise" from background

**Make both versions.** Default recommendation: Option A for consistency across Kingdom Words episodes.
""",

    "countdown": """\
## Canva Design Brief: Countdown Animation

**Dimensions:** 1080 x 1920 px (story) + 1080 x 1080 (post)

**Animated sequence (3-second loop):**
Frame 1: Number fills 70% of screen — Montserrat ExtraBold, white, centered
Frame 2: Number fades slightly; text appears: "Days until HLANGANA"
Frame 3: Return to number — pulse animation

**Static background:**
- Deep indigo gradient (dark top, slightly lighter bottom)
- Subtle gold particle effect (Canva "confetti" or "sparkle" element, gold, 10% opacity)

**Text elements:**
- "[X] DAYS" — large, centered, white, ExtraBold
- "HLANGANA — [RELEASE DATE]" — gold, 28pt, below
- "Fire & Flow Gospel" — white, 20pt
- Bonfire logo: bottom center, small

**Export both sizes as animated GIF (for story) and static PNG (for feed post).**
""",
}


class CanvaWorker(BaseWorker):
    key         = "canva"
    name        = "Canva"
    description = "Design briefs for static assets: quote cards, thumbnails, story slides, countdowns"
    icon        = "🎨"
    color       = "#22C55E"
    provider_url = "https://canva.com"
    supported_types = _DESIGN_JOB_TYPES

    @property
    def available(self) -> bool:
        return bool(os.environ.get("CANVA_API_KEY"))

    def estimate_time(self, job: dict) -> str:
        return "~30 min manual design"

    def generate(self, job: dict, brand_context: str = "") -> WorkerResult:
        jtype = job.get("job_type", "quote_card")
        brief = _MOCK_BRIEFS.get(jtype, f"# Canva Design Brief: {job.get('job_label', jtype)}\n\n[Design brief for {jtype}]")
        spec = _SPECS.get(jtype, {})

        full_output = f"# Canva Design Brief: {job.get('job_label', jtype)}\n\n"
        if spec:
            full_output += f"**Size:** {spec.get('size', '')}\n"
            full_output += f"**Format:** {spec.get('format', '')}\n"
            full_output += f"**Tool:** {spec.get('tool', 'Canva')}\n\n"
            full_output += "**Required elements:**\n"
            for el in spec.get("elements", []):
                full_output += f"- {el}\n"
            full_output += "\n"
        full_output += brief

        return WorkerResult(
            success=True,
            output_text=full_output,
            mock=True,
            metadata={"size": spec.get("size", ""), "format": spec.get("format", "")},
        )
