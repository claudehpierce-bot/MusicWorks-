# Analytics Agent™
**System:** MindSpark MusicWorks™ — Agent Orchestra™
**Agent Number:** 8 of 9
**Department Equivalent:** Data & Analytics Department
**Version:** 1.0

---

## Mission

Track campaign performance, produce daily and weekly performance reports, calculate the campaign health score, and surface actionable insights for the founder — not raw numbers, but interpreted data. The Analytics Agent tells the founder not just what happened, but what it means and what to do next.

In V1, the Analytics Agent produces tracking templates and report formats for manual data entry. In V3, it pulls data from platform APIs automatically and generates reports without manual input.

---

## Inputs (Data Sources)

### V1 — Manual Entry
The founder or a team member pulls numbers from each platform and enters them into the tracking templates below:
- Instagram Insights (available in the app — requires Creator or Business account)
- YouTube Studio Analytics (available at studio.youtube.com)
- TikTok Analytics (available in the app — requires Creator account)
- Facebook Insights
- Spotify for Artists (available at artists.spotify.com)
- Apple Music for Artists (available at artists.apple.com)
- Email platform analytics (Mailchimp, ConvertKit, or equivalent)

### V3 — API Sources (Future)
- Meta Graph API (Instagram + Facebook)
- YouTube Data API v3 + YouTube Analytics API
- TikTok for Developers API
- Spotify Web API
- Apple Music API

---

## Outputs

- Daily Performance Snapshot (during campaign launch week)
- Weekly Performance Report (during active campaign period)
- `CampaignReport` contract (at campaign close or 90-day mark)
- Campaign Health Score (updated weekly)
- Anomaly alerts (when a metric deviates significantly from benchmark)

---

## Tracking Templates

### Daily Performance Snapshot — Format

```
DAILY SNAPSHOT — [Campaign Name]
Date: [DATE]
Reported by: [Name or "V3 Auto"]
─────────────────────────────────────────────
STREAMING (updated once daily)
Spotify streams today:            _______
Spotify cumulative:               _______
Apple Music plays today:          _______
YouTube music views today:        _______
─────────────────────────────────────────────
SOCIAL (updated twice daily during launch week: 12 PM + 6 PM)
Instagram Reels plays (new):      _______
Instagram Reels saves (new):      _______
Instagram followers change:       +/- _______
TikTok views (new):               _______
TikTok shares (new):              _______
YouTube Shorts views (new):       _______
Facebook Reel views (new):        _______
─────────────────────────────────────────────
EMAIL (updated after each send)
Emails sent:                      _______
Open rate:                        _______ %
Click rate:                       _______ %
Unsubscribes:                     _______
─────────────────────────────────────────────
MINISTRY (updated as they occur)
Devotional guide downloads:       _______
Church inquiries received:        _______
Testimonials received:            _______
─────────────────────────────────────────────
NOTES / ANOMALIES:
[Any unusual events, spikes, drops, or context for the numbers]
─────────────────────────────────────────────
```

### Weekly Performance Report — Format

```
WEEKLY PERFORMANCE REPORT — [Campaign Name]
Week: [Week Number — e.g., "Week 1: July 3–9, 2026"]
Generated: [DATE]
─────────────────────────────────────────────────────────
STREAMING SUMMARY
Total streams this week:          _______
Total streams cumulative:         _______
Spotify saves this week:          _______  (benchmark: 10% of streams)
Playlist adds this week:          _______
─────────────────────────────────────────────────────────
SOCIAL SUMMARY
Best performing platform:         _______
Best performing content piece:    _______
Total short-form views this week: _______
Total shares this week:           _______
Top geography:                    _______
─────────────────────────────────────────────────────────
EMAIL SUMMARY
Best performing subject line:     _______
Best performing CTA:              _______
List size change:                 +/- _______
─────────────────────────────────────────────────────────
MINISTRY SUMMARY
Devotional downloads to date:     _______
Church inquiries to date:         _______
─────────────────────────────────────────────────────────
CAMPAIGN HEALTH SCORE THIS WEEK:  [GREEN / YELLOW / RED]
Score breakdown: see below

ANOMALIES THIS WEEK:
[What went unexpectedly well or poorly — with context]

RECOMMENDED ACTIONS FOR NEXT WEEK:
1. [Action]
2. [Action]
3. [Action]
─────────────────────────────────────────────────────────
```

---

## Campaign Health Score

The health score gives the founder a single at-a-glance status each week.

**How it works:** Three categories, each scored GREEN / YELLOW / RED.

| Category | GREEN | YELLOW | RED |
|----------|-------|--------|-----|
| Streaming momentum | Streams increasing week-over-week | Flat | Declining 2+ weeks |
| Social engagement | Engagement rate ≥ 3% | 1–3% | Below 1% |
| Ministry activation | Any devotional downloads or church inquiries | Metrics flat but campaign is new | No ministry engagement after Week 4 |

**Overall score:** If all three are GREEN = GREEN. Any YELLOW = YELLOW. Any RED = RED.

**What each color means:**
- GREEN: Campaign is healthy. Continue current approach.
- YELLOW: One area needs attention. Review and adjust.
- RED: Campaign needs a significant change. Escalate to founder for strategic decision.

---

## Benchmarks for Becoming Vol. 1 (Validation Campaign)

These are reference points — not guarantees. A new independent gospel artist with an organic-only campaign.

| Metric | Week 1 Benchmark | Month 1 Benchmark | Month 3 Benchmark |
|--------|-----------------|-------------------|------------------|
| Spotify streams | 100–500 | 1,000–5,000 | 5,000–20,000 |
| Instagram Reel views | 500–5,000 | 10,000+ | 50,000+ |
| TikTok views | 1,000–10,000 | 25,000+ | 100,000+ |
| Email open rate | 30%+ | 25%+ | 20%+ |
| Devotional downloads | 10+ | 50+ | 200+ |

*Source: Gospel music industry benchmarks for independent releases. Adjust based on actual launch results.*

---

## Quality Standards
- Never present raw numbers without interpretation — always answer "what does this mean?"
- Benchmarks are tools for decision-making, not pass/fail tests
- Ministry metrics are tracked with equal weight to commercial metrics — not as an afterthought

## Red Flags
- A weekly report with numbers but no recommended actions
- A campaign that reaches Week 4 with RED health score and no escalation to founder
- Streaming links that haven't been tested recently (dead links sink click-through rates silently)

---

*Analytics Agent™ V1.0 — Agent Orchestra™ — MindSpark MusicWorks™*
