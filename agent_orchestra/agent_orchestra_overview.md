# Agent Orchestra™ — Overview
**System:** MindSpark MusicWorks™
**Module:** Autonomous Creative Agents™
**Version:** 1.0
**Status:** Sprint 3 — Architecture Complete

---

## What Is the Agent Orchestra?

The Agent Orchestra is the campaign execution layer of MusicWorks. Where the Core pipeline (Agents 01–13) takes an album from idea to distribution-ready, the Agent Orchestra takes approved music and produces the actual campaign assets — the videos, captions, thumbnails, blog posts, press releases, posting schedules, and analytics frameworks — ready for founder review and approval before anything goes public.

**The experience the founder should have:**

> "MusicWorks prepared the campaign. Here is your review queue. Approve, revise, or reject each asset."

Not: "Here are some prompts. Go run these in five different tools."

---

## How the Orchestra Differs From Core

| | MusicWorks Core (Agents 01–13) | Agent Orchestra™ |
|--|-------------------------------|-----------------|
| **What it does** | Takes album from concept to distribution-ready | Takes approved music and produces campaign assets |
| **When it runs** | Before release | After distribution approval; during campaign |
| **Output type** | Strategy documents, checklists, packages | Specific assets ready for review and publication |
| **Approval** | Hard gates at theology and QC | Every asset individually approved before publishing |
| **Runs** | Once per release | Continuously — one campaign package per song, short, or content piece |

---

## The Nine Agents

| # | Agent | Department Equivalent | Primary Output |
|---|-------|----------------------|----------------|
| 1 | Video Production Agent™ | Video Department | Storyboard, shot list, Veo/Hedra job plan, preview package |
| 2 | Social Media Agent™ | Social Department | Platform-specific captions, hashtags, CTAs, schedule |
| 3 | Blog & Press Agent™ | PR Department | Blog posts, press release, devotional articles |
| 4 | Thumbnail & Art Agent™ | Creative/Design Department | Thumbnail concepts, Canva briefs, image specs |
| 5 | Publishing Agent™ | Distribution Department | Publish-ready checklist, file confirmations, schedule package |
| 6 | Campaign Agent™ | Marketing Department | Campaign calendar, mode selection, agent coordination |
| 7 | Approval Agent™ | Executive Office | Approval queue, decision log, revision tracking |
| 8 | Analytics Agent™ | Data Department | Performance tracking, daily report, health score |
| 9 | Learning Agent™ | Strategy Department | Post-campaign review, pattern capture, feed-forward |

---

## The Orchestration Flow

Every campaign package follows this flow:

```
[SONG INPUT + CAMPAIGN INPUT]
           ↓
[6] Campaign Agent™
  — selects campaign mode
  — assigns tasks to agents
  — sets content calendar
           ↓
 ┌─────────────────────────────────────────┐
 │  Agents run in parallel:                │
 │  [1] Video Production Agent™            │
 │  [2] Social Media Agent™                │
 │  [3] Blog & Press Agent™                │
 │  [4] Thumbnail & Art Agent™             │
 └─────────────────────────────────────────┘
           ↓
[5] Publishing Agent™
  — assembles all assets
  — confirms file names, links, captions
  — prepares publish packages
           ↓
[7] Approval Agent™
  — collects everything
  — presents unified review queue to founder
  — status: READY_FOR_REVIEW
           ↓
[FOUNDER REVIEWS — YES / NO / REVISE]
           ↓
  APPROVED → [5] Publishing Agent™ schedules
  REJECTED → archived, not used
  REVISION → returns to originating agent
           ↓
[8] Analytics Agent™
  — tracks performance after publishing
  — produces daily and weekly reports
           ↓
[9] Learning Agent™
  — post-campaign review
  — feeds findings into next campaign's [6] Campaign Agent™
```

---

## The Non-Negotiable Rule

**Nothing moves to SCHEDULED or PUBLISHED status without founder APPROVED status.**

This is not a preference. It is a structural constraint baked into every agent's output format and enforced by the Approval Agent. The Approval Agent is the only agent that can change an asset's status from READY_FOR_REVIEW to APPROVED — and only after the founder explicitly marks it as approved.

---

## Version States

| Version | State | What Works |
|---------|-------|-----------|
| V1 (Now) | Document simulation | Agents produce fully-written assets in markdown documents. Founder reviews documents. Manual execution. |
| V2 | Claude API powered | Agents are live Claude API calls. Assets generated on demand. Approval queue is a real interface. Manual publishing. |
| V3 | External integrations | Approved assets are automatically delivered to YouTube, TikTok, Instagram, email, Canva, etc. |

**We are in V1. Every asset in V1 is a complete, human-readable document. The founder can read exactly what the asset is, approve it, and manually execute the publication. V1 proves the workflow. V2 and V3 automate what is proven.**

---

## Relationship to the Fire & Flow Launch Engine

The Launch Engine (Sprint 2) defines the campaign strategy — what modes to run, when to post, what the 90-day calendar looks like. The Agent Orchestra executes that strategy by producing the actual assets that fill the calendar.

- **Launch Engine** = the plan
- **Agent Orchestra** = the execution
- **Approval Agent** = the control gate between them

---

## First Deployment: HLANGANA — Kingdom Word Short #001

The first simulated Agent Orchestra campaign package is for the Fire & Flow Gospel campaign "Kingdom Word Short #001," featuring the song HLANGANA (meaning: Gather Together, Scripture: Hebrews 10:25). The complete simulated output is in `/sample_outputs/sample_hlangana_campaign_package.md`.

---

*Agent Orchestra™ — MindSpark MusicWorks™ — V1.0*
