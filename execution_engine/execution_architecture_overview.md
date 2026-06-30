# MusicWorks™ Execution Engine
## Architecture Overview
**System:** MindSpark MusicWorks™
**Sprint:** Execution Architecture
**Version:** 1.0 — Design Specification
**Status:** DESIGN ONLY — No code built yet. This document is the blueprint.

---

## What We Are Building — Plain English First

In V1, you did this manually:
1. You opened Claude and typed a prompt
2. Claude gave you a caption — you copied it into Instagram
3. Claude gave you a Canva brief — you opened Canva and built the thumbnail yourself
4. Claude gave you a Veo prompt — you opened Veo and ran it yourself
5. You downloaded the video, renamed it, moved it to a folder
6. You reviewed it and decided if it was good

That works once. It doesn't scale to an album of 12 songs, each with 6 platform variants, each refreshed weekly.

**The Execution Engine replaces every manual step between "Claude produces a brief" and "finished asset appears in your approval screen."**

You will do exactly three things:
1. **Trigger the campaign** — one input, one time
2. **Approve the campaign plan** — a 5-minute review before any work starts
3. **Review finished assets** — watch previews and press APPROVE / REVISE / REJECT

Everything else — building prompts, calling APIs, generating files, storing them, presenting them to you — happens automatically while you are doing something else.

---

## The Before and After

### Before (V1 — Manual)
```
You → Prompt Claude → Copy caption → Paste into Instagram
You → Prompt Claude → Get Canva brief → Open Canva → Build thumbnail → Download → Rename → Upload
You → Prompt Claude → Get Veo prompt → Open Veo → Run generation → Wait 5 min → Download → Move file
You → Open 4 different folders → Decide if asset is good → Post manually
```
Total founder time per campaign: **8–12 hours**
Risk: Wrong file version posted. Broken links. Forgotten assets.

### After (V3 — Execution Engine)
```
You → Type: "Run HLANGANA in Blitz mode" → Review plan (5 min) → Approve
                    [System works for 30–60 minutes]
You → Open Approval Queue → Watch video preview → Press APPROVE
You → Done
```
Total founder time per campaign: **30–45 minutes**
Risk: Near-zero. Every asset is versioned, tracked, and linked. Nothing posts without your APPROVED stamp.

---

## The Four Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MINDSPARK MUSICWORKS™                            │
│                     EXECUTION ENGINE                                │
└─────────────────────────────────────────────────────────────────────┘

LAYER 1: CREATIVE INTELLIGENCE
┌──────────────────────────────────────────────────────────────────┐
│  Agent Orchestra™  (Sprint 3 — already built)                    │
│  Campaign Agent · Video Production · Social Media · Blog & Press │
│  Thumbnail · Publishing · Approval · Analytics · Learning        │
│  ↓ Produces: Prompts, briefs, task contracts                     │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
LAYER 2: ORCHESTRATION
┌──────────────────────────────────────────────────────────────────┐
│  RENDER ORCHESTRATOR™                                            │
│  Reads agent output → Selects renderer → Builds API payload     │
│  → Dispatches jobs → Monitors completion → Routes results       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
LAYER 3: EXECUTION
┌──────────────────────────────────────────────────────────────────┐
│  JOB QUEUE™                                                      │
│  Holds all pending render jobs in priority order                 │
│  Manages concurrency · Handles failures · Tracks status         │
│      │              │              │              │              │
│      ▼              ▼              ▼              ▼              │
│  [Veo API]    [Hedra API]    [Canva API]   [Claude API]         │
│  (videos)     (avatars)      (graphics)    (text assets)        │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
LAYER 4: STORAGE
┌──────────────────────────────────────────────────────────────────┐
│  ASSET LIBRARY™                                                  │
│  Single source of truth for every generated file                 │
│  Versioned · Organized by campaign · Preview URLs ready         │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
LAYER 5: FOUNDER INTERFACE
┌──────────────────────────────────────────────────────────────────┐
│  APPROVAL QUEUE™                                                 │
│  Founder sees all assets in one place                            │
│  Video previews · Image previews · Text previews                │
│  APPROVE → Publishing Agent                                      │
│  REVISE  → Render Orchestrator (re-renders automatically)       │
│  REJECT  → Archived                                             │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
LAYER 6: DISTRIBUTION
┌──────────────────────────────────────────────────────────────────┐
│  Publishing Agent™  (Sprint 3 — already designed)               │
│  V2: Generates execution-ready checklist                         │
│  V3: Calls platform APIs directly (YouTube, Meta, TikTok)       │
└──────────────────────────────────────────────────────────────────┘
```

---

## The Founder's Complete Journey (V3)

```
STEP 1 — TRIGGER                               [Founder: 1 minute]
─────────────────────────────────────────────────────────────────
You: "Campaign for HLANGANA — Kingdom Word Short #001 — Blitz mode"

System: Campaign Agent reads SongInput, selects Blitz mode,
        builds content calendar, identifies risks.

─────────────────────────────────────────────────────────────────
STEP 2 — PLAN APPROVAL                         [Founder: 5 minutes]
─────────────────────────────────────────────────────────────────
You see: Calendar, mode, risks. You press APPROVE.

System: Campaign Agent dispatches task contracts to all agents.
        Agents produce prompts and briefs.
        Render Orchestrator reads all briefs.
        Jobs enter the Job Queue.

─────────────────────────────────────────────────────────────────
STEP 3 — RENDERING                             [System: 30–60 min]
─────────────────────────────────────────────────────────────────
You: Doing something else.

System:
  Veo receives 3 video clip jobs → renders → returns MP4 files
  Canva receives 2 thumbnail jobs → renders → returns PNG files
  Claude receives 6 caption jobs → returns text in seconds
  Claude receives 1 blog post job → returns text in seconds
  All outputs land in Asset Library

─────────────────────────────────────────────────────────────────
STEP 4 — APPROVAL REVIEW                       [Founder: 20–30 min]
─────────────────────────────────────────────────────────────────
You receive notification: "Your HLANGANA campaign is ready for review."

You open the Approval Queue.
You see 10 assets with inline previews.
You watch the video. You read the captions. You see the thumbnail.
You press APPROVE on 8 items.
You press REVISE on 1 item (the video needs the scripture earlier).
You type your note. Press SUBMIT.

System: Revision job enters the Job Queue. Re-renders automatically.
        5 minutes later: revised video appears back in your queue.

You press APPROVE on the revised video.
All 10 assets: APPROVED.

─────────────────────────────────────────────────────────────────
STEP 5 — PUBLISHING                            [Founder: 10 minutes OR 0]
─────────────────────────────────────────────────────────────────
V2: Publishing Agent generates a pre-populated checklist.
    You open Instagram. One-click paste. Post. Done in 10 minutes.

V3: You press SCHEDULE.
    Publishing Agent calls Instagram API, YouTube API, TikTok API.
    Posts scheduled. Go live automatically at the approved time.
    You get a confirmation notification.
```

---

## What Each Renderer Does

| Renderer | Asset Type | V2 Status | V3 Status |
|----------|-----------|-----------|-----------|
| **Veo (Google)** | Short-form video clips, B-roll footage | Prompts generated; human runs Veo manually | Full API integration; clips auto-render |
| **Hedra** | AI avatar video (presenter speaking to camera) | Prompts generated; human runs Hedra manually | Full API integration; avatar auto-renders |
| **Canva API** | Thumbnails, quote cards, story frames | Semi-auto: system pre-fills template; founder one-click downloads | Full API; PNG files auto-generated |
| **Claude API** | All text: captions, blog posts, press releases, email copy | Fully automated in V2 | Fully automated in V3 |
| **Audio** | Song master, stems, clips | Never automated — always human-approved master | Same |

---

## Renderer Selection Logic

The Render Orchestrator reads each agent's job plan and selects the right renderer using this decision tree:

```
Asset requested:
│
├── IS IT TEXT? (caption, blog post, press release, email)
│   └── Renderer: Claude API  ✓ (fast, reliable, V2-ready)
│
├── IS IT A STATIC IMAGE? (thumbnail, quote card, story frame)
│   └── Renderer: Canva API  ✓ (template-based, V2-ready with setup)
│
├── IS IT A SHORT-FORM VIDEO (B-roll, word reveal, lyric visual)?
│   └── Renderer: Veo  (V3 — V2 humans run Veo manually from generated prompts)
│
├── IS IT AN AI AVATAR/PRESENTER VIDEO?
│   └── Renderer: Hedra  (V3 — V2 humans run Hedra manually)
│
└── IS IT AUDIO?
    └── Renderer: NONE — human-created master only. Never auto-generated.
```

---

## Version Roadmap

### V2 — "Smart Automation" (Build this first)
Claude API generates all text assets automatically.
Canva API generates thumbnails automatically.
Veo/Hedra prompts are generated automatically and presented to you as one-click "Run this in Veo" links — you still click run, but the prompt is already perfect.
Asset Library stores everything.
Approval Queue presents assets for review.
Publishing checklist is pre-populated — one-click paste into each platform.

**Founder experience improvement over V1:** Text and thumbnails fully automatic. Video still requires one manual step per clip.

### V3 — "Full Execution" (Build after V2 validation)
Veo API integration — system calls Veo directly, no manual step.
Hedra API integration — same.
Platform publishing APIs — Instagram, YouTube, TikTok, Facebook.
Full hands-off pipeline: trigger → approve plan → review assets → approve → done.

---

## Critical Design Principles

**1. The Asset Library is the ground truth.**
Every agent, every renderer, every approver reads from and writes to the Asset Library. Nothing lives in anyone's local folder, email attachment, or Dropbox. If it's not in the Asset Library, it doesn't exist.

**2. Status drives behavior.**
Every asset and every job has a status. The system only moves forward when statuses advance. A QUEUED job doesn't dispatch. A RENDERING job doesn't go to Asset Library. An APPROVED asset goes to Publishing — nothing else does.

**3. The founder never touches a file path.**
The founder approves content, not files. The system handles file naming, versioning, storage, and retrieval. The founder never downloads, renames, or re-uploads anything.

**4. Revisions re-render automatically.**
When the founder requests a revision, the system rebuilds the render job with the new instructions. The founder never re-runs a Veo prompt manually. They type a note. The system handles it.

**5. Audio is sacred.**
No system component ever generates or modifies audio. The human-approved master is the only audio source. All video renders use it as input — they do not create it.

---

*Execution Architecture Overview — MindSpark MusicWorks™ — Version 1.0*
