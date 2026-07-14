"""MusicWorks(tm) / MindSpark -- governed brand asset resolver.

Application code must never reference brand asset files by a hard-coded
path. It asks this module for an institutional asset ID (e.g.
"SAGE-AVATAR-1") and gets back a resolved, verified path. The registry
(brand/registry/asset_registry.json) is the single source of truth for
what that ID currently points to; this module is the single place that
turns registry-relative paths into real filesystem paths.

A missing or unregistered asset raises AssetNotFoundError rather than
silently falling back to a placeholder or a different image -- an
institutional guide's identity is never allowed to quietly substitute.
"""
import json
from functools import lru_cache
from pathlib import Path

# v2/execution/ -> v2/ -> musicworks/ (brand/ is a sibling of v2/, not nested
# inside it, so this registry is not tied to any one app version).
_REPO_ROOT = Path(__file__).parent.parent.parent
_BRAND_DIR = _REPO_ROOT / "brand"
_REGISTRY_PATH = _BRAND_DIR / "registry" / "asset_registry.json"


class AssetNotFoundError(Exception):
    """Raised when an asset ID isn't registered, or a registered file is
    missing from disk. Callers must not catch this and substitute a
    different image -- surface it, don't paper over it."""


@lru_cache(maxsize=1)
def _load_registry() -> dict:
    if not _REGISTRY_PATH.exists():
        raise AssetNotFoundError(f"Brand asset registry not found: {_REGISTRY_PATH.name}")
    return json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))


def get_asset_metadata(asset_id: str) -> dict:
    """Full registry entry for an asset ID (status, checksum, approved use
    contexts, prohibited modifications, etc)."""
    registry = _load_registry()
    if asset_id not in registry:
        raise AssetNotFoundError(f"Unregistered asset ID: {asset_id!r}")
    return registry[asset_id]


def get_asset_path(asset_id: str) -> Path:
    """Resolved path to an asset's canonical (full-resolution) source file."""
    meta = get_asset_metadata(asset_id)
    path = _REPO_ROOT / meta["canonical_source_path"]
    if not path.exists():
        raise AssetNotFoundError(
            f"{asset_id} is registered but its canonical file is missing on disk."
        )
    return path


def get_derivative_path(asset_id: str, variant: str) -> Path:
    """Resolved path to a named derivative (e.g. 'avatar_small').

    Raises AssetNotFoundError if the variant isn't registered OR if it's
    registered but hasn't been built yet (run
    v2/scripts/build_sage_assets.py) -- never silently returns the
    canonical image as a stand-in for a missing derivative.
    """
    meta = get_asset_metadata(asset_id)
    derivatives = meta.get("derivatives", {})
    if variant not in derivatives:
        known = ", ".join(sorted(derivatives)) or "none registered"
        raise AssetNotFoundError(f"Unknown derivative {variant!r} for {asset_id}. Known: {known}")
    path = _REPO_ROOT / derivatives[variant]["path"]
    if not path.exists():
        raise AssetNotFoundError(
            f"{asset_id} derivative {variant!r} is registered but not built yet "
            f"-- run v2/scripts/build_sage_assets.py."
        )
    return path


def verify_checksum(asset_id: str) -> bool:
    """True if the canonical file on disk still matches the checksum recorded
    at approval time -- a tamper/drift guard, not just an existence check."""
    import hashlib
    meta = get_asset_metadata(asset_id)
    path = get_asset_path(asset_id)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    return actual == meta.get("checksum_sha256")
