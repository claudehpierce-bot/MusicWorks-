# Founder Approval Model
**System:** MindSpark MusicWorks™ — Agent Orchestra™
**Document:** Sprint 3
**Version:** 1.0

---

## The Core Promise

Every asset produced by every agent in the orchestra waits in a review queue until the founder makes a decision. The founder's three decisions are:

| Decision | Code | What Happens |
|----------|------|-------------|
| **YES** | `APPROVED` | Asset moves to Publishing Agent for scheduling |
| **NO** | `REJECTED` | Asset is archived. Not used. No explanation required. |
| **REVISE** | `REVISION_REQUESTED` | Asset returns to the originating agent with the founder's revision notes |

**Nothing else happens.** There is no auto-publish. There is no default action. There is no "if you don't respond in 24 hours we'll publish anyway." The queue waits.

---

## The Seven Asset Statuses

### 1. DRAFT
The agent is actively working on this asset. Not yet ready for review.
- Who sets it: The originating agent (Video Production, Social Media, etc.)
- What it means: Work in progress — do not review yet
- Founder action: None

### 2. READY_FOR_REVIEW
The agent has completed the asset and submitted it to the Approval Agent queue.
- Who sets it: The originating agent when work is complete
- What it means: This asset is finished and awaiting founder decision
- Founder action: Review, then choose APPROVED / REJECTED / REVISION_REQUESTED

### 3. APPROVED
The founder has reviewed the asset and said YES.
- Who sets it: The Approval Agent, after recording founder's YES decision
- What it means: This asset may be scheduled for publication
- Next step: Publishing Agent picks it up and prepares the publish package

### 4. REJECTED
The founder has reviewed the asset and said NO.
- Who sets it: The Approval Agent, after recording founder's NO decision
- What it means: This asset will not be used in this campaign
- Next step: Archived in the campaign record. The Campaign Agent may request a replacement from the originating agent if the asset was critical to the calendar.

### 5. REVISION_REQUESTED
The founder has reviewed the asset and said REVISE, with specific notes.
- Who sets it: The Approval Agent, after recording the founder's revision notes
- What it means: The asset goes back to the originating agent with a RevisionRequest contract containing the founder's exact notes
- Next step: Originating agent produces a revised version → returns to READY_FOR_REVIEW

### 6. SCHEDULED
The approved asset has a confirmed publication date and time.
- Who sets it: The Publishing Agent, after receiving an APPROVED asset
- What it means: This asset is in the publishing queue
- Founder can still pull it back from here if circumstances change (requires REJECTED override)

### 7. PUBLISHED
The asset has gone live on its target platform.
- Who sets it: Publishing Agent confirms after publication (manual confirmation in V1; automated callback in V3)
- What it means: This asset is live and cannot be easily recalled
- Next step: Analytics Agent begins tracking performance

---

## The Approval Queue

The Approval Agent maintains the queue — a single document (V1) or interface (V2+) that shows the founder every asset awaiting review, organized by priority.

### Queue Display Format (V1 Document)

```
APPROVAL QUEUE — [Campaign Name]
Generated: [Date]
Awaiting Founder Decision: [N] assets

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ASSET #001
Type:        Short-Form Video
Agent:       Video Production Agent™
Title:       HLANGANA — Kingdom Word Short #001
Platform:    Instagram Reels / YouTube Shorts / TikTok
Status:      READY_FOR_REVIEW
Submitted:   [Date/Time]
Preview:     [Full asset content]

FOUNDER DECISION: [ ] APPROVED  [ ] REJECTED  [ ] REVISION_REQUESTED
Revision Notes (if applicable): _______________________________

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ASSET #002
Type:        Instagram Caption
Agent:       Social Media Agent™
Title:       HLANGANA — Instagram Reel Caption
Platform:    Instagram
Status:      READY_FOR_REVIEW
...

[Continues for all assets]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

APPROVAL SUMMARY
Total assets in queue:   [N]
Approved:                [ ]
Rejected:                [ ]
Revision requested:      [ ]
Pending:                 [ ]

Founder Signature: _____________________ Date: _________
```

---

## The Approval Log

Every approval decision is recorded permanently in the Approval Log. This log is never edited after an entry is made. It is the audit trail for every published asset.

### Log Entry Format

```
LOG ENTRY — ASSET #001
Campaign:         HLANGANA — Kingdom Word Short #001
Asset Type:       Short-Form Video
Originating Agent: Video Production Agent™
Submitted:        [Date + Time]
Decision:         APPROVED
Decision By:      [Founder Name]
Decision Date:    [Date + Time]
Revision Count:   0
Notes:            None
```

### Log Entry — Revision Example

```
LOG ENTRY — ASSET #003 (Revision 1)
Campaign:         HLANGANA — Kingdom Word Short #001
Asset Type:       Blog Post
Originating Agent: Blog & Press Agent™
Submitted:        [Date + Time]
Decision:         REVISION_REQUESTED
Decision By:      [Founder Name]
Decision Date:    [Date + Time]
Revision Notes:   "The third paragraph is too promotional. Rewrite as
                   devotional reflection, not a product description."
Next Action:      Blog & Press Agent™ revises and resubmits
```

---

## Revision Protocol

When a founder requests a revision:

1. **Founder writes specific notes** — not "make it better" but "change X to Y because Z"
2. **Approval Agent creates a RevisionRequest** (see shared contracts) containing the exact notes
3. **RevisionRequest is sent to the originating agent** — the agent re-processes using the notes
4. **Revised asset returns as a new READY_FOR_REVIEW submission** with revision count incremented
5. **Founder reviews the revised version** — same YES / NO / REVISE decision

**Revision limit:** If an asset reaches 3 revisions without approval, the Campaign Agent escalates to the founder for direct intervention. The asset is marked BLOCKED until the founder makes a strategic decision about it.

---

## What the Founder Reviews in Each Asset

The approval queue is designed so the founder reviews **substance, not mechanics**. Every asset in the queue has already been checked for:
- Complete fields (no placeholders)
- Correct link formatting
- Hashtag relevance
- Brand voice compliance (by the originating agent's quality check)

The founder reviews for:
- **Theological accuracy** — Does this represent the Gospel correctly?
- **Brand voice** — Does this sound like Fire & Flow Gospel?
- **Strategic fit** — Is this the right angle for this campaign moment?
- **Personal comfort** — Would I be proud for this to represent my ministry publicly?

If any of these four questions produces doubt, the answer is REVISE or REJECT.

---

## Approval SLAs (Service Level Agreements)

These are not hard deadlines — they are quality guidelines to keep campaigns on schedule.

| Asset Type | Review Within |
|-----------|--------------|
| Time-sensitive content (launch day posts) | 24 hours of submission |
| Standard social content | 48–72 hours |
| Blog / long-form content | 72–96 hours |
| Video packages | 96 hours (more to review) |
| Press release | 48 hours |

**If the queue sits unreviewed for more than 7 days**, the Campaign Agent generates a stale queue alert. Stale approvals create scheduling problems and reduce campaign momentum.

---

## The Founder's Approval Rhythm (Recommended)

Rather than reviewing assets ad-hoc as they arrive, the recommended founder workflow is a **scheduled approval session** — a dedicated block of time to clear the queue.

**Recommended cadence:**
- **During Blitz mode:** Daily approval session (15–30 minutes)
- **During Standard mode:** Every 48 hours (15–20 minutes)
- **During Ministry Push mode:** 2–3 times per week (15–20 minutes)

**Session structure:**
1. Open the approval queue
2. Read each READY_FOR_REVIEW asset
3. Mark decision on each
4. Write revision notes on any REVISION_REQUESTED items
5. Sign and date the queue document
6. Hand signed queue to Publishing Agent

---

*Approval Model V1.0 — Agent Orchestra™ — MindSpark MusicWorks™*
*"Nothing publishes without approval. Not once. Not ever."*
