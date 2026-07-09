"""
Static mock data for all 5 agents.

Every dict here matches the exact JSON shape the real agent would return.
Source: sample_hlangana_campaign_package.md (Sprint 3 simulation).
Used when MOCK_MODE=true or --mock flag is passed to main.py.
No external calls are made from this file.
"""
from contracts.models import CampaignPlan

# ── Campaign Agent ─────────────────────────────────────────────────────────────

CAMPAIGN_OUTPUT = {
    "campaign_id": "hlangana-blitz-launch-001",
    "campaign_name": "HLANGANA — Kingdom Word Short #001 Launch",
    "campaign_mode": "blitz",
    "campaign_goal": (
        "Introduce the word HLANGANA and the Kingdom Words series to new audiences "
        "while creating devotional depth for existing listeners. Launch alongside the "
        "Becoming Vol. 1 release."
    ),
    "platforms": ["instagram_reels", "youtube_shorts", "tiktok", "facebook_reels"],
    "content_calendar": [
        {
            "date": "2026-07-03",
            "time_est": "8:30 AM",
            "platform": "Instagram Reels",
            "asset_type": "short_form_video",
            "notes": "HLANGANA Kingdom Word Short #001 — launch post",
        },
        {
            "date": "2026-07-03",
            "time_est": "8:30 AM",
            "platform": "YouTube Shorts",
            "asset_type": "short_form_video",
            "notes": "HLANGANA Kingdom Word Short #001 — launch post",
        },
        {
            "date": "2026-07-03",
            "time_est": "9:00 AM",
            "platform": "TikTok",
            "asset_type": "short_form_video",
            "notes": "Staggered 30 min from Instagram/YouTube to allow monitoring",
        },
        {
            "date": "2026-07-03",
            "time_est": "10:00 AM",
            "platform": "Facebook Reels",
            "asset_type": "short_form_video",
            "notes": "Facebook church demographic peaks mid-morning",
        },
        {
            "date": "2026-07-03",
            "time_est": "3:00 PM",
            "platform": "All platforms",
            "asset_type": "engagement_check",
            "notes": "Reply to early comments — algorithm reward window",
        },
        {
            "date": "2026-07-05",
            "time_est": "8:00 AM",
            "platform": "Website/Blog",
            "asset_type": "blog_post",
            "notes": "Saturday morning — devotional reading time",
        },
        {
            "date": "2026-07-05",
            "time_est": "10:00 AM",
            "platform": "Email",
            "asset_type": "email_devotional",
            "notes": "HLANGANA devotional sequence — send to list",
        },
        {
            "date": "2026-07-07",
            "time_est": "10:00 AM",
            "platform": "Media Outreach",
            "asset_type": "press_release",
            "notes": "Monday morning press window — gospel media distribution",
        },
        {
            "date": "2026-07-10",
            "time_est": "9:00 AM",
            "platform": "Instagram",
            "asset_type": "behind_the_song",
            "notes": "1-week post-launch — 'Why I chose a Zulu word'",
        },
    ],
    "risk_log": [
        {
            "risk_id": "RISK-001",
            "severity": "low",
            "description": "Streaming link must be live by July 3 — pre-save link needed before July 3.",
            "mitigation": "Use pre-save link in all pre-launch captions. Confirm streaming link is live by midnight July 2.",
            "status": "open",
            "requires_founder_action": True,
            "founder_action": "Confirm streaming pre-save link is active and placed in bio before July 1.",
        },
        {
            "risk_id": "RISK-002",
            "severity": "medium",
            "description": "HLANGANA pronunciation — non-English word may be mispronounced in video.",
            "mitigation": "Confirm pronunciation guide (H-La-Nga-Na) with native Zulu speaker before production.",
            "status": "open",
            "requires_founder_action": True,
            "founder_action": "Confirm pronunciation is correct and burned into the video caption/subtitle layer.",
        },
        {
            "risk_id": "RISK-003",
            "severity": "low",
            "description": "July 3 = US Independence Day eve. Potential reduced US engagement.",
            "mitigation": (
                "Primary diaspora audience (UK, West Africa, Caribbean) is entirely unaffected. "
                "US launch timing is acceptable."
            ),
            "status": "mitigated",
            "requires_founder_action": False,
            "founder_action": "",
        },
    ],
    "ministry_angle": (
        "HLANGANA speaks directly to the post-pandemic Church's struggle with reconnection. "
        "The devotional guide and church outreach blurb activate pastors as distribution partners. "
        "Every piece of content ends with an invitation to community, not just a call to stream."
    ),
}


def get_campaign_plan(song, mode: str) -> CampaignPlan:
    data = {**CAMPAIGN_OUTPUT, "campaign_mode": mode}
    return CampaignPlan(
        campaign_id=data["campaign_id"],
        campaign_name=data["campaign_name"],
        campaign_mode=data["campaign_mode"],
        campaign_goal=data["campaign_goal"],
        platforms=data["platforms"],
        content_calendar=data["content_calendar"],
        risk_log=data["risk_log"],
        ministry_angle=data["ministry_angle"],
        song_id=song.song_id,
    )


# ── Live Creative Brief (mock Creative Director output) ────────────────────────

MOCK_BRIEF_FIELDS = {
    "campaign_theme": "You were never meant to do this alone — HLANGANA as an invitation back to gathering.",
    "campaign_title": "HLANGANA: Gather Together",
    "core_message": "A Zulu word for 'gather together' is also a command in Hebrews 10:25 — this is that command set to music.",
    "target_audience": "African and Caribbean diaspora Christians, 20s-40s, who feel disconnected from in-person church community.",
    "emotion": "Warm, communal, gently urgent — a call home, not a guilt trip.",
    "mood": "Golden-hour warmth. Amapiano groove under gospel choir. Sunrise, not spotlight.",
    "story": "Isolation → recognition of the word HLANGANA → the command in Hebrews 10:25 → the invitation to gather.",
    "keywords": "HLANGANA meaning, Zulu word gather together, Hebrews 10:25, Afro-Gospel, Amapiano Gospel",
    "seo": "Own the search for 'HLANGANA meaning' and 'Hebrews 10:25 song' simultaneously.",
    "tagline": "Gather Together.",
    "hashtags": "#HLANGANA, #KingdomWords, #GatherTogether, #FireAndFlowGospel, #AfroGospel",
    "visual_direction": "Deep indigo grounding every frame, warm gold Montserrat type, sunrise-gradient warmth rising from the bottom third.",
    "colour_direction": "#2D1B69 deep indigo primary, #D4A853 warm gold accent, warm white for body text.",
    "campaign_goals": "1,000 streams in week one; devotional guide becomes the #1 shared asset; 3 churches request bulk copies.",
    "artist_narrative": "Fire & Flow Gospel writes from inside the diaspora experience, not about it — HLANGANA is personal before it's public.",
    "scripture_emphasis": "Hebrews 10:25 — not giving up meeting together.",
    "call_to_action": "Stream HLANGANA, then gather with someone this week — don't just share the song, share the invitation.",
    "platform_strategy": "Instagram and YouTube Shorts lead (visual word-lesson format); Facebook for the church-community share; TikTok for discovery.",
    "playlist_direction": "Gospel/Amapiano crossover playlists and Sunday-morning devotional playlists — lead with the groove for secular crossover contexts.",
    "campaign_duration": "A focused two-week launch moment, not a slow build — this song wants urgency.",
    "publishing_priority": "Lead with the Instagram/YouTube Shorts word-lesson video; press and blog follow within 48 hours.",
}


def get_campaign_brief(song, mode: str) -> dict:
    return dict(MOCK_BRIEF_FIELDS)


# ── Social Media Agent ─────────────────────────────────────────────────────────

SOCIAL_MEDIA_OUTPUT = {
    "instagram": {
        "caption": (
            "Do you know this word?\n\n"
            "HLANGANA (H-La-Nga-Na)\n\n"
            "It's a Zulu word that means: GATHER TOGETHER.\n\n"
            "And the Bible speaks directly to this — Hebrews 10:25 says:\n"
            '"not giving up meeting together, as some are in the habit of doing, but\n'
            'encouraging one another — and all the more as you see the Day approaching."\n\n'
            "The African Church has always known something the digital age keeps trying to\n"
            "forget: you cannot do this alone.\n\n"
            "HLANGANA is a reminder that gathering isn't optional. It's a command wrapped\n"
            "in a promise.\n\n"
            "This is the first song on Becoming Vol. 1 — an album about the journey of\n"
            "becoming who God made you to be, together with the people He placed around you.\n\n"
            "🎵 Stream HLANGANA — link in bio\n"
            "📖 Download the free 7-day devotional guide — link in bio\n\n"
            "This is Kingdom Word #001 — follow for more words that unlock the Bible."
        ),
        "hashtags": [
            "#HLANGANA", "#KingdomWords", "#GatherTogether", "#Hebrews1025",
            "#FireAndFlowGospel", "#BecomingVol1", "#AfroGospel", "#GospelMusic",
            "#AfricanWorship", "#DiasporaFaith", "#ZuluWord", "#GospelRelease2026",
            "#ChristianMusic", "#BibleVerse", "#GospelArtist", "#NewGospelMusic",
            "#WordOfGod", "#GospelMovement", "#FaithCommunity", "#ChurchFamily",
        ],
        "pinned_comment": (
            "📖 Hebrews 10:25 — \"not giving up meeting together, as some are in the habit\n"
            "of doing, but encouraging one another — and all the more as you see the Day\n"
            "approaching.\"\n\n"
            "What does gathering look like for you this season? Let us know below. ⬇️"
        ),
        "posting_time_recommendation": "2026-07-03 8:30 AM EST",
        "posting_time_rationale": "Hits US morning + UK afternoon + West Africa afternoon simultaneously",
    },
    "tiktok": {
        "caption": (
            "This Zulu word is in the Bible 🤯\n\n"
            "HLANGANA = Gather Together\n\n"
            "Hebrews 10:25 — do you know it?"
        ),
        "hashtags": [
            "#HLANGANA", "#KingdomWords", "#GospelMusic", "#AfroGospel",
            "#Hebrews1025", "#BibleTok", "#ChristianTikTok", "#NewMusic",
        ],
        "first_comment": (
            "Reply: \"I need to know more Kingdom Words\" and I'll drop the next one in your\n"
            "comments 👇 Hebrews 10:25 — not giving up meeting together. This season,\n"
            "who are you gathering with?"
        ),
        "posting_time_recommendation": "2026-07-03 9:00 AM EST",
        "posting_time_rationale": "30-minute stagger from Instagram allows monitoring of early engagement",
    },
    "youtube": {
        "title": 'HLANGANA Means "Gather Together" — Kingdom Word Short #001 | Fire & Flow Gospel',
        "description": (
            "HLANGANA (H-La-Nga-Na) — a Zulu word meaning \"Gather Together\"\n\n"
            "Hebrews 10:25 — \"not giving up meeting together, as some are in the habit of\n"
            "doing, but encouraging one another—and all the more as you see the Day\n"
            "approaching.\"\n\n"
            "From the album Becoming Vol. 1 — out now on all platforms.\n\n"
            "🎵 Stream Becoming Vol. 1: [STREAMING LINK]\n"
            "📖 Free 7-Day Devotional Guide: [DEVOTIONAL LINK]\n\n"
            "This is Kingdom Words — a series teaching words from African and global\n"
            "languages that unlock scripture. Follow for Episode 2."
        ),
        "hashtags": [
            "#HLANGANA", "#KingdomWords", "#Shorts", "#GospelMusic", "#Hebrews1025",
            "#AfroGospel", "#BecomingVol1", "#FireAndFlowGospel", "#BibleVerse",
            "#ChristianShorts", "#AfricanWorship", "#GospelArtist",
            "#NewGospelMusic", "#GospelRelease2026", "#WordOfGod",
        ],
        "posting_time_recommendation": "2026-07-03 8:30 AM EST",
        "posting_time_rationale": "Same as Instagram — simultaneous launch maximises initial momentum",
    },
    "facebook": {
        "caption": (
            "This is a word the Church needs right now.\n\n"
            "HLANGANA — pronounced H-La-Nga-Na — is a Zulu word from Southern Africa.\n"
            "It means: Gather Together.\n\n"
            "And it's not just a beautiful word from a beautiful culture. It's at the\n"
            "heart of one of the most practical commands in the New Testament:\n\n"
            "\"not giving up meeting together, as some are in the habit of doing, but\n"
            "encouraging one another — and all the more as you see the Day approaching.\"\n"
            "— Hebrews 10:25\n\n"
            "We are living in a time when it is increasingly easy to \"do church\" alone.\n"
            "A podcast here. A livestream there. HLANGANA is a gentle, firm reminder that\n"
            "gathering in person — with your people, your community, your church family —\n"
            "is not a tradition. It is a discipline.\n\n"
            "This is the first song on Becoming Vol. 1, the debut album from Fire & Flow\n"
            "Gospel. And it's the first episode of Kingdom Words — a series teaching\n"
            "words from African, Caribbean, and global languages that illuminate scripture\n"
            "in ways the English translation sometimes can't.\n\n"
            "🎵 Stream HLANGANA and the full album: [STREAMING LINK]\n"
            "📖 Download the free 7-day devotional companion guide: [DEVOTIONAL LINK]\n\n"
            "Share this with your church family — someone needs to hear HLANGANA today."
        ),
        "hashtags": [
            "#HLANGANA", "#KingdomWords", "#GatherTogether",
            "#Hebrews1025", "#FireAndFlowGospel", "#AfroGospel",
        ],
        "posting_time_recommendation": "2026-07-03 10:00 AM EST",
        "posting_time_rationale": "Facebook church demographic peaks mid-morning; staggered from other platforms",
    },
}


# ── Blog & Press Agent ─────────────────────────────────────────────────────────

BLOG_PRESS_OUTPUT = {
    "blog_post": {
        "title": "What Does HLANGANA Mean — And Why This Zulu Word Is in Your Bible",
        "meta_description": (
            "HLANGANA is a Zulu word meaning \"Gather Together\" — and it captures something "
            "Hebrews 10:25 says better than English can. Here's why it matters."
        ),
        "primary_keyword": "HLANGANA",
        "content": """\
There is a word from Southern Africa that has been sitting in your Bible for 2,000 years.

You just didn't know what it was called.

**HLANGANA** (pronounced H-La-Nga-Na) is a Zulu word. It means: *gather together*. And the moment you read Hebrews 10:25 with this word in mind, the verse opens up in a way the English translation only partially captures.

*"not giving up meeting together, as some are in the habit of doing, but encouraging one another — and all the more as you see the Day approaching."*
— Hebrews 10:25

---

## The Word Behind the Word

In Zulu, HLANGANA is not a passive word. It is active. It is a summons. When you HLANGANA, you are not merely occupying the same space as other people. You are arriving with intention. You are choosing to gather — with all that the gathering requires: presence, vulnerability, commitment.

The writer of Hebrews understood this. The instruction is not "try to attend church when you can." It is a direct counter to a specific habit — the habit of withdrawal. Of staying home. Of doing faith alone.

HLANGANA is the answer to that habit.

---

## Why an African Word?

Fire & Flow Gospel is the sound of the African and Caribbean diaspora encountering the living God. The languages of the continent — Zulu, Yoruba, Twi, Amharic, Igbo — carry spiritual weight that predates colonialism, and much of that weight is held in single words with no English equivalent.

HLANGANA is one of those words.

The Kingdom Words series exists to recover these words and return them to the Church. Not as cultural curiosity. As living theology.

---

## The Song

HLANGANA, the track, opens *Becoming Vol. 1* — the debut album from Fire & Flow Gospel. It sets the album's tone: you are not on this journey alone. You were made to become who you are *with* the people God placed around you.

The song is set to an Afro-Gospel/Amapiano soundscape — warm, rhythmic, communal. It sounds like gathering. That's the point.

*🎵 Stream HLANGANA on all platforms — [STREAMING LINK]*

---

## The Invitation

Hebrews 10:25 is not primarily about attendance. It is about encouragement. When you HLANGANA — when you genuinely gather — you strengthen the people around you. And they strengthen you.

In a season when many believers have quietly disconnected from their church communities, this word is a gentle, firm call back.

HLANGANA. Gather together.

*📖 Download the free 7-day devotional guide for HLANGANA — [DEVOTIONAL LINK]*
*Follow the Kingdom Words series for more words that unlock Scripture.*""",
        "word_count": 320,
        "cta_streaming": "🎵 Stream HLANGANA on all platforms — [STREAMING LINK]",
        "cta_devotional": "📖 Download the free 7-day devotional guide — [DEVOTIONAL LINK]",
    },
    "press_release": {
        "headline": (
            "FIRE & FLOW GOSPEL LAUNCHES DEBUT ALBUM AND FIRST EPISODE OF "
            '"KINGDOM WORDS" VIDEO SERIES ON JULY 3, 2026'
        ),
        "dateline": "[CITY, STATE] — July 3, 2026",
        "body": (
            "Fire & Flow Gospel, the gospel music project developed in partnership with "
            "MindSpark MusicWorks™, released its debut album Becoming Vol. 1 on July 3, 2026, "
            "alongside the first episode of its Kingdom Words short-form video series.\n\n"
            "Kingdom Words is a content series that teaches words from African, Caribbean, "
            "and global languages that illuminate biblical concepts — starting with HLANGANA, "
            "a Zulu word meaning \"Gather Together,\" drawn from Hebrews 10:25. The first "
            "episode was released simultaneously across Instagram Reels, YouTube Shorts, "
            "TikTok, and Facebook on launch day.\n\n"
            "Becoming Vol. 1 explores the spiritual and personal journey of becoming who "
            "God made you to be — in community, through struggle, and in surrender. The "
            "album blends Afro-Gospel and Amapiano elements with scripture-anchored lyrics, "
            "reflecting the sound of the African and Caribbean diaspora.\n\n"
            "A free 7-day devotional companion guide based on the album's themes is "
            "available at [WEBSITE LINK].\n\n"
            "Becoming Vol. 1 is available on Spotify, Apple Music, YouTube Music, and all "
            "major streaming platforms."
        ),
        "founder_quote_draft": (
            "There is so much theological wealth sitting in the languages of the African "
            "diaspora that the Church has not fully unlocked. HLANGANA is one word that "
            "has been sitting in Hebrews 10:25 for 2,000 years. We wanted to find it, "
            "name it, and give it back to the people it belongs to."
        ),
        "quote_requires_founder_rewrite": True,
        "boilerplate_fire_and_flow": (
            "Fire & Flow Gospel is an independent Afro-Gospel / Amapiano Gospel artist "
            "representing the African and Caribbean diaspora. Debut album: Becoming Vol. 1 (2026)."
        ),
        "boilerplate_musicworks": (
            "MindSpark MusicWorks™ is an AI-assisted gospel music operating system built "
            "to help independent gospel artists take their music from concept to campaign "
            "with integrity and excellence."
        ),
        "contact_placeholder": "[NAME] | [EMAIL] | [PHONE]",
    },
    "church_blurb": {
        "content": (
            "Dear Pastor,\n\n"
            "I wanted to share a new resource that may serve your congregation. Fire & "
            "Flow Gospel has released a free 7-day devotional guide based on the scripture "
            "Hebrews 10:25 — centered on the Zulu word HLANGANA, meaning \"Gather Together.\" "
            "It's designed to help believers reconnect with the value of gathering in "
            "community, making it suitable for small groups, mid-week study, or personal "
            "devotion. The guide is available for free download at [LINK]. We'd love for "
            "your church family to use it."
        )
    },
}


# ── Video Production Agent ─────────────────────────────────────────────────────

VIDEO_PRODUCTION_OUTPUT = {
    "concept_statement": (
        "A 45-second short-form word lesson: the word HLANGANA appears on screen in gold "
        "on indigo, is pronounced aloud, its meaning revealed, then connected to Hebrews "
        "10:25 through song and imagery of people gathering."
    ),
    "storyboard": [
        {
            "timecode": "0:00–0:03",
            "label": "THE WORD",
            "visual": "Deep indigo background. 'HLANGANA' appears letter-by-letter in bold gold Montserrat font — center screen, large. Slight shimmer animation on the letters.",
            "audio": "Silence. At 0:02, a clear voice pronounces: 'H-La-Nga-Na.'",
            "on_screen_text": "HLANGANA (large, centered, gold #D4A853)",
            "notes": "First frame must be visually striking — this is the hook and the thumbnail.",
        },
        {
            "timecode": "0:03–0:08",
            "label": "THE MEANING",
            "visual": "Below the word, smaller text fades in: 'ZULU • GATHER TOGETHER'. Subtle sunrise gradient begins to warm the indigo from the bottom.",
            "audio": "Single note piano tone — warm, resonant.",
            "on_screen_text": "ZULU • GATHER TOGETHER (smaller, centered, warm white)",
            "notes": "Ensure text is readable on muted view — TikTok audience often watches without sound.",
        },
        {
            "timecode": "0:08–0:15",
            "label": "THE SCRIPTURE",
            "visual": "Background softens. Subtle B-roll begins — hands reaching, a door being opened, warm light. (Veo Clip 1)",
            "audio": "The song HLANGANA begins — opening bars, low in the mix.",
            "on_screen_text": "'not giving up meeting together...' (Hebrews 10:25, top third of frame)",
            "notes": "Scripture must appear on screen before second 15 — hard rule.",
        },
        {
            "timecode": "0:15–0:35",
            "label": "THE MUSIC",
            "visual": "Album artwork animation — gentle zoom. Brief imagery sequence: congregation entering, people embracing, sunrise over community. (Veo Clip 2)",
            "audio": "Song excerpt at full energy — the hook or most recognizable lyrical moment.",
            "on_screen_text": "Lower third: 'HLANGANA — Fire & Flow Gospel'. Subtle Kente-pattern border animation.",
            "notes": "Most emotionally engaging section — pacing should feel communal, not rushed.",
        },
        {
            "timecode": "0:35–0:42",
            "label": "THE IDENTITY",
            "visual": "Returns to indigo background. Artist name appears.",
            "audio": "Music fades slightly — present but lower.",
            "on_screen_text": "'Fire & Flow Gospel' (mid-size, centered) + 'Becoming Vol. 1 — Out Now' (smaller, below)",
            "notes": "",
        },
        {
            "timecode": "0:42–0:47",
            "label": "THE CTA",
            "visual": "Series badge appears — 'Kingdom Words' in upper corner. Hold 2 seconds on final frame.",
            "audio": "Music fades out gently.",
            "on_screen_text": "'Follow for more Kingdom Words' (bold, white, centered)",
            "notes": "CTA must appear in final 8 seconds — hard rule. Hold final frame 2 seconds.",
        },
    ],
    "veo_job_plan": [
        {
            "clip_number": 1,
            "label": "Gathering imagery — scripture moment",
            "timecode_in_video": "0:08–0:15",
            "duration_seconds": 7,
            "veo_prompt": (
                "Cinematic footage of diverse people entering a sunlit church or community space — "
                "warm golden morning light streaming through open doors, people greeting each other "
                "warmly, hands reaching out in welcome, no identifiable faces in close-up, "
                "photorealistic, gospel music atmosphere, deep indigo and warm gold color grade, "
                "9:16 vertical aspect ratio, no text, no logos, no watermarks"
            ),
            "negative_prompt": "text, logos, watermarks, identifiable faces in close-up, violent content, sexual content, generic stock photo look",
            "aspect_ratio": "9:16",
            "style_notes": "Match brand palette: deep indigo (#2D1B69) + warm gold (#D4A853). Morning light. Cinematic, not amateur.",
        },
        {
            "clip_number": 2,
            "label": "Community gathering — music section",
            "timecode_in_video": "0:15–0:35",
            "duration_seconds": 20,
            "veo_prompt": (
                "Aerial view of people in a circle, hands joined, in a sunlit outdoor gathering "
                "space — warm gold morning light, Southern African architectural elements visible "
                "in background, community feeling, no identifiable faces, warm gold and indigo "
                "color grade, 9:16 vertical crop, photorealistic, no text, no logos"
            ),
            "negative_prompt": "text, logos, watermarks, identifiable faces in close-up, violent content, sexual content, cold lighting, generic Western church imagery",
            "aspect_ratio": "9:16",
            "style_notes": "Cultural specificity: Southern African setting. Warm, communal, celebratory. Not somber.",
        },
    ],
    "production_notes_human": (
        "1. Produce in Canva Video, CapCut, or DaVinci Resolve.\n"
        "2. Foundation: deep indigo background (#2D1B69).\n"
        "3. 'HLANGANA' in Montserrat ExtraBold, gold (#D4A853) — animate letter-by-letter with Canva 'appear' animation.\n"
        "4. Record or source a clean pronunciation of 'H-La-Nga-Na' — confirm with native Zulu speaker.\n"
        "5. Audio: trim the master WAV to the strongest 25-second moment (the hook). Do not use AI-generated audio.\n"
        "6. Veo clips: paste each Veo prompt above into veo.google.com, download results, import to editor.\n"
        "7. Stock footage fallback (if Veo unavailable): Pexels search — 'congregation morning light', 'community gathering sunrise'.\n"
        "8. Burn pronunciation subtitle at 0:02 for muted viewers.\n"
        "9. Export: 1080x1920px MP4, H.264, no letter/pillarboxing."
    ),
    "estimated_production_time": "3–4 hours first time; 1–2 hours with template",
}


# ── Thumbnail & Art Agent ──────────────────────────────────────────────────────

THUMBNAIL_OUTPUT = {
    "concept_a": {
        "label": "Text-Only (Recommended)",
        "description": (
            "Deep indigo full bleed with warm gold sunrise gradient rising from the bottom third. "
            "'HLANGANA' in large gold Montserrat ExtraBold dominates the upper frame. "
            "Thin gold horizontal rule. 'GATHER TOGETHER' in white below. "
            "Hebrews 10:25 reference bottom left. Series badge top left. Artist name bottom right."
        ),
        "background": "#2D1B69 full bleed with warm gold (#D4A853) gradient bleeding up from bottom 40%",
        "headline_text": "HLANGANA",
        "headline_color": "#D4A853",
        "headline_font": "Montserrat ExtraBold",
        "subtext": "GATHER TOGETHER",
        "subtext_color": "#FFFFFF",
        "scripture_reference": "Hebrews 10:25",
        "artist_name_placement": "Lower right, small — 'Fire & Flow Gospel', gold #D4A853",
        "series_badge": "'Kingdom Words #001' — upper left corner, white text on dark #1A0F42 badge shape",
        "canva_instructions": (
            "1. Open Canva → Create a design → Custom size → 1080 x 1920 px\n"
            "2. Background: Click background → solid color → #2D1B69\n"
            "3. Add gradient: Elements → Gradients → choose 'Bottom fade' → set color to #D4A853, opacity 60%, cover bottom 40% of frame\n"
            "4. Add text: 'HLANGANA' → Font: Montserrat → Style: ExtraBold → Size: 120 → Color: #D4A853 → Position: horizontal center, vertical 25–45%\n"
            "5. Add thin line: Elements → Lines → horizontal rule → color #D4A853 → width: 60% of frame → position below 'HLANGANA'\n"
            "6. Add text: 'GATHER TOGETHER' → Font: Montserrat → Style: Regular → Size: 55 → Color: #FFFFFF → Position: horizontal center, just below the line\n"
            "7. Add text: 'Hebrews 10:25' → Font: Montserrat → Style: Light Italic → Size: 28 → Color: rgba(255,255,255,0.7) → Position: lower left, 8% from left edge, 10% from bottom\n"
            "8. Add badge shape: Elements → Shapes → Rectangle with rounded corners → color #1A0F42 → Position: upper left, 4% from left and top\n"
            "9. Add text over badge: 'Kingdom Words #001' → Size: 22 → Color: #FFFFFF → Center on badge\n"
            "10. Add text: 'Fire & Flow Gospel' → Size: 26 → Color: #D4A853 → Position: lower right, 8% from right, 6% from bottom\n"
            "11. Download as PNG → Resolution: 2x (2160 x 3840) → Resize down to 1080 x 1920 for posting\n"
            "Estimated time: 30–45 minutes first design; 15 minutes with template saved."
        ),
    },
    "concept_b": {
        "label": "Photography-Based",
        "description": (
            "Warm-toned photography of people gathering — hands, a door, or a congregation entering. "
            "40% dark indigo gradient from top. 'HLANGANA' in gold upper half. "
            "'Fire & Flow Gospel' in white lower third."
        ),
        "stock_photo_search_terms": [
            "congregation morning light",
            "community gathering sunrise",
            "church doors opening warm light",
            "people greeting hands reaching",
            "gospel worship hands raised",
        ],
        "stock_photo_site": "Pexels (free) — pexels.com/search/congregation",
        "text_overlay_spec": (
            "Dark indigo gradient (#2D1B69, 70% opacity) from top, fading to transparent at mid-frame. "
            "'HLANGANA' in Montserrat ExtraBold gold (#D4A853), upper 40% of frame. "
            "'Fire & Flow Gospel' in white, lower third."
        ),
        "canva_instructions": (
            "1. Open Canva → Create a design → Custom size → 1080 x 1920 px\n"
            "2. Upload your chosen stock photo as background — resize to fill frame\n"
            "3. Add gradient overlay: Elements → Gradients → Top fade → #2D1B69 at 70% opacity\n"
            "4. Add text: 'HLANGANA' → Montserrat ExtraBold → Size: 100 → Color: #D4A853 → Upper 40%, centered\n"
            "5. Add text: 'GATHER TOGETHER' → Montserrat Regular → Size: 45 → Color: #FFFFFF → Below headline\n"
            "6. Add text: 'Fire & Flow Gospel' → Montserrat Regular → Size: 30 → Color: #FFFFFF → Lower third, centered\n"
            "7. Add series badge (same as Option A): 'Kingdom Words #001' → upper left\n"
            "8. Download as PNG → 1080 x 1920 px"
        ),
    },
    "ai_image_prompt_for_concept_b": (
        "Photorealistic wide shot of a diverse group of people gathering at sunrise outside a "
        "Southern African community building — warm golden morning light, people greeting each "
        "other warmly, no identifiable faces in close-up, Afro-Gospel atmosphere, deep indigo "
        "and warm gold color grade, 9:16 vertical composition, no text, no watermarks, "
        "no logos, cinematic quality — do NOT include any text in the image"
    ),
    "platform_crop_notes": (
        "Instagram Reels/YouTube Shorts/TikTok/Facebook Reels cover: 1080x1920 — use as-is (native 9:16). "
        "Blog header (16:9, 1200x628): crop to center on 'HLANGANA' — series badge may be cut, reposition to top center. "
        "Instagram Grid (1:1, 1080x1080): square crop centered on word — Hebrews reference and badge may be cut."
    ),
    "estimated_canva_time": "30–45 minutes",
}


# ── Growth & Discovery Agent ────────────────────────────────────────────────────

GROWTH_CONTENT_OUTPUT = {
    "website_copy": {
        "heading": "HLANGANA — Kingdom Word #001",
        "body": (
            "HLANGANA is a Zulu word meaning \"gather together\" — and it's the first entry in "
            "Kingdom Words, a series that recovers words from African, Caribbean, and global "
            "languages that unlock scripture in ways English sometimes can't. Stream the song, "
            "read the word study, and download the free 7-day devotional guide below."
        ),
    },
    "artist_story": {
        "content": (
            "I didn't set out to write a song about a Zulu word. I set out to write about why so "
            "many of us stopped gathering — why it became easier to livestream a sermon than sit "
            "in a room with people who know our names. Then I found HLANGANA, and it named the "
            "thing I couldn't. Not \"attend.\" Not \"show up.\" Gather — arrive with intention, be "
            "known, be counted. Hebrews 10:25 isn't asking for our calendar. It's asking for our "
            "presence. HLANGANA opens Becoming Vol. 1 because before you can become anything, you "
            "have to be willing to become it in community. This song is my own reminder as much as "
            "it's an invitation to anyone listening: come back to the room."
        ),
    },
    "behind_song_article": {
        "title": "The Making of HLANGANA: Finding a Word the English Bible Doesn't Have",
        "content": (
            "HLANGANA started as a voice memo, not a lyric — just the word, said out loud, over and "
            "over, until the rhythm of it became the song's first hook. The production leans into "
            "Amapiano's log-drum low end under a gospel choir stack, built to feel like a room "
            "filling up rather than a track dropping. We tracked the choir in a single afternoon, "
            "deliberately loose — call-and-response, not quantized — because gathering isn't "
            "supposed to sound perfect. The bridge strips back to just voice and hand percussion, "
            "the closest the record gets to what the word actually describes: people, together, "
            "no production needed."
        ),
    },
    "seo": {
        "seo_title": "HLANGANA Meaning — Zulu Word for Gather Together | Fire & Flow Gospel",
        "seo_description": (
            "HLANGANA is a Zulu word meaning \"gather together,\" rooted in Hebrews 10:25. Stream "
            "the song, read the word study, and download the free devotional guide."
        ),
        "seo_keywords": [
            "HLANGANA meaning", "Zulu word gather together", "Hebrews 10:25 meaning",
            "Afro-Gospel music", "Amapiano Gospel", "Fire & Flow Gospel", "Kingdom Words series",
            "gospel devotional guide", "African gospel music 2026", "Becoming Vol 1 album",
        ],
    },
    "hashtag_set": {
        "core": ["#HLANGANA", "#KingdomWords", "#FireAndFlowGospel"],
        "niche": ["#AfroGospel", "#AmapianoGospel", "#GospelMusic2026", "#ZuluWord"],
        "community": ["#GatherTogether", "#ChurchFamily", "#DiasporaFaith", "#FaithCommunity"],
    },
    "playlist_pitch": {
        "content": (
            "HLANGANA is the debut single from Fire & Flow Gospel, an Afro-Gospel/Amapiano Gospel "
            "project for the African and Caribbean diaspora. It opens on a spoken Zulu word — "
            "\"HLANGANA,\" gather together — before dropping into a log-drum Amapiano groove under "
            "a call-and-response gospel choir. It sits at the intersection of worship and Afrobeats "
            "crossover, built for listeners who found Gospel through Amapiano, not the other way "
            "around. Runtime 3:24, clean radio edit available."
        ),
    },
    "playlist_target_notes": {
        "content": (
            "Best fit: Gospel/Amapiano crossover playlists, African diaspora worship playlists, and "
            "Sunday-morning devotional playlists that already mix English and vernacular-language "
            "tracks. Tempo and low-end make it a plausible add to secular Amapiano playlists open to "
            "a gospel crossover moment — lead with the groove, not the scripture reference, in that "
            "pitch context."
        ),
    },
    "genre_positioning": {
        "content": (
            "HLANGANA sits at the intersection of traditional Gospel choir arrangement and Amapiano "
            "production — log-drum bass, piano stabs, and call-and-response vocals over a 4-on-the-"
            "floor groove. It's closer to the Amapiano-Gospel crossover lane than to Contemporary "
            "Christian or traditional Gospel proper."
        ),
    },
    "similar_artist_notes": {
        "content": (
            "Neyi Zimu — shares the Amapiano-meets-worship production palette. "
            "Blaqbonez ft. gospel choir collaborations — similar crossover-audience strategy. "
            "Sinach — comparable devotional lyric depth, different (more Western) production lane. "
            "Tribl / Maverick City Music — comparable communal, call-and-response vocal arrangement."
        ),
    },
    "discovery_copy": {
        "content": (
            "A Zulu word for \"gather together\" becomes a log-drum Gospel anthem. Fire & Flow "
            "Gospel opens Becoming Vol. 1 with HLANGANA, the first entry in a series recovering "
            "African-language words that unlock scripture."
        ),
    },
    "artist_bio_short": {
        "content": (
            "Fire & Flow Gospel is an independent Afro-Gospel/Amapiano Gospel project for the "
            "African and Caribbean diaspora. Debut album: Becoming Vol. 1 (2026)."
        ),
    },
    "artist_bio_long": {
        "content": (
            "Fire & Flow Gospel is the sound of the African and Caribbean diaspora encountering the "
            "living God — Afro-Gospel and Amapiano production built around scripture-anchored "
            "songwriting. The project's debut album, Becoming Vol. 1, explores the journey of "
            "becoming who God made you to be, in community and through surrender. Its lead single, "
            "HLANGANA, opens the Kingdom Words series: a body of work that recovers words from "
            "African, Caribbean, and global languages carrying theological weight the English Bible "
            "doesn't fully capture. Fire & Flow Gospel is a project of MindSpark MusicWorks™, built "
            "to help independent gospel artists take their music from concept to campaign with "
            "integrity and excellence."
        ),
    },
    "x_post": {
        "content": (
            "HLANGANA is a Zulu word for \"gather together.\" It's also Hebrews 10:25. "
            "Out now — first single from Becoming Vol. 1. 🎵 [STREAMING_LINK]"
        ),
    },
    "threads_post": {
        "content": (
            "Been sitting with this word for months: HLANGANA. Zulu for \"gather together.\" "
            "It's Hebrews 10:25 in one word. That's the whole song. Out now — link in bio."
        ),
    },
    "rumble_description": {
        "content": (
            "HLANGANA — Kingdom Word #001. A Zulu word meaning \"gather together,\" rooted in "
            "Hebrews 10:25. First single from Becoming Vol. 1 by Fire & Flow Gospel. Free 7-day "
            "devotional guide: [DEVOTIONAL_LINK]. Stream everywhere: [STREAMING_LINK]."
        ),
    },
    "community_post": {
        "content": (
            "Family — HLANGANA is officially out! This one means a lot: it's a Zulu word for "
            "\"gather together,\" and it's basically Hebrews 10:25 set to music. If you've been "
            "part of this journey with us, thank you. Stream it, share it with someone who needs "
            "to hear it, and grab the free devotional guide if you want to go deeper. 🙏"
        ),
    },
    "countdown_graphic": {
        "description": (
            "Deep indigo background, large gold countdown number center frame, 'HLANGANA drops in' "
            "above it, release date below. Same brand system as the thumbnail concepts."
        ),
        "canva_instructions": (
            "1. Canva → Custom size → 1080x1080 (feed) or 1080x1920 (story)\n"
            "2. Background: solid #2D1B69\n"
            "3. Large text: countdown number (e.g. '3') → Montserrat ExtraBold → Size 200 → Color #D4A853 → centered\n"
            "4. Above it: 'HLANGANA drops in' → Montserrat Regular → Size 40 → Color #FFFFFF\n"
            "5. Below it: 'DAYS' + release date → Montserrat Regular → Size 30 → Color #FFFFFF\n"
            "6. Footer: 'Fire & Flow Gospel' → Size 22 → Color #D4A853\n"
            "Estimated time: 10 minutes per day of countdown using the template."
        ),
    },
    "release_announcement_graphic": {
        "description": (
            "Same brand system, 'OUT NOW' badge replaces the countdown number, streaming link CTA "
            "at the bottom."
        ),
        "canva_instructions": (
            "1. Duplicate the countdown template\n"
            "2. Replace countdown number with 'OUT NOW' badge → rounded rectangle, #D4A853 fill, #1A0F42 text\n"
            "3. Headline: 'HLANGANA' → Montserrat ExtraBold → Size 120 → Color #D4A853\n"
            "4. Subtext: 'Stream now — link in bio' → Size 30 → Color #FFFFFF\n"
            "5. Download PNG at 2x resolution\n"
            "Estimated time: 10 minutes."
        ),
    },
    "campaign_poster": {
        "description": (
            "Print-friendly poster for church bulletins/lobby screens — portrait, high contrast, "
            "readable from a distance, QR code space reserved bottom right."
        ),
        "canva_instructions": (
            "1. Canva → Custom size → 8.5x11in (print) or 1080x1350 (digital)\n"
            "2. Background: solid #2D1B69, full bleed\n"
            "3. Headline: 'HLANGANA' → Montserrat ExtraBold → Size 140 → Color #D4A853 → upper third\n"
            "4. Subtext: 'Gather Together — Hebrews 10:25' → Size 36 → Color #FFFFFF\n"
            "5. 'Fire & Flow Gospel — Becoming Vol. 1' → Size 28 → Color #FFFFFF → lower third\n"
            "6. Reserve bottom-right 15% for a QR code linking to the streaming link (add after export "
            "via a free QR generator, then re-import as an image element)\n"
            "7. For print: Download as PDF Print, CMYK color profile\n"
            "Estimated time: 20 minutes."
        ),
    },
}
