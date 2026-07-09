"""MusicWorks™ V7 Phase 2 — the cross-department review pairing table.

Constitutional roadmap, Phase 2: departments review each other's work so the
founder receives a cohesive campaign, not disconnected assets. Two of the
Constitution's own worked examples don't correspond to anything buildable
today and are deliberately excluded, not faked:

- "Film reviews storyboards" is self-review (Film checking its own output
  before it ever leaves the department) -- already implicit in generation,
  not a cross-department pairing.
- "Artist Relations reviews scripts" cannot run -- Artist Relations has no
  real agent and produces nothing yet (execution/department_map.py always
  shows it at zero). A review pairing with no content to review would be
  exactly the fake success the Constitution forbids.

Reviewers and targets are execution/brief_dependencies.py's REGEN_GROUPS
keys, not execution/department_map.py's 4 department keys -- reviews need
to read one agent's actual current output, and REGEN_GROUPS is where that
lives. The Boardroom aggregates back up to department granularity for
display (see ui/pages/wizard.py's _render_campaign_ready).
"""

REVIEW_PAIRINGS = [
    # Creative Director checks brand cohesion across all 4 real content
    # groups -- the constitutional test: "if two pieces of a campaign could
    # have come from two different artists' releases, the Brief was not
    # followed."
    {"reviewer": "creative_director", "target": "captions", "lens": "brand cohesion"},
    {"reviewer": "creative_director", "target": "written",  "lens": "brand cohesion"},
    {"reviewer": "creative_director", "target": "video",    "lens": "brand cohesion"},
    {"reviewer": "creative_director", "target": "artwork",  "lens": "brand cohesion"},
    # Growth additionally checks message accuracy on the two groups most
    # likely to drift from what the campaign is actually supposed to say.
    {"reviewer": "growth", "target": "artwork", "lens": "message accuracy"},
    {"reviewer": "growth", "target": "video",   "lens": "message accuracy"},
]

REVIEWER_LABELS = {
    "creative_director": "Creative Director",
    "growth": "Growth & Discovery",
}


def pairing_key(reviewer: str, target: str) -> str:
    return f"{reviewer}:{target}"


def pairings_for_target(target: str) -> list[dict]:
    return [p for p in REVIEW_PAIRINGS if p["target"] == target]


def relevant_brief_fields(target: str) -> list[str]:
    """Reverse lookup of brief_dependencies.BRIEF_FIELD_REGEN_GROUPS -- which
    Brief fields actually feed this target group. Used for the mock reviewer's
    Brief-completeness signal (execution/review_agent... see agents/review_agent.py)."""
    from execution.brief_dependencies import BRIEF_FIELD_REGEN_GROUPS
    return [field for field, groups in BRIEF_FIELD_REGEN_GROUPS.items() if target in groups]
