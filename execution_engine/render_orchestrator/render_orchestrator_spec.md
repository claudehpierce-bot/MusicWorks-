# Render Orchestrator™
## Technical Specification
**System:** MindSpark MusicWorks™ — Execution Engine
**Component:** Render Orchestrator™
**Version:** 1.0 — Design Specification

---

## What This Is — Plain English

The Render Orchestrator is the traffic controller for every rendering operation in MusicWorks.

When the Agent Orchestra produces a campaign brief — a Veo job plan, a Canva thumbnail brief, six social captions — it hands all of that to the Render Orchestrator. The Orchestrator's job is to read every brief, decide which tool handles which asset, build the exact API payload for each tool, dispatch the jobs to the Job Queue in the right order, watch for completions and failures, and route finished assets to the Asset Library.

Without the Render Orchestrator, you would have to read each brief yourself, build each prompt yourself, open each tool yourself, and move each file yourself. The Orchestrator does all of that automatically.

**One analogy:** The Render Orchestrator is the production manager of a film shoot. The director (Campaign Agent) says what needs to happen. The production manager figures out which crew (Veo, Hedra, Canva, Claude) does which job, schedules everyone, and makes sure the finished scenes land in the right place.

---

## Inputs

| Input | Source | When |
|-------|--------|------|
| VideoAssetRequest | Video Production Agent™ | After founder approves campaign plan |
| SocialPostRequest | Social Media Agent™ | Same |
| Written asset briefs | Blog & Press Agent™ | Same |
| Thumbnail briefs | Thumbnail & Art Agent™ | Same |
| RevisionRequest | Approval Queue™ | When founder requests a revision |
| LearningRecord | Learning Agent™ | Read once at campaign start — may affect prompt style |

---

## Outputs

| Output | Destination | When |
|--------|-------------|------|
| RenderJob records | Job Queue™ | For every asset that requires rendering |
| Direct text output | Asset Library™ | For Claude API text assets (no queue needed — returns in seconds) |
| Status updates | Campaign Agent™ | As jobs complete or fail |
| Revision jobs | Job Queue™ | When revision requests arrive from Approval Queue |

---

## The RenderJob Schema

Every job that enters the Job Queue is a RenderJob. This is the data structure the Render Orchestrator writes and the Job Queue reads.

```json
{
  "job_id": "job-hlangana-video-001",
  "campaign_id": "kingdom-word-short-001",
  "song_id": "fire-flow-hlangana-001",
  "asset_type": "short_form_video_clip",
  "asset_description": "HLANGANA word reveal + B-roll sequence, 0:00–0:35",
  "renderer": "veo",
  "priority": "urgent",
  "status": "QUEUED",
  "created_at": "2026-07-02T21:30:00Z",
  "dispatched_at": null,
  "completed_at": null,
  "retry_count": 0,
  "max_retries": 3,
  "batch_id": "batch-hlangana-video-001",
  "batch_position": 1,
  "batch_total": 3,
  "prompt_payload": {
    "prompt": "Cinematic text reveal sequence: the word HLANGANA appears letter by letter on a deep indigo background (#2D1B69), warm gold color (#D4A853), Montserrat font style. Sunrise gradient bleeds upward from the bottom. Duration: 15 seconds. No people. No other text. Photorealistic lighting. Gospel music atmosphere.",
    "duration_seconds": 15,
    "aspect_ratio": "9:16",
    "style": "cinematic",
    "negative_prompt": "text other than HLANGANA, people, faces, logos, watermarks"
  },
  "output_asset_id": null,
  "output_file_path": null,
  "error_message": null,
  "is_revision": false,
  "revision_of_job_id": null,
  "revision_notes": null,
  "founder_notes_applied": null
}
```

---

## Renderer Selection Decision Logic

The Render Orchestrator reads each agent brief and applies this logic to select the right renderer.

```python
def select_renderer(asset_brief):

    if asset_brief.asset_type in ["caption", "blog_post", "press_release",
                                   "email_copy", "church_blurb", "youtube_description"]:
        return "claude_api"
        # Fast. Returns in seconds. No queue needed — direct output.

    elif asset_brief.asset_type in ["thumbnail", "quote_card",
                                     "story_frame", "cover_graphic"]:
        return "canva_api"
        # Template-based. Returns PNG in seconds via API.
        # Requires: Canva templates pre-built and template_id known.

    elif asset_brief.asset_type in ["short_form_video_clip", "b_roll_footage",
                                     "lyric_visual", "word_reveal_animation"]:
        return "veo"
        # Slow (2–10 min per clip). Goes to Job Queue with URGENT priority.
        # V2: system builds Veo prompt; human runs it manually.
        # V3: Veo API called directly.

    elif asset_brief.asset_type in ["avatar_video", "presenter_intro",
                                     "ai_host_segment"]:
        return "hedra"
        # Requires: avatar image + audio script + voice selection.
        # V2: system builds Hedra job; human runs it manually.
        # V3: Hedra API called directly.

    elif asset_brief.asset_type in ["audio_clip", "song_master", "stem"]:
        raise HardBlockError("Audio assets are never auto-generated. "
                             "Use human-approved master only.")
```

---

## Prompt Assembly — The Core Responsibility

The most important thing the Render Orchestrator does is build the exact prompt that gets sent to each renderer. This is not passed in from the agent — the agent provides a structured job plan, and the Orchestrator builds the API-ready payload from it.

### For Veo

The Video Production Agent writes a Veo Job Plan in structured format:
```
Clip 1 — Background imagery (0:08–0:15)
Description: "Diverse people entering a sunlit church, warm golden morning
light, no identifiable faces"
Duration: 8 seconds
Style: Cinematic, photorealistic
Do NOT include: text, logos, identifiable faces
```

The Render Orchestrator converts this to a Veo API payload:
```json
{
  "model": "veo-2",
  "prompt": "Cinematic footage of diverse people entering a sunlit church or community space. Warm golden morning light streaming through open doors. People greeting each other. No identifiable faces in close-up. No text. No logos. Photorealistic. Gospel music atmosphere. Duration: 8 seconds.",
  "negative_prompt": "text, logos, watermarks, identifiable faces, violent content, sexual content",
  "duration": 8,
  "aspect_ratio": "9:16",
  "fps": 24,
  "resolution": "1080x1920"
}
```

The Orchestrator also adds brand safety context from a standing "Veo Safety Rules" config:
- Always include in negative_prompt: "violent content, sexual content, profanity"
- Always match aspect ratio to target platform
- Always request 24fps minimum

### For Canva API

The Thumbnail & Art Agent writes a design brief:
```
Template type: Vertical short-form cover
Background: #2D1B69 (deep indigo)
Headline text: "HLANGANA"
Subtext: "GATHER TOGETHER"
Bottom label: "Hebrews 10:25"
Artist name: "Fire & Flow Gospel"
Series badge: "Kingdom Words #001"
Font: Montserrat ExtraBold for headline
```

The Render Orchestrator converts this to a Canva API payload:
```json
{
  "template_id": "fire-flow-gospel-kingdom-words-cover-v1",
  "variables": {
    "background_color": "#2D1B69",
    "gradient_color": "#D4A853",
    "headline_text": "HLANGANA",
    "headline_color": "#D4A853",
    "subtext": "GATHER TOGETHER",
    "scripture_reference": "Hebrews 10:25",
    "artist_name": "Fire & Flow Gospel",
    "series_badge": "Kingdom Words #001"
  },
  "output_format": "PNG",
  "output_resolution": "1080x1920"
}
```

This requires the Canva template to be pre-built with named variable slots. This is a one-time setup task per template style.

### For Claude API

The Social Media Agent writes a SocialPostRequest. The Orchestrator builds a Claude API call:
```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 1024,
  "system": "[Full Social Media Agent™ system prompt — from social_media_agent.md]",
  "messages": [
    {
      "role": "user",
      "content": {
        "platform": "instagram",
        "song_title": "HLANGANA",
        "song_meaning": "Gather Together",
        "song_language": "Zulu",
        "scripture": "Hebrews 10:25",
        "scripture_text": "not giving up meeting together...",
        "themes": ["Community", "Church", "Gathering", "African Identity"],
        "campaign_goal": "Introduce HLANGANA and the Kingdom Words series",
        "cta": "stream + follow for more Kingdom Words",
        "tone": "Educational + Devotional",
        "hashtag_count": 20
      }
    }
  ]
}
```

The agent's system prompt provides all the brand voice, formatting rules, and quality standards. The user message provides the song-specific data. Claude returns a ready-to-post caption.

---

## Batch Management

A single campaign produces multiple assets that belong together — three Veo clips that will be edited into one video, two thumbnail options (A/B), four platform captions. The Render Orchestrator groups these into **batches**.

A batch is a collection of related RenderJobs that together produce one deliverable for the founder's review.

```json
{
  "batch_id": "batch-hlangana-video-001",
  "description": "HLANGANA short-form video — all clips",
  "campaign_id": "kingdom-word-short-001",
  "jobs": ["job-001", "job-002", "job-003"],
  "status": "RENDERING",
  "completed_jobs": 1,
  "total_jobs": 3,
  "all_complete": false,
  "route_to_asset_library_when_complete": true,
  "asset_type_on_completion": "short_form_video_raw_clips"
}
```

When all jobs in a batch complete, the batch status becomes COMPLETE and the Asset Library receives all clips together as a package.

---

## Dependency Management

Some assets cannot be generated until other assets exist. The Render Orchestrator enforces dependencies before dispatching jobs.

| Asset | Depends On | Why |
|-------|-----------|-----|
| Social captions (with streaming links) | Streaming link confirmed live | Cannot link to a dead URL |
| Thumbnail (first-frame option) | Video clip rendered | Can't extract first frame from video that doesn't exist |
| Press release | Founder supplies personal quote | Hard block — quote cannot be generated by the system |
| Publishing checklist | All approved assets | Can't list file names of files that haven't been approved |

When a dependency is missing, the Render Orchestrator queues the job with status `BLOCKED` and creates a dependency alert:
```
DEPENDENCY ALERT
Job: social-captions-ig-001
Blocked by: Streaming link not yet confirmed live
Required action: Confirm streaming link in SongInput record before
                 this job can be dispatched.
ETA to unblock: July 3, 2026 (distribution activation date)
```

---

## Revision Handling

When the founder requests a revision in the Approval Queue, the Orchestrator receives a RevisionRequest and re-runs the job:

### For Video Revisions
1. Read original RenderJob (the Veo job that produced the video)
2. Read founder's revision notes
3. Build a new prompt incorporating the change
4. Create new RenderJob with `is_revision: true` and `revision_of_job_id: original_id`
5. Dispatch to Job Queue at HIGH priority

**Example:**
> Founder note: "Move scripture overlay to appear at 0:08 instead of 0:20"

Original Veo prompt: *"Text overlay appears at 0:20..."*
Revised prompt: *"Text overlay of Hebrews 10:25 appears at 0:08, immediately after the sunrise gradient begins. Duration: hold for 7 seconds, then fade..."*

### For Text Revisions
Text revisions bypass the Job Queue — Claude re-generates in seconds.
The Orchestrator calls the Claude API directly with the original prompt plus revision notes appended.

### For Thumbnail Revisions
The Canva API call is re-submitted with the corrected variable values.

---

## Error Handling

| Error | Response |
|-------|----------|
| Renderer API timeout | Retry after 30 seconds — up to 3 times |
| Renderer API returns error (rate limit) | Hold job for 5 minutes, retry |
| Renderer API returns error (content policy) | FAILED status + alert to founder — content review required |
| Renderer returns file but it's corrupt/empty | Auto-retry once; if fails again, FAILED + alert |
| Dependency not met | BLOCKED status — alert to founder with action required |
| 3 retries exhausted | DEAD status — alert to founder: "This job requires manual intervention" |
| Press release sent without founder's personal quote | Hard block — job cannot dispatch. System error if this is ever bypassed. |

---

## V2 vs V3 Behavior

### V2 (Build First)
The Render Orchestrator builds everything except video renders. For video:
- It builds the exact Veo prompt
- It presents it to the founder in the Approval Queue as: "Here is your Veo prompt — click to open Veo, paste this, run it"
- When the founder returns with the rendered file, they upload it to the Asset Library
- From there, everything is automated

Text and thumbnails (Canva API): fully automated in V2.

### V3 (After V2 Validation)
All renderers automated. Founder never touches Veo, Hedra, or Canva. Assets appear in Asset Library automatically.

---

## Implementation Notes (V2 Python)

```python
class RenderOrchestrator:

    def __init__(self, job_queue, asset_library, approval_queue):
        self.job_queue = job_queue
        self.asset_library = asset_library
        self.approval_queue = approval_queue

    def process_campaign_brief(self, campaign_input, agent_outputs):
        """
        Main entry point. Called after founder approves the campaign plan.
        Reads all agent outputs and dispatches render jobs.
        """
        jobs = []
        for agent_output in agent_outputs:
            renderer = self.select_renderer(agent_output)
            if renderer == "claude_api":
                # Fast — run immediately, skip queue
                result = self.call_claude(agent_output)
                self.asset_library.store(result, agent_output)
            else:
                job = self.build_render_job(agent_output, renderer)
                self.job_queue.enqueue(job)
                jobs.append(job)
        return jobs

    def handle_revision(self, revision_request):
        """
        Called when founder requests a revision in Approval Queue.
        """
        original_job = self.job_queue.get_job(revision_request.original_job_id)
        new_job = self.build_revision_job(original_job, revision_request)
        self.job_queue.enqueue(new_job)
        return new_job
```

---

*Render Orchestrator™ Specification — MindSpark MusicWorks™ Execution Engine — Version 1.0*
