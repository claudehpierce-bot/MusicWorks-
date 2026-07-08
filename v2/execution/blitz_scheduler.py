"""MusicWorks™ V6.2 — Blitz Scheduler: spreads a campaign's already-APPROVED
assets across its chosen launch window, never generating new content and
never calling any external publishing API — it only assigns scheduled_date
and flips status locally (approved -> scheduled). Founders mark items
published manually once they've actually posted them.

This is intentionally separate from execution/media_calendar.py, which spawns
brand-new empty template jobs on a fixed cadence unrelated to real content —
the wrong tool once real approved assets already exist.
"""
from datetime import datetime, timezone, timedelta

from execution.production_queue import list_jobs, get_job, save_job
from execution import campaign_store
from execution.campaign_store import INTENSITY_POSTS_PER_DAY

# Platform checklist shown in the Control Center — matches the spec's
# SCHEDULING OPTIONS list. Press releases and Spotify Canvas art aren't on
# this list (the spec doesn't ask founders to toggle them) so they're always
# included alongside job_type platform "all" — see _platform_matches.
PLATFORM_OPTIONS = [
    "YouTube", "YouTube Shorts", "Instagram", "TikTok", "Facebook", "X",
    "Threads", "Rumble", "Website", "Newsletter", "Church outreach",
]


def _platform_matches(job: dict, platforms: list[str]) -> bool:
    job_type = job.get("job_type", "")
    platform = job.get("platform", "")

    # Channel-agnostic / supplementary media always goes out with the blitz.
    if platform in ("all", "press", "spotify"):
        return True

    if not platforms:
        return False

    # youtube_short and long-form video share platform "youtube" in
    # JOB_TYPE_META — disambiguate by job_type so the two checkboxes are
    # independent.
    if job_type == "youtube_short":
        return "YouTube Shorts" in platforms
    if platform == "youtube":
        return "YouTube" in platforms
    if job_type == "email":
        return "Newsletter" in platforms
    if job_type == "church_outreach":
        return "Church outreach" in platforms

    label_by_platform = {
        "instagram": "Instagram",
        "tiktok":    "TikTok",
        "facebook":  "Facebook",
        "x":         "X",
        "rumble":    "Rumble",
        "website":   "Website",
    }
    label = label_by_platform.get(platform)
    return bool(label) and label in platforms


def _window_days(campaign: dict) -> int:
    ctype = campaign.get("campaign_type", "")
    if ctype == "48h":
        return 2
    if ctype == "7d":
        return 7
    if ctype == "14d":
        return 14
    if ctype == "30d":
        return 30
    if ctype == "custom":
        start, end = campaign.get("window_start", ""), campaign.get("window_end", "")
        if start and end:
            try:
                days = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).days
                return max(days, 1)
            except Exception:
                pass
    return 7


def _time_slots(n: int) -> list[tuple[int, int]]:
    """n evenly spaced (hour, minute) posting slots between 08:00 and 20:00."""
    if n <= 1:
        return [(9, 0)]
    start_min, end_min = 8 * 60, 20 * 60
    step = (end_min - start_min) // (n - 1)
    return [divmod(start_min + i * step, 60) for i in range(n)]


def _schedule_jobs(artist_id: str, jobs: list[dict], start: datetime, posts_per_day: int) -> None:
    slots = _time_slots(posts_per_day)
    for idx, job in enumerate(jobs):
        day_offset = idx // posts_per_day
        hour, minute = slots[idx % posts_per_day]
        sched_dt = (start + timedelta(days=day_offset)).replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )
        full = get_job(artist_id, job["job_id"])
        if not full:
            continue
        full["scheduled_date"] = sched_dt.isoformat()
        full["status"] = "scheduled"
        save_job(full)


def launch_blitz(artist_id: str, campaign_id: str) -> dict:
    """Schedule a campaign's approved assets. Returns counts:
    scheduled = assets given a scheduled_date this run,
    leftover = matched assets that didn't fit the window/intensity capacity,
    unmatched = approved assets whose platform wasn't in the chosen list."""
    campaign = campaign_store.get_campaign(artist_id, campaign_id)
    if not campaign:
        return {"scheduled": 0, "leftover": 0, "unmatched": 0}

    approved = list_jobs(artist_id, status="approved", campaign_id=campaign_id)
    platforms = campaign.get("platforms", [])
    matched = [j for j in approved if _platform_matches(j, platforms)]
    unmatched_count = len(approved) - len(matched)
    matched.sort(key=lambda j: (j.get("priority", 5), j.get("job_id", "")))

    intensity = campaign.get("intensity") or "standard"
    posts_per_day = INTENSITY_POSTS_PER_DAY.get(intensity, 3)
    capacity = _window_days(campaign) * posts_per_day

    to_schedule, leftover = matched[:capacity], matched[capacity:]

    launch_dt = campaign.get("launch_datetime") or ""
    try:
        start = datetime.fromisoformat(launch_dt) if launch_dt else datetime.now(timezone.utc)
    except Exception:
        start = datetime.now(timezone.utc)

    _schedule_jobs(artist_id, to_schedule, start, posts_per_day)

    return {"scheduled": len(to_schedule), "leftover": len(leftover), "unmatched": unmatched_count}


def extend_blitz(artist_id: str, campaign_id: str, additional_days: int = 7) -> dict:
    """Schedule any still-approved assets (including previous leftovers) into
    a window appended after the campaign's latest scheduled/published post."""
    campaign = campaign_store.get_campaign(artist_id, campaign_id)
    if not campaign:
        return {"scheduled": 0, "leftover": 0, "unmatched": 0}

    approved = list_jobs(artist_id, status="approved", campaign_id=campaign_id)
    platforms = campaign.get("platforms", [])
    matched = [j for j in approved if _platform_matches(j, platforms)]
    unmatched_count = len(approved) - len(matched)
    matched.sort(key=lambda j: (j.get("priority", 5), j.get("job_id", "")))

    intensity = campaign.get("intensity") or "standard"
    posts_per_day = INTENSITY_POSTS_PER_DAY.get(intensity, 3)
    capacity = max(additional_days, 1) * posts_per_day
    to_schedule, leftover = matched[:capacity], matched[capacity:]

    all_campaign_jobs = list_jobs(artist_id, campaign_id=campaign_id)
    existing_dates = [
        j["scheduled_date"] for j in all_campaign_jobs
        if j.get("scheduled_date") and j.get("status") in ("scheduled", "published")
    ]
    start = datetime.now(timezone.utc)
    if existing_dates:
        try:
            start = max(datetime.fromisoformat(d) for d in existing_dates) + timedelta(days=1)
        except Exception:
            pass

    _schedule_jobs(artist_id, to_schedule, start, posts_per_day)

    campaign["extension_count"] = campaign.get("extension_count", 0) + 1
    campaign_store.save_campaign(campaign)

    return {"scheduled": len(to_schedule), "leftover": len(leftover), "unmatched": unmatched_count}


def reset_schedule(artist_id: str, campaign_id: str) -> int:
    """Flip every 'scheduled' job in this campaign back to 'approved',
    clearing scheduled_date — used by Reschedule before re-running launch_blitz."""
    jobs = list_jobs(artist_id, status="scheduled", campaign_id=campaign_id)
    for job in jobs:
        full = get_job(artist_id, job["job_id"])
        if not full:
            continue
        full["status"] = "approved"
        full["scheduled_date"] = ""
        save_job(full)
    return len(jobs)


def pull_back_job(artist_id: str, job_id: str) -> dict | None:
    """Revert a single scheduled job back to approved — Asset Review's filters
    don't surface 'scheduled' jobs, so this is the only per-item edit path
    for something already scheduled but not yet posted."""
    job = get_job(artist_id, job_id)
    if not job:
        return None
    job["status"] = "approved"
    job["scheduled_date"] = ""
    save_job(job)
    return job
