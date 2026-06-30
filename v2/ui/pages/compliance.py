"""MusicWorks™ V4.3 — Compliance Center™: Release Readiness & AI Governance."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html, navigate_to
from brand_brain.artist_library import list_artists
from execution.distrokid_store import list_releases
from execution.compliance import (
    SECTIONS, STATUS_READY, STATUS_NEEDS_REVIEW, STATUS_BLOCKED, STATUS_NOT_CHECKED,
    STATUS_LABELS, STATUS_COLORS, STATUS_ICONS,
    compute_release_score, get_item, set_item,
    PLATFORM_KEYS, PLATFORM_NAMES, PLATFORM_ICONS,
    get_profile, update_profile,
    CREATION_TYPE_LABELS, CREATION_TYPE_COLORS,
    scan_for_song, ai_usage_summary, build_governance_report,
    COPYRIGHT_ITEMS, ITEM_MAP, OWNERSHIP_OPTIONS, OWNERSHIP_COLORS, OWNERSHIP_LABELS,
    load_checklist, save_checklist_item, checklist_summary,
    RISK_COLORS, RISK_ICONS, RISK_LABELS,
    compute_risk_report,
)

_DISCLAIMER = """
<div class="mw-card" style="padding:1rem 1.5rem; border-left:3px solid #F59E0B; margin-bottom:1.5rem;">
<div style="font-size:13px; color:#C8C4BE; line-height:1.7;">
<strong style="color:#F59E0B;">Important:</strong>
MusicWorks™ Compliance Center provides <strong>operational guidance and release readiness recommendations only</strong>.
It does NOT constitute legal advice, platform compliance certification, or copyright clearance.
All publishing decisions are made by the Founder.
MusicWorks does not guarantee platform acceptance of any content.
</div>
</div>
"""


def render():
    page_header("Compliance Center™", "AI-assisted. Human-decided. Responsibly built.", "🛡️")
    render_html(_DISCLAIMER)

    # ── Artist + song selector ─────────────────────────────────────────────────
    artists = list_artists()
    if not artists:
        render_html('<div class="mw-card" style="padding:2rem; text-align:center; color:#8A8480;">No artists yet — add an artist first.</div>')
        if st.button("Add Artist →", type="primary"):
            navigate_to("artists")
        return

    artist_names = [a["artist_name"] for a in artists]
    artist_ids   = [a["artist_id"]   for a in artists]

    col_a, col_s = st.columns(2)
    with col_a:
        sel_idx   = st.selectbox("Artist:", range(len(artist_names)),
                                 format_func=lambda i: artist_names[i], key="cc_artist")
        sel_id    = artist_ids[sel_idx]

    with col_s:
        releases   = list_releases(sel_id)
        if not releases:
            st.info("No releases registered. Register a release in Production → Release Setup.")
            song_id    = ""
            song_title = "No releases"
        else:
            rel_labels = [f"{r.get('song_title','')} ({r.get('release_date','')[:10]})" for r in releases]
            rel_idx    = st.selectbox("Release:", range(len(releases)),
                                      format_func=lambda i: rel_labels[i], key="cc_song")
            song_id    = releases[rel_idx].get("song_id", "")
            song_title = releases[rel_idx].get("song_title", "")

    if not song_id:
        return

    # ── Release score banner ───────────────────────────────────────────────────
    score_data = compute_release_score(sel_id, song_id)
    score      = score_data["score"]
    status     = score_data["status"]
    sc         = STATUS_COLORS.get(status, "#6A6460")
    si         = STATUS_ICONS.get(status, "○")
    sl         = STATUS_LABELS.get(status, status)

    render_html(f"""
    <div class="mw-card" style="padding:1.25rem 1.5rem; border-left:4px solid {sc}; margin-bottom:1.5rem;
         display:flex; align-items:center; gap:2rem;">
        <div style="text-align:center; min-width:80px;">
            <div style="font-size:36px; font-weight:900; color:{sc};">{score}</div>
            <div style="font-size:10px; color:#8A8480; text-transform:uppercase;">Release Score</div>
        </div>
        <div>
            <div style="font-size:18px; font-weight:700; color:{sc};">{si}  {sl}</div>
            <div style="font-size:13px; color:#C8C4BE; margin-top:4px;">{song_title}</div>
            <div style="font-size:12px; color:#8A8480; margin-top:2px;">
                Score updates automatically as you complete the readiness checklist below.
            </div>
        </div>
    </div>
    """)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    t1, t2, t3, t4, t5 = st.tabs([
        "📋  Release Readiness",
        "📱  Platform Profiles",
        "🤖  AI Governance",
        "©️  Copyright",
        "🎯  Risk Dashboard",
    ])

    with t1:
        _render_readiness(sel_id, song_id, song_title, score_data)

    with t2:
        _render_platform_profiles()

    with t3:
        _render_ai_governance(sel_id, song_id, song_title)

    with t4:
        _render_copyright(sel_id, song_id, song_title)

    with t5:
        _render_risk_dashboard(sel_id, song_id, song_title)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RELEASE READINESS
# ═══════════════════════════════════════════════════════════════════════════════

def _render_readiness(artist_id, song_id, song_title, score_data):
    render_html("""
    <div style="font-size:13px; color:#8A8480; margin-bottom:1.5rem; line-height:1.7;">
        Work through each section. Mark items as Ready, Needs Review, or Blocked.
        Your Release Score updates automatically.
    </div>
    """)

    for section in SECTIONS:
        skey    = section["key"]
        slabel  = section["label"]
        sicon   = section["icon"]
        sec_status = score_data["sections"].get(skey, STATUS_NOT_CHECKED)
        sc      = STATUS_COLORS.get(sec_status, "#6A6460")
        si      = STATUS_ICONS.get(sec_status, "○")

        with st.expander(f"{sicon}  **{slabel}** — {si} {STATUS_LABELS.get(sec_status, '')}", expanded=False):
            for item_key, item_label, item_desc in section["items"]:
                current = get_item(artist_id, song_id, item_key)
                cur_status = current.get("status", STATUS_NOT_CHECKED)
                cur_note   = current.get("note", "")

                col_info, col_status, col_note = st.columns([3, 2, 3])
                with col_info:
                    render_html(f"""
                    <div style="padding:4px 0;">
                        <div style="font-size:13px; font-weight:600; color:#F0EDE8;">{item_label}</div>
                        <div style="font-size:11px; color:#8A8480; margin-top:2px;">{item_desc}</div>
                    </div>
                    """)

                with col_status:
                    opts = [STATUS_READY, STATUS_NEEDS_REVIEW, STATUS_BLOCKED, STATUS_NOT_CHECKED]
                    new_status = st.selectbox(
                        "Status",
                        opts,
                        index=opts.index(cur_status) if cur_status in opts else 3,
                        format_func=lambda s: f"{STATUS_ICONS[s]} {STATUS_LABELS[s]}",
                        key=f"rs_{skey}_{item_key}",
                        label_visibility="collapsed",
                    )

                with col_note:
                    new_note = st.text_input("Note", value=cur_note,
                                             key=f"rn_{skey}_{item_key}",
                                             label_visibility="collapsed",
                                             placeholder="Optional note…")

                if new_status != cur_status or new_note != cur_note:
                    set_item(artist_id, song_id, item_key, new_status, new_note)
                    st.rerun()

    render_html("""
    <div style="margin-top:1.5rem; font-size:12px; color:#6A6460; line-height:1.7;">
        ✓ Ready = confirmed &nbsp;·&nbsp; ⚠ Needs Review = requires attention but not blocking &nbsp;·&nbsp;
        ✗ Blocked = must be resolved before publishing &nbsp;·&nbsp; ○ Not Checked = not yet reviewed
    </div>
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PLATFORM PROFILES
# ═══════════════════════════════════════════════════════════════════════════════

def _render_platform_profiles():
    render_html("""
    <div class="mw-card" style="padding:1rem 1.5rem; border-left:3px solid #9B89D4; margin-bottom:1.5rem;">
        <div style="font-size:13px; color:#C8C4BE; line-height:1.7;">
            Platform publishing guidance is <strong style="color:#D4A853;">fully editable</strong>.
            As platforms update their policies, update these profiles — no code changes required.
            MusicWorks will use this guidance during release reviews.
        </div>
    </div>
    """)

    platform_key = st.selectbox(
        "Select platform:",
        PLATFORM_KEYS,
        format_func=lambda k: f"{PLATFORM_ICONS.get(k, '')}  {PLATFORM_NAMES.get(k, k)}",
        key="cc_platform",
    )
    profile = get_profile(platform_key)

    with st.form(f"platform_form_{platform_key}"):
        render_html(f'<div class="mw-section-label">{PLATFORM_ICONS.get(platform_key, "")}  {profile.get("name", "")} — Publishing Guidance</div>')

        c1, c2 = st.columns(2)
        with c1:
            ai_notes   = st.text_area("AI / Synthetic Media Notes",
                                       value=profile.get("ai_notes", ""), height=120, key="ccai")
            music_notes = st.text_area("Music Usage Notes",
                                        value=profile.get("music_notes", ""), height=100, key="ccmu")
            hashtag_g  = st.text_input("Hashtag Guidance",
                                        value=profile.get("hashtag_guidance", ""), key="cchash")

        with c2:
            # Video lengths as text area (JSON-free editing)
            vl_text = _dict_to_text(profile.get("video_lengths", {}))
            vl_new  = st.text_area("Video Lengths (one per line: label: value)",
                                    value=vl_text, height=100, key="ccvl")

            is_text = _dict_to_text(profile.get("image_sizes", {}))
            is_new  = st.text_area("Image Sizes (one per line: label: value)",
                                    value=is_text, height=100, key="ccis")

            cl      = profile.get("caption_length", {})
            cl_max  = st.number_input("Caption Max Length (0 = no limit)",
                                       min_value=0, value=int(cl.get("max", 0)), key="cccl")

        best_prac = "\n".join(profile.get("best_practices", []))
        bp_new    = st.text_area("Best Practices (one per line)",
                                  value=best_prac, height=120, key="ccbp")

        ref_links = "\n".join(profile.get("reference_links", []))
        rl_new    = st.text_area("Reference Links (one per line)",
                                  value=ref_links, height=60, key="ccrl")

        last_upd  = st.text_input("Last Updated (YYYY-MM-DD)",
                                   value=profile.get("last_updated", ""), key="cclu")

        if st.form_submit_button("💾  Save Platform Profile", type="primary"):
            update_profile(platform_key, {
                "ai_notes":        ai_notes,
                "music_notes":     music_notes,
                "hashtag_guidance": hashtag_g,
                "video_lengths":   _text_to_dict(vl_new),
                "image_sizes":     _text_to_dict(is_new),
                "caption_length":  {"max": cl_max},
                "best_practices":  [l.strip() for l in bp_new.splitlines() if l.strip()],
                "reference_links": [l.strip() for l in rl_new.splitlines() if l.strip()],
                "last_updated":    last_upd,
            })
            st.success(f"✓ {profile.get('name', '')} profile saved.")
            st.rerun()

    # Read-only summary of current profile
    with st.expander("View Full Profile (read-only)", expanded=False):
        col_v, col_i = st.columns(2)
        with col_v:
            render_html('<div class="mw-section-label">Video Lengths</div>')
            for k, v in profile.get("video_lengths", {}).items():
                render_html(f'<div style="font-size:12px; color:#C8C4BE; padding:2px 0;"><strong style="color:#8A8480;">{k}:</strong> {v}</div>')
        with col_i:
            render_html('<div class="mw-section-label">Image Sizes</div>')
            for k, v in profile.get("image_sizes", {}).items():
                render_html(f'<div style="font-size:12px; color:#C8C4BE; padding:2px 0;"><strong style="color:#8A8480;">{k}:</strong> {v}</div>')

        render_html('<div class="mw-section-label" style="margin-top:1rem;">Best Practices</div>')
        for bp in profile.get("best_practices", []):
            render_html(f'<div style="font-size:12px; color:#C8C4BE; padding:3px 0;">• {bp}</div>')


def _dict_to_text(d: dict) -> str:
    return "\n".join(f"{k}: {v}" for k, v in d.items())


def _text_to_dict(text: str) -> dict:
    result = {}
    for line in text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip()
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI GOVERNANCE
# ═══════════════════════════════════════════════════════════════════════════════

def _render_ai_governance(artist_id, song_id, song_title):
    render_html(f"""
    <div class="mw-card" style="padding:1rem 1.5rem; border-left:3px solid #9B89D4; margin-bottom:1.5rem;">
        <div style="font-size:13px; color:#C8C4BE; line-height:1.7;">
            Every AI-generated asset for <strong style="color:#D4A853;">{song_title}</strong>
            is tracked here. Provider used, prompt, generation time, approval status.
            This is your audit trail for responsible AI-assisted production.
        </div>
    </div>
    """)

    summary = ai_usage_summary(artist_id, song_id)
    records = scan_for_song(artist_id, song_id)

    # Summary stats
    s1, s2, s3, s4 = st.columns(4)
    _mini_stat(s1, "Total Assets", str(summary.get("total", 0)), "#9B89D4")
    _mini_stat(s2, "Approved",     str(summary.get("approved", 0)), "#22C55E")
    _mini_stat(s3, "Approval %",   f"{summary.get('approval_pct', 0)}%", "#D4A853")
    _mini_stat(s4, "Mock Output",  str(summary.get("mock", 0)), "#6A6460")

    if not records:
        render_html("""
        <div class="mw-card" style="padding:2rem; text-align:center; color:#8A8480; margin-top:1rem;">
            No AI-generated assets for this release yet.
            Generate content in the Production Queue to populate this report.
        </div>
        """)
        return

    # Provider breakdown
    by_prov = summary.get("by_provider", {})
    if by_prov:
        render_html('<div class="mw-section-label">Provider Breakdown</div>')
        pcols = st.columns(min(len(by_prov), 5))
        for col, (prov, count) in zip(pcols, by_prov.items()):
            with col:
                render_html(f"""
                <div class="mw-card" style="padding:0.75rem; text-align:center;">
                    <div style="font-size:18px; font-weight:700; color:#D4A853;">{count}</div>
                    <div style="font-size:10px; color:#8A8480; text-transform:uppercase;">{prov}</div>
                </div>
                """)

    # Asset timeline
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    render_html('<div class="mw-section-label">Asset Provenance — Generation Timeline</div>')

    for rec in records:
        is_approved = rec.get("approved", False)
        is_mock     = rec.get("mock", True)
        prov        = rec.get("provider_used", "mock")
        ct          = rec.get("creation_type", "ai_assisted")
        gen_at      = (rec.get("generated_at", "") or "")[:16].replace("T", " ")

        status_dot  = "🟢" if is_approved else "🟡"
        mock_badge  = '<span style="background:#1E1E1E; color:#6A6460; font-size:10px; padding:1px 6px; border-radius:10px; margin-left:6px;">MOCK</span>' if is_mock else ""
        ct_color    = CREATION_TYPE_COLORS.get(ct, "#8A8480")
        ct_label    = CREATION_TYPE_LABELS.get(ct, ct)

        with st.expander(f"{status_dot}  {rec.get('job_label', rec.get('job_type',''))}  ·  {prov}  ·  {gen_at}", expanded=False):
            m1, m2, m3, m4 = st.columns(4)
            m1.caption(f"Type: {rec.get('job_type','')}")
            m2.caption(f"Provider: {prov}")
            m3.caption(f"Time: {rec.get('generation_time_ms',0)}ms")
            m4.caption(f"Status: {rec.get('status','')}")

            render_html(f"""
            <div style="margin:6px 0;">
                <span style="background:{ct_color}22; color:{ct_color}; font-size:11px; padding:2px 8px; border-radius:10px; font-weight:600;">
                    {ct_label}
                </span>{mock_badge}
                {'<span style="background:#22C55E22; color:#22C55E; font-size:11px; padding:2px 8px; border-radius:10px; margin-left:6px;">Founder Approved</span>' if is_approved else '<span style="background:#F59E0B22; color:#F59E0B; font-size:11px; padding:2px 8px; border-radius:10px; margin-left:6px;">Pending Approval</span>'}
            </div>
            """)

            if rec.get("prompt_used"):
                with st.expander("Prompt used", expanded=False):
                    st.code(rec["prompt_used"][:1500], language=None)

    # Export
    report = build_governance_report(artist_id, song_id)
    import json
    st.download_button(
        "⬇  Export Governance Report (JSON)",
        data=json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8"),
        file_name=f"governance_{artist_id}_{song_id}.json",
        mime="application/json",
        key="cc_export_gov",
    )

    render_html(f"""
    <div style="margin-top:1rem; font-size:11px; color:#6A6460; line-height:1.7;">
        {report['disclaimer']}
    </div>
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — COPYRIGHT
# ═══════════════════════════════════════════════════════════════════════════════

def _render_copyright(artist_id, song_id, song_title):
    render_html(f"""
    <div class="mw-card" style="padding:1rem 1.5rem; border-left:3px solid #EF4444; margin-bottom:1.5rem;">
        <div style="font-size:13px; color:#C8C4BE; line-height:1.7;">
            <strong style="color:#EF4444;">Copyright Reminder:</strong>
            MusicWorks tracks founder confirmations only. This is NOT legal advice.
            Confirm each item below to document your ownership and permissions for
            <strong style="color:#D4A853;">{song_title}</strong>.
        </div>
    </div>
    """)

    items_data = load_checklist(artist_id, song_id)
    summary    = checklist_summary(artist_id, song_id)

    # Progress
    pct = summary["pct"]
    bar_color = "#22C55E" if pct == 100 else ("#F59E0B" if pct >= 50 else "#EF4444")
    render_html(f"""
    <div style="margin-bottom:1.5rem;">
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
            <span style="font-size:13px; color:#C8C4BE;">Copyright Checklist Completion</span>
            <span style="font-size:13px; color:{bar_color}; font-weight:700;">{summary['resolved']}/{summary['total']} confirmed</span>
        </div>
        <div style="background:#1E1E1E; border-radius:4px; height:6px;">
            <div style="background:{bar_color}; width:{pct}%; height:6px; border-radius:4px;"></div>
        </div>
    </div>
    """)

    for item_key, item_label, question, guidance in COPYRIGHT_ITEMS:
        existing = items_data.get(item_key, {})
        cur_own  = existing.get("ownership_status", "not_checked")
        cur_note = existing.get("notes", "")
        own_color = OWNERSHIP_COLORS.get(cur_own, "#8A8480")

        with st.expander(
            f"{OWNERSHIP_COLORS.get(cur_own,'●')}  **{item_label}** — {OWNERSHIP_LABELS.get(cur_own, 'Not Checked')}",
            expanded=(cur_own in ("not_checked", "unresolved"))
        ):
            render_html(f"""
            <div style="font-size:13px; color:#C8C4BE; margin-bottom:8px;">{question}</div>
            <div style="font-size:11px; color:#8A8480; margin-bottom:12px; padding:8px; background:#0A0A0A; border-radius:6px;">{guidance}</div>
            """)

            col_s, col_n = st.columns([2, 3])
            with col_s:
                own_opts = [k for k, _, _ in OWNERSHIP_OPTIONS]
                new_own  = st.selectbox(
                    "Status",
                    own_opts,
                    index=own_opts.index(cur_own) if cur_own in own_opts else len(own_opts)-1,
                    format_func=lambda k: OWNERSHIP_LABELS.get(k, k),
                    key=f"cc_own_{item_key}",
                )
            with col_n:
                new_note = st.text_input("Notes / License details", value=cur_note,
                                          key=f"cc_note_{item_key}",
                                          placeholder="e.g. Original composition, fully owned…")

            if new_own != cur_own or new_note != cur_note:
                save_checklist_item(artist_id, song_id, item_key, new_own, new_note)
                st.rerun()

    render_html("""
    <div style="margin-top:1rem; font-size:11px; color:#6A6460; line-height:1.7;">
        Owned/Original · Licensed · Cleared = resolved &nbsp;·&nbsp;
        Not Applicable = item doesn't apply to this release &nbsp;·&nbsp;
        Unresolved = needs attention before publishing
    </div>
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — RISK DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def _render_risk_dashboard(artist_id, song_id, song_title):
    report = compute_risk_report(artist_id, song_id)
    overall_level = report["overall_level"]
    overall_score = report["overall_score"]
    oc     = RISK_COLORS[overall_level]
    oi     = RISK_ICONS[overall_level]
    ol     = RISK_LABELS[overall_level]

    render_html(f"""
    <div class="mw-card" style="padding:1.5rem; border-top:4px solid {oc}; margin-bottom:2rem; text-align:center;">
        <div style="font-size:11px; color:#8A8480; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Overall Release Risk</div>
        <div style="font-size:48px; margin-bottom:8px;">{oi}</div>
        <div style="font-size:24px; font-weight:800; color:{oc}; margin-bottom:4px;">{ol}</div>
        <div style="font-size:28px; font-weight:900; color:{oc};">{overall_score}/100</div>
        <div style="font-size:12px; color:#6A6460; margin-top:8px;">{song_title}</div>
    </div>
    """)

    # Dimension cards
    dims = list(report["dimensions"].values())
    rows = [dims[i:i+3] for i in range(0, len(dims), 3)]
    for row in rows:
        cols = st.columns(len(row))
        for col, dim in zip(cols, row):
            dc = RISK_COLORS[dim["level"]]
            di = RISK_ICONS[dim["level"]]
            with col:
                render_html(f"""
                <div class="mw-card" style="padding:1rem; border-top:3px solid {dc}; margin-bottom:0.75rem; text-align:center; min-height:160px;">
                    <div style="font-size:16px; margin-bottom:4px;">{dim['icon']}</div>
                    <div style="font-size:11px; font-weight:700; color:#F0EDE8; margin-bottom:6px;">{dim['label']}</div>
                    <div style="font-size:22px; margin-bottom:4px;">{di}</div>
                    <div style="font-size:20px; font-weight:800; color:{dc}; margin-bottom:6px;">{dim['score']}</div>
                    <div style="font-size:10px; color:#8A8480; line-height:1.4;">{dim['note'][:80]}{'…' if len(dim['note']) > 80 else ''}</div>
                </div>
                """)

    # Legend
    render_html("""
    <div style="font-size:12px; color:#6A6460; line-height:1.8; margin-top:1rem;">
        🟢 <strong style="color:#22C55E;">Low Risk</strong> (80–100) — On track<br>
        🟡 <strong style="color:#F59E0B;">Review Recommended</strong> (50–79) — Some items need attention<br>
        🔴 <strong style="color:#EF4444;">Attention Needed</strong> (0–49) — Important items unresolved
    </div>
    """)

    render_html(f"""
    <div style="margin-top:1.5rem; font-size:11px; color:#6A6460; line-height:1.7;">
        {report['disclaimer']}
    </div>
    """)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mini_stat(col, label, value, color):
    with col:
        render_html(f"""
        <div class="mw-card" style="padding:1rem; text-align:center; border-top:3px solid {color};">
            <div style="font-size:24px; font-weight:800; color:{color};">{value}</div>
            <div style="font-size:10px; color:#8A8480; margin-top:4px; text-transform:uppercase;">{label}</div>
        </div>
        """)
