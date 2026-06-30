"""MusicWorks™ V3 — Creative Studio page (V3 roadmap preview)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html


_DEPARTMENTS = [
    {
        "icon": "✨",
        "name": "Spiritual Exploration",
        "desc": "Deep-dive theology sessions. Give the Studio a scripture, theme, or question — it maps the theological landscape, finds connecting passages, and surfaces the creative angles that honor the text.",
        "examples": ["'What does Hebrews 10:25 say about community?' → full theological map", "Scripture-to-song concept briefs", "Theme development from one verse to a full album arc"],
    },
    {
        "icon": "🎵",
        "name": "Musical Brainstorm",
        "desc": "Production and sound direction. Describe a feeling, a season, a scripture — the Studio returns genre directions, BPM ranges, instrumentation notes, and Afro-Gospel reference tracks.",
        "examples": ["'What would HLANGANA sound like as Sgija gospel?' → full production direction", "Arrangement concepts for diaspora worship contexts", "Tempo and key recommendations by campaign mode"],
    },
    {
        "icon": "🔤",
        "name": "Kingdom Words Naming",
        "desc": "Research and validate new Kingdom Words series entries. Provide a concept or biblical theme — the Studio searches African, Caribbean, and global languages for words that unlock the scripture.",
        "examples": ["'Find a word in Yoruba for 'covenant'' → research brief + pronunciation", "Episode concept development for the Kingdom Words series", "Cultural context validation for diaspora audiences"],
    },
    {
        "icon": "🎨",
        "name": "Visual Concepts",
        "desc": "Campaign visual direction briefs. The Studio translates a song's theology into specific scene descriptions, color stories, lighting guides, and photography directions — all rooted in Creative DNA.",
        "examples": ["'Visual concept for a song about community in exile' → full scene brief", "Color story development per campaign mode", "Shot list ideas for manual videography"],
    },
    {
        "icon": "🤖",
        "name": "AI Prompt Generation",
        "desc": "Production-ready Veo, Imagen, and Canva prompts. The Studio takes your creative concept and outputs optimized prompts for every AI tool in the MusicWorks pipeline.",
        "examples": ["Veo prompts optimized for Fire & Flow gospel atmosphere", "Canva design briefs with exact dimensions and style notes", "Imagen prompts for thumbnail concept generation"],
    },
]


def render():
    page_header("Creative Studio™", "AI-assisted creative exploration for every project.", "🎬")

    render_html("""
    <div style="background:linear-gradient(135deg, #0D0D0D, #1A0F42);
                border:1px solid rgba(212,168,83,0.3); border-radius:16px;
                padding:2.5rem; text-align:center; margin-bottom:2rem;">
        <div style="font-size:36px; margin-bottom:0.75rem;">🎬</div>
        <div style="font-size:22px; font-weight:800; color:#F0EDE8; margin-bottom:0.5rem;">
            Creative Studio™
        </div>
        <div style="font-size:14px; color:#9B89D4; margin-bottom:0.5rem;">
            Five AI-assisted creative departments. One unified creative workspace.
        </div>
        <div style="font-size:13px; color:#8A8480; margin-bottom:1.25rem;">
            Available as an add-on module in V3
        </div>
        <span class="badge badge-revision" style="font-size:12px; padding:4px 12px;">Coming in V3</span>
    </div>
    """)

    st.markdown("<div class='mw-section-label'>Five Creative Departments</div>", unsafe_allow_html=True)

    for dept in _DEPARTMENTS:
        with st.expander(f"{dept['icon']}  {dept['name']}", expanded=False):
            render_html(f"""
            <div style="font-size:14px; color:#C8C4BE; line-height:1.7; margin-bottom:1rem;">
                {dept['desc']}
            </div>
            """)

            st.markdown("<div style='font-size:11px; color:#8A8480; font-weight:600; letter-spacing:0.6px; text-transform:uppercase; margin-bottom:0.5rem;'>Examples</div>", unsafe_allow_html=True)
            for ex in dept["examples"]:
                render_html(f"""
                <div style="font-size:12px; color:#D4A853; padding:4px 0;
                            border-left:2px solid #D4A853; padding-left:10px; margin-bottom:4px;">
                    {ex}
                </div>
                """)

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)

    # Pricing preview
    st.markdown("<div class='mw-section-label'>Pricing Tiers (V3 Roadmap)</div>", unsafe_allow_html=True)

    tiers = [
        ("Core", "Campaign generation + Approval Queue + Publishing", "#8A8480"),
        ("Professional", "Core + Brand Brain + Analytics + Multi-artist support", "#C8C4BE"),
        ("Creative Studio™ Add-on", "Professional + all 5 Studio departments", "#D4A853"),
        ("Enterprise", "Custom volume + dedicated onboarding + ministry licensing", "#FF6B2B"),
    ]

    cols = st.columns(4)
    for col, (name, desc, color) in zip(cols, tiers):
        col.markdown(f"""
        <div class="mw-card" style="padding:1.25rem; text-align:center; border-top:3px solid {color};">
            <div style="font-size:13px; font-weight:700; color:{color}; margin-bottom:0.5rem;">{name}</div>
            <div style="font-size:11px; color:#8A8480; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    st.caption("Creative Studio™ is designed as a separate product with shared brand identity. It is not part of the core campaign pipeline.")
