"""MusicWorks™ V7 Phase 1 — The Live Creative Brief™.

The single source of creative truth every department reads from. Founder-
editable, versioned, and the home of selective regeneration — never a
"regenerate everything" button (V7 Constitution, Amendment I).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html, navigate_to
from brand_brain.artist_library import list_artists
from execution import campaign_store, brief_store
from execution.brief_store import BRIEF_FIELDS, FIELD_LABELS
from execution.brief_dependencies import REGEN_GROUPS, BRIEF_FIELD_REGEN_GROUPS, affected_groups

# Grouped for the form's layout only — mirrors brief_dependencies.py's own
# clustering so the page reads the same way the dependency table does.
FIELD_SECTIONS = [
    ("Foundational", ["campaign_theme", "scripture_emphasis"]),
    ("Naming & Message", ["campaign_title", "core_message", "call_to_action", "tagline"]),
    ("Audience & Strategy", ["target_audience", "campaign_goals", "artist_narrative", "platform_strategy"]),
    ("Tone & Atmosphere", ["emotion", "mood", "story"]),
    ("Visual Direction", ["visual_direction", "colour_direction"]),
    ("Discovery & SEO", ["keywords", "seo", "hashtags", "playlist_direction"]),
    ("Operational (Campaign Operations, not a regeneration trigger)", ["campaign_duration", "publishing_priority"]),
]


def _field_widget(field: str, value: str):
    long_fields = {"story", "artist_narrative", "core_message", "campaign_theme", "seo", "call_to_action"}
    if field in long_fields:
        return st.text_area(FIELD_LABELS[field], value=value or "", height=80, key=f"brief_{field}")
    return st.text_input(FIELD_LABELS[field], value=value or "", key=f"brief_{field}")


def render():
    page_header("Creative Brief", "The single source of creative truth your whole team works from.", "📄")

    artists = list_artists()
    if not artists:
        render_html('<div class="mw-card" style="text-align:center;padding:3rem;color:#8A8480;">Create an artist first.</div>')
        return

    names = [a["artist_name"] for a in artists]
    ids = [a["artist_id"] for a in artists]
    a_idx = st.selectbox("Artist:", range(len(names)), format_func=lambda i: names[i], key="cb_artist")
    artist_id = ids[a_idx]

    campaigns = campaign_store.list_campaigns(artist_id)
    if not campaigns:
        render_html(
            '<div class="mw-card" style="text-align:center;padding:2rem;color:#8A8480;">'
            '<div style="font-size:16px;color:#F0EDE8;margin-bottom:0.5rem;">No campaigns yet</div>'
            '<div style="font-size:13px;">Build one from the Launch Campaign wizard first — your Creative '
            'Director writes the first version of the Brief the moment your campaign is built.</div></div>'
        )
        if st.button("🚀  Launch Campaign", type="primary", key="cb_go_wizard"):
            navigate_to("wizard")
        return

    camp_labels = [c["song_title"] for c in campaigns]
    c_idx = st.selectbox("Campaign:", range(len(camp_labels)), format_func=lambda i: camp_labels[i], key="cb_campaign")
    campaign = campaigns[c_idx]
    campaign_id = campaign["campaign_id"]

    current = brief_store.get_current(artist_id, campaign_id)
    if not current:
        render_html('<div class="mw-card" style="text-align:center;padding:2rem;color:#8A8480;">No Creative Brief for this campaign yet.</div>')
        return

    st.markdown(f"### {campaign['song_title']}")
    st.caption(f"Version {current['version']} · edited by {current.get('authored_by','')} · {current.get('created_at','')[:16].replace('T',' ')}")

    # ── Which regeneration groups does the CURRENT version's diff touch ────────
    pending_groups = affected_groups(current.get("changed_fields", []))
    if pending_groups and current["version"] > 1:
        labels = ", ".join(REGEN_GROUPS[g]["label"] for g in pending_groups)
        st.info(f"🔄 Your last edit affects: **{labels}**. Regenerate below when you're ready — nothing happens automatically.")

    # ── Edit form ────────────────────────────────────────────────────────────
    render_html('<div class="mw-section-label">Edit the Brief</div>')
    with st.form("cb_edit_form"):
        new_values = {}
        for section_label, fields in FIELD_SECTIONS:
            st.markdown(f"**{section_label}**")
            for field in fields:
                new_values[field] = _field_widget(field, current["fields"].get(field, ""))
            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

        if st.form_submit_button("💾  Save New Version", type="primary"):
            new_version = brief_store.save_version(artist_id, campaign_id, new_values, authored_by="founder")
            if new_version["changed_fields"]:
                st.success(f"Saved as Version {new_version['version']} — {len(new_version['changed_fields'])} field(s) changed.")
            else:
                st.info("Saved — no fields actually changed.")
            st.rerun()

    # ── Regeneration ─────────────────────────────────────────────────────────
    render_html('<div class="mw-section-label" style="margin-top:1.5rem;">Regenerate</div>')
    st.caption(
        "Selective only — regenerating a department never touches another department's work, "
        "and never overwrites anything you've already approved. It creates a new alternative for "
        "you to compare in Asset Review."
    )

    cols = st.columns(len(REGEN_GROUPS))
    for col, (group_key, meta) in zip(cols, REGEN_GROUPS.items()):
        with col:
            is_pending = group_key in pending_groups
            btn_label = f"{meta['icon']} {meta['label']}"
            if st.button(btn_label, key=f"cb_regen_{group_key}", type="primary" if is_pending else "secondary", use_container_width=True):
                with st.spinner(f"Regenerating {meta['label']}..."):
                    try:
                        from config import ANTHROPIC_API_KEY
                        mock_mode = not bool(ANTHROPIC_API_KEY)
                    except ImportError:
                        mock_mode = True
                    from execution.asset_library import AssetLibrary
                    from execution.orchestrator import RenderOrchestrator
                    orchestrator = RenderOrchestrator(AssetLibrary(), mock_mode=mock_mode)
                    result = orchestrator.regenerate_group(artist_id, campaign_id, group_key, printer=lambda *a: None)
                st.success(f"{result['alternatives_created']} new alternative(s) ready — review them in Asset Review.")
                st.session_state.approval_campaign_id = campaign_id
            if not is_pending:
                st.caption("No pending changes")

    if st.button("✅  Open Asset Review", key="cb_open_review"):
        navigate_to("approval")

    # ── Version history ──────────────────────────────────────────────────────
    render_html('<div class="mw-section-label" style="margin-top:1.5rem;">Version History</div>')
    versions = list(reversed(brief_store.list_versions(artist_id, campaign_id)))
    for v in versions:
        is_current = v["version"] == current["version"]
        title = f"Version {v['version']}{' (current)' if is_current else ''} — {v.get('authored_by','')}"
        with st.expander(title, expanded=False):
            st.caption(v.get("created_at", "")[:16].replace("T", " "))
            if v["version"] == 1:
                st.caption("Initial Creative Brief, written by your Creative Director.")
            elif v.get("changed_fields"):
                st.markdown("**Changed:**")
                for f in v["changed_fields"]:
                    st.caption(f"- {FIELD_LABELS.get(f, f)}: {v['fields'].get(f, '')[:140]}")
            else:
                st.caption("No fields changed from the previous version.")
            if not is_current:
                if st.button("↺ Restore this version", key=f"cb_restore_{v['version']}"):
                    brief_store.restore_version(artist_id, campaign_id, v["version"])
                    st.success(f"Restored — saved as a new version. Nothing was deleted.")
                    st.rerun()
