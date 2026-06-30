"""MusicWorks™ V4.2 — Provider Router: intelligent auto-selection with fallback.

The founder never asks "which AI should I use?"
MusicWorks answers that question automatically based on:
  - Which providers are connected (API key present)
  - Which subscriptions are active
  - Which providers have the needed capability
  - Routing table order (primary → fallbacks)
  - Founder overrides (stored in data/routing/overrides.json)

Flow: task_category → route() → best available provider key (or "mock")
"""
import json
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR     = Path(__file__).parent.parent / "data"
ROUTING_DIR  = DATA_DIR / "routing"
OVERRIDE_FILE = ROUTING_DIR / "overrides.json"


# ── Routing Table ──────────────────────────────────────────────────────────────

@dataclass
class RoutingEntry:
    task:        str
    label:       str
    icon:        str
    primary:     str
    fallbacks:   list
    job_types:   list               # which job_type strings map here
    description: str = ""


ROUTING_TABLE: dict[str, RoutingEntry] = {e.task: e for e in [
    RoutingEntry("writing",          "Writing",          "✍️",  "claude",       ["perplexity"],
                 ["blog", "email", "press_release", "church_outreach", "post_launch", "reaction"],
                 "Long-form and short-form text content"),

    RoutingEntry("research",         "Research",         "🔍", "perplexity",   ["claude"],
                 [],
                 "Gospel context, trends, fact-checking, artist research"),

    RoutingEntry("video",            "Music Video",      "🎥", "veo",          ["heygen"],
                 ["instagram_reel", "tiktok", "youtube_short", "facebook_reel",
                  "x_video", "rumble_video", "spotify_canvas"],
                 "AI-generated cinematic video for all social platforms"),

    RoutingEntry("talking_avatar",   "Talking Avatar",   "🎙️", "hedra",        ["heygen"],
                 ["behind_scenes"],
                 "AI presenter / devotional / talking-head content"),

    RoutingEntry("hero_artwork",     "Hero Artwork",     "🎨", "leonardo",     ["google_imagen"],
                 ["thumbnail_set"],
                 "Album covers, artist portraits, campaign hero images"),

    RoutingEntry("graphics",         "Graphics",         "🖼️",  "canva",        ["leonardo"],
                 ["quote_card", "story_slides", "countdown"],
                 "Branded quote cards, story slides, countdown graphics"),

    RoutingEntry("voice",            "Voice / Audio",    "🔊", "elevenlabs",   [],
                 [],
                 "Voice narration, spoken scripture, devotional audio"),

    RoutingEntry("video_repurposing","Video Repurposing","📐", "vizard",       ["capcut"],
                 [],
                 "Extract clips from long-form video, auto-caption for social"),

    RoutingEntry("editing",          "Video Editing",    "✂️",  "capcut",       ["pictory"],
                 [],
                 "Assemble and edit short-form video content"),
]}

# ── job_type → task category lookup ──────────────────────────────────────────

JOB_TYPE_TO_TASK: dict[str, str] = {}
for _entry in ROUTING_TABLE.values():
    for _jt in _entry.job_types:
        JOB_TYPE_TO_TASK[_jt] = _entry.task


def task_for_job(job_type: str) -> str:
    return JOB_TYPE_TO_TASK.get(job_type, "writing")


# ── Override persistence ───────────────────────────────────────────────────────

def _load_overrides() -> dict:
    ROUTING_DIR.mkdir(parents=True, exist_ok=True)
    if not OVERRIDE_FILE.exists():
        return {}
    try:
        return json.loads(OVERRIDE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_overrides(data: dict) -> None:
    ROUTING_DIR.mkdir(parents=True, exist_ok=True)
    OVERRIDE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def set_override(task: str, provider_key: str) -> None:
    """Founder manually overrides which provider handles a task."""
    data = _load_overrides()
    data[task] = provider_key
    _save_overrides(data)


def clear_override(task: str) -> None:
    data = _load_overrides()
    data.pop(task, None)
    _save_overrides(data)


def get_override(task: str) -> str | None:
    return _load_overrides().get(task)


# ── Availability check ────────────────────────────────────────────────────────

def is_available(provider_key: str) -> bool:
    """True if this provider can be used right now.

    API-key providers: key is set.
    Subscription-only providers: subscription is active.
    """
    from execution.provider_registry import PROVIDER_MAP, is_api_key_set
    from execution.subscription_store import is_subscription_active

    p = PROVIDER_MAP.get(provider_key)
    if not p:
        return False

    if p.requires_api_key:
        return is_api_key_set(provider_key)

    # subscription-only tool (capcut, vizard, pictory, etc.)
    return is_subscription_active(provider_key)


# ── Core routing ──────────────────────────────────────────────────────────────

def route(task: str) -> str:
    """Return the best available provider for this task.
    Checks override → primary → fallbacks → "mock" if nothing is connected.
    """
    entry = ROUTING_TABLE.get(task)
    if not entry:
        return "mock"

    # 1. Founder override
    override = get_override(task)
    if override and is_available(override):
        return override

    # 2. Primary
    if is_available(entry.primary):
        return entry.primary

    # 3. Fallbacks in order
    for fb in entry.fallbacks:
        if is_available(fb):
            return fb

    # 4. Nothing connected → mock output
    return "mock"


def route_for_job(job_type: str) -> str:
    """Convenience: route a job by its job_type string."""
    return route(task_for_job(job_type))


def auto_fallback(task: str, failed_provider: str) -> str:
    """Skip failed_provider and return the next available provider for this task."""
    entry = ROUTING_TABLE.get(task)
    if not entry:
        return "mock"

    candidates = [entry.primary] + list(entry.fallbacks)
    for candidate in candidates:
        if candidate != failed_provider and is_available(candidate):
            return candidate
    return "mock"


# ── Factory Plan ──────────────────────────────────────────────────────────────

def get_factory_plan() -> list[dict]:
    """Return the current routing plan for every task in the routing table.
    Each entry: task, label, icon, provider_key, provider_name, is_mock, has_override.
    """
    from execution.provider_registry import PROVIDER_MAP
    plan = []
    overrides = _load_overrides()

    for task, entry in ROUTING_TABLE.items():
        selected  = route(task)
        prov      = PROVIDER_MAP.get(selected)
        override  = overrides.get(task)
        fallback_used = (selected != entry.primary and selected != "mock" and selected != override)

        # What would happen if primary fails?
        fb_key  = auto_fallback(task, entry.primary) if not is_available(entry.primary) else entry.primary
        fb_prov = PROVIDER_MAP.get(fb_key) if fb_key != "mock" else None

        plan.append({
            "task":           task,
            "label":          entry.label,
            "icon":           entry.icon,
            "description":    entry.description,
            "primary_key":    entry.primary,
            "primary_name":   PROVIDER_MAP[entry.primary].name if entry.primary in PROVIDER_MAP else entry.primary,
            "primary_avail":  is_available(entry.primary),
            "fallback_keys":  entry.fallbacks,
            "selected_key":   selected,
            "selected_name":  prov.name if prov else "Mock Output",
            "selected_icon":  prov.icon if prov else "🤖",
            "is_mock":        selected == "mock",
            "fallback_used":  fallback_used,
            "has_override":   bool(override),
            "override_key":   override or "",
        })
    return plan
