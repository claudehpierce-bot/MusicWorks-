"""MusicWorks™ V4 — Media Calendar: schedule generation from release date."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from execution.production_queue import create_job, list_jobs, JOB_TYPE_META

DATA_DIR   = Path(__file__).parent.parent / "data"
CAL_DIR    = DATA_DIR / "calendar"


def _cal_path(artist_id: str) -> Path:
    CAL_DIR.mkdir(parents=True, exist_ok=True)
    return CAL_DIR / f"{artist_id}.json"


# ── Campaign schedule template ────────────────────────────────────────────────
# Each entry: (days_from_release, time_str, job_type, phase, priority)
# Negative = pre-release, 0 = launch day, positive = post-release

_SCHEDULE_TEMPLATE = [
    # Pre-release
    (-21, "08:30", "quote_card",      "pre_release", 7),
    (-21, "09:00", "story_slides",    "pre_release", 7),
    (-21, "10:00", "blog",            "pre_release", 6),
    (-14, "08:30", "behind_scenes",   "pre_release", 6),
    (-14, "09:00", "quote_card",      "pre_release", 7),
    (-10, "08:30", "instagram_reel",  "pre_release", 5),
    (-7,  "08:30", "countdown",       "pre_release", 5),
    (-7,  "09:00", "story_slides",    "pre_release", 5),
    (-5,  "08:30", "tiktok",          "pre_release", 5),
    (-3,  "08:30", "countdown",       "pre_release", 4),
    (-3,  "09:00", "email",           "pre_release", 4),
    (-3,  "10:00", "church_outreach", "pre_release", 4),
    (-2,  "08:30", "story_slides",    "pre_release", 4),
    (-1,  "08:30", "countdown",       "pre_release", 3),
    (-1,  "09:00", "story_slides",    "pre_release", 3),
    (-1,  "18:00", "tiktok",          "pre_release", 3),

    # Launch Day
    (0, "08:30", "instagram_reel",  "launch", 1),
    (0, "08:30", "tiktok",          "launch", 1),
    (0, "08:30", "youtube_short",   "launch", 1),
    (0, "08:30", "facebook_reel",   "launch", 1),
    (0, "08:30", "x_video",         "launch", 1),
    (0, "08:30", "spotify_canvas",  "launch", 1),
    (0, "09:00", "blog",            "launch", 2),
    (0, "10:00", "press_release",   "launch", 2),
    (0, "14:00", "story_slides",    "launch", 3),
    (0, "20:00", "reaction",        "launch", 4),

    # Post-release
    (1,  "08:30", "post_launch",     "post_release", 2),
    (1,  "09:00", "story_slides",    "post_release", 3),
    (3,  "08:30", "quote_card",      "post_release", 3),
    (3,  "09:00", "tiktok",          "post_release", 3),
    (5,  "10:00", "press_release",   "post_release", 4),
    (7,  "08:00", "blog",            "post_release", 4),
    (7,  "09:00", "church_outreach", "post_release", 4),
    (10, "08:30", "email",           "post_release", 5),
    (14, "08:30", "instagram_reel",  "post_release", 5),
    (14, "09:00", "reaction",        "post_release", 5),
    (21, "08:30", "quote_card",      "post_release", 6),
    (30, "08:30", "post_launch",     "post_release", 6),

    # Evergreen (relative to release, starting at +45)
    (45,  "08:30", "behind_scenes",  "evergreen", 7),
    (60,  "08:30", "quote_card",     "evergreen", 7),
    (90,  "08:30", "blog",           "evergreen", 8),
    (120, "08:30", "instagram_reel", "evergreen", 8),
]


def generate_calendar(
    artist_id: str,
    song_id: str,
    song_title: str,
    release_date_str: str,
    campaign_mode: str = "blitz",
) -> list[dict]:
    """
    Generate a full campaign calendar from a release date.
    Returns list of job dicts created in the production queue.
    Skips job types already queued for same artist/song.
    """
    release_dt = datetime.fromisoformat(release_date_str).replace(tzinfo=timezone.utc)

    # Check existing jobs to avoid duplicates
    existing = {(j["job_type"], j["phase"]) for j in list_jobs(artist_id)}

    jobs_created = []
    for (days, time_str, job_type, phase, priority) in _SCHEDULE_TEMPLATE:
        if (job_type, phase) in existing:
            continue

        # Blitz mode: all phases; Standard: skip deep post-release; Slow: launch only
        if campaign_mode == "standard" and phase == "evergreen":
            continue
        if campaign_mode == "slow" and phase in ("pre_release", "post_release", "evergreen"):
            continue

        sched_dt = release_dt + timedelta(days=days)
        h, m = map(int, time_str.split(":"))
        sched_dt = sched_dt.replace(hour=h, minute=m, second=0)

        job = create_job(
            artist_id=artist_id,
            job_type=job_type,
            song_id=song_id,
            song_title=song_title,
            release_date=release_date_str,
            phase=phase,
            scheduled_date=sched_dt.isoformat(),
            priority=priority,
        )
        jobs_created.append(job)

    # Store calendar summary
    _save_calendar_meta(artist_id, song_id, song_title, release_date_str, len(jobs_created))
    return jobs_created


def _save_calendar_meta(artist_id, song_id, song_title, release_date, count):
    p = _cal_path(artist_id)
    data = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    data.setdefault("releases", [])
    # Update or insert
    for r in data["releases"]:
        if r["song_id"] == song_id:
            r.update({"release_date": release_date, "jobs": count, "song_title": song_title})
            break
    else:
        data["releases"].append({
            "song_id": song_id,
            "song_title": song_title,
            "release_date": release_date,
            "jobs": count,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_calendar_meta(artist_id: str) -> dict:
    p = _cal_path(artist_id)
    if not p.exists():
        return {"releases": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"releases": []}


def get_upcoming_jobs(artist_id: str, days_ahead: int = 14) -> list[dict]:
    """Return jobs scheduled in the next N days, sorted by scheduled_date."""
    from execution.production_queue import list_jobs
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days_ahead)
    jobs = []
    for job in list_jobs(artist_id):
        sd = job.get("scheduled_date", "")
        if not sd:
            continue
        try:
            sdt = datetime.fromisoformat(sd)
            if now <= sdt <= cutoff:
                jobs.append(job)
        except Exception:
            continue
    return sorted(jobs, key=lambda j: j.get("scheduled_date", ""))


def get_jobs_by_phase(artist_id: str) -> dict[str, list]:
    from execution.production_queue import list_jobs, PHASES
    result = {p: [] for p in PHASES}
    for job in list_jobs(artist_id):
        phase = job.get("phase", "launch")
        result.setdefault(phase, []).append(job)
    for phase in result:
        result[phase].sort(key=lambda j: j.get("scheduled_date", ""))
    return result
