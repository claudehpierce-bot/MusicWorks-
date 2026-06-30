# Approval Queue™
## Technical Specification
**System:** MindSpark MusicWorks™ — Execution Engine
**Component:** Approval Queue™
**Version:** 1.0 — Design Specification

---

## What This Is — Plain English

The Approval Queue is the only screen you need.

It is the founder's dashboard. Everything your agents produced, everything the renderers created, everything that is waiting for your decision — it all appears here, in one place, with previews, in the order you should review it.

You watch the video. You read the caption. You see the thumbnail. You press APPROVE or REVISE. That is the complete founder experience. You never open another app to review an asset. You never receive files in email. You never dig through a folder looking for the right version.

**The goal:** A founder who is excellent at discernment — who knows immediately whether a caption is right, whether the video serves the mission, whether the thumbnail will stop the scroll — should be able to review an entire campaign in 20 minutes. The Approval Queue is designed around that founder.

---

## The Screen — Complete Layout

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MUSICWORKS™  ·  APPROVAL QUEUE
  HLANGANA — Kingdom Word Short #001
  10 items ready · 0 approved · Campaign launches in 9h 15m
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CAMPAIGN HEALTH          MODE            LAUNCH WINDOW
  🟡 Awaiting Review       Blitz           July 3, 2026 8:30 AM EST

  ───────────────────────────────────────────────────────────────
  FILTER:  [ All (10) ]  [ Video (1) ]  [ Social (4) ]  [ Written (3) ]  [ Visual (2) ]
  SORT:    [ By deadline ▼ ]  [ By type ]  [ By status ]
  ───────────────────────────────────────────────────────────────

  ┌─ ITEM 1 ───────────────────────────────────── TIME-SENSITIVE ─┐
  │                                                               │
  │  VIDEO PACKAGE                                                │
  │  HLANGANA Kingdom Word Short #001                             │
  │                                                               │
  │  ┌─────────────────────────────────────────────────────────┐  │
  │  │                                                         │  │
  │  │           [▶ 47-second video preview plays here]        │  │
  │  │                                                         │  │
  │  │           Resolution: 1080×1920  ·  Aspect: 9:16        │  │
  │  │           Has captions: Yes  ·  Has audio: Yes          │  │
  │  └─────────────────────────────────────────────────────────┘  │
  │                                                               │
  │  Platforms: Instagram Reels · YouTube Shorts · TikTok        │
  │  Due:       July 3, 2026 8:30 AM EST (9h 15m from now)       │
  │  Rendered by: Veo + human assembly                            │
  │  Version:   1  ·  Revision count: 0                          │
  │  Theological flags: NONE                                      │
  │                                                               │
  │  ┌──────────────┐  ┌─────────────────────┐  ┌────────────┐  │
  │  │  ✓ APPROVE   │  │  ↺ REQUEST REVISION  │  │  ✗ REJECT  │  │
  │  └──────────────┘  └─────────────────────┘  └────────────┘  │
  └───────────────────────────────────────────────────────────────┘

  ┌─ ITEM 2 ───────────────────────────────────── TIME-SENSITIVE ─┐
  │  INSTAGRAM REEL CAPTION                                       │
  │  ─────────────────────────────────────────────────────────    │
  │  Do you know this word?                                       │
  │                                                               │
  │  HLANGANA (H-La-Nga-Na)                                       │
  │                                                               │
  │  It's a Zulu word that means: GATHER TOGETHER.                │
  │                                                               │
  │  And the Bible speaks directly to this — Hebrews 10:25...     │
  │                                                          [▼]  │
  │  ─────────────────────────────────────────────────────────    │
  │  Characters: 980/2200  ·  Hashtags: 20  ·  Has CTA: Yes      │
  │  Scripture: Hebrews 10:25 ✓  ·  Theological flags: NONE      │
  │  ─────────────────────────────────────────────────────────    │
  │  PINNED COMMENT:                                              │
  │  📖 Hebrews 10:25 — "not giving up meeting together..."       │
  │  ─────────────────────────────────────────────────────────    │
  │  ┌──────────────┐  ┌─────────────────────┐  ┌────────────┐  │
  │  │  ✓ APPROVE   │  │  ↺ REQUEST REVISION  │  │  ✗ REJECT  │  │
  │  └──────────────┘  └─────────────────────┘  └────────────┘  │
  └───────────────────────────────────────────────────────────────┘

  [... Items 3–10 continue below ...]
```

---

## Item Card Specification

Each item in the queue is displayed as a card. The card design differs slightly by asset type.

### Video Card
- Inline video player — plays without leaving the page
- First-frame thumbnail shown before play
- Duration, resolution, aspect ratio shown
- Platform badges (which platforms this video is for)
- Theological flag indicator
- Revision count (shows how many times this asset has been revised already)
- Time-to-deadline badge (red if under 4 hours, yellow if under 24 hours)
- Full-resolution download link (for detailed inspection on a TV screen, etc.)

### Caption Card
- Full caption text, scrollable
- Platform icon
- Character count + limit
- Hashtag count
- CTA type
- Scripture reference with accuracy indicator
- Expandable "Pinned comment" section
- "Compare platforms" toggle (shows all 4 platform captions side-by-side)

### Thumbnail Card
- Full-size image preview (fills the card)
- Shows actual size proportional preview
- Resolution confirmation
- A/B toggle if two options are presented
- Canva instructions expandable section (in case founder wants to modify in Canva)

### Written Asset Card (Blog Post, Press Release)
- Full text in a readable formatted preview (markdown rendered)
- Word count
- SEO check summary (keywords, meta description)
- Theological check summary
- For press release: a bold warning banner if the founder quote is still a draft
- Scripture accuracy indicator

---

## The Revision Flow — What Happens When You Click REVISE

This is the most important interaction in the entire system. The Approval Queue must make revisions fast and specific.

### Step 1: Founder clicks REVISE

The revision panel slides open beneath the asset card:

```
┌─────────────────────────────────────────────────────────────────┐
│  REQUEST REVISION — HLANGANA Kingdom Word Short Video           │
│                                                                 │
│  What needs to change? Be specific.                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ The scripture overlay appears too late — it shows at    │   │
│  │ 0:20 but I want it at 0:08, right after the sunrise     │   │
│  │ gradient starts. Also: the pronunciation guide should   │   │
│  │ come before the meaning reveal.                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Which version to base the revision on?                         │
│  ● Version 1 (current)                                          │
│                                                                 │
│  Priority:                                                      │
│  ● HIGH — needed before launch                                  │
│  ○ NORMAL — can wait                                            │
│                                                                 │
│  [ Submit Revision Request ]    [ Cancel ]                      │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: System Processes the Revision

1. Approval Queue creates a `RevisionRequest` contract with the founder's notes
2. Asset status in Asset Library → `REVISION_REQUESTED`
3. Approval Queue sends `RevisionRequest` to Render Orchestrator
4. Render Orchestrator reads the notes, builds a new prompt, dispatches to Job Queue
5. Job Queue renders the revision (priority: HIGH)
6. Revised asset arrives in Asset Library as version 2
7. Approval Queue shows a notification: "Revision ready for review"
8. Founder sees the revised item in the queue, with both versions visible

### Step 3: Before/After Comparison

When a revision is ready, the founder sees both versions simultaneously:

```
┌─ ITEM 1 — REVISION READY ─────────────────────────────────────┐
│                                                               │
│  VIDEO PACKAGE  ·  Revision 1 of 1                           │
│                                                               │
│  ┌──────────────────────┐  ┌──────────────────────┐          │
│  │  VERSION 1 (original)│  │  VERSION 2 (revised) │          │
│  │  ─────────────────   │  │  ─────────────────   │          │
│  │  [▶ preview]         │  │  [▶ preview]         │          │
│  │                      │  │                      │          │
│  │  Scripture at: 0:20  │  │  Scripture at: 0:08  │          │
│  └──────────────────────┘  └──────────────────────┘          │
│                                                               │
│  Your revision note: "Scripture overlay appears too late..."  │
│                                                               │
│  ┌────────────────────────┐  ┌───────────────────────────┐   │
│  │  ✓ APPROVE VERSION 2   │  │  ↺ REVISE AGAIN (Round 2) │   │
│  └────────────────────────┘  └───────────────────────────┘   │
│                                                               │
│  ⚠ This is revision 1 of 3 maximum. After 3 revision cycles, │
│    this item will require a direct review session.           │
└───────────────────────────────────────────────────────────────┘
```

---

## The 3-Revision Limit and Escalation

If an asset reaches 3 revision cycles without approval, the Approval Queue escalates:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESCALATION NOTICE — HLANGANA Video
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This asset has been revised 3 times without reaching approval.
This usually means there is a fundamental problem with the
concept — not just execution details.

What you should do:
Option A: Review all three versions side by side and select the
          closest one. Approve it and note remaining concerns in
          the approval log.

Option B: Reject this asset and ask the Video Production Agent
          to propose a completely different concept.

Option C: Approve the current version as "provisional" and plan
          a full re-do for the next campaign, using what you
          learned from this round.

All three versions are preserved in the Asset Library.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Special Handling — Founder-Required Input

Some assets cannot be fully reviewed until the founder provides personal input that no agent can generate. The Approval Queue identifies these and blocks approval until the input is received.

### The Press Release Quote

```
┌─ ITEM 7 ─────────────────────────────────── ACTION REQUIRED ──┐
│                                                               │
│  PRESS RELEASE  ·  ⚠ REQUIRES YOUR INPUT BEFORE APPROVAL     │
│                                                               │
│  The attributed quote in this press release is a draft        │
│  written by the agent. You cannot approve this document       │
│  until you replace this quote with your own words.            │
│                                                               │
│  DRAFT QUOTE (from agent — DO NOT SEND AS IS):                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ "There is so much theological wealth sitting in the     │  │
│  │  languages of the African diaspora that the Church has  │  │
│  │  not fully unlocked..." — [FOUNDER NAME]                │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  YOUR QUOTE (type your actual words here):                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                                                         │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  [ Save My Quote and Continue Review ]                        │
│                                                               │
│  ⓘ This is the only asset in MusicWorks that requires your   │
│    personal words. Everything else can be generated and       │
│    reviewed. This one requires you.                           │
└───────────────────────────────────────────────────────────────┘
```

---

## Stale Review Alerts

If an item has been in `READY_FOR_REVIEW` for more than 7 days without a decision, the Approval Queue sends a stale review alert. If the item has an imminent publication deadline, the warning escalates.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ STALE REVIEW ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Asset:          HLANGANA Blog Post
In queue since: 8 days ago (June 27, 2026)
Deadline:       July 5, 2026 (6 days from now)

This asset will miss its publication window if not reviewed
by July 3, 2026.

Review now →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Batch Operations

For campaigns with many similar assets (e.g., four platform captions for the same video), the founder can review them in batch mode.

### Platform Caption Comparison Mode

```
CAPTION COMPARISON — HLANGANA Kingdom Word Short #001
All four platform captions, side by side.

┌─────────────────────┐ ┌──────────────────────┐
│  INSTAGRAM          │ │  TIKTOK               │
│  ───────────────    │ │  ───────────────       │
│  Do you know this   │ │  This Zulu word is    │
│  word?              │ │  in the Bible 🤯       │
│                     │ │                       │
│  HLANGANA...        │ │  HLANGANA = Gather    │
│  [scroll]           │ │  Together             │
│                     │ │                       │
│  Chars: 980/2200    │ │  Chars: 180/2200      │
│  Tags: 20           │ │  Tags: 8              │
└─────────────────────┘ └──────────────────────┘

┌─────────────────────┐ ┌──────────────────────┐
│  YOUTUBE            │ │  FACEBOOK             │
│  ───────────────    │ │  ───────────────       │
│  HLANGANA Means     │ │  This is a word the   │
│  "Gather Together"  │ │  Church needs right   │
│  — Kingdom Word     │ │  now...               │
│  Short #001         │ │                       │
│  [scroll]           │ │  [scroll]             │
│                     │ │                       │
│  Chars: 640/5000    │ │  Chars: 670/63000     │
│  Tags: 15           │ │  Tags: 6              │
└─────────────────────┘ └──────────────────────┘

Are these consistent with each other? Core facts align?
[ ✓ APPROVE ALL 4 CAPTIONS ]  [ Review individually ]
```

---

## Notification System

### V2
Email notification to founder when:
- All rendering completes and queue is ready for review
- A revision is complete and ready for re-review
- A stale review alert fires
- A job fails (DEAD status)

### V3
Push notification (mobile app) + email + in-app badge count.

Notification format:
```
Subject: Your HLANGANA campaign is ready for review (10 items)
Body:
Your Agent Orchestra has finished generating assets for
HLANGANA — Kingdom Word Short #001.

10 assets are waiting for your review in the Approval Queue.
Campaign launches in 9h 15m.

[Review Now →]
```

---

## Approval Log — What Gets Written

Every decision the founder makes in the Approval Queue is written to the Asset Library's approval log permanently.

```json
{
  "log_entry_id": "log-001",
  "asset_id": "asset-hlangana-video-001",
  "campaign_id": "kingdom-word-short-001",
  "decision": "APPROVED",
  "decision_by": "founder",
  "decision_at": "2026-07-02T22:17:00Z",
  "revision_count_at_decision": 0,
  "theological_flags_at_decision": [],
  "founder_notes": "This is exactly what I envisioned. The opening silence with the word appearing — that's the hook.",
  "asset_version_approved": 1,
  "forwarded_to_publishing_agent_at": "2026-07-02T22:17:01Z"
}
```

This log is the permanent record. It cannot be edited or deleted. If a post generates controversy, the log shows what you approved, when you approved it, and that no theological flags were present at the time of approval.

---

## Technical Implementation Notes

### V2 — Minimum Viable Interface

The simplest V2 Approval Queue is a Streamlit app with one page per campaign. Streamlit is a Python library that turns a Python script into a web app in about 20 lines of code.

```python
import streamlit as st
from asset_library import AssetLibrary

st.title("MusicWorks™ Approval Queue")
st.subheader("HLANGANA — Kingdom Word Short #001")

library = AssetLibrary()
assets = library.get_ready_for_review(campaign_id="kingdom-word-short-001")

for asset in assets:
    st.markdown(f"### {asset.description}")

    if asset.asset_category == "video":
        st.video(asset.preview_url)
    elif asset.asset_category == "image":
        st.image(asset.preview_url)
    elif asset.asset_category == "text":
        st.markdown(asset.preview_text)

    col1, col2, col3 = st.columns(3)
    if col1.button(f"✓ APPROVE", key=f"approve_{asset.asset_id}"):
        library.approve(asset.asset_id, decision_by="founder")
    if col2.button(f"↺ REVISE", key=f"revise_{asset.asset_id}"):
        notes = st.text_area("Revision notes:", key=f"notes_{asset.asset_id}")
        if st.button("Submit", key=f"submit_{asset.asset_id}"):
            library.request_revision(asset.asset_id, notes=notes)
    if col3.button(f"✗ REJECT", key=f"reject_{asset.asset_id}"):
        library.reject(asset.asset_id)
```

This is buildable in one afternoon. It is not beautiful but it is functional. The founder's experience is materially better than reviewing files in email.

### V3 — Production Interface

A proper React or Next.js web app with:
- Inline video player (HLS streaming from CDN)
- Side-by-side comparison mode
- Keyboard shortcuts (A = approve, R = revise, X = reject, → = next)
- Mobile-friendly (founder can review on their phone)
- Real-time updates (new assets appear without page refresh via WebSocket)
- Push notifications via Firebase Cloud Messaging

---

## Hard Rules for the Approval Queue

**Rule 1: Nothing publishes without APPROVED status.**
This is the foundational rule of the entire system. The Approval Queue is the gate. It does not open without an explicit founder decision.

**Rule 2: The founder never downloads, renames, or moves a file.**
All file handling is invisible. The founder sees content, not files.

**Rule 3: Every decision is final and logged.**
An APPROVED decision cannot be undone by clicking a button. If you want to un-approve something, you REJECT the current version and request a new render. This creates a clear audit trail.

**Rule 4: Revision notes are mandatory.**
You cannot submit a revision request without notes. "Make it better" is not a note. The system will prompt for specific instructions.

**Rule 5: Press release quotes are always human-written.**
The Approval Queue will never let a press release with a generated quote pass to APPROVED status. It enforces this at the UI level — the APPROVE button is disabled until the founder types their own quote.

---

*Approval Queue™ Specification — MindSpark MusicWorks™ Execution Engine — Version 1.0*
