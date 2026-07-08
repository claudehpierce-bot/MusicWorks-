"""MusicWorks™ V4 — Production Queue: job management for every media deliverable."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

DATA_DIR  = Path(__file__).parent.parent / "data"
JOBS_DIR  = DATA_DIR / "jobs"

JOB_TYPES = [
    # (key, label, icon, default_worker, platform)
    # ── Hero Worker #1: Cinematic Video (Veo) — long-form storytelling ─────────
    ("music_video",         "Official Music Video", "🎬", "veo",        "youtube"),
    ("trailer",             "Trailer",               "🎞️", "veo",        "youtube"),
    ("lyric_visualizer",    "Lyric Visualizer",      "🌊", "veo",        "youtube"),
    ("cinematic_scenes",    "Cinematic Scenes",      "🎥", "veo",        "youtube"),
    ("worship_background",  "Worship Background",    "🕊️", "veo",        "youtube"),
    ("youtube_video",       "YouTube Video",         "▶️", "veo",        "youtube"),
    ("rumble_video",        "Rumble Video",          "🔴", "veo",        "rumble"),
    ("spotify_canvas",      "Spotify Canvas",        "🎧", "veo",        "spotify"),

    # ── Hero Worker #2: Artist Presence (Hedra) — human connection ─────────────
    ("instagram_reel",  "Instagram Reel",       "📱", "hedra",      "instagram"),
    ("tiktok",          "TikTok Video",          "🎵", "hedra",      "tiktok"),
    ("youtube_short",   "YouTube Short",         "▶️", "hedra",      "youtube"),
    ("facebook_reel",   "Facebook Reel",         "👥", "hedra",      "facebook"),
    ("x_video",         "X Video",               "✖️", "hedra",      "x"),
    ("reaction",        "Reaction Content",      "💫", "hedra",      "tiktok"),
    ("behind_scenes",   "Behind the Scenes",     "🎬", "hedra",      "instagram"),
    ("countdown",        "Countdown Video",       "⏱️", "hedra",      "instagram"),
    ("artist_welcome",   "Artist Welcome",        "👋", "hedra",      "instagram"),
    ("devotional",        "Devotional",             "🙏", "hedra",      "instagram"),
    ("scripture_reflection", "Scripture Reflection", "📖", "hedra",   "instagram"),

    # ── Text (Claude) ───────────────────────────────────────────────────────────
    ("blog",            "Blog Post",             "✍️", "claude",     "website"),
    ("email",           "Email Newsletter",      "📧", "claude",     "email"),
    ("press_release",   "Press Release",         "📰", "claude",     "press"),
    ("church_outreach", "Church Outreach",       "⛪", "claude",     "email"),
    ("post_launch",     "Post-Launch Post",      "🚀", "claude",     "all"),

    # ── Growth & Discovery writing (Claude) — website/SEO/bio/pitch copy ───────
    ("website_copy",         "Website Copy",             "🌐", "claude", "website"),
    ("artist_story",         "Artist Story",             "📖", "claude", "website"),
    ("behind_song_article",  "Behind the Song Article",  "🎼", "claude", "website"),
    ("seo_title",            "SEO Title",                "🔍", "claude", "website"),
    ("seo_description",     "SEO Description",           "🔍", "claude", "website"),
    ("seo_keywords",         "SEO Keywords",              "🔑", "claude", "website"),
    ("hashtag_set",          "Hashtag Set",               "#️⃣", "claude", "all"),
    ("playlist_pitch",       "Playlist Pitch Copy",       "🎧", "claude", "spotify"),
    ("playlist_target_notes", "Playlist Target Notes",   "🎯", "claude", "spotify"),
    ("genre_positioning",    "Genre Positioning",         "🎼", "claude", "all"),
    ("similar_artist_notes", "Similar Artist Notes",      "🎤", "claude", "all"),
    ("discovery_copy",       "Music Discovery Copy",      "🔎", "claude", "all"),
    ("artist_bio_short",     "Short Artist Bio",          "👤", "claude", "all"),
    ("artist_bio_long",      "Long Artist Bio",           "📝", "claude", "all"),

    # ── Growth & Discovery social text (Claude) — distinct from the video
    # job types above that share the same platform names ─────────────────────
    ("x_post",              "X Post",                    "✖️", "claude", "x"),
    ("threads_post",        "Threads Post",              "🧵", "claude", "threads"),
    ("rumble_description",  "Rumble Description",        "🔴", "claude", "rumble"),
    ("community_post",      "Community Post",            "💬", "claude", "all"),

    # ── Graphics (Canva / Leonardo) ─────────────────────────────────────────────
    ("quote_card",      "Quote Card",            "💬", "canva",      "all"),
    ("story_slides",    "Story Slides",          "📲", "canva",      "instagram"),
    ("thumbnail_set",   "Thumbnail Set",         "🖼️", "canva",      "youtube"),
    ("countdown_graphic",             "Countdown Graphic",              "⏳", "canva", "instagram"),
    ("release_announcement_graphic",  "Release Announcement Graphic",   "📢", "canva", "all"),
    ("campaign_poster",               "Campaign Poster",                "🖼️", "canva", "all"),
]

JOB_STATUSES = [
    ("pending",     "Pending",    "#6A6460"),
    ("queued",      "Queued",     "#F59E0B"),
    ("generating",  "Generating", "#9B89D4"),
    ("review",      "In Review",  "#3B82F6"),
    ("approved",    "Approved",   "#22C55E"),
    ("scheduled",   "Scheduled",  "#D4A853"),
    ("published",   "Published",  "#10B981"),
    ("rejected",    "Rejected",   "#EF4444"),
]

STATUS_COLOR  = {k: c for k, _, c in JOB_STATUSES}
STATUS_LABELS = {k: l for k, l, _ in JOB_STATUSES}

JOB_TYPE_META: dict[str, dict] = {
    k: {"label": l, "icon": i, "worker": w, "platform": p}
    for k, l, i, w, p in JOB_TYPES
}

PHASES = ["pre_release", "launch", "post_release", "evergreen"]
PHASE_LABELS = {
    "pre_release":  "Pre-Release",
    "launch":       "Launch Day",
    "post_release": "Post-Release",
    "evergreen":    "Evergreen",
}


# ── Paths ─────────────────────────────────────────────────────────────────────

def _artist_dir(artist_id: str) -> Path:
    d = JOBS_DIR / artist_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _job_path(artist_id: str, job_id: str) -> Path:
    return _artist_dir(artist_id) / f"{job_id}.json"


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_job(
    artist_id: str,
    job_type: str,
    song_id: str = "",
    song_title: str = "",
    release_date: str = "",
    phase: str = "launch",
    scheduled_date: str = "",
    notes: str = "",
    priority: int = 5,
    prompt: str = "",
    campaign_id: str = "",
) -> dict:
    meta = JOB_TYPE_META.get(job_type, {})
    job_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).isoformat()
    job = {
        "job_id":        job_id,
        "artist_id":     artist_id,
        "campaign_id":   campaign_id,
        "song_id":       song_id,
        "song_title":    song_title,
        "release_date":  release_date,
        "job_type":      job_type,
        "job_label":     meta.get("label", job_type),
        "job_icon":      meta.get("icon", "📄"),
        "platform":      meta.get("platform", ""),
        "worker":        meta.get("worker", "claude"),
        "phase":         phase,
        "scheduled_date": scheduled_date,
        "status":        "pending",
        "priority":      priority,
        "prompt":        prompt,
        "output_files":  [],
        "version":       1,
        "versions":      [],
        "notes":         notes,
        "created_at":    now,
        "updated_at":    now,
        "approved_at":   None,
        "published_at":  None,
    }
    _job_path(artist_id, job_id).write_text(
        json.dumps(job, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return job


def get_job(artist_id: str, job_id: str) -> dict | None:
    p = _job_path(artist_id, job_id)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save_job(job: dict) -> None:
    job["updated_at"] = datetime.now(timezone.utc).isoformat()
    _job_path(job["artist_id"], job["job_id"]).write_text(
        json.dumps(job, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def update_job_status(artist_id: str, job_id: str, status: str, notes: str = "") -> dict | None:
    job = get_job(artist_id, job_id)
    if not job:
        return None
    job["status"] = status
    if notes:
        job["notes"] = notes
    if status == "approved":
        job["approved_at"] = datetime.now(timezone.utc).isoformat()
    if status == "published":
        job["published_at"] = datetime.now(timezone.utc).isoformat()
    save_job(job)
    return job


def add_output_file(artist_id: str, job_id: str, file_path: str, label: str = "") -> dict | None:
    job = get_job(artist_id, job_id)
    if not job:
        return None
    job["output_files"].append({"path": file_path, "label": label, "added_at": datetime.now(timezone.utc).isoformat()})
    job["versions"].append({"version": job["version"], "files": list(job["output_files"]), "at": datetime.now(timezone.utc).isoformat()})
    job["version"] += 1
    save_job(job)
    return job


def delete_job(artist_id: str, job_id: str) -> bool:
    p = _job_path(artist_id, job_id)
    if p.exists():
        p.unlink()
        return True
    return False


def list_jobs(
    artist_id: str,
    status: str | None = None,
    phase: str | None = None,
    campaign_id: str | None = None,
) -> list[dict]:
    d = _artist_dir(artist_id)
    jobs = []
    for f in sorted(d.glob("*.json")):
        try:
            job = json.loads(f.read_text(encoding="utf-8"))
            if status and job.get("status") != status:
                continue
            if phase and job.get("phase") != phase:
                continue
            if campaign_id and job.get("campaign_id") != campaign_id:
                continue
            jobs.append(job)
        except Exception:
            continue
    return sorted(jobs, key=lambda j: (j.get("priority", 5), j.get("scheduled_date", "")))


def queue_stats(artist_id: str, campaign_id: str | None = None) -> dict:
    jobs = list_jobs(artist_id, campaign_id=campaign_id)
    stats: dict[str, int] = {}
    for _, lbl, _ in JOB_STATUSES:
        pass
    for k, *_ in JOB_STATUSES:
        stats[k] = sum(1 for j in jobs if j.get("status") == k)
    stats["total"] = len(jobs)
    return stats
