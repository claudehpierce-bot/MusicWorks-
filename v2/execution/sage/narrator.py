"""MusicWorks(tm) -- Sage's narration engine.

Per SAGE_PERSONA.md: Sage never invents workflow state, progress,
approvals, department decisions, or future outcomes. Every function here
renders text from real institutional state only -- Brand Brain, the Live
Creative Brief, department_status() (execution/department_map.py, which
already refuses to fabricate ratings), and campaign_store. When real state
is missing, a moment either omits the detail honestly or returns None
entirely rather than inventing something to say.

This is the one MusicWorks-specific file in the Sage pipeline (per the
original architecture split): the moment keys and their copy are this
product's script. A future MindSpark product would supply its own
narrator.py; voice.py, history.py, and ui/sage.py are product-agnostic.

Callers get a transcript string (or None) from a single `narrate(moment,
**kwargs)` entry point -- they never string-build Sage's lines themselves.
"""


def _welcome(artist_name: str | None, draft_title: str | None, draft_step_label: str | None) -> str:
    lines = ["Welcome back to MusicWorks."]
    if draft_title and draft_step_label:
        lines.append(
            f"You have an unfinished campaign for {draft_title}"
            + (f" with {artist_name}" if artist_name else "")
            + f" — you last completed {draft_step_label}."
        )
        lines.append("I'll stay with you throughout the process, and explain why each step exists when it isn't obvious.")
    else:
        lines.append("I'll stay with you throughout the process — whenever something isn't obvious, I'll explain why we're doing it.")
    return " ".join(lines)


def _step_artist() -> str:
    return (
        "Let's begin by selecting the artist. Every campaign begins with identity — "
        "everything our departments create reflects the artist's voice."
    )


def _step_creative_master() -> str:
    return (
        "Now let's upload your Creative Master. This recording becomes the foundation every "
        "department studies — they aren't just listening for melody, they're learning emotion, "
        "pacing, atmosphere, and creative intent."
    )


def _step_lyrics() -> str:
    return (
        "The Creative Director studies your lyrics to understand message, audience, scripture, "
        "and emotional direction. Growth & Discovery also uses them to understand search language "
        "and campaign positioning."
    )


def _step_artwork() -> str:
    return (
        "Reference artwork helps our Art Department understand your visual language. "
        "These images inspire direction — they are never copied."
    )


def _step_release_info() -> str:
    return (
        "These release details anchor your campaign to where the release actually stands, "
        "so nothing our departments generate points to information that doesn't exist yet."
    )


def _draft_recovery(artist_name: str | None = None, song_title: str | None = None,
                     last_step_label: str | None = None, saved_label: str | None = None) -> str:
    # The specific facts (artist / song / step / saved time) are shown in the
    # structured recovery card right below this -- Sage's line stays the
    # short emotional reassurance so the two don't just repeat each other.
    return "Welcome back. We found an unfinished campaign — your work is safe, right where you left it."


def _creative_brief_intro() -> str:
    return (
        "This is the heart of the agency. Every department reads this Brief. "
        "Changing one sentence here changes the direction of the entire campaign."
    )


def _boardroom_intro(pending_departments: list[str]) -> str:
    if pending_departments:
        return (
            "Your departments have completed their first creative pass. "
            f"{', '.join(pending_departments)} still {'has' if len(pending_departments) == 1 else 'have'} work in progress — "
            "let's review what's ready so far."
        )
    return "Your departments have completed their first creative pass. Let's review what they built together."


def _department_moment(dept_label: str, status_line: str, rating: int | None) -> str:
    """status_line and rating come straight from department_map.department_status()
    -- real data, never invented here."""
    intro = {
        "Art Department": "These visuals reflect the emotional direction described in your Creative Brief.",
        "Film Department": "The Film Department has translated your campaign into cinematic language.",
        "Growth & Discovery": "These recommendations are designed to help the right audience discover your music naturally.",
        "Artist Relations": "Artist Relations carries your personal, on-camera presence through the campaign.",
    }.get(dept_label, f"Here's where {dept_label} stands.")
    line = f"{intro} {status_line}."
    if rating:
        line += f" Cross-department review rated this work {rating} of 5."
    return line


def _campaign_operations_ready() -> str:
    return (
        "Everything is ready. When you're comfortable with the campaign, "
        "we'll coordinate the release according to your schedule. Nothing publishes without your approval."
    )


def _campaign_completion(song_title: str | None = None) -> str:
    who = f" for {song_title}" if song_title else ""
    return (
        f"This campaign{who} is complete. Whatever you learned along the way now lives in your "
        "artist's Brand Brain, ready to make the next campaign better."
    )


_MOMENTS = {
    "welcome": _welcome,
    "step_artist": _step_artist,
    "step_creative_master": _step_creative_master,
    "step_lyrics": _step_lyrics,
    "step_artwork": _step_artwork,
    "step_release_info": _step_release_info,
    "draft_recovery": _draft_recovery,
    "creative_brief_intro": _creative_brief_intro,
    "boardroom_intro": _boardroom_intro,
    "department_moment": _department_moment,
    "campaign_operations_ready": _campaign_operations_ready,
    "campaign_completion": _campaign_completion,
}


def narrate(moment: str, **kwargs) -> str | None:
    """Render the transcript for a moment key. Returns None for an unknown
    moment key rather than raising -- a narration miss must never break a
    page; the UI simply shows no Sage line for that spot."""
    fn = _MOMENTS.get(moment)
    if fn is None:
        return None
    try:
        return fn(**kwargs)
    except TypeError:
        return None


def known_moments() -> list[str]:
    return sorted(_MOMENTS.keys())
