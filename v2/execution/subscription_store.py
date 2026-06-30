"""MusicWorks™ V4.2 — Subscription Store: track plan status for every provider.

No API keys stored here. Only plan metadata: tier, renewal date, credits.
Data lives in data/subscriptions/subscriptions.json.
"""
import json
from datetime import datetime, timezone, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SUB_DIR  = DATA_DIR / "subscriptions"
SUB_FILE = SUB_DIR / "subscriptions.json"

PLAN_OPTIONS   = ["monthly", "yearly", "trial", "paused", "cancelled", "free", ""]
PLAN_LABELS    = {
    "monthly":   "Monthly",
    "yearly":    "Yearly",
    "trial":     "Trial",
    "paused":    "Paused",
    "cancelled": "Cancelled",
    "free":      "Free",
    "":          "Not set",
}
PLAN_COLORS    = {
    "monthly":   "#22C55E",
    "yearly":    "#10B981",
    "trial":     "#F59E0B",
    "paused":    "#F59E0B",
    "cancelled": "#EF4444",
    "free":      "#6A6460",
    "":          "#6A6460",
}
ACTIVE_PLANS   = {"monthly", "yearly", "trial", "free"}


# ── Persistence ───────────────────────────────────────────────────────────────

def _load() -> dict:
    SUB_DIR.mkdir(parents=True, exist_ok=True)
    if not SUB_FILE.exists():
        return {}
    try:
        return json.loads(SUB_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict) -> None:
    SUB_DIR.mkdir(parents=True, exist_ok=True)
    SUB_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── CRUD ─────────────────────────────────────────────────────────────────────

def save_subscription(key: str, plan: str, renewal_date: str = "",
                      credits_remaining: int | None = None,
                      credits_total: int | None = None,
                      notes: str = "") -> None:
    data = _load()
    data[key] = {
        "plan":             plan,
        "renewal_date":     renewal_date,
        "credits_remaining": credits_remaining,
        "credits_total":    credits_total,
        "notes":            notes,
        "updated_at":       datetime.now(timezone.utc).isoformat(),
    }
    _save(data)


def get_subscription(key: str) -> dict:
    data = _load()
    return data.get(key, {
        "plan": "", "renewal_date": "", "credits_remaining": None,
        "credits_total": None, "notes": "", "updated_at": "",
    })


def get_all_subscriptions() -> dict:
    return _load()


# ── Computed properties ────────────────────────────────────────────────────────

def is_subscription_active(key: str) -> bool:
    sub = get_subscription(key)
    if sub.get("plan", "") not in ACTIVE_PLANS:
        return False
    rd = sub.get("renewal_date", "")
    if rd:
        try:
            exp = date.fromisoformat(rd[:10])
            if exp < date.today():
                return False
        except Exception:
            pass
    return True


def days_until_renewal(key: str) -> int | None:
    """Return days until renewal/expiry. Negative = already expired."""
    sub = get_subscription(key)
    rd = sub.get("renewal_date", "")
    if not rd:
        return None
    try:
        exp = date.fromisoformat(rd[:10])
        return (exp - date.today()).days
    except Exception:
        return None


def renewal_warning(key: str) -> str | None:
    """Return a warning string if renewal is near or expired, else None."""
    days = days_until_renewal(key)
    if days is None:
        return None
    if days < 0:
        return f"Expired {abs(days)} day(s) ago"
    if days == 0:
        return "Renews today"
    if days <= 7:
        return f"Renews in {days} day(s)"
    return None
