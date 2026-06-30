"""MusicWorks™ V4.3 — Compliance Center package.

Modules:
  compliance_store      Persistence layer (readiness, copyright, ai_usage, governance)
  release_readiness     Readiness report model: 11 sections, scoring, status
  platform_profiles     Editable platform publishing guidance (9 platforms, updateable JSON)
  ai_usage_tracker      AI provenance tracking: scan generated assets, governance report
  copyright_checklist   Copyright confirmation checklist (9 items, founder-confirmed)
  risk_engine           6-dimension risk scoring: green / yellow / red

MusicWorks does NOT provide legal advice.
MusicWorks does NOT guarantee platform compliance.
This is operational guidance. Founder makes all publishing decisions.
"""
from .compliance_store import (
    load_readiness, save_readiness,
    load_copyright, save_copyright,
    load_profile, save_profile,
    load_ai_usage, save_ai_usage,
    load_governance_log, append_governance_log,
)
from .release_readiness import (
    SECTIONS, SECTION_MAP,
    STATUS_READY, STATUS_NEEDS_REVIEW, STATUS_BLOCKED, STATUS_NOT_CHECKED,
    STATUS_LABELS, STATUS_COLORS, STATUS_ICONS,
    compute_release_score, get_item, set_item,
)
from .platform_profiles import (
    PLATFORM_KEYS, PLATFORM_NAMES, PLATFORM_ICONS,
    get_profile, update_profile, list_platform_profiles,
)
from .ai_usage_tracker import (
    CREATION_TYPES, CREATION_TYPE_LABELS, CREATION_TYPE_COLORS,
    scan_ai_records, scan_for_song, ai_usage_summary, build_governance_report,
)
from .copyright_checklist import (
    COPYRIGHT_ITEMS, ITEM_MAP,
    OWNERSHIP_OPTIONS, OWNERSHIP_COLORS, OWNERSHIP_LABELS,
    load_checklist, save_checklist_item, checklist_summary,
)
from .risk_engine import (
    RISK_GREEN, RISK_YELLOW, RISK_RED,
    RISK_COLORS, RISK_ICONS, RISK_LABELS,
    compute_risk_report,
)
