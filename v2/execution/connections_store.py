"""MusicWorks™ V5.4 — Connections Store: test-result persistence for providers.

Single source of truth for WHICH providers exist and their env vars is
execution/provider_registry.py — this module no longer maintains its own
duplicate provider list (that used to drift: e.g. "google_ai" here vs.
"google_imagen" in provider_registry, and several providers — Perplexity,
HeyGen, Leonardo, CapCut, Vizard, Pictory — missing entirely). This module
now only stores WHEN a provider was last tested and what happened.

API keys are NEVER stored here — they live in environment variables or
st.secrets.
"""
import os
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR  = Path(__file__).parent.parent / "data"
CONN_DIR  = DATA_DIR / "connections"
META_FILE = CONN_DIR / "status.json"


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
    """Return full status dict for a provider key (from provider_registry)."""
    from execution.provider_registry import PROVIDER_MAP
    provider = PROVIDER_MAP.get(key)
    env_var  = provider.env_var if provider else ""
    has_key  = bool(env_var and _get_env(env_var))
    stored   = _load_meta().get(key, {})
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
    """True if the provider has a configured API key/URL."""
    from execution.provider_registry import PROVIDER_MAP
    provider = PROVIDER_MAP.get(key)
    if not provider or not provider.env_var:
        return False
    return bool(_get_env(provider.env_var))


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
    """Return status for every registered provider."""
    from execution.provider_registry import PROVIDERS
    return [get_connection_status(p.key) for p in PROVIDERS]


_REAL_TESTS = {}  # populated below, key -> test function


def test_connection(key: str) -> tuple[bool, str]:
    """Run a live test for the provider. Returns (success, message)."""
    tester = _REAL_TESTS.get(key)
    if tester:
        return tester()
    # All other providers: check if key is present (real live tests are not
    # yet implemented for them — only Claude, Google AI, HeyGen, and Veo
    # have working live checks today).
    status = get_connection_status(key)
    if status["has_key"]:
        msg = "API key present (live test not yet implemented for this provider)"
        record_test(key, True, msg)
        return True, msg
    msg = "Not configured — set the environment variable to connect"
    record_test(key, False, msg)
    return False, msg


def _test_claude() -> tuple[bool, str]:
    status = get_connection_status("claude")
    if not status["has_key"]:
        msg = "Not configured — set ANTHROPIC_API_KEY to connect"
        record_test("claude", False, msg)
        return False, msg
    try:
        import anthropic
        client = anthropic.Anthropic()
        client.models.list()
        msg = "Connected — Claude API responding"
        record_test("claude", True, msg)
        return True, msg
    except Exception as e:
        msg = f"Configuration error: {str(e)[:100]}"
        record_test("claude", False, msg)
        return False, msg


def _test_google_imagen() -> tuple[bool, str]:
    status = get_connection_status("google_imagen")
    if not status["has_key"]:
        msg = "Not configured — set GOOGLE_AI_API_KEY to connect"
        record_test("google_imagen", False, msg)
        return False, msg
    try:
        from google import genai
        client = genai.Client(api_key=_get_env("GOOGLE_AI_API_KEY"))
        list(client.models.list())
        msg = "Connected — Google AI API responding"
        record_test("google_imagen", True, msg)
        return True, msg
    except Exception as e:
        msg = f"Configuration error: {str(e)[:100]}"
        record_test("google_imagen", False, msg)
        return False, msg


def _test_heygen() -> tuple[bool, str]:
    status = get_connection_status("heygen")
    if not status["has_key"]:
        msg = "Not configured — set HEYGEN_API_KEY to connect"
        record_test("heygen", False, msg)
        return False, msg
    try:
        import requests
        resp = requests.get(
            "https://api.heygen.com/v2/user/remaining_quota",
            headers={"X-Api-Key": _get_env("HEYGEN_API_KEY")},
            timeout=10,
        )
        if resp.status_code == 200:
            msg = "Connected — HeyGen API responding"
            record_test("heygen", True, msg)
            return True, msg
        if resp.status_code in (401, 403):
            msg = f"Configuration error: HeyGen rejected the API key (HTTP {resp.status_code})"
            record_test("heygen", False, msg)
            return False, msg
        msg = f"Configuration error: HeyGen returned HTTP {resp.status_code}"
        record_test("heygen", False, msg)
        return False, msg
    except Exception as e:
        msg = f"Configuration error: {str(e)[:100]}"
        record_test("heygen", False, msg)
        return False, msg


_REAL_TESTS.update({
    "claude": _test_claude,
    "google_imagen": _test_google_imagen,
    "heygen": _test_heygen,
})
