"""MusicWorks™ V3 — Executive Interface."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from ui.styles import inject_styles
from ui.components import nav_sidebar

st.set_page_config(
    page_title="MusicWorks™ — The Creative Agency Operating System™",
    page_icon="🎵",
    layout="wide",
)


@st.cache_resource
def _bootstrap_secrets():
    """Copy Streamlit Cloud secrets (st.secrets) into os.environ once on cold
    start. Every worker/config module reads API keys via os.environ — without
    this bridge, keys set in Settings -> Secrets are never detected."""
    try:
        for key, value in st.secrets.items():
            if isinstance(value, str) and key not in os.environ:
                os.environ[key] = value
    except Exception:
        pass
    return True


@st.cache_resource
def _bootstrap_demo():
    """Seed demo data once on cold start if database is empty. Runs once per server instance."""
    try:
        from scripts.seed_demo import seed_demo
        seed_demo(silent=True)
    except Exception:
        pass
    return True


_bootstrap_secrets()
_bootstrap_demo()

# Sage first-arrival fix: must run before any page renders, on every single
# script execution -- see ui/sage.py::begin_script_run() for why.
import ui.sage as _sage

if hasattr(_sage, "begin_script_run"):
    _sage.begin_script_run()
else:
    # ── TEMPORARY -- P0 Cloud import diagnostic. The deployed environment is
    # raising AttributeError on _sage.begin_script_run() despite the local
    # source and full test suite being clean. This proves exactly what
    # module Cloud actually imported, without ever printing secret values.
    # Remove this whole block once the module-resolution mismatch is found.
    import subprocess

    def _diag_git_commit() -> str:
        repo_root = Path(__file__).parent.parent
        try:
            out = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(repo_root), capture_output=True, text=True, timeout=5,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except Exception:
            pass
        try:
            head = (repo_root / ".git" / "HEAD").read_text().strip()
            if head.startswith("ref:"):
                ref_path = repo_root / ".git" / head.split(" ", 1)[1].strip()
                return ref_path.read_text().strip()
            return head
        except Exception:
            return "unavailable"

    _sage_attrs = sorted(
        a for a in dir(_sage)
        if not a.startswith("_") and (a.startswith("begin") or a.startswith("sage"))
    )
    _relevant_paths = [p for p in sys.path if "musicworks" in p.lower() or p.rstrip("/\\").lower().endswith("v2")]

    st.error("⚠️ Sage Startup Diagnostic — `begin_script_run()` was not found on the imported `_sage` module.")
    st.code(
        "\n".join([
            f"_sage.__file__            = {getattr(_sage, '__file__', 'unknown')}",
            f"hasattr begin_script_run  = False",
            f"public begin_/sage_ attrs = {_sage_attrs}",
            f"deployed git commit       = {_diag_git_commit()}",
            f"python version            = {sys.version.split()[0]}",
            f"sys.path (relevant)       = {_relevant_paths}",
        ]),
        language="text",
    )
    st.stop()
    # ── END TEMPORARY diagnostic block ──────────────────────────────────────

inject_styles()
page = nav_sidebar()

if page == "home":
    from ui.pages.home import render
    render()
elif page == "media_studio":
    from ui.pages.media_studio import render
    render()
elif page == "production":
    from ui.pages.production import render
    render()
elif page == "calendar":
    from ui.pages.calendar import render
    render()
elif page == "artists":
    from ui.pages.artists import render
    render()
elif page == "projects":
    from ui.pages.projects import render
    render()
elif page == "wizard":
    from ui.pages.wizard import render
    render()
elif page == "studio":
    from ui.pages.studio import render
    render()
elif page == "campaigns":
    from ui.pages.campaigns import render
    render()
elif page == "approval":
    from ui.pages.approval import render
    render()
elif page == "publishing":
    from ui.pages.publishing import render
    render()
elif page == "media_blitz":
    from ui.pages.media_blitz import render
    render()
elif page == "creative_brief":
    from ui.pages.creative_brief import render
    render()
elif page == "analytics":
    from ui.pages.analytics import render
    render()
elif page == "brand_brain":
    from ui.pages.brand_brain import render
    render()
elif page == "connections":
    from ui.pages.connections import render
    render()
elif page == "compliance":
    from ui.pages.compliance import render
    render()
elif page == "media_library":
    from ui.pages.media_library import render
    render()
elif page == "settings":
    from ui.pages.settings import render
    render()
else:
    from ui.pages.home import render
    render()
