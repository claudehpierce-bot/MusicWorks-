"""MusicWorks™ V4.3 — Risk Engine: dynamic release risk assessment.

Risk scores are guidance only. Nothing is blocked automatically.
Founder always makes the final publishing decision.
MusicWorks does NOT guarantee compliance or provide legal advice.
"""
from .release_readiness import compute_release_score, STATUS_READY, STATUS_BLOCKED
from .copyright_checklist import checklist_summary
from .ai_usage_tracker import ai_usage_summary

RISK_GREEN  = "green"
RISK_YELLOW = "yellow"
RISK_RED    = "red"

RISK_COLORS = {RISK_GREEN: "#22C55E", RISK_YELLOW: "#F59E0B", RISK_RED: "#EF4444"}
RISK_ICONS  = {RISK_GREEN: "🟢", RISK_YELLOW: "🟡", RISK_RED: "🔴"}
RISK_LABELS = {RISK_GREEN: "Low Risk", RISK_YELLOW: "Review Recommended", RISK_RED: "Attention Needed"}


def _level(score: int) -> str:
    if score >= 80:
        return RISK_GREEN
    if score >= 50:
        return RISK_YELLOW
    return RISK_RED


# ── Risk Dimensions ───────────────────────────────────────────────────────────

def _copyright_risk(artist_id: str, song_id: str) -> dict:
    summary = checklist_summary(artist_id, song_id)
    pct     = summary["pct"]
    unres   = summary["unresolved"]
    score   = max(0, pct - (unres * 20))
    note    = (
        f"{summary['resolved']}/{summary['total']} items confirmed."
        + (f" {unres} unresolved item(s) need attention." if unres else "")
        + (" Complete the Copyright Checklist." if pct < 50 else "")
    )
    return {"key": "copyright", "label": "Copyright Review", "icon": "©️",
            "score": score, "level": _level(score), "note": note}


def _platform_risk(artist_id: str, song_id: str) -> dict:
    result  = compute_release_score(artist_id, song_id)
    sections = result.get("sections", {})
    platform_status = sections.get("platform_review", "not_checked")
    score = {"ready": 100, "needs_review": 50, "blocked": 0, "not_checked": 40}.get(platform_status, 40)
    note  = (
        "Platform community guidelines reviewed and confirmed."
        if platform_status == STATUS_READY
        else "Review the Platform Review section in Release Readiness."
    )
    return {"key": "platform", "label": "Platform Readiness", "icon": "📱",
            "score": score, "level": _level(score), "note": note}


def _ai_transparency_risk(artist_id: str, song_id: str) -> dict:
    summary  = ai_usage_summary(artist_id, song_id)
    total    = summary.get("total", 0)
    approved = summary.get("approved", 0)
    pct      = summary.get("approval_pct", 0) if total > 0 else 100
    score    = pct if total > 0 else 85   # no AI assets = low risk
    note     = (
        f"{approved}/{total} AI-generated assets approved by founder."
        if total > 0
        else "No AI-generated assets found — or none generated yet."
    )
    return {"key": "ai_transparency", "label": "AI Transparency", "icon": "🤖",
            "score": score, "level": _level(score), "note": note}


def _brand_consistency_risk(artist_id: str, song_id: str) -> dict:
    result  = compute_release_score(artist_id, song_id)
    brand_s = result.get("sections", {}).get("brand", "not_checked")
    score   = {"ready": 100, "needs_review": 55, "blocked": 10, "not_checked": 60}.get(brand_s, 60)
    note    = (
        "Brand consistency confirmed." if brand_s == STATUS_READY
        else "Review the Brand section in Release Readiness to confirm consistency."
    )
    return {"key": "brand", "label": "Brand Consistency", "icon": "🧠",
            "score": score, "level": _level(score), "note": note}


def _publishing_readiness_risk(artist_id: str, song_id: str) -> dict:
    result  = compute_release_score(artist_id, song_id)
    pub_s   = result.get("sections", {}).get("publishing", "not_checked")
    score   = {"ready": 100, "needs_review": 50, "blocked": 5, "not_checked": 45}.get(pub_s, 45)
    note    = (
        "Publishing schedule and assets confirmed." if pub_s == STATUS_READY
        else "Complete the Publishing section in Release Readiness."
    )
    return {"key": "publishing", "label": "Publishing Readiness", "icon": "🚀",
            "score": score, "level": _level(score), "note": note}


def _metadata_risk(artist_id: str, song_id: str) -> dict:
    result  = compute_release_score(artist_id, song_id)
    meta_s  = result.get("sections", {}).get("metadata", "not_checked")
    score   = {"ready": 100, "needs_review": 55, "blocked": 10, "not_checked": 50}.get(meta_s, 50)
    note    = (
        "Metadata complete." if meta_s == STATUS_READY
        else "Complete title, release date, ISRC, genre, and descriptions."
    )
    return {"key": "metadata", "label": "Metadata Completeness", "icon": "🏷️",
            "score": score, "level": _level(score), "note": note}


# ── Overall report ────────────────────────────────────────────────────────────

DIMENSIONS = [
    _copyright_risk,
    _platform_risk,
    _ai_transparency_risk,
    _brand_consistency_risk,
    _publishing_readiness_risk,
    _metadata_risk,
]


def compute_risk_report(artist_id: str, song_id: str) -> dict:
    """Return full risk report for a release."""
    dims  = [fn(artist_id, song_id) for fn in DIMENSIONS]
    scores = [d["score"] for d in dims]
    overall_score = int(sum(scores) / len(scores)) if scores else 0
    # If any dimension is red, overall is at least yellow
    if any(d["level"] == RISK_RED for d in dims):
        overall_level = RISK_RED if sum(1 for d in dims if d["level"] == RISK_RED) >= 2 else RISK_YELLOW
    elif any(d["level"] == RISK_YELLOW for d in dims):
        overall_level = RISK_YELLOW
    else:
        overall_level = RISK_GREEN

    return {
        "artist_id":     artist_id,
        "song_id":       song_id,
        "overall_score": overall_score,
        "overall_level": overall_level,
        "dimensions":    {d["key"]: d for d in dims},
        "disclaimer":    (
            "Risk scores are operational guidance only. "
            "MusicWorks does NOT provide legal advice or guarantee platform compliance. "
            "All publishing decisions are made by the Founder."
        ),
    }
