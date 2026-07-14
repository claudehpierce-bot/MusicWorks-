"""MusicWorks(tm) / MindSpark -- Sage governed asset builder.

Two distinct governed assets, per Founder direction (2026-07-14 asset
governance review):

  SAGE-AVATAR-1              -- Sage's canonical portrait. Her identity.
                                 Reusable in UI.
  SAGE-PRESENCE-REFERENCE-1  -- The composed dashboard mockup. A design-
                                 language reference (layout, spacing,
                                 typography, palette, hierarchy,
                                 interaction language). NOT a reusable UI
                                 asset -- never crop production UI pieces
                                 out of it.

This script has two independent steps:

  extract_avatar_canonical() -- a deliberate, one-time (or explicitly
      re-triggered) promotion: losslessly crops Sage's portrait out of
      the SAGE-PRESENCE-REFERENCE-1 source and saves it as its own PNG
      master. This is what makes SAGE-AVATAR-1's canonical file, not a
      derivative of it -- once run, the output is registered as
      canonical in its own right and is NOT silently regenerated on
      every build (that would let the "canonical" checksum drift under
      you). Re-run only when the Founder approves a new source portrait.

  build_avatar_derivatives() -- the resizeable-derivative step, same as
      before, but now sourced from SAGE-AVATAR-1's own canonical file,
      not reaching back into the presence-reference mockup each time.

Run standalone: `python scripts/build_sage_assets.py`
"""
import hashlib
import sys
from pathlib import Path

from PIL import Image

BRAND_DIR = Path(__file__).parent.parent.parent / "brand"

PRESENCE_REFERENCE_PATH = BRAND_DIR / "assets" / "sage" / "presence_reference" / "sage_presence_reference_2026.png"

AVATAR_DIR = BRAND_DIR / "assets" / "sage" / "avatar"
AVATAR_CANONICAL_PATH = AVATAR_DIR / "sage_avatar_canonical_2026.png"
AVATAR_DERIVATIVES_DIR = AVATAR_DIR / "derivatives"

# Crop coordinates within the 1402x1122 presence-reference source, fixed by
# visual inspection once -- documents exactly how the avatar canonical was
# isolated, for audit purposes. This crop is only ever performed against the
# presence-reference source; it does not run against the avatar canonical.
PORTRAIT_CROP_BOX = (224, 16, 622, 580)   # left, top, right, bottom -> 398x564

# The square/avatar derivative crop is the top square subset of the AVATAR
# CANONICAL itself (face + hair + top of shoulders) -- sourced from the
# avatar canonical, not from the presence-reference.
SQUARE_CROP_BOX = (0, 0, 398, 398)

DERIVATIVE_SPECS = {
    "sage_portrait_medium.webp": {"source": "portrait", "size": (480, 680)},
    "sage_avatar_square.webp":   {"source": "square",   "size": (320, 320)},
    "sage_avatar_small.webp":    {"source": "square",   "size": (96, 96)},
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_avatar_canonical() -> dict:
    """Losslessly isolate Sage's portrait from the presence-reference mockup
    and save it as SAGE-AVATAR-1's own canonical PNG. Deliberate promotion
    step, not an auto-regenerated derivative."""
    if not PRESENCE_REFERENCE_PATH.exists():
        print(f"ERROR: presence-reference source missing at {PRESENCE_REFERENCE_PATH}", file=sys.stderr)
        sys.exit(1)

    source = Image.open(PRESENCE_REFERENCE_PATH).convert("RGB")
    portrait = source.crop(PORTRAIT_CROP_BOX)

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    # Lossless PNG, no resampling beyond the pixel-exact crop -- preserves
    # image quality of the source region exactly.
    portrait.save(AVATAR_CANONICAL_PATH, format="PNG", optimize=True)

    result = {
        "path": str(AVATAR_CANONICAL_PATH.relative_to(BRAND_DIR.parent)),
        "dimensions": {"width": portrait.width, "height": portrait.height},
        "checksum_sha256": _sha256(AVATAR_CANONICAL_PATH),
        "cropped_from": str(PRESENCE_REFERENCE_PATH.relative_to(BRAND_DIR.parent)),
        "crop_box": list(PORTRAIT_CROP_BOX),
    }
    print(f"extracted avatar canonical: {portrait.width}x{portrait.height} -> {AVATAR_CANONICAL_PATH}")
    return result


def build_avatar_derivatives() -> dict:
    """Resize derivatives, sourced from the avatar canonical (not the
    presence-reference mockup)."""
    if not AVATAR_CANONICAL_PATH.exists():
        print("ERROR: avatar canonical missing -- run extract_avatar_canonical() first", file=sys.stderr)
        sys.exit(1)

    canonical = Image.open(AVATAR_CANONICAL_PATH).convert("RGB")
    portrait = canonical  # the avatar canonical IS the portrait, full-frame
    square = canonical.crop(SQUARE_CROP_BOX)
    sources = {"portrait": portrait, "square": square}

    AVATAR_DERIVATIVES_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for filename, spec in DERIVATIVE_SPECS.items():
        src = sources[spec["source"]]
        resized = src.resize(spec["size"], Image.LANCZOS)
        out_path = AVATAR_DERIVATIVES_DIR / filename
        resized.save(out_path, format="WEBP", quality=90, method=6)
        results[filename] = {
            "path": str(out_path.relative_to(BRAND_DIR.parent)),
            "dimensions": {"width": resized.width, "height": resized.height},
            "checksum_sha256": _sha256(out_path),
            "source_region": spec["source"],
        }
        print(f"built {filename}: {resized.width}x{resized.height} -> {out_path}")
    return results


if __name__ == "__main__":
    extract_avatar_canonical()
    build_avatar_derivatives()
