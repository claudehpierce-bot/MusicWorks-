# Job Queue™
## Technical Specification
**System:** MindSpark MusicWorks™ — Execution Engine
**Component:** Job Queue™
**Version:** 1.0 — Design Specification

---

## What This Is — Plain English

The Job Queue is the waiting room for every render job in the system.

When the Render Orchestrator creates a Veo job, it doesn't call Veo immediately. It places the job in the Job Queue. The Job Queue manages the line — deciding which job goes next, how many can run at the same time (some renderers have limits), what happens when a job fails, and when to alert you that something needs your attention.

Without a Job Queue, the system would try to start all renders at once. Veo might only accept two concurrent renders. The third would get rejected. Nobody would know. The system would silently fail.

**One analogy:** The Job Queue is the production floor of a recording studio. Jobs are like session bookings. The studio manager (Job Queue) makes sure Studio A (Veo) doesn't have two sessions booked at the same minute, that the urgent session for the album launch happens before the regular session, and that if an engineer doesn't show up (API failure), the session gets rebooked rather than cancelled.

---

## Job Lifecycle — The State Machine

Every job moves through exactly these states, in order:

```
          ┌─────────────┐
          │   QUEUED    │  ← Job created by Render Orchestrator
          └──────┬──────┘
                 │  (Job Queue picks up job for dispatch)
                 ▼
          ┌─────────────┐
          │ DISPATCHED  │  ← API call made to renderer
          └──────┬──────┘
                 │  (Renderer confirms job received)
                 ▼
          ┌─────────────┐
          │  RENDERING  │  ← Renderer is actively working
          └──────┬──────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
 ┌─────────────┐   ┌─────────────┐
 │  COMPLETED  │   │   FAILED    │
 └──────┬──────┘   └──────┬──────┘
        │                 │
        │          ┌──────┴──────┐
        │          │ retry_count │
        │          │ < max (3)?  │
        │          └──────┬──────┘
        │           YES   │   NO
        │           ┌─────┘
        │           ▼           ▼
        │       QUEUED      ┌──────────┐
        │      (re-queue)   │   DEAD   │  ← Alert founder
        │                   └──────────┘
        ▼
 ┌─────────────┐
 │  DELIVERED  │  ← Asset stored in Asset Library
 └─────────────┘

Additional states:
 ┌─────────────┐
 │   BLOCKED   │  ← Dependency not met — waiting for prerequisite
 └─────────────┘

 ┌─────────────┐
 │  CANCELLED  │  ← Founder rejected the parent asset; render no longer needed
 └─────────────┘
```

---

## The RenderJob Record (Full Schema)

```json
{
  "job_id": "job-hlangana-veo-clip-001",
  "created_at": "2026-07-02T21:30:00Z",
  "updated_at": "2026-07-02T21:45:00Z",

  "campaign_id": "kingdom-word-short-001",
  "song_id": "fire-flow-hlangana-001",
  "batch_id": "batch-hlangana-main-video",
  "batch_position": 1,
  "batch_total": 3,

  "asset_type": "short_form_video_clip",
  "asset_description": "Word reveal sequence — HLANGANA on indigo, 0:00–0:15",
  "target_platforms": ["instagram_reels", "youtube_shorts", "tiktok"],

  "renderer": "veo",
  "renderer_model": "veo-2",
  "renderer_job_id": null,

  "priority": "urgent",
  "status": "QUEUED",

  "prompt_payload": {
    "prompt": "Cinematic text reveal: the word HLANGANA appears letter by letter on deep indigo background (#2D1B69). Gold color (#D4A853), Montserrat bold font style. A warm sunrise gradient bleeds upward from the bottom of frame starting at second 3. Clean, devotional aesthetic. Duration: 15 seconds. Aspect ratio 9:16.",
    "negative_prompt": "faces, people, other text, logos, watermarks, violent content, sexual content",
    "duration": 15,
    "aspect_ratio": "9:16",
    "fps": 24,
    "resolution": "1080x1920",
    "style_reference": null
  },

  "dispatched_at": null,
  "rendering_started_at": null,
  "completed_at": null,

  "retry_count": 0,
  "max_retries": 3,
  "last_error": null,

  "output_file_url": null,
  "output_file_size_bytes": null,
  "output_asset_id": null,

  "is_revision": false,
  "revision_of_job_id": null,
  "revision_number": null,
  "revision_notes": null,

  "dependency_job_ids": [],
  "blocked_reason": null,

  "estimated_render_time_seconds": 300,
  "actual_render_time_seconds": null
}
```

---

## Priority System

Jobs are dispatched from the queue in priority order, not creation order.

| Priority | When Used | Example |
|----------|-----------|---------|
| `urgent` | Launch-day assets, anything due within 2 hours | HLANGANA video on July 3 launch day |
| `high` | Revision renders after founder review | Re-render requested at 10:30 PM, needed for 8:30 AM post |
| `normal` | Standard campaign assets due within 72 hours | Week 2 social content |
| `low` | Future campaign planning, non-time-sensitive | Kingdom Words episode 3 concept renders |

**Priority rules:**
1. Within the same priority, oldest jobs go first (FIFO)
2. URGENT jobs can preempt a NORMAL job currently in RENDERING only if the renderer supports cancellation (Veo does not — URGENT waits until the current slot is free)
3. Revision jobs are automatically set to HIGH priority

---

## Concurrency Management

Different renderers have different limits on how many jobs they can handle at once. The Job Queue enforces these limits and holds excess jobs in QUEUED state.

| Renderer | Max Concurrent Jobs | Job Duration Estimate | Notes |
|----------|--------------------|-----------------------|-------|
| Veo | 2 | 3–10 min per clip | Google's rate limits — subject to change |
| Hedra | 1 | 5–15 min per video | Conservative — Hedra is slower |
| Canva API | 5 | 5–30 seconds each | Very fast — batch these |
| Claude API | 10 | 2–10 seconds each | Very fast — batch these |

**Why this matters:** If a campaign needs 3 Veo clips and the limit is 2 concurrent, the Job Queue dispatches clips 1 and 2 together, waits for one to complete, then dispatches clip 3. This prevents rejected API calls and ensures all clips render without manual supervision.

---

## Polling and Webhooks

After dispatching a job, the Job Queue needs to know when it's done.

### V2 — Polling
The Job Queue checks the renderer's status API every 30 seconds.
```
Every 30 seconds, for each RENDERING job:
→ Call renderer_status_api(renderer_job_id)
→ If status == "complete": update job to COMPLETED, retrieve output file
→ If status == "failed": update job to FAILED, increment retry_count
→ If status == "rendering": no action, check again in 30 seconds
```

### V3 — Webhooks
Renderer sends a callback to MusicWorks when the job completes.
```
Renderer → POST https://musicworks.mindsparklabs.com/webhooks/render_complete
           {
             "renderer_job_id": "veo-job-123",
             "status": "complete",
             "output_url": "https://cdn.veo.ai/..."
           }
Job Queue → Match renderer_job_id to internal job_id → Update status → Route to Asset Library
```

Webhooks eliminate 30-second polling delay and reduce unnecessary API calls.

---

## Dead Job Alert Format

When a job reaches DEAD status (3 retries exhausted), the Job Queue sends a structured alert to the founder:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RENDER FAILURE ALERT — Manual Intervention Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Job ID:       job-hlangana-veo-clip-001
Asset:        HLANGANA word reveal clip (0:00–0:15)
Renderer:     Veo
Status:       DEAD (3 retries failed)
Last error:   "content_policy_violation: generated content contains
               text overlay inconsistent with policy"

What happened:
Veo rejected all 3 render attempts. The most likely cause is that
Veo's safety filter is detecting the brand name or text overlay
instructions as a policy issue.

What you should do:
Option A: Open Veo manually, paste the prompt below, and run it.
          When it completes, upload the file to the Asset Library.
Option B: Revise the prompt to remove text overlay instructions
          and add the text in post-production (CapCut).
Option C: Skip the Veo clip and use a static image + animation instead.

The Veo prompt that failed:
[prompt_payload.prompt]

Impact on campaign:
This clip is needed before: July 3, 8:30 AM EST
Current time: July 2, 11:00 PM EST
Time remaining: 9.5 hours
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Queue Dashboard — What the System Shows

The founder can view the current state of the Job Queue at any time:

```
JOB QUEUE™ — Current Status
Campaign: HLANGANA Kingdom Word Short #001
As of: July 2, 2026 — 10:00 PM EST
──────────────────────────────────────────────────────────────────
STATUS SUMMARY
  Completed: 8     Rendering: 2     Queued: 1     Blocked: 0
  Failed: 0        Dead: 0
──────────────────────────────────────────────────────────────────
ACTIVE JOBS (rendering now)
  ▶ job-001  Veo — Word reveal clip (0:00–0:15)        ~6 min left
  ▶ job-002  Veo — Community gathering clip (0:08–0:25) ~3 min left

QUEUED (waiting for slot)
  ⏳ job-003  Veo — Album art animation (0:35–0:42)    Priority: URGENT

COMPLETED
  ✓ job-004  Claude — Instagram caption                2 sec
  ✓ job-005  Claude — TikTok caption                   1 sec
  ✓ job-006  Claude — YouTube description              2 sec
  ✓ job-007  Claude — Facebook caption                 1 sec
  ✓ job-008  Claude — Blog post                        4 sec
  ✓ job-009  Canva  — Thumbnail Option A               8 sec
  ✓ job-010  Canva  — Thumbnail Option B               7 sec
  ✓ job-011  Claude — Church outreach blurb            1 sec
──────────────────────────────────────────────────────────────────
ESTIMATED COMPLETION: ~10 min
All assets ready for review approximately 10:10 PM EST
──────────────────────────────────────────────────────────────────
```

---

## Database Schema (V2 — SQLite or Airtable)

For V2, the Job Queue can be implemented as a simple SQLite database or an Airtable base with one table: `render_jobs`.

**If Airtable:**
- One base: "MusicWorks Execution Engine"
- One table: "Render Jobs"
- Fields: all fields from the RenderJob schema above
- Views:
  - "Active Queue" — filtered by status IN (QUEUED, DISPATCHED, RENDERING)
  - "Campaign View" — filtered by campaign_id, sorted by status
  - "Failed Jobs" — filtered by status IN (FAILED, DEAD)

**If SQLite:**
```sql
CREATE TABLE render_jobs (
    job_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    song_id TEXT NOT NULL,
    batch_id TEXT,
    asset_type TEXT NOT NULL,
    renderer TEXT NOT NULL CHECK(renderer IN ('veo','hedra','canva_api','claude_api')),
    priority TEXT NOT NULL CHECK(priority IN ('urgent','high','normal','low')),
    status TEXT NOT NULL DEFAULT 'QUEUED'
        CHECK(status IN ('QUEUED','DISPATCHED','RENDERING','COMPLETED',
                         'FAILED','DEAD','DELIVERED','BLOCKED','CANCELLED')),
    prompt_payload JSON,
    created_at TEXT NOT NULL,
    dispatched_at TEXT,
    completed_at TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_error TEXT,
    output_file_url TEXT,
    output_asset_id TEXT,
    is_revision INTEGER DEFAULT 0,
    revision_of_job_id TEXT,
    revision_notes TEXT
);

CREATE INDEX idx_render_jobs_campaign ON render_jobs(campaign_id);
CREATE INDEX idx_render_jobs_status ON render_jobs(status);
CREATE INDEX idx_render_jobs_priority_created ON render_jobs(priority, created_at);
```

---

## V2 Build Instructions

To implement Job Queue in V2:

1. Create the Airtable table (or SQLite database) with the schema above
2. Build a Python class `JobQueue` with methods: `enqueue()`, `dispatch_next()`, `poll_status()`, `mark_complete()`, `mark_failed()`
3. Run a background worker (simple `while True` loop with 30-second sleep) that calls `dispatch_next()` and `poll_status()`
4. Connect to the Render Orchestrator so new jobs are added on campaign trigger
5. Connect to the Asset Library so completed jobs route their output files

Estimated V2 build time: 1 day for a functional version.

---

*Job Queue™ Specification — MindSpark MusicWorks™ Execution Engine — Version 1.0*
