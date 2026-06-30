# MusicWorks™ V3.1 — Streamlit Cloud Deployment Guide

## What this deploys

MusicWorks™ V3.1 — a live public demo of an AI-assisted gospel music operating system with:
- **Editable artist profiles** — view/edit mode with full identity fields
- **Brand Vault** — upload and manage artist photos, logos, album covers, mood boards
- **Distribution Setup** — configure social, streaming, and owned channel destinations
- **Campaign Engine** — New Project Wizard → Asset Library → Approval Queue → Publishing
- **Streamlit Cloud demo mode** — auto-seeds Fire & Flow Gospel data on cold start
- **Founder-approved release workflow** — nothing publishes without approval

No API key required. Runs in Mock Mode automatically.

---

## Step 1 — Push to GitHub

```bash
cd C:\Users\claud\musicworks

# Initialize git if not already done
git init
git add .
git commit -m "MusicWorks V3 — Streamlit Cloud deployment"

# Push to your GitHub repo
git remote add origin https://github.com/YOUR_USERNAME/musicworks.git
git branch -M main
git push -u origin main
```

---

## Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **New app**
3. Fill in the form:
   - **Repository:** `YOUR_USERNAME/musicworks`
   - **Branch:** `main`
   - **Main file path:** `v2/app.py`  ← this is the entry point
4. Click **Deploy**

Streamlit Cloud will install `v2/requirements.txt` automatically.

---

## Entry point

```
v2/app.py
```

Streamlit Cloud must be configured to point to `v2/app.py`, not `app.py` at
the repo root.

---

## Python version

Python **3.11** recommended. Streamlit Cloud defaults to the latest stable
Python; the app is compatible with Python 3.10+.

To pin the version, create `v2/runtime.txt`:
```
python-3.11
```

---

## Secrets / environment variables

**No secrets are required for the public demo.** The app detects a missing
`ANTHROPIC_API_KEY` and enables Mock Mode automatically.

If you want to connect a real Anthropic API key for live agent runs:
1. In Streamlit Cloud → your app → **Settings** → **Secrets**
2. Add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```

---

## Demo data

On cold start, the app checks whether the SQLite database is empty. If it is,
it automatically seeds:

| Asset | Details |
|---|---|
| Artist | Fire & Flow Gospel (full Brand Brain) |
| Song | HLANGANA — Zulu · Gather Together · Hebrews 10:25 |
| Campaign | `hlangana-blitz-launch-001` — Blitz launch, July 3 2026 |
| Assets | 10 demo assets, all `READY_FOR_REVIEW` |
| Press release | Quote locked — founder must enter their own words in the Approval Queue |

To manually seed (or re-seed after wiping the database):
```bash
cd v2
python scripts/seed_demo.py
```

---

## Local verification

```bash
cd C:\Users\claud\musicworks\v2

# Optional: seed demo data first
python scripts/seed_demo.py

# Launch the app
python -m streamlit run app.py --server.headless true --browser.gatherUsageStats false
```

Open [http://localhost:8501](http://localhost:8501).

---

## Risks and notes

| Risk | Mitigation |
|---|---|
| SQLite is ephemeral on Streamlit Cloud | Auto-seed runs on every cold start — data is always present |
| No persistent file storage | Asset text is stored in SQLite `preview_text` column — UI works without asset files on disk |
| Release date (Jul 3 2026) will pass | Dashboard switches from "days until launch" to "days since launch" automatically |
| Multiple visitors share one DB | For a founder demo this is fine — all visitors see the same seeded data |

---

## Files created for this deployment

| File | Purpose |
|---|---|
| `v2/requirements.txt` | Python dependencies for Streamlit Cloud |
| `v2/.streamlit/config.toml` | Disables usage stats, enables headless mode |
| `v2/scripts/seed_demo.py` | Seeds Fire & Flow Gospel demo data |
| `v2/scripts/__init__.py` | Makes scripts/ importable from app.py |
| `v2/app.py` | Updated — auto-seeds on cold start via `@st.cache_resource` |
| `v2/config.py` | Updated — MOCK_MODE auto-enables when no API key present |
