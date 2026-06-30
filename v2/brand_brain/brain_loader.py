"""
Brain Loader — converts an ArtistBrain into a compact context string
that is prepended to every agent's system prompt.

Design rule: every agent receives the same brain context block.
It tells the agent WHO the artist is before any task-specific instructions.
"""
from brand_brain.models import ArtistBrain
from brand_brain.artist_library import load_artist


def load_context(artist_id: str) -> str:
    """Load artist brain and return the formatted context string. Empty string if not found."""
    if not artist_id:
        return ""
    brain = load_artist(artist_id)
    if brain is None:
        return ""
    return render_context(brain)


def render_context(brain: ArtistBrain) -> str:
    """Convert ArtistBrain to the context string that agents receive."""
    dna = brain.creative_dna
    voice = brain.brand_voice
    theo = brain.theological_guardrails
    lines = [
        "=" * 60,
        f"BRAND BRAIN: {brain.artist_name}",
        "=" * 60,
        "",
        "ARTIST IDENTITY",
        f"Name: {brain.artist_name}",
        f"Tagline: {brain.tagline}",
        f"Mission: {brain.mission}",
        f"Genre: {', '.join(brain.genre)}",
        f"Heritage: {', '.join(brain.heritage)}",
        "",
        f"Bio: {brain.bio_short}",
        "",
    ]

    if brain.team_members:
        lines.append("TEAM")
        for m in brain.team_members:
            lines.append(f"  {m.get('name')} ({m.get('role')}): {m.get('personality', '')}")
        lines.append("")

    lines += [
        "CREATIVE DNA",
        f"Colors: {dna.color_palette.get('primary', '')} + {dna.color_palette.get('secondary', '')}",
        f"Lighting: {', '.join(dna.lighting)}",
        f"Environment: {', '.join(dna.environment)}",
        f"Architecture: {', '.join(dna.architecture)}",
        f"Lens: {dna.lens_style}",
        f"Camera: {dna.camera_movement}",
        f"Composition: {dna.composition}",
        f"Typography: headline={dna.typography.get('headline_font', '')} body={dna.typography.get('body_font', '')}",
        f"Visual keywords: {', '.join(dna.visual_keywords)}",
        f"Rendering keywords: {', '.join(dna.rendering_keywords)}",
        f"Emotion: {', '.join(dna.emotion)}",
        f"Energy: {', '.join(dna.energy)}",
        f"Movement style: {', '.join(dna.movement)}",
        f"Festival style: {dna.festival_style}",
        f"Church style: {dna.church_style}",
        f"Performance style: {dna.performance_style}",
    ]
    if dna.what_to_avoid:
        lines.append(f"NEVER: {', '.join(dna.what_to_avoid)}")
    lines.append("")

    lines += [
        "BRAND VOICE",
        f"Tone: {', '.join(voice.tone)}",
        f"Style: {', '.join(voice.style)}",
        f"Vocabulary the brand uses: {', '.join(voice.vocabulary)}",
        f"Scripture style: {voice.scripture_style}",
        f"CTA style: {voice.cta_style}",
    ]
    if voice.avoid:
        lines.append(f"Voice — NEVER: {', '.join(voice.avoid)}")
    if voice.platform_voice:
        lines.append("Platform voice notes:")
        for platform, note in voice.platform_voice.items():
            lines.append(f"  {platform}: {note}")
    lines.append("")

    lines += [
        "THEOLOGICAL GUARDRAILS",
        f"Theological stance: {theo.theological_stance}",
        f"Scripture accuracy: {theo.scripture_accuracy}",
    ]
    if theo.required:
        lines.append(f"Always: {', '.join(theo.required)}")
    if theo.forbidden:
        lines.append(f"Never (theological): {', '.join(theo.forbidden)}")
    lines.append("")

    if brain.brand_rules:
        lines.append("BRAND RULES (non-negotiable)")
        for rule in brain.brand_rules:
            lines.append(f"  - {rule}")
        lines.append("")

    if brain.founder_preferences:
        lines.append("FOUNDER PREFERENCES")
        for pref in brain.founder_preferences:
            lines.append(f"  - {pref}")
        lines.append("")

    if brain.campaign_history:
        lines.append("CAMPAIGN HISTORY — LESSONS LEARNED")
        for mem in brain.campaign_history[-3:]:
            lines.append(f"  Campaign: {mem.song_title} ({mem.date})")
            if mem.winning_hooks:
                lines.append(f"    Winning hooks: {'; '.join(mem.winning_hooks[:2])}")
            if mem.lessons_learned:
                for lesson in mem.lessons_learned[:3]:
                    lines.append(f"    Lesson: {lesson}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("Apply this Brand Brain to every creative decision below.")
    lines.append("Never contradict these guardrails.")
    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)
