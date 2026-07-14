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
network call and returns real audio bytes. Without a key (the state of
this repo's dev environment as of this milestone -- no key has been
configured), every call cleanly returns None and the UI shows transcript
only, exactly the DS-1 / SAGE_PERSONA "text guarantees accessibility"
requirement, not a fallback bolted on afterward.
"""
import hashlib
import os
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


def synthesize(text: str, voice_standard: str = "SVS-1") -> bytes | None:
    """Real ElevenLabs synthesis for `text`, spoken as `voice_standard`.
    Returns audio bytes, or None if unavailable/failed -- never raises."""
    if not text or not text.strip():
        return None
    try:
        provider, provider_voice_id = resolve_voice(voice_standard)
    except VoiceNotFoundError:
        return None
    if provider != "elevenlabs":
        return None  # only provider wired up so far

    cache_file = _cache_path(provider_voice_id, text)
    if cache_file.exists():
        return cache_file.read_bytes()

    if not is_available():
        return None

    try:
        import requests
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
        if resp.status_code != 200 or not resp.content:
            return None
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_bytes(resp.content)
        return resp.content
    except Exception:
        return None
