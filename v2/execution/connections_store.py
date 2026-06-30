"""MusicWorks™ V4.1 — Connections Store: service registry and connection status.

API keys are NEVER stored here — they live in environment variables or
st.secrets. This module stores connection metadata: last test time,
status, and notes.
"""
import os
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR  = Path(__file__).parent.parent / "data"
CONN_DIR  = DATA_DIR / "connections"
META_FILE = CONN_DIR / "status.json"

# ── Service registry ──────────────────────────────────────────────────────────
# (key, name, category, env_var, icon, color, description, provider_url)

SERVICES = [
    # Writing / AI
    ("claude",      "Claude",       "AI — Writing",   "ANTHROPIC_API_KEY",    "🧠", "#D4A853",
     "Text generation: blog, email, press releases, captions, church outreach",
     "https://claude.ai"),
    ("google_ai",   "Google AI",    "AI — Image",     "GOOGLE_AI_API_KEY",    "🔵", "#4285F4",
     "Imagen: AI image generation for thumbnails and quote cards",
     "https://ai.google.dev"),
    ("veo",         "Veo",          "AI — Video",     "GOOGLE_VEO_API_KEY",   "🎥", "#FF6B2B",
     "AI video generation: Reels, Shorts, TikTok, Canvas, reaction clips",
     "https://deepmind.google/technologies/veo"),
    ("hedra",       "Hedra",        "AI — Avatar",    "HEDRA_API_KEY",        "🎙️", "#9B89D4",
     "AI avatar: talking-head devotional content without manual camera",
     "https://www.hedra.com"),
    ("elevenlabs",  "ElevenLabs",   "AI — Voice",     "ELEVENLABS_API_KEY",   "🔊", "#F59E0B",
     "Voice narration: devotional audio, podcast intros, spoken scripture",
     "https://elevenlabs.io"),
    ("canva",       "Canva",        "AI — Design",    "CANVA_API_KEY",        "🎨", "#22C55E",
     "Design briefs: quote cards, thumbnails, story slides, countdowns",
     "https://canva.com"),

    # Publishing
    ("youtube",     "YouTube",      "Publishing",     "YOUTUBE_API_KEY",      "▶️", "#FF0000",
     "Video publishing and YouTube Shorts",
     "https://studio.youtube.com"),
    ("instagram",   "Instagram",    "Publishing",     "INSTAGRAM_API_KEY",    "📸", "#E1306C",
     "Reels, posts, and Stories",
     "https://instagram.com"),
    ("tiktok",      "TikTok",       "Publishing",     "TIKTOK_API_KEY",       "🎵", "#69C9D0",
     "TikTok videos and Kingdom Words series",
     "https://tiktok.com"),
    ("facebook",    "Facebook",     "Publishing",     "FACEBOOK_API_KEY",     "👥", "#1877F2",
     "Facebook Reels and long-form posts",
     "https://facebook.com"),
    ("x",           "X",            "Publishing",     "X_API_KEY",            "✖️", "#F0EDE8",
     "X (Twitter) posts and video",
     "https://x.com"),
    ("threads",     "Threads",      "Publishing",     "THREADS_API_KEY",      "🧵", "#C8C4BE",
     "Threads posts (Meta)",
     "https://threads.net"),
    ("rumble",      "Rumble",       "Publishing",     "RUMBLE_API_KEY",       "🔴", "#85C742",
     "Rumble video uploads",
     "https://rumble.com"),

    # Newsletter
    ("mailchimp",   "Mailchimp",    "Newsletter",     "MAILCHIMP_API_KEY",    "📧", "#FFE01B",
     "Email newsletters to subscriber list",
     "https://mailchimp.com"),
    ("beehiiv",     "Beehiiv",      "Newsletter",     "BEEHIIV_API_KEY",      "🐝", "#F59E0B",
     "Beehiiv newsletter publishing",
     "https://beehiiv.com"),

    # Website / Other
    ("website",     "Website",      "Website",        "WEBSITE_URL",          "🌐", "#6A6460",
     "Artist website for blog posts and devotional guides",
     ""),
    ("distrokid",   "DistroKid",    "Distribution",   "",                     "🎵", "#8B5CF6",
     "Music distribution (metadata only — no automation)",
     "https://distrokid.com"),
]

SERVICE_MAP = {s[0]: s for s in SERVICES}

# ── Status persistence ────────────────────────────────────────────────────────

def _load_meta() -> dict:
    CONN_DIR.mkdir(parents=True, exist_ok=True)
    if not META_FILE.exists():
        return {}
    try:
        return json.loads(META_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_meta(data: dict) -> None:
    CONN_DIR.mkdir(parents=True, exist_ok=True)
    META_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def record_test(key: str, success: bool, message: str = "") -> None:
    """Record the result of a connection test."""
    meta = _load_meta()
    meta[key] = {
        "last_tested": datetime.now(timezone.utc).isoformat(),
        "last_status": "connected" if success else "error",
        "last_message": message,
    }
    _save_meta(meta)


def get_connection_status(key: str) -> dict:
    """Return full status dict for a service key."""
    meta = _load_meta()
    env_var = SERVICE_MAP.get(key, ("", "", "", "", "", "", "", ""))[3]
    has_key = bool(env_var and _get_env(env_var))
    stored  = meta.get(key, {})
    return {
        "key":          key,
        "has_key":      has_key,
        "env_var":      env_var,
        "last_tested":  stored.get("last_tested", ""),
        "last_status":  stored.get("last_status", ""),
        "last_message": stored.get("last_message", ""),
        "connected":    has_key,
    }


def is_connected(key: str) -> bool:
    """True if the service has a configured API key/URL."""
    env_var = SERVICE_MAP.get(key, (None, None, None, ""))[3]
    if not env_var:
        return False
    return bool(_get_env(env_var))


def _get_env(var: str) -> str:
    """Check st.secrets first, then os.environ."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and var in st.secrets:
            return st.secrets[var]
    except Exception:
        pass
    return os.environ.get(var, "")


def get_all_statuses() -> list[dict]:
    """Return status for every registered service."""
    return [get_connection_status(s[0]) for s in SERVICES]


def test_connection(key: str) -> tuple[bool, str]:
    """Run a live test for the service. Returns (success, message)."""
    if key == "claude":
        return _test_claude()
    # All other services: check if key is present
    status = get_connection_status(key)
    if status["has_key"]:
        msg = "API key present (live test not yet implemented for this provider)"
        record_test(key, True, msg)
        return True, msg
    msg = "Not configured — set the environment variable to connect"
    record_test(key, False, msg)
    return False, msg


def _test_claude() -> tuple[bool, str]:
    try:
        import anthropic
        client = anthropic.Anthropic()
        client.models.list()
        msg = "Connected — Claude API responding"
        record_test("claude", True, msg)
        return True, msg
    except Exception as e:
        msg = f"Error: {str(e)[:100]}"
        record_test("claude", False, msg)
        return False, msg
