# Shared Data Contracts
**System:** MindSpark MusicWorks™ — Agent Orchestra™
**Document:** Sprint 3
**Version:** 1.0
**Purpose:** Architecture contracts for inter-agent communication. V1: document templates. V2+: JSON API payloads.

---

> These contracts define the data that flows between agents. Every agent reads from one or more contracts and writes to one or more contracts. In V1, they are structured document templates. In V2, they become typed JSON objects passed between Claude API calls. The structure does not change between versions — only the implementation does.

---

## CONTRACT 1: SongInput

**Purpose:** The foundational data about a specific song. Every agent reads from this contract.
**Produced by:** Founder (via intake form)
**Read by:** All agents

```json
{
  "song_id": "unique-slug — e.g., fire-flow-hlangana-001",
  "title": "HLANGANA",
  "title_meaning": "Gather Together",
  "title_language": "Zulu",
  "artist_name": "Fire & Flow Gospel",
  "album_title": "Becoming Vol. 1",
  "album_id": "becoming-vol-1",
  "track_number": 3,
  "release_date": "2026-07-03",
  "duration_seconds": 247,
  "bpm": 94,
  "key": "G Major",
  "genre": ["Afro-Gospel", "Amapiano Gospel"],
  "mood": ["Devotional", "Communal", "Hopeful"],
  "scripture_primary": "Hebrews 10:25",
  "scripture_primary_text": "not giving up meeting together, as some are in the habit of doing, but encouraging one another—and all the more as you see the Day approaching.",
  "scripture_supporting": ["Acts 2:42", "Psalm 122:1"],
  "themes": ["Community", "Church", "Gathering", "African Identity", "Discipleship"],
  "lyrics_approved": true,
  "theology_approved": true,
  "audio_qc_approved": true,
  "audio_file_path": "/assets/audio/hlangana_master_v1.wav",
  "artwork_file_path": "/assets/artwork/becoming_vol1_cover_4000x4000.jpg",
  "lyrics_file_path": "/assets/lyrics/hlangana_approved_lyrics.md",
  "streaming_url_spotify": "PENDING",
  "streaming_url_apple": "PENDING",
  "streaming_url_youtube": "PENDING",
  "isrc": "US-XXX-26-00003",
  "content_advisory": "none"
}
```

---

## CONTRACT 2: CampaignInput

**Purpose:** Defines the campaign strategy for a specific content piece or series.
**Produced by:** Campaign Agent™ (founder-reviewed)
**Read by:** All creative agents

```json
{
  "campaign_id": "kingdom-word-short-001",
  "campaign_name": "Kingdom Word Short #001 — HLANGANA",
  "song_id": "fire-flow-hlangana-001",
  "campaign_type": "short_form_series",
  "series_name": "Kingdom Words",
  "series_episode": 1,
  "campaign_mode": "Blitz",
  "campaign_goal": "Teach the meaning of HLANGANA and introduce Fire & Flow Gospel's movement to new audiences",
  "target_audience": {
    "age_range": "18-45",
    "geography": ["US", "UK", "Nigeria", "Ghana", "South Africa", "Caribbean"],
    "faith_background": "Christian — all denominations",
    "interest_keywords": ["gospel music", "African worship", "Bible study", "diaspora faith"]
  },
  "platforms": ["instagram_reels", "youtube_shorts", "tiktok", "facebook_reels"],
  "content_pieces_requested": [
    "short_form_video",
    "instagram_caption",
    "tiktok_caption",
    "youtube_shorts_description",
    "facebook_caption",
    "blog_post",
    "thumbnail_concept",
    "press_release"
  ],
  "publishing_window": {
    "earliest": "2026-07-03",
    "ideal": "2026-07-05",
    "latest": "2026-07-10"
  },
  "budget_level": "low",
  "ministry_angle": "Encourage believers to prioritize gathering with their faith community",
  "founder_notes": "Lead with the Zulu word — make it educational AND devotional. This is the first in the Kingdom Words series so it needs to clearly establish the format."
}
```

---

## CONTRACT 3: VideoAssetRequest

**Purpose:** Task assignment from Campaign Agent to Video Production Agent.
**Produced by:** Campaign Agent™
**Read by:** Video Production Agent™

```json
{
  "request_id": "video-req-001",
  "campaign_id": "kingdom-word-short-001",
  "song_id": "fire-flow-hlangana-001",
  "video_type": "short_form_word_lesson",
  "series": "Kingdom Words",
  "episode": 1,
  "target_duration_seconds": 45,
  "target_platforms": ["instagram_reels", "youtube_shorts", "tiktok"],
  "aspect_ratio": "9:16",
  "hook_requirement": "Must establish the word HLANGANA within first 3 seconds",
  "required_elements": [
    "word_display_with_pronunciation",
    "word_meaning_reveal",
    "scripture_overlay",
    "audio_excerpt_from_song",
    "cta_follow_for_more_kingdom_words"
  ],
  "visual_style": "Warm, African-inspired, devotional — deep indigo + gold palette",
  "veo_job_required": true,
  "hedra_job_required": false,
  "audio_file_path": "/assets/audio/hlangana_master_v1.wav",
  "artwork_file_path": "/assets/artwork/becoming_vol1_cover_4000x4000.jpg",
  "priority": "high",
  "due_for_review": "2026-07-01"
}
```

---

## CONTRACT 4: SocialPostRequest

**Purpose:** Task assignment from Campaign Agent to Social Media Agent.
**Produced by:** Campaign Agent™
**Read by:** Social Media Agent™

```json
{
  "request_id": "social-req-001",
  "campaign_id": "kingdom-word-short-001",
  "song_id": "fire-flow-hlangana-001",
  "platforms_requested": ["instagram", "tiktok", "youtube_shorts", "facebook"],
  "post_type": "video_caption",
  "primary_hook": "Teach the word HLANGANA",
  "scripture": "Hebrews 10:25",
  "cta_type": "follow_for_series",
  "tone": "Educational + Devotional",
  "hashtag_count": {
    "instagram": 20,
    "tiktok": 8,
    "youtube": 15,
    "facebook": 5
  },
  "include_pinned_comment": true,
  "include_first_comment": true,
  "character_limit": {
    "tiktok": 2200,
    "instagram": 2200,
    "youtube_shorts": 5000,
    "facebook": 63206
  },
  "due_for_review": "2026-07-01"
}
```

---

## CONTRACT 5: ApprovalItem

**Purpose:** The universal wrapper for any asset awaiting founder approval.
**Produced by:** Any creative agent when submitting to Approval Agent
**Read by:** Approval Agent™, Founder

```json
{
  "approval_item_id": "approval-001",
  "campaign_id": "kingdom-word-short-001",
  "asset_type": "short_form_video",
  "originating_agent": "video_production_agent",
  "title": "HLANGANA — Kingdom Word Short #001 — Video Package",
  "platform": ["instagram_reels", "youtube_shorts", "tiktok"],
  "status": "READY_FOR_REVIEW",
  "submitted_at": "2026-06-30T14:00:00Z",
  "revision_count": 0,
  "asset_preview_path": "/sample_outputs/hlangana_video_package.md",
  "theological_flags": [],
  "brand_flags": [],
  "quality_check_passed": true,
  "founder_decision": null,
  "founder_decision_at": null,
  "founder_notes": null
}
```

---

## CONTRACT 6: RevisionRequest

**Purpose:** Structured revision instruction sent from Approval Agent back to the originating agent.
**Produced by:** Approval Agent™ (based on founder's revision notes)
**Read by:** Originating creative agent

```json
{
  "revision_id": "revision-001",
  "approval_item_id": "approval-001",
  "campaign_id": "kingdom-word-short-001",
  "originating_agent": "video_production_agent",
  "revision_number": 1,
  "requested_at": "2026-07-01T09:00:00Z",
  "founder_notes": "The hook is strong but the scripture overlay appears too late — move Hebrews 10:25 to appear by second 8, not second 20. Also add the pronunciation guide before the meaning reveal.",
  "specific_changes": [
    {
      "element": "scripture_overlay_timing",
      "current": "appears at 0:20",
      "requested": "appears at 0:08"
    },
    {
      "element": "pronunciation_guide",
      "current": "missing",
      "requested": "add after hook, before meaning reveal — phonetic: H-La-Nga-Na"
    }
  ],
  "priority": "high",
  "due_revised": "2026-07-02T12:00:00Z"
}
```

---

## CONTRACT 7: CampaignReport

**Purpose:** Performance summary for a completed campaign. Produced by Analytics Agent.
**Produced by:** Analytics Agent™
**Read by:** Learning Agent™, Founder

```json
{
  "report_id": "campaign-report-001",
  "campaign_id": "kingdom-word-short-001",
  "song_id": "fire-flow-hlangana-001",
  "report_period": {
    "start": "2026-07-03",
    "end": "2026-10-01"
  },
  "generated_at": "2026-10-02T08:00:00Z",
  "streaming_metrics": {
    "total_streams": 0,
    "spotify_streams": 0,
    "apple_streams": 0,
    "youtube_views": 0,
    "saves": 0,
    "playlist_adds": 0
  },
  "social_metrics": {
    "instagram_views": 0,
    "instagram_engagement_rate": 0,
    "tiktok_views": 0,
    "youtube_shorts_views": 0,
    "facebook_views": 0,
    "total_shares": 0
  },
  "email_metrics": {
    "emails_sent": 0,
    "open_rate": 0,
    "click_rate": 0
  },
  "ministry_metrics": {
    "devotional_downloads": 0,
    "church_inquiries": 0,
    "testimonials_received": 0
  },
  "top_performing_platform": null,
  "top_performing_content_piece": null,
  "top_performing_geography": null,
  "revenue_total": 0,
  "assets_approved": 0,
  "assets_rejected": 0,
  "assets_revised": 0
}
```

---

## CONTRACT 8: LearningRecord

**Purpose:** Structured lessons learned from a campaign. The feed-forward data that improves the next campaign.
**Produced by:** Learning Agent™
**Read by:** Campaign Agent™ (on next campaign initialization)

```json
{
  "learning_id": "learning-001",
  "campaign_id": "kingdom-word-short-001",
  "created_at": "2026-10-02T10:00:00Z",
  "what_worked": [
    {
      "element": "video_hook_format",
      "description": "Opening with the foreign word on screen generated strong viewer curiosity",
      "evidence": "High watch-through rate vs. other short-form concepts",
      "replicate": true
    }
  ],
  "what_failed": [
    {
      "element": "posting_time",
      "description": "Friday 8:30 AM Eastern missed the West African peak time (Friday afternoon local)",
      "evidence": "Ghana/Nigeria geography underperformed vs. UK/US",
      "change": "For African diaspora content, post at 3 PM Eastern / 8 PM West Africa"
    }
  ],
  "best_platform": null,
  "best_hook_format": null,
  "best_scripture_angle": null,
  "best_posting_time": null,
  "founder_narrative": null,
  "recommendations_for_next_campaign": [],
  "agent_performance_notes": {
    "video_production_agent": null,
    "social_media_agent": null,
    "blog_press_agent": null,
    "thumbnail_art_agent": null
  }
}
```

---

*All contracts version 1.0. Fields marked `null` or `0` are placeholders for live data.*
*Contract schemas are stable — do not change field names without updating all agents that reference them.*
