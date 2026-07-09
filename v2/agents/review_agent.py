"""Review Agent — one department reviewing another department's current work
against the Live Creative Brief. V7 Constitution, Phase 2 (Department
Collaboration). Reusable across every pairing in
execution/review_dependencies.py's REVIEW_PAIRINGS -- parameterized by lens
rather than needing a bespoke prompt per pairing."""
from agents.base import call_claude, format_brief_section
from execution.brief_store import BRIEF_FIELDS
from execution.review_dependencies import relevant_brief_fields

SYSTEM_PROMPT_TEMPLATE = """You are {reviewer_label}, reviewing another department's work for MindSpark MusicWorks™'s Creative Agency Operating System.

You did NOT make this work. You are checking it against the Live Creative Brief -- the single source of creative truth for this campaign -- specifically through the lens of {lens}.

Be honest, not encouraging. A 5 means this work could not be told apart from the Brief itself. A rating below 5 must come with a specific, actionable note -- never just "needs work."

RETURN ONLY A VALID JSON OBJECT. No other text. No markdown fences.
{{
  "rating": 1-5 (integer, 5 = fully matches the Brief, 1 = does not belong to this campaign at all),
  "verdict": "One specific, actionable sentence."
}}"""


def run(brief: dict, target_content: list[str], lens: str, reviewer_label: str, brand_context: str = "") -> dict:
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(reviewer_label=reviewer_label, lens=lens)
    brief_section = format_brief_section(brief, BRIEF_FIELDS)
    content_block = "\n\n---\n\n".join(target_content) if target_content else "(no content currently live for this department)"

    user_message = f"""{brief_section}

THE WORK TO REVIEW ({len(target_content)} piece(s)):
{content_block}

Rate how well this work matches the Live Creative Brief through the lens of {lens}."""

    result = call_claude(system_prompt, user_message, max_tokens=300, brand_context=brand_context)

    if result.get("parse_error"):
        return {"rating": 3, "verdict": "Review could not be completed — treated as neutral.", "parse_error": True}

    rating = result.get("rating", 3)
    try:
        rating = max(1, min(5, int(rating)))
    except (TypeError, ValueError):
        rating = 3
    return {"rating": rating, "verdict": result.get("verdict", "")}


def mock_rating(target: str, brief: dict) -> dict:
    """Deterministic mock signal — not a hash, not random. Scores by how
    complete the Brief actually is for this target's relevant fields (per
    execution/review_dependencies.relevant_brief_fields), so a thin Brief
    scores lower than a fully-fleshed-out one. Matches agents/mock_data.py's
    existing all-static, no-randomness convention, and deliberately avoids
    an "always five stars" Boardroom (V7 Phase 2 risk notes)."""
    fields = relevant_brief_fields(target)
    if not fields:
        return {"rating": 5, "verdict": "Nothing in the Brief to check this against."}

    substantive = sum(1 for f in fields if len((brief or {}).get(f, "") or "") >= 15)
    ratio = substantive / len(fields)
    rating = max(2, min(5, round(2 + ratio * 3)))

    if rating >= 5:
        verdict = "Fully matches the Brief."
    elif rating >= 4:
        verdict = "Matches the Brief well — one or two fields could be more specific."
    elif rating >= 3:
        verdict = "Generally on-brief, but several relevant Brief fields are thin."
    else:
        verdict = "Several Brief fields this work should be following are empty or too thin to guide it."
    return {"rating": rating, "verdict": verdict}
