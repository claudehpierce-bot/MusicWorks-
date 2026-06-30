"""MusicWorks™ V3 — Executive Interface."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from ui.styles import inject_styles
from ui.components import nav_sidebar

st.set_page_config(
    page_title="MusicWorks™ by MindSpark Labs",
    page_icon="🎵",
    layout="wide",
)


@st.cache_resource
def _bootstrap_demo():
    """Seed demo data once on cold start if database is empty. Runs once per server instance."""
    try:
        from scripts.seed_demo import seed_demo
        seed_demo(silent=True)
    except Exception:
        pass
    return True


_bootstrap_demo()

inject_styles()
page = nav_sidebar()

if page == "home":
    from ui.pages.home import render
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
elif page == "analytics":
    from ui.pages.analytics import render
    render()
elif page == "brand_brain":
    from ui.pages.brand_brain import render
    render()
elif page == "settings":
    from ui.pages.settings import render
    render()
else:
    from ui.pages.home import render
    render()
