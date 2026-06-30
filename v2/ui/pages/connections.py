"""MusicWorks™ V4.1 — Connections: manage all service integrations."""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html
from execution.connections_store import (
    SERVICES, SERVICE_MAP, get_connection_status, get_all_statuses,
    test_connection, is_connected,
)
from execution.connectors import ALL_CONNECTORS

_CATEGORIES = [
    ("AI — Writing",    "Content generation"),
    ("AI — Video",      "Video production"),
    ("AI — Image",      "Image & design"),
    ("AI — Voice",      "Voice & avatar"),
    ("AI — Avatar",     "Avatar video"),
    ("AI — Design",     "Design briefs"),
    ("Publishing",      "Platform distribution"),
    ("Newsletter",      "Email marketing"),
    ("Website",         "Web presence"),
    ("Distribution",    "Music distribution"),
]


def render():
    page_header("Connections", "Every service. Every status. One place.", "🔌")

    render_html("""
    <div class="mw-card" style="padding:1.25rem 1.5rem; border-left:3px solid #D4A853; margin-bottom:2rem;">
        <div style="font-size:13px; color:#C8C4BE; line-height:1.7;">
            <strong style="color:#D4A853;">Security note:</strong>
            API keys are never stored by MusicWorks. They are read from environment variables
            or Streamlit secrets. Set keys in your <code>.streamlit/secrets.toml</code> file
            or in the Streamlit Cloud dashboard under Settings → Secrets.
        </div>
    </div>
    """)

    # ── Connector architecture overview ───────────────────────────────────────
    with st.expander("Connector Architecture", expanded=False):
        render_html("""
        <div style="font-size:13px; color:#C8C4BE; line-height:1.8; margin-bottom:0.75rem;">
            MusicWorks uses a <strong style="color:#D4A853;">Connector Layer</strong> between jobs and providers.
            When new AI tools emerge, only the connector needs updating — jobs, workers, and UI stay unchanged.
        </div>
        """)
        cols = st.columns(len(ALL_CONNECTORS))
        for col, connector in zip(cols, ALL_CONNECTORS):
            with col:
                avail = connector.available_provider()
                avail_html = (
                    f'<span style="color:#22C55E; font-size:11px; font-weight:600;">● {avail}</span>'
                    if avail else
                    '<span style="color:#6A6460; font-size:11px;">● not configured</span>'
                )
                render_html(f"""
                <div class="mw-card" style="padding:0.75rem; text-align:center;">
                    <div style="font-size:20px; margin-bottom:4px;">{connector.icon}</div>
                    <div style="font-size:11px; font-weight:700; color:#F0EDE8; margin-bottom:4px;">{connector.name}</div>
                    <div style="margin-bottom:4px;">{avail_html}</div>
                    <div style="font-size:9px; color:#6A6460; line-height:1.4;">
                        Future: {', '.join(connector.future_providers[:2]) if connector.future_providers else 'planned'}
                    </div>
                </div>
                """)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Summary stats ─────────────────────────────────────────────────────────
    all_statuses = get_all_statuses()
    connected_n = sum(1 for s in all_statuses if s["connected"])
    total_n = len(all_statuses)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_html(f"""
        <div class="mw-card" style="padding:1.25rem; text-align:center; border-top:3px solid #22C55E;">
            <div style="font-size:28px; font-weight:800; color:#22C55E;">{connected_n}</div>
            <div style="font-size:11px; color:#8A8480; margin-top:4px; text-transform:uppercase;">Connected</div>
        </div>
        """)
    with c2:
        render_html(f"""
        <div class="mw-card" style="padding:1.25rem; text-align:center; border-top:3px solid #6A6460;">
            <div style="font-size:28px; font-weight:800; color:#6A6460;">{total_n - connected_n}</div>
            <div style="font-size:11px; color:#8A8480; margin-top:4px; text-transform:uppercase;">Not Configured</div>
        </div>
        """)
    with c3:
        render_html(f"""
        <div class="mw-card" style="padding:1.25rem; text-align:center; border-top:3px solid #D4A853;">
            <div style="font-size:28px; font-weight:800; color:#D4A853;">{total_n}</div>
            <div style="font-size:11px; color:#8A8480; margin-top:4px; text-transform:uppercase;">Total Services</div>
        </div>
        """)

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)

    # ── Group by category ─────────────────────────────────────────────────────
    services_by_cat: dict[str, list] = {}
    for s in SERVICES:
        cat = s[2]
        services_by_cat.setdefault(cat, []).append(s)

    grouped_cats = list(dict.fromkeys(s[2] for s in SERVICES))

    for cat in grouped_cats:
        cat_services = services_by_cat.get(cat, [])
        render_html(f'<div class="mw-section-label">{cat}</div>')

        cols = st.columns(min(len(cat_services), 3))
        for col, svc in zip(cols, cat_services):
            key, name, _, env_var, icon, color, desc, url = svc
            status = get_connection_status(key)
            _render_service_card(col, key, name, icon, color, desc, url, env_var, status)

        if len(cat_services) > 3:
            extra_rows = [cat_services[i:i+3] for i in range(3, len(cat_services), 3)]
            for row in extra_rows:
                cols2 = st.columns(min(len(row), 3))
                for col, svc in zip(cols2, row):
                    key, name, _, env_var, icon, color, desc, url = svc
                    status = get_connection_status(key)
                    _render_service_card(col, key, name, icon, color, desc, url, env_var, status)

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

    # ── How to configure ─────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    with st.expander("How to configure API keys", expanded=False):
        render_html("""
        <div style="font-size:13px; color:#C8C4BE; line-height:1.8;">
            <strong style="color:#D4A853;">Option 1 — Local development:</strong><br>
            Create <code>.streamlit/secrets.toml</code> in your project root:<br>
            <pre style="background:#0A0A0A; padding:1rem; border-radius:8px; font-size:12px; margin:0.5rem 0;">
ANTHROPIC_API_KEY = "sk-ant-..."
ELEVENLABS_API_KEY = "..."
GOOGLE_VEO_API_KEY = "..."
            </pre>

            <strong style="color:#D4A853;">Option 2 — Streamlit Cloud:</strong><br>
            Go to your app → Settings → Secrets → paste each key in the format above.<br><br>

            <strong style="color:#D4A853;">Option 3 — Environment variables:</strong><br>
            Set <code>ANTHROPIC_API_KEY=sk-ant-...</code> in your shell or system environment.<br><br>

            <strong style="color:#F59E0B;">Publishing platforms (Instagram, TikTok, YouTube, etc.):</strong><br>
            Platform API keys enable future automated publishing. For now, MusicWorks
            prepares your content for manual publishing. No platform keys are required
            for the core Media Factory to operate.
        </div>
        """)


def _render_service_card(col, key: str, name: str, icon: str, color: str,
                          desc: str, url: str, env_var: str, status: dict):
    with col:
        connected   = status["connected"]
        last_tested = status.get("last_tested", "")[:10] if status.get("last_tested") else ""
        last_status = status.get("last_status", "")
        last_msg    = status.get("last_message", "")

        border_color = "#22C55E" if connected else "#2A2A2A"
        dot_color    = "#22C55E" if connected else "#6A6460"
        dot_label    = "Connected" if connected else "Not configured"

        render_html(f"""
        <div class="mw-card" style="padding:1rem; border-top:3px solid {border_color}; margin-bottom:0.75rem; min-height:180px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <span style="font-size:24px;">{icon}</span>
                <div>
                    <div style="font-size:14px; font-weight:700; color:#F0EDE8;">{name}</div>
                    <div style="font-size:10px; color:{dot_color}; font-weight:600;">● {dot_label}</div>
                </div>
            </div>
            <div style="font-size:11px; color:#8A8480; line-height:1.5; margin-bottom:8px;">{desc}</div>
            {f'<div style="font-size:10px; color:#6A6460; margin-bottom:6px;">Env var: <code style="color:#9B89D4;">{env_var}</code></div>' if env_var else ''}
            {f'<div style="font-size:10px; color:#6A6460;">Last tested: {last_tested}</div>' if last_tested else ''}
            {f'<div style="font-size:10px; color:#{"22C55E" if last_status == "connected" else "EF4444"};">{last_msg[:60]}</div>' if last_msg else ''}
        </div>
        """)

        # Test button
        if st.button(f"Test {name}", key=f"test_{key}", use_container_width=True):
            with st.spinner(f"Testing {name}…"):
                success, msg = test_connection(key)
            if success:
                st.success(f"✓ {msg}")
            else:
                st.warning(f"⚠ {msg}")
            st.rerun()
