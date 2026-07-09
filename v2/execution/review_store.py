"""MusicWorks™ V7 Phase 2 — persisted cross-department review results.

Not versioned like the Live Creative Brief: a review is a snapshot of "does
the CURRENTLY LIVE output hold up," not a history to compare or restore.
Each pairing (execution/review_dependencies.REVIEW_PAIRINGS) gets overwritten
the next time it's re-run.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR    = Path(__file__).parent.parent / "data"
REVIEWS_DIR = DATA_DIR / "reviews"


def _path(artist_id: str) -> Path:
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    return REVIEWS_DIR / f"{artist_id}.json"


def _load_all(artist_id: str) -> dict:
    """{campaign_id: {"reviewer:target": {rating, verdict, reviewed_at, live_job_ids}}}"""
    p = _path(artist_id)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_all(artist_id: str, data: dict) -> None:
    _path(artist_id).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def save_review(
    artist_id: str, campaign_id: str, reviewer: str, target: str,
    rating: int, verdict: str, live_job_ids: list[str],
) -> None:
    from execution.review_dependencies import pairing_key

    all_data = _load_all(artist_id)
    campaign_reviews = all_data.setdefault(campaign_id, {})
    campaign_reviews[pairing_key(reviewer, target)] = {
        "reviewer": reviewer,
        "target": target,
        "rating": rating,
        "verdict": verdict,
        "live_job_ids": live_job_ids,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_all(artist_id, all_data)


def get_reviews(artist_id: str, campaign_id: str) -> dict:
    """All current reviews for a campaign, keyed by 'reviewer:target'."""
    return _load_all(artist_id).get(campaign_id, {})


def get_reviews_for_target(artist_id: str, campaign_id: str, target: str) -> list[dict]:
    return [r for r in get_reviews(artist_id, campaign_id).values() if r["target"] == target]
