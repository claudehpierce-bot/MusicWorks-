"""MusicWorks™ V7 Phase 4 — Campaign Operations: real, computed health signals.

Every number here is arithmetic over data that already exists (production_queue,
review_store) — never a prediction, never an "adaptive" adjustment. This
product has no live publishing/analytics integration, so there is no real
signal to adapt scheduling or "optimize" a campaign against yet. Building
that now would be exactly the fake success the Constitution forbids.
What IS real and honest: how much friction this specific campaign actually
had, and what real cross-department review scores it actually received.
"""
from datetime import datetime, timezone
from execution import production_queue, review_store


def compute_health(artist_id: str, campaign_id: str) -> dict:
    jobs = production_queue.list_jobs(artist_id, campaign_id=campaign_id)
    reviews = review_store.get_reviews(artist_id, campaign_id)

    total = len(jobs)
    approved = sum(1 for j in jobs if j.get("status") in ("approved", "scheduled", "published"))
    in_review = sum(1 for j in jobs if j.get("status") == "review")
    regenerated = sum(1 for j in jobs if j.get("alternative_of"))

    approval_rate = round(approved / total * 100) if total else None

    # Constitutional Integrity Patch, P0: no averaged score. Averaging
    # single-pass subjective 1-5 judgments and presenting it as "3.5/5"
    # implies a precision the underlying reviews don't carry (same reasoning
    # already applied to the Boardroom's _RATING_OBSERVATION headlines in
    # wizard.py). What's real and countable instead: how many of the
    # reviews that actually completed came back at full alignment.
    # Reviews with rating=None (a failed/incomplete review) are excluded --
    # they were never scored, not scored zero.
    scored = [r for r in reviews.values() if r.get("rating") is not None]
    reviewed_count = len(scored)
    full_alignment_count = sum(1 for r in scored if r["rating"] == 5)
    worst = min(scored, key=lambda r: r["rating"]) if scored else None

    oldest_review_days = None
    now = datetime.now(timezone.utc)
    review_ages = []
    for j in jobs:
        if j.get("status") != "review":
            continue
        try:
            created = datetime.fromisoformat(j.get("created_at", ""))
            review_ages.append((now - created).days)
        except (ValueError, TypeError):
            continue
    if review_ages:
        oldest_review_days = max(review_ages)

    return {
        "total_assets": total,
        "approved_count": approved,
        "in_review_count": in_review,
        "regenerated_count": regenerated,
        "approval_rate": approval_rate,
        "reviewed_count": reviewed_count,
        "full_alignment_count": full_alignment_count,
        "worst_rating": worst["rating"] if worst else None,
        "worst_verdict": worst["verdict"] if worst else None,
        "worst_target": worst["target"] if worst else None,
        "oldest_review_days": oldest_review_days,
    }
