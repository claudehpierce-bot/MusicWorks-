"""MusicWorks™ — Sage's governed avatar renderer.

Split out of ui/sage.py so ui/components.py's nav-rail presence marker can
render Sage's avatar without importing the full ui.sage module. ui.sage
itself imports ui.components (for render_html), so ui.components importing
ui.sage back created a circular dependency between the two -- under some
import orderings that left ui.sage only partially initialized, missing
everything defined after the point circular re-entry occurred (including
begin_script_run()).

This module has zero dependency on ui.components or ui.sage, so it can be
imported safely from either direction. It contains only the governed
avatar lookup/render -- no identity, transcript, voice, or message logic;
that all still lives solely in ui/sage.py.
"""
import base64

from execution.brand_asset_registry import AssetNotFoundError, get_asset_metadata, get_derivative_path


def avatar_html(variant: str = "avatar_square", width: int = 64) -> str:
    """The one accessible way to render Sage's avatar anywhere in the app.

    st.image() in this Streamlit version has no `alt` parameter -- it emits
    alt="0" by default, which fails real accessibility requirements. This
    renders a plain <img> instead, with alt text sourced from the governed
    accessibility_description in the asset registry (never a filename, per
    that registry's own test suite). Returns "" if the asset can't resolve
    -- callers simply render nothing rather than a broken image.
    """
    try:
        path = get_derivative_path("SAGE-AVATAR-1", variant)
        meta = get_asset_metadata("SAGE-AVATAR-1")
    except AssetNotFoundError:
        return ""
    alt = meta.get("accessibility_description", "Sage, MindSpark Labs' institutional guide")
    ext = path.suffix.lstrip(".") or "webp"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img src="data:image/{ext};base64,{b64}" width="{width}" alt="{alt}" style="border-radius:8px;display:block;">'
