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

    # Constitutional Integrity Patch, P0: a failed review must never be
    # stored as a fabricated "neutral" rating -- None means "not reviewed,"
    # not "reviewed and scored 3." Callers/aggregators treat None as
    # excluded from any count or comparison, the same way department_map.py
    # already treats "no review yet" as None rather than inventing one.
    if result.get("parse_error"):
        return {"rating": None, "verdict": "Review could not be completed — try again.", "parse_error": True}

    rating = result.get("rating")
    try:
        rating = max(1, min(5, int(rating)))
    except (TypeError, ValueError):
        rating = None
    return {"rating": rating, "verdict": result.get("verdict", "")}


def mock_rating(target: str, brief: dict) -> dict:
    """Preview-mode signal, used only when no live review model is
    configured. This does NOT look at the department's actual generated
    content -- there is no Claude call in preview mode to judge it with
    (see orchestrator.py: content is fetched but never passed in here).
    It measures one real, checkable thing instead: how much of the Brief
    actually gives this department direction (per
    execution/review_dependencies.relevant_brief_fields). The verdict text
    says exactly that, on purpose (Constitutional Integrity Patch, P1) --
    it must never read as "the work matches the Brief," because no work
    was ever compared to anything here. Deterministic, not random."""
    fields = relevant_brief_fields(target)
    if not fields:
        return {"rating": None, "verdict": "Nothing in the Brief guides this department yet.", "basis": "brief_completeness"}

    substantive = sum(1 for f in fields if len((brief or {}).get(f, "") or "") >= 15)
    ratio = substantive / len(fields)
    rating = max(2, min(5, round(2 + ratio * 3)))  # kept only to rank "worst first" in department_rating()

    if substantive == len(fields):
        verdict = f"All {len(fields)} relevant Brief fields have real direction for this department."
    elif substantive > 0:
        verdict = f"{substantive} of {len(fields)} relevant Brief fields have real direction; the rest are still thin."
    else:
        verdict = f"None of the {len(fields)} relevant Brief fields have real direction yet."
    return {"rating": rating, "verdict": verdict, "basis": "brief_completeness"}
