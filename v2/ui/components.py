"""MusicWorks™ V3 — Shared UI components."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import date


# ── HTML render helper ────────────────────────────────────────────────────────

def render_html(html: str):
    """Render HTML stripping per-line leading whitespace so Markdown never
    mis-reads indented closing tags as indented code blocks."""
    import re
    cleaned = re.sub(r'\n[ \t]+', '\n', html.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# ── Navigation ────────────────────────────────────────────────────────────────

_CREATOR_NAV = [
    ("🏠", "Home",             "home"),
    ("🚀", "Launch Campaign",  "wizard"),
    ("📄", "Creative Brief",   "creative_brief"),
    ("🎯", "Media Blitz",      "media_blitz"),
    ("👥", "Artists",          "artists"),
    ("📚", "Media Library",    "media_library"),
    ("📊", "Results",          "analytics"),
]

_STUDIO_NAV = [
    ("🏠", "Home",             "home"),
    ("🏭", "Media Factory",    "media_studio"),
    ("👥", "Artists",          "artists"),
    ("📋", "Production",       "production"),
    ("📅", "Calendar",         "calendar"),
    ("🎵", "Projects",         "projects"),
    ("🗄️", "Studio",           "studio"),
    ("📦", "Releases",         "campaigns"),
    ("📄", "Creative Brief",   "creative_brief"),
    ("✅", "Asset Review",     "approval"),
    ("🎯", "Media Blitz",      "media_blitz"),
    ("🚀", "Publishing",       "publishing"),
    ("📊", "Analytics",        "analytics"),
    ("🧠", "Brand Brain",      "brand_brain"),
    ("🔌", "Connections",      "connections"),
    ("🛡️", "Compliance",       "compliance"),
    ("⚙",  "Settings",         "settings"),
]


def _sage_nav_presence():
    """Sage's compact avatar in the nav rail -- a calm, static, unnarrated
    identity marker per DS-1 (she does not speak from every page load; her
    narrated moments live at the specific workflow surfaces in
    ui/sage.py::render_moment, called from Home, the Wizard, the Creative
    Brief, and the Boardroom)."""
    try:
        import ui.sage as sage
        avatar = sage.avatar_html("avatar_small", width=36)
    except Exception:
        return
    if not avatar:
        return

    col_a, col_b = st.columns([1, 4])
    with col_a:
        render_html(avatar)
    with col_b:
        st.markdown(
            "<div style='font-size:12px;color:#F0EDE8;font-weight:600;padding-top:6px;'>Sage</div>"
            "<div style='font-size:9px;color:#6A6460;margin-top:-2px;'>Institutional Guide</div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)


def nav_sidebar() -> str:
    """Render left navigation. Returns current page id."""
    if "studio_mode" not in st.session_state:
        st.session_state.studio_mode = False

    with st.sidebar:
        st.markdown("""
        <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid #1E1E1E; margin-bottom: 1rem;">
            <div style="font-family: 'Inter', sans-serif; font-size: 19px; font-weight: 800;
                        color: #F0EDE8; letter-spacing: -0.5px;">
                MusicWorks™
            </div>
            <div style="font-size: 10px; color: #D4A853; margin-top: 3px;
                        letter-spacing: 0.8px; text-transform: uppercase;">
                The Creative Agency Operating System™
            </div>
            <div style="font-size: 9px; color: #6A6460; margin-top: 2px; font-style: italic;">
                Create the music. We'll build the movement.
            </div>
        </div>
        """, unsafe_allow_html=True)

        _sage_nav_presence()

        current = st.session_state.get("page", "home")
        studio_mode = st.session_state.studio_mode

        nav_items = _STUDIO_NAV if studio_mode else _CREATOR_NAV

        for icon, label, page_id in nav_items:
            is_active = current == page_id
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = page_id
                st.rerun()

        # ── Mode toggle ────────────────────────────────────────────────────────
        st.markdown("""
        <div class="mw-mode-section">
            <div class="mw-mode-label">View Mode</div>
        </div>
        """, unsafe_allow_html=True)

        mode_col1, mode_col2 = st.columns(2)
        with mode_col1:
            creator_type = "primary" if not studio_mode else "secondary"
            if st.button("✨ Creator", key="mode_creator", use_container_width=True, type=creator_type):
                st.session_state.studio_mode = False
                st.rerun()
        with mode_col2:
            studio_type = "primary" if studio_mode else "secondary"
            if st.button("⚙ Studio", key="mode_studio", use_container_width=True, type=studio_type):
                st.session_state.studio_mode = True
                st.rerun()

        # Active artist card
        st.markdown("""
        <div style="margin-top: 1.25rem;">
            <div style="background: linear-gradient(135deg, #1A0F42, #2D1B69);
                        border-radius: 10px; padding: 0.875rem 1rem;
                        border: 1px solid rgba(212,168,83,0.2);">
                <div style="font-size: 10px; color: #D4A853; font-weight: 600;
                            letter-spacing: 0.6px; text-transform: uppercase; margin-bottom: 4px;">
                    Active Artist
                </div>
                <div style="font-size: 13px; color: #F0EDE8; font-weight: 600;">
                    Fire &amp; Flow Gospel
                </div>
                <div style="font-size: 11px; color: #8A8480; margin-top: 2px;">
                    Becoming Vol. 1
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return current


# ── Page header ───────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "", icon: str = ""):
    icon_html = f'<span style="margin-right:10px;">{icon}</span>' if icon else ""
    sub_html = (
        f'<p style="color:#8A8480; font-size:15px; margin:0.25rem 0 0 0;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(
        f"""<div style="margin-bottom:2rem;">
            <h1 style="margin:0;">{icon_html}{title}</h1>
            {sub_html}
        </div>""",
        unsafe_allow_html=True,
    )


# ── Navigation helper ─────────────────────────────────────────────────────────

def navigate_to(page: str, **kwargs):
    """Set page and optional session state then rerun."""
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()


# ── Status badge HTML ─────────────────────────────────────────────────────────

def status_badge(status: str) -> str:
    MAP = {
        "APPROVED":           ("badge-approved", "✓ Approved"),
        "READY_FOR_REVIEW":   ("badge-pending",  "● Pending"),
        "REVISION_REQUESTED": ("badge-revision", "↺ Revision"),
        "REJECTED":           ("badge-rejected", "✗ Rejected"),
    }
    cls, label = MAP.get(status, ("badge-pending", status))
    return f'<span class="badge {cls}">{label}</span>'


# ── Countdown ─────────────────────────────────────────────────────────────────

def countdown_days(release_date_str: str) -> int:
    try:
        release = date.fromisoformat(release_date_str)
        return (release - date.today()).days
    except Exception:
        return 0


# ── Progress bar HTML ─────────────────────────────────────────────────────────

def progress_bar_html(pct: float, label: str = "") -> str:
    pct = max(0, min(100, pct))
    label_html = f'<div style="font-size:11px;color:#8A8480;margin-bottom:4px;">{label}</div>' if label else ""
    return f'{label_html}<div class="mw-progress-track"><div class="mw-progress-fill" style="width:{pct:.0f}%;"></div></div>'


# ── Tag list HTML ─────────────────────────────────────────────────────────────

def tag_list_html(items: list, cls: str = "tag") -> str:
    return "".join(f'<span class="{cls}">{item}</span>' for item in items)


# ── Asset type icon map ───────────────────────────────────────────────────────

ASSET_ICONS = {
    "caption_instagram": "📷",
    "caption_tiktok":    "📱",
    "caption_youtube":   "▶️",
    "caption_facebook":  "📘",
    "blog_post":         "📝",
    "press_release":     "📰",
    "church_blurb":      "⛪",
    "thumbnail_concept": "🖼️",
    "video_package":     "🎬",
}

TYPE_ORDER = {
    "video_package":     0,
    "caption_instagram": 1,
    "caption_tiktok":    2,
    "caption_youtube":   3,
    "caption_facebook":  4,
    "blog_post":         5,
    "press_release":     6,
    "church_blurb":      7,
    "thumbnail_concept": 8,
}
