# Autonomous Creative Agents™ — System Specification
**System:** MindSpark MusicWorks™
**Document:** Sprint 3 Technical Specification
**Version:** 1.0

---

## System Purpose

The Autonomous Creative Agents™ system is the AI-powered campaign production layer of MusicWorks. Its single purpose is to convert approved song and campaign inputs into finished, founder-reviewable creative assets — then hold those assets in a review queue until the founder approves them.

The system never publishes. It prepares and waits.

---

## Agent Operating States

Every agent in the orchestra exists in one of four operating states at any given time:

| State | Meaning |
|-------|---------|
| `IDLE` | No active task. Awaiting assignment from Campaign Agent. |
| `ACTIVE` | Processing a task. Producing outputs. |
| `WAITING_APPROVAL` | Output complete. Asset in Approval Agent queue. Awaiting founder decision. |
| `IN_REVISION` | Founder requested revision. Agent re-processing with revision notes. |

---

## Asset Status Lifecycle

Every asset produced by any agent carries a status field. Status flows in one direction only — no asset can skip a status or move backward without a revision cycle.

```
DRAFT
  ↓
READY_FOR_REVIEW      ← Agent submits to Approval Agent
  ↓
  ├── APPROVED         ← Founder says YES
  │     ↓
  │   SCHEDULED        ← Publishing Agent sets date/time
  │     ↓
  │   PUBLISHED        ← Asset has gone live (manual or automated)
  │
  ├── REJECTED         ← Founder says NO — asset archived, not used
  │
  └── REVISION_REQUESTED ← Founder says REVISE with notes
            ↓
          DRAFT         ← Returns to originating agent with revision brief
```

**Hard rule:** No asset may reach SCHEDULED or PUBLISHED without passing through APPROVED. This constraint is checked by the Approval Agent and is not overridable.

---

## How Agents Communicate (The Contract System)

In V1, agents communicate through structured documents. In V2+, they communicate through typed JSON data contracts. The same contracts are used in both versions — V1 uses them as document templates; V2+ uses them as actual API payloads.

All contract definitions are in `/shared_contracts/shared_contracts.md`.

**Data flow example:**
```
Campaign Agent reads:    SongInput + CampaignInput
Campaign Agent writes:   VideoAssetRequest → Video Production Agent
                         SocialPostRequest → Social Media Agent
                         [etc.]

Video Production Agent reads:  VideoAssetRequest + SongInput
Video Production Agent writes: ApprovalItem (status: READY_FOR_REVIEW) → Approval Agent

Approval Agent reads:   All ApprovalItems
Approval Agent writes:  ApprovalItem.status = APPROVED/REJECTED/REVISION_REQUESTED
                        If APPROVED → PublishingAgent
                        If REVISION → RevisionRequest → originating agent

Analytics Agent reads:  Published ApprovalItems + manual performance data
Analytics Agent writes: CampaignReport

Learning Agent reads:   CampaignReport + all ApprovalItems
Learning Agent writes:  LearningRecord → feeds next campaign's CampaignInput
```

---

## The Campaign Agent as Orchestrator

The Campaign Agent is the conductor of the orchestra. It does not produce creative assets itself. It:

1. Receives the SongInput and CampaignInput
2. Selects the campaign mode (Standard / Growth / Blitz / Chart Push / Ministry Push)
3. Assigns tasks to each creative agent
4. Sets the content calendar (what publishes when)
5. Monitors for conflicts (two agents producing duplicate messaging)
6. Escalates risks or blockers to the founder

The Campaign Agent is the first agent that runs. Nothing else starts until the Campaign Agent has produced its campaign plan.

---

## The Approval Agent as Gatekeeper

The Approval Agent is the last agent before the founder and the last agent before publication. It:

1. Collects every asset produced by every agent
2. Organizes them into a clean, readable approval queue
3. Presents the queue to the founder
4. Records every founder decision with timestamp
5. Routes decisions back to agents (revision) or forward to Publishing Agent (approved)
6. Maintains the permanent approval log for audit purposes

The Approval Agent never generates creative content. It only manages the flow of assets and decisions.

---

## V1 Behavior (Document Simulation — Current)

In V1, every agent is a structured document that:
- Describes exactly what it would produce
- Contains the actual content it would generate (written by the system)
- Uses all status fields and contract formats as document headers
- Requires manual execution after approval

**The founder experience in V1:**
- Opens the approval package document
- Reads each prepared asset
- Marks YES / NO / REVISE on each asset
- Manually executes publication of approved assets
- Records performance data manually into the Analytics Agent template

**V1 is not a limitation. It is a deliberate validation step.** The workflow is proven in documents before it is built in code.

---

## V2 Behavior (Claude API — Next)

In V2, agents are live Claude API calls:
- Campaign Agent sends a task prompt to Claude
- Claude returns a structured JSON response (the asset)
- The response is parsed into the appropriate contract format
- The asset appears in a real approval queue interface (Notion, Airtable, or custom)
- Founder approves in the interface with a button click
- Publishing Agent prepares manual posting instructions automatically

**V2 removes the document-writing overhead. The content is generated on demand, not pre-written.**

---

## V3 Behavior (External Integrations — Future)

In V3, approved assets are automatically delivered:
- Video Production Agent → sends render job to Veo or Hedra API → receives rendered video
- Social Media Agent → approved captions are scheduled in Buffer, Later, or native platform APIs
- Blog & Press Agent → approved articles are published to WordPress or CMS
- Thumbnail & Art Agent → approved briefs are sent to Canva API for generation
- Publishing Agent → automated publication with confirmation callback

**V3 removes manual publishing. The founder approves. The system executes.**

---

## Quality Standards That Apply to Every Agent

These standards apply to every asset produced by every agent, regardless of content type:

1. **Theological accuracy:** No scripture misquoted, no theology misrepresented. Every agent's output is subject to the brand's theological standards.
2. **Brand voice:** Warm, confident, spiritually grounded, credible. Never preachy, never hype.
3. **Transparency:** Where AI generation is involved in the final published content (e.g., AI-generated imagery), the disclosure standard from the business brief applies.
4. **One CTA per post:** No asset may contain more than one primary call to action.
5. **Completeness:** An asset submitted as READY_FOR_REVIEW must be complete — no placeholder text, no "[insert here]" fields left unfilled.

---

## Error Handling (V1 — Document System)

| Error | How It Is Handled |
|-------|------------------|
| Incomplete SongInput | Campaign Agent flags it before running. Cannot proceed without complete input. |
| Theological concern in draft output | Agent flags it with a RED NOTE before submitting for review. Founder must address before approval. |
| Asset rejected after 3 revisions | Campaign Agent escalates to founder for direct intervention. |
| Approval queue item older than 14 days with no decision | Campaign Agent sends reminder. Stale reviews are a campaign risk. |
| Missing link at time of publishing | Publishing Agent blocks the publish package until all links are confirmed working. |

---

*Specification Version 1.0 — Agent Orchestra™ — MindSpark MusicWorks™*
