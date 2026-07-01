"""MusicWorks™ V3 — Design System CSS"""
import streamlit as st

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Hide Streamlit chrome ── */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

[data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0D0D0D !important;
}

.main .block-container {
    padding: 2rem 2.5rem 4rem 2.5rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #0A0A0A !important;
    border-right: 1px solid #1E1E1E !important;
}
section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1rem !important;
}

/* ── Sidebar nav buttons: inactive ── */
section[data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
    background: transparent !important;
    border: none !important;
    color: #8A8480 !important;
    text-align: left !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 9px 14px !important;
    border-radius: 8px !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover {
    background: #1A1A1A !important;
    color: #F0EDE8 !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* ── Sidebar nav buttons: active ── */
section[data-testid="stSidebar"] [data-testid="baseButton-primary"] {
    background: rgba(255, 107, 43, 0.12) !important;
    border: 1px solid rgba(255, 107, 43, 0.25) !important;
    color: #FF6B2B !important;
    text-align: left !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 9px 14px !important;
    border-radius: 8px !important;
    width: 100% !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] [data-testid="baseButton-primary"]:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 12px !important;
    padding: 1.25rem 1.5rem !important;
}
[data-testid="stMetricLabel"] p {
    color: #8A8480 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
[data-testid="stMetricValue"] {
    color: #F0EDE8 !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* ── Custom cards (HTML classes) ── */
.mw-card {
    background: #141414;
    border: 1px solid #242424;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.mw-card-elevated {
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
    padding: 1.5rem;
}
.mw-hero {
    background: linear-gradient(135deg, #1A0F42 0%, #2D1B69 50%, #1a1212 100%);
    border: 1px solid rgba(212, 168, 83, 0.2);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
}
.mw-section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #8A8480;
    margin-bottom: 0.75rem;
}
.mw-stat-number {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #F0EDE8;
    line-height: 1;
}
.mw-countdown {
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -2px;
    color: #FF6B2B;
    line-height: 1;
}

/* ── Status badges ── */
.badge {
    display: inline-block;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.badge-approved { background: rgba(34,197,94,0.1); color: #22C55E; border: 1px solid rgba(34,197,94,0.25); }
.badge-pending  { background: rgba(245,158,11,0.1); color: #F59E0B; border: 1px solid rgba(245,158,11,0.25); }
.badge-revision { background: rgba(96,165,250,0.1); color: #60A5FA; border: 1px solid rgba(96,165,250,0.25); }
.badge-rejected { background: rgba(239,68,68,0.1);  color: #EF4444; border: 1px solid rgba(239,68,68,0.25); }
.badge-live     { background: rgba(255,107,43,0.1); color: #FF6B2B; border: 1px solid rgba(255,107,43,0.25); }

/* ── Tags / chips ── */
.tag {
    display: inline-block;
    background: #1E1E1E;
    color: #8A8480;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 12px;
    margin: 2px;
}
.tag-gold   { background: rgba(212,168,83,0.1);  color: #D4A853; border: 1px solid rgba(212,168,83,0.2); }
.tag-fire   { background: rgba(255,107,43,0.1);  color: #FF6B2B; border: 1px solid rgba(255,107,43,0.2); }
.tag-indigo { background: rgba(45,27,105,0.3);   color: #9B89D4; border: 1px solid rgba(45,27,105,0.5); }
.tag-green  { background: rgba(34,197,94,0.1);   color: #22C55E; border: 1px solid rgba(34,197,94,0.2); }
.tag-red    { background: rgba(239,68,68,0.1);   color: #EF4444; border: 1px solid rgba(239,68,68,0.2); }

/* ── Progress bar ── */
.mw-progress-track {
    background: #242424;
    border-radius: 4px;
    height: 6px;
    margin-top: 8px;
    overflow: hidden;
}
.mw-progress-fill {
    background: linear-gradient(90deg, #FF6B2B, #D4A853);
    border-radius: 4px;
    height: 6px;
    transition: width 0.3s ease;
}

/* ── Color swatches ── */
.color-swatch {
    display: inline-block;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-right: 8px;
    vertical-align: middle;
}

/* ── Timeline entry ── */
.timeline-entry {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #1E1E1E;
}
.timeline-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}

/* ── Typography ── */
h1 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
    color: #F0EDE8 !important;
    font-size: 2rem !important;
}
h2 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.3px !important;
    color: #F0EDE8 !important;
}
h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #F0EDE8 !important;
}
p { color: #C8C4BE; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 10px !important;
}
[data-testid="stExpanderHeader"] p { color: #C8C4BE !important; }

/* ── Main content buttons (primary = fire orange) ── */
.main [data-testid="baseButton-primary"] {
    background: #FF6B2B !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(255,107,43,0.3) !important;
}
.main [data-testid="baseButton-primary"]:hover {
    background: #e55a1e !important;
    box-shadow: 0 4px 12px rgba(255,107,43,0.4) !important;
}
.main [data-testid="baseButton-secondary"] {
    background: #1E1E1E !important;
    border: 1px solid #333 !important;
    color: #C8C4BE !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}
.main [data-testid="baseButton-secondary"]:hover {
    background: #2A2A2A !important;
    color: #F0EDE8 !important;
}

/* ── Divider ── */
hr { border-color: #242424 !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border-left-width: 3px !important;
}

/* ── Select box ── */
[data-testid="stSelectbox"] > div > div {
    background: #141414 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    color: #F0EDE8 !important;
}

/* ── Text input / textarea ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #141414 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    color: #F0EDE8 !important;
}

/* ── Number input ── */
[data-testid="stNumberInput"] input {
    background: #141414 !important;
    border: 1px solid #333 !important;
    color: #F0EDE8 !important;
}

/* ── Date input ── */
[data-testid="stDateInput"] input {
    background: #141414 !important;
    border: 1px solid #333 !important;
    color: #F0EDE8 !important;
    border-radius: 8px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #141414 !important;
    border: 1px dashed #333 !important;
    border-radius: 10px !important;
}

/* ── Columns gap ── */
[data-testid="stHorizontalBlock"] { gap: 1rem; }

/* ── Status/spinner ── */
[data-testid="stStatusWidget"] {
    background: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 10px !important;
}

/* ── Caption / small text ── */
[data-testid="stCaptionContainer"] p { color: #6A6460 !important; font-size: 12px !important; }

/* ── Form submit button ── */
[data-testid="stFormSubmitButton"] button {
    background: #FF6B2B !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label p { color: #C8C4BE !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: #1E1E1E !important;
    border: 1px solid #333 !important;
    color: #D4A853 !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-testid="stTabsTabList"] {
    background: transparent !important;
    border-bottom: 1px solid #242424 !important;
    gap: 0 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    color: #8A8480 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
    box-shadow: none !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #F0EDE8 !important;
    border-bottom: 2px solid #FF6B2B !important;
    background: transparent !important;
    box-shadow: none !important;
}
[data-testid="stTabs"] button[role="tab"]:hover {
    color: #F0EDE8 !important;
    background: rgba(255,255,255,0.03) !important;
}

/* ── Status widget (Build Campaign progress) ── */
[data-testid="stStatusWidget"] {
    background: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 12px !important;
}
[data-testid="stStatusWidget"] p {
    color: #C8C4BE !important;
    font-size: 13px !important;
}

/* ── Wizard step progress nodes ── */
.wizard-step-active {
    background: #FF6B2B;
    color: white;
}
.wizard-step-done {
    background: #22C55E;
    color: white;
}
.wizard-step-pending {
    background: #242424;
    color: #6A6460;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label p {
    color: #C8C4BE !important;
    font-size: 14px !important;
}

/* ── Image caption ── */
[data-testid="stImage"] {
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ── Number input ── */
[data-testid="stNumberInput"] {
    border-color: #333 !important;
}

/* ── Multiselect ── */
[data-testid="stMultiSelect"] > div > div {
    background: #141414 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    color: #F0EDE8 !important;
}
[data-testid="stMultiSelect"] span {
    background: rgba(45,27,105,0.4) !important;
    color: #9B89D4 !important;
    border-radius: 4px !important;
}

/* ── Artist card DNA tags ── */
.dna-tag {
    display: inline-block;
    background: rgba(45,27,105,0.25);
    color: #9B89D4;
    border: 1px solid rgba(45,27,105,0.5);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 12px;
    margin: 2px;
}

/* ── Gradient section dividers ── */
.mw-section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2D1B69, transparent);
    margin: 2rem 0;
}

/* ── Publishing checklist item ── */
.publish-item-ready {
    border-left: 3px solid #22C55E;
    background: rgba(34,197,94,0.04);
}
.publish-item-pending {
    border-left: 3px solid #F59E0B;
    background: rgba(245,158,11,0.04);
}

/* ── Campaign build progress log ── */
.build-log-line {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 12px;
    color: #8A8480;
    padding: 2px 0;
}
.build-log-done {
    color: #22C55E;
}

/* ════════════════════════════════════════════
   V5 — Founder Experience Design System
   ════════════════════════════════════════════ */

/* ── V5 Action Cards (home page) ── */
.mw-action-card {
    border-radius: 20px;
    padding: 1.75rem 2rem;
    margin-bottom: 0.75rem;
    min-height: 155px;
    position: relative;
    overflow: hidden;
}
.mw-action-card-release  { background: linear-gradient(135deg, #1A0F42 0%, #2D1B69 100%); border: 1px solid rgba(168,85,247,0.25); }
.mw-action-card-continue { background: linear-gradient(135deg, #0F1A2A 0%, #1A3A4A 100%); border: 1px solid rgba(96,165,250,0.2); }
.mw-action-card-artists  { background: linear-gradient(135deg, #0F2A1A 0%, #1A4A2A 100%); border: 1px solid rgba(34,197,94,0.2); }
.mw-action-card-results  { background: linear-gradient(135deg, #2A1A0F 0%, #3A2A0F 100%); border: 1px solid rgba(212,168,83,0.2); }

/* ── V5 Asset filter sidebar ── */
.mw-filter-list { background: #0D0D0D; border: 1px solid #1E1E1E; border-radius: 12px; padding: 0.5rem; margin-bottom: 1rem; }
.mw-filter-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-radius: 8px; font-size: 13px; color: #C8C4BE; margin-bottom: 2px; }
.mw-filter-item-active { background: rgba(255,107,43,0.1); color: #FF6B2B; font-weight: 600; }
.mw-filter-count { background: #242424; color: #8A8480; font-size: 11px; font-weight: 600; border-radius: 10px; padding: 1px 7px; }

/* ── V5 Platform pills (publishing) ── */
.mw-platform-row { display: flex; flex-wrap: wrap; gap: 10px; margin: 1rem 0 1.5rem 0; }
.mw-platform-pill { display: inline-flex; align-items: center; gap: 8px; background: #141414; border: 1px solid #333; border-radius: 40px; padding: 10px 20px; font-size: 14px; font-weight: 500; color: #C8C4BE; }
.mw-platform-pill-on { background: rgba(255,107,43,0.12); border: 1px solid rgba(255,107,43,0.4); color: #FF6B2B; font-weight: 600; }

/* ── V5 Asset preview card ── */
.mw-asset-preview { background: #0D0D14; border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 1.75rem 2rem; }

/* ── V5 Mode toggle (sidebar) ── */
.mw-mode-section { margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #1E1E1E; }
.mw-mode-label { font-size: 10px; color: #6A6460; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 0.5rem; }

/* ── V5 Release snapshot (home) ── */
.mw-release-snapshot { background: linear-gradient(135deg, #0F0F1E 0%, #1A0F42 100%); border: 1px solid rgba(168,85,247,0.15); border-radius: 16px; padding: 1.5rem 2rem; margin-top: 2rem; }
"""


def inject_styles():
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
