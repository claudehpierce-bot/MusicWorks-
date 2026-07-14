"""MusicWorks(tm) / MindSpark -- governed voice resolver.

Application code must never reference a provider voice ID directly. It asks
this module for an institutional voice standard (e.g. "SVS-1") and gets back
the provider + provider-specific voice ID together. The registry
(brand/registry/voice_registry.json) is the single source of truth for what
that standard currently resolves to.

Mirrors v2/execution/brand_asset_registry.py's pattern deliberately --
identity resolution (visual or vocal) should look the same everywhere in
this codebase, not invent a second convention.
"""
import json
from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
_REGISTRY_PATH = _REPO_ROOT / "brand" / "registry" / "voice_registry.json"


class VoiceNotFoundError(Exception):
    """Raised when a voice standard isn't registered. Callers must not catch
    this and substitute a different voice -- an institutional guide's voice
    is never allowed to quietly substitute."""


@lru_cache(maxsize=1)
def _load_registry() -> dict:
    if not _REGISTRY_PATH.exists():
        raise VoiceNotFoundError(f"Voice registry not found: {_REGISTRY_PATH.name}")
    return json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))


def get_voice_metadata(voice_standard: str) -> dict:
    registry = _load_registry()
    if voice_standard not in registry:
        raise VoiceNotFoundError(f"Unregistered voice standard: {voice_standard!r}")
    return registry[voice_standard]


def resolve_voice(voice_standard: str) -> tuple[str, str]:
    """Returns (provider, provider_voice_id) for a voice standard."""
    meta = get_voice_metadata(voice_standard)
    provider = meta.get("provider")
    provider_voice_id = meta.get("provider_voice_id")
    if not provider or not provider_voice_id:
        raise VoiceNotFoundError(f"{voice_standard} is registered but incompletely configured.")
    return provider, provider_voice_id
