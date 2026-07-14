"""MusicWorks(tm) -- governance tests for the Sage brand asset pipeline.

Covers both governed assets:
  SAGE-AVATAR-1              -- Sage's canonical portrait (reusable in UI)
  SAGE-PRESENCE-REFERENCE-1  -- the dashboard mockup (design reference only,
                                 must never resolve as a reusable UI asset)

Dependency-free by design (this repo has no pytest suite yet): run directly
with `python tests/test_brand_assets.py` from the v2/ directory. Exits 0
on pass, 1 on any failure, and prints a PASS/FAIL line per check so a
failure is legible without a diff.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

REPO_ROOT = Path(__file__).parent.parent.parent
V2_ROOT = Path(__file__).parent.parent

results = []


def check(name: str, passed: bool, detail: str = ""):
    results.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    line = f"[{status}] {name}"
    if detail and not passed:
        line += f" -- {detail}"
    print(line)


def run():
    from execution.brand_asset_registry import (
        AssetNotFoundError,
        get_asset_metadata,
        get_asset_path,
        get_derivative_path,
        verify_checksum,
    )

    metas = {}

    # 1-3: common checks across both governed assets
    for asset_id in ("SAGE-AVATAR-1", "SAGE-PRESENCE-REFERENCE-1"):
        try:
            path = get_asset_path(asset_id)
            check(f"{asset_id}: canonical asset exists on disk", path.exists())
        except AssetNotFoundError as e:
            check(f"{asset_id}: canonical asset exists on disk", False, str(e))

        try:
            meta = get_asset_metadata(asset_id)
            metas[asset_id] = meta
            check(
                f"{asset_id}: registry entry resolves with expected fields",
                all(k in meta for k in (
                    "asset_id", "subject", "status", "canonical_source_path",
                    "checksum_sha256", "accessibility_description",
                    "approved_use_contexts", "prohibited_modifications",
                    "derivatives", "reusable_ui_asset",
                )),
            )
        except AssetNotFoundError as e:
            check(f"{asset_id}: registry entry resolves with expected fields", False, str(e))
            metas[asset_id] = {}

        try:
            check(f"{asset_id}: checksum matches approved source", verify_checksum(asset_id))
        except AssetNotFoundError as e:
            check(f"{asset_id}: checksum matches approved source", False, str(e))

        alt = metas.get(asset_id, {}).get("accessibility_description", "")
        check(
            f"{asset_id}: accessibility description present and not a filename",
            bool(alt) and not alt.endswith(".png") and not alt.endswith(".webp"),
        )

    # 4. SAGE-AVATAR-1 derivatives exist when referenced
    for variant in ("portrait_medium", "avatar_square", "avatar_small"):
        try:
            dpath = get_derivative_path("SAGE-AVATAR-1", variant)
            check(f"SAGE-AVATAR-1: derivative '{variant}' exists and resolves", dpath.exists())
        except AssetNotFoundError as e:
            check(f"SAGE-AVATAR-1: derivative '{variant}' exists and resolves", False, str(e))

    # 5. Governance distinction is real and machine-checkable, not just prose:
    # the avatar is a reusable UI asset, the presence reference is not, and
    # the presence reference has zero registered derivatives.
    avatar_meta = metas.get("SAGE-AVATAR-1", {})
    reference_meta = metas.get("SAGE-PRESENCE-REFERENCE-1", {})
    check("SAGE-AVATAR-1 is flagged reusable_ui_asset=true", avatar_meta.get("reusable_ui_asset") is True)
    check(
        "SAGE-PRESENCE-REFERENCE-1 is flagged reusable_ui_asset=false",
        reference_meta.get("reusable_ui_asset") is False,
    )
    check(
        "SAGE-PRESENCE-REFERENCE-1 has no registered derivatives",
        reference_meta.get("derivatives", "missing") == {},
    )

    # 6. The avatar canonical is a genuinely separate file from the presence
    # reference -- not accidentally still pointing at the mockup.
    try:
        avatar_checksum = get_asset_metadata("SAGE-AVATAR-1")["checksum_sha256"]
        reference_checksum = get_asset_metadata("SAGE-PRESENCE-REFERENCE-1")["checksum_sha256"]
        check("avatar canonical is a distinct file from the presence reference", avatar_checksum != reference_checksum)
    except AssetNotFoundError as e:
        check("avatar canonical is a distinct file from the presence reference", False, str(e))

    # 7. No absolute local filesystem paths committed in the registry JSON
    registry_text = (REPO_ROOT / "brand" / "registry" / "asset_registry.json").read_text(encoding="utf-8")
    has_absolute = ("C:\\" in registry_text) or (str(REPO_ROOT) in registry_text) or ("/home/" in registry_text)
    check("registry contains no absolute filesystem paths", not has_absolute)

    # 8. No base64 image data embedded in source (the resolver or the build
    # script -- not this test file, which necessarily mentions the pattern
    # names it's checking for)
    source_files = [
        V2_ROOT / "execution" / "brand_asset_registry.py",
        V2_ROOT / "scripts" / "build_sage_assets.py",
    ]
    has_base64_blob = False
    for f in source_files:
        text = f.read_text(encoding="utf-8")
        if "base64" in text.lower() or "iVBOR" in text or "data:image" in text:
            has_base64_blob = True
    check("no base64 image data embedded in source", not has_base64_blob)

    # 9. No external URL required to resolve either asset
    resolver_text = (V2_ROOT / "execution" / "brand_asset_registry.py").read_text(encoding="utf-8")
    check("resolver makes no external network calls", "http://" not in resolver_text and "https://" not in resolver_text)

    # 10. Missing asset fails clearly -- never silently substitutes
    try:
        get_asset_metadata("SAGE-AVATAR-DOES-NOT-EXIST")
        check("unknown asset ID raises AssetNotFoundError", False, "no exception raised")
    except AssetNotFoundError:
        check("unknown asset ID raises AssetNotFoundError", True)

    try:
        get_derivative_path("SAGE-AVATAR-1", "nonexistent_variant")
        check("unknown derivative variant raises AssetNotFoundError", False, "no exception raised")
    except AssetNotFoundError:
        check("unknown derivative variant raises AssetNotFoundError", True)

    try:
        get_derivative_path("SAGE-PRESENCE-REFERENCE-1", "avatar_small")
        check(
            "requesting a derivative from the presence reference raises AssetNotFoundError",
            False, "no exception raised -- presence reference must never resolve reusable derivatives",
        )
    except AssetNotFoundError:
        check("requesting a derivative from the presence reference raises AssetNotFoundError", True)

    # 11. UI/app code references either asset only through the resolver,
    # never a hard-coded path to a canonical file or its derivatives.
    offending = []
    search_root = V2_ROOT / "ui"
    if search_root.exists():
        for py_file in search_root.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            if (
                "sage_avatar_canonical" in text
                or "sage_presence_reference" in text
                or "brand/assets/sage" in text
                or "brand\\assets\\sage" in text
            ):
                offending.append(str(py_file.relative_to(V2_ROOT)))
    check("no hard-coded Sage asset paths in ui/", not offending, ", ".join(offending))

    print()
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"{passed}/{total} checks passed")
    return passed == total


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
