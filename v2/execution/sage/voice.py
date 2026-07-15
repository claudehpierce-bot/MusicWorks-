"""MusicWorks(tm) -- Sage's real voice synthesis, via the governed SVS-1
voice standard (never a raw provider ID -- see execution/voice_registry.py).

synthesize() is the only function callers need. It:
  1. Resolves SVS-1 -> (elevenlabs, provider_voice_id) through the registry.
  2. Returns a cached clip if this exact text has been spoken before (a
     fixed, small set of narration moments -- caching avoids re-billing
     and re-latency on every rerun of the same step).
  3. Otherwise calls the real ElevenLabs text-to-speech REST API.
  4. Returns None -- never raises -- if no API key is configured or the
     call fails for any reason. Voice is an enhancement; a synthesis
     failure must never break a page that only needs its transcript.

Nothing here is mocked: with ELEVENLABS_API_KEY set, this makes a real
network call and returns real audio bytes. Without a key, every call
cleanly returns None and the UI shows transcript only, exactly the DS-1 /
SAGE_PERSONA "text guarantees accessibility" requirement, not a fallback
bolted on afterward.

synthesize() is a thin wrapper around _synthesize_core() -- there is
exactly one real implementation. _synthesize_core() additionally returns a
diagnostics dict (Sage Voice Diagnostics, Studio Mode only -- see
ui/sage.py); the two never drift because they're the same code path.
"""
import hashlib
import os
import time
from pathlib import Path

from execution.voice_registry import VoiceNotFoundError, resolve_voice

CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "sage_voice_cache"

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
# Stability/similarity per SAGE_PERSONA.md's Voice Tone: warm, calm, confident,
# patient -- high stability, medium similarity (natural, not over-produced),
# same philosophy already documented for the existing devotional-audio
# ElevenLabs worker (execution/workers/elevenlabs_worker.py).
VOICE_SETTINGS = {"stability": 0.65, "similarity_boost": 0.55}
MODEL_ID = "eleven_multilingual_v2"


def _cache_path(voice_id: str, text: str) -> Path:
    digest = hashlib.sha256(f"{voice_id}::{text}".encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.mp3"


def is_available() -> bool:
    return bool(os.environ.get("ELEVENLABS_API_KEY"))


def _secret_present() -> bool:
    """Whether ELEVENLABS_API_KEY exists in Streamlit secrets -- membership
    check only, the value itself is never read or returned. Safe to call
    outside a Streamlit context (e.g. tests): returns False rather than
    raising."""
    try:
        import streamlit as st
        return "ELEVENLABS_API_KEY" in st.secrets
    except Exception:
        return False


def _new_diagnostics() -> dict:
    return {
        "secret_present": None,
        "env_bootstrap": None,
        "provider_available": None,
        "registry_resolved": None,
        "provider": None,
        "voice_id": None,
        "http_attempted": False,
        "http_status": None,
        "http_duration_ms": None,
        "bytes_received": 0,
        "valid_audio": False,
        "cache_source": None,   # "fresh" | "cached" | "invalidated" | "bypassed"
        "final_outcome": "unknown",
        "audio_bytes": None,
    }


def _synthesize_core(text: str, voice_standard: str = "SVS-1", bypass_cache: bool = False) -> dict:
    """The one real synthesis implementation. Always returns a diagnostics
    dict; `diag["audio_bytes"]` holds the result (or None). `bypass_cache`
    exists only for Sage Voice Diagnostics, so a diagnostic run can prove
    the *current* key works rather than silently reading an old cached
    clip and reporting a false pass."""
    diag = _new_diagnostics()

    if not text or not text.strip():
        diag["final_outcome"] = "empty_text"
        return diag

    diag["secret_present"] = _secret_present()
    diag["env_bootstrap"] = bool(os.environ.get("ELEVENLABS_API_KEY"))

    try:
        provider, provider_voice_id = resolve_voice(voice_standard)
        diag["registry_resolved"] = True
        diag["provider"] = provider
        diag["voice_id"] = provider_voice_id
    except VoiceNotFoundError:
        diag["registry_resolved"] = False
        diag["final_outcome"] = "voice_not_registered"
        return diag

    if provider != "elevenlabs":
        diag["final_outcome"] = "unsupported_provider"
        return diag

    diag["provider_available"] = is_available()

    cache_file = _cache_path(provider_voice_id, text)
    if bypass_cache:
        diag["cache_source"] = "bypassed"
    elif cache_file.exists():
        cached = cache_file.read_bytes()
        if cached:
            diag["cache_source"] = "cached"
            diag["bytes_received"] = len(cached)
            diag["valid_audio"] = True
            diag["final_outcome"] = "success"
            diag["audio_bytes"] = cached
            return diag
        # A zero-byte cache file can only happen from a corrupted/partial
        # write -- never written by this code path, but detected rather
        # than trusted blindly.
        diag["cache_source"] = "invalidated"

    if not diag["provider_available"]:
        diag["final_outcome"] = "missing_secret"
        return diag

    if diag["cache_source"] is None:
        diag["cache_source"] = "fresh"

    try:
        import requests
        t0 = time.monotonic()
        diag["http_attempted"] = True
        resp = requests.post(
            ELEVENLABS_TTS_URL.format(voice_id=provider_voice_id),
            headers={
                "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json={"text": text, "model_id": MODEL_ID, "voice_settings": VOICE_SETTINGS},
            timeout=30,
        )
        diag["http_duration_ms"] = round((time.monotonic() - t0) * 1000, 1)
        diag["http_status"] = resp.status_code

        if resp.status_code != 200:
            diag["final_outcome"] = "auth_failed" if resp.status_code in (401, 403) else "api_rejected"
            return diag
        if not resp.content:
            diag["final_outcome"] = "empty_audio"
            return diag

        diag["bytes_received"] = len(resp.content)
        diag["valid_audio"] = True
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_bytes(resp.content)
        diag["audio_bytes"] = resp.content
        diag["final_outcome"] = "success"
        return diag
    except requests.exceptions.RequestException:
        diag["final_outcome"] = "network_failure"
        return diag
    except Exception:
        diag["final_outcome"] = "unknown"
        return diag


def synthesize(text: str, voice_standard: str = "SVS-1") -> bytes | None:
    """Real ElevenLabs synthesis for `text`, spoken as `voice_standard`.
    Returns audio bytes, or None if unavailable/failed -- never raises.
    Unchanged external contract; internally a one-line wrapper around
    _synthesize_core()."""
    return _synthesize_core(text, voice_standard)["audio_bytes"]
