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

    ratings = [r["rating"] for r in reviews.values()]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None
    worst = min(reviews.values(), key=lambda r: r["rating"]) if reviews else None

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
        "avg_rating": avg_rating,
        "worst_rating": worst["rating"] if worst else None,
        "worst_verdict": worst["verdict"] if worst else None,
        "worst_target": worst["target"] if worst else None,
        "oldest_review_days": oldest_review_days,
    }
