# Next Build Steps — Agent Orchestra™
**System:** MindSpark MusicWorks™
**Document:** Sprint 3 — Final Planning Document
**Version:** 1.0

---

## Where We Are Now

Sprint 3 is complete. The Agent Orchestra™ is fully designed and documented at V1 level:

- 9 agent instruction files written
- 8 shared data contracts defined
- Founder approval model documented
- Sample campaign package (HLANGANA) produced
- The V1 system is fully runnable manually

The entire system works today — with Claude, a document editor, and a founder who is willing to follow the workflow. No code required.

---

## The V2 Build (Recommended Next Sprint)

**What V2 adds:** Claude API integration. Instead of manually prompting Claude and copying outputs into documents, the system runs Claude as an agent programmatically. Each agent becomes a function call; each contract becomes a typed JSON payload.

**What V2 does NOT add:** External platform integrations. V2 is still human-in-the-loop for all publishing. The founder still posts manually.

### V2 Build Order

Build in this sequence — each item depends on the one before it.

**Step 1: Define the technical stack**
- Language: Python 3.11+
- Claude SDK: `anthropic` (official Python SDK)
- Storage: Airtable (recommended) or Notion for contract storage
- File storage: Google Drive or Cloudflare R2 for media assets
- Interface: Claude.ai interface initially; simple web UI in V2.1

**Step 2: Implement the SongInput contract as a database record**
- Create an Airtable base called "MusicWorks Core"
- Table: Songs — one row per song, fields match SongInput contract exactly
- Required fields must be validated before a campaign can start
- Theology Approved and Audio QC Approved are boolean fields — campaign cannot start without both = TRUE

**Step 3: Implement the Campaign Agent as a Python function**
```
Dependencies: shared_contracts, anthropic SDK
Input: SongInput record + founder campaign brief
Process:
  1. Read SongInput from Airtable
  2. Read most recent LearningRecord from learning_agent/records/
  3. Call Claude claude-sonnet-4-6 with CampaignAgent system prompt
  4. Return: CampaignInput JSON + ContentCalendar JSON + RiskLog JSON
  5. Write CampaignInput to Airtable
  6. Present to founder for approval before dispatching other agents
Output: Approved CampaignInput record
```

**Step 4: Implement each creative agent as a Python function**
Follow the same pattern for each:
- Video Production Agent
- Social Media Agent
- Blog & Press Agent
- Thumbnail & Art Agent

Each function takes a task contract as input and returns an `ApprovalItem` as output.

**Step 5: Implement the Approval Agent as an interface**
The approval queue should be a simple web page (or Claude artifact) that:
- Shows all READY_FOR_REVIEW assets in priority order
- Allows founder to click APPROVE / REJECT / REVISE
- Records decisions to Airtable with timestamp
- Triggers revision workflows automatically

**Step 6: Implement the Publishing Agent as a checklist generator**
Takes all APPROVED assets and generates a human-executable publishing checklist as a formatted document. Still manual publishing in V2 — just better organized.

**Step 7: Implement the Analytics and Learning Agents**
- Analytics Agent: reads from manually-entered spreadsheet, generates reports
- Learning Agent: runs on-demand at campaign close; writes LearningRecord to Airtable

---

## V2 Technical Dependencies

| Dependency | Purpose | Notes |
|-----------|---------|-------|
| `anthropic` Python SDK | All agent calls | Use latest stable version |
| Airtable API | Contract storage | Free tier works for validation |
| Google Drive API | Media asset storage | For managing video/audio/art files |
| Python `pydantic` | Contract validation | Validates SongInput completeness |
| Simple HTML/CSS or Streamlit | Approval interface | Streamlit is 10-line MVP |

---

## V3 Build (After V2 Validation)

**What V3 adds:** External platform integrations. The founder approves assets and V3 publishes them automatically.

### V3 Integration Priority Order

1. **YouTube API** — highest ROI. Upload Shorts and videos directly from approved assets.
2. **Instagram/Facebook Meta API** — publish Reels automatically with approved captions.
3. **Veo API (Google)** — generate video footage from the Video Production Agent's job plans.
4. **DistroKid or TuneCore API** — automate distribution confirmation and ISRC registration.
5. **TikTok for Developers API** — last, because TikTok's API is restrictive for music content.

**Do NOT build V3 before:**
- V2 has been used for at least 3 complete campaigns
- Every V2 workflow is stable and the founder trusts the output quality
- The founder has explicitly decided to remove manual publishing and accept automated publishing with oversight

---

## V1 Remediation Items (CTO Review — Still Unaddressed)

These items were identified in the Sprint 1 CTO review. They should be addressed before or alongside V2 build:

| Item | Priority | Status |
|------|----------|--------|
| Initialize Git repository | CRITICAL | Not done |
| Add Legal & Rights Clearance Agent (Agent 03.5) | HIGH | Not done |
| Promote pre-distribution check to hard gate | HIGH | Not done |
| Define document header standard | MEDIUM | Not done |
| Create Quick Start Guide | MEDIUM | Not done |
| Master Campaign Calendar template | MEDIUM | Not done |

**Recommended next action:** Initialize the Git repository first (15 minutes). Everything else builds on top of version control.

---

## Creative Studio™ (V3 Optional Module)

Designed in Session 4 — not yet built. Creative Studio™ is a completely separate module from MusicWorks Core that adds suggestion-layer brainstorming tools. It is optional, never auto-applies, and recommended for the V3 build phase.

Do not build Creative Studio™ until V2 Core is stable.

---

## Multi-Artist / Multi-Tenant (V4)

The current system is single-artist, single-album. V4 introduces:
- Project namespace system (isolate campaigns by artist and album)
- Team permissions (who can approve? who can edit? who can only view?)
- Template library (reuse campaign structures across artists)
- Billing and access tiers (if MindSpark MusicWorks™ becomes a SaaS product)

Do not design V4 until V2 has been used by at least one artist other than Fire & Flow Gospel.

---

## Summary: What to Build Next

| Priority | Sprint | Item | Estimated Effort |
|----------|--------|------|-----------------|
| 1 | Now (10 min) | Git init | 10 minutes |
| 2 | V1 Remediation | Legal Agent, header standard, Quick Start | 2–4 hours |
| 3 | V2 Sprint 1 | SongInput Airtable schema + Campaign Agent Python function | 1 day |
| 4 | V2 Sprint 2 | All 4 creative agents as Python functions | 2–3 days |
| 5 | V2 Sprint 3 | Approval Agent interface (Streamlit) | 1–2 days |
| 6 | V2 Sprint 4 | Analytics + Learning Agent | 1 day |
| 7 | V3 | YouTube API integration | 2–3 days |
| 8 | V3 | Meta API integration | 2–3 days |

---

*Next Build Steps — Agent Orchestra™ — MindSpark MusicWorks™ — Version 1.0*
