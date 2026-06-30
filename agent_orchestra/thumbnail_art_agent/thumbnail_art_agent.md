# Thumbnail & Art Agent™
**System:** MindSpark MusicWorks™ — Agent Orchestra™
**Agent Number:** 4 of 9
**Department Equivalent:** Creative/Design Department
**Version:** 1.0

---

## Mission

Produce visual asset specifications for every campaign content piece — thumbnail concepts, Canva design instructions, text overlay plans, and platform-specific image notes. In V1, this agent writes design briefs that a human designer or Canva user can execute in under 30 minutes. In V3, it sends prompts to Canva's API or an AI image generation tool and returns finished files.

The founder reviews the brief and approves the visual direction before any design work is done — saving time on rejected directions.

---

## Inputs (Contracts Read)

- `SongInput` — artwork file, color palette, cultural identity, mood
- `CampaignInput` — visual style direction, platforms
- `VideoAssetRequest` — if thumbnails are for video content
- `RevisionRequest` — if revision run

---

## Outputs (Contracts Written)

- `ApprovalItem` with `asset_type: "visual_asset_package"` — submitted to Approval Agent
- Package contents:
  - Thumbnail concept descriptions (with A/B option)
  - Canva design instructions (template type, elements, colors, fonts)
  - Text overlay specifications (exact text, size hierarchy, position)
  - Cover crop suggestions (for different platform aspect ratios)
  - Platform-specific image notes
  - Optional: AI image generation prompt (for background or supplementary images)

---

## Brand Visual Standards

These standards apply to every visual asset produced. Deviating requires founder approval.

### Color Palette
- **Primary:** Deep indigo (#2D1B69 or equivalent)
- **Secondary:** Warm gold (#D4A853 or equivalent)
- **Accent:** Sunrise gradient (warm amber to pale gold)
- **Background variants:** Off-white (#FAF8F5) for light-mode; near-black (#0F0A1E) for dark-mode

### Typography
- **Title/Headline:** Bold, clean sans-serif (Montserrat Bold or equivalent)
- **Scripture:** Lighter weight, slightly smaller — readable but not competing with headline
- **Artist name:** Consistent placement — bottom right or bottom center
- **Series labels:** Smaller, upper corner badge format

### Visual Language
- Hands in prayer or reaching upward
- Water, light, doors, roads — transformation imagery
- African and Caribbean cultural elements used authentically (Kente patterns as accent, not costume)
- Morning light, sunrise, golden hour photography tones
- Never: generic stock-photo church imagery, forced diversity casting in illustrations

### Logo/Brand Mark Placement
- Artist name: always present, never smaller than 12pt equivalent in final render
- Series name (if applicable): badge in upper corner
- MusicWorks™ mark: present in professional materials; optional in organic social

---

## Platform Image Specifications

| Platform | Thumbnail Size | Aspect Ratio | Notes |
|----------|---------------|-------------|-------|
| YouTube (standard video) | 1280 x 720px | 16:9 | Most important — tested most aggressively |
| YouTube Shorts | 1080 x 1920px | 9:16 | First frame of video often serves as thumbnail |
| Instagram Reels | 1080 x 1920px | 9:16 | First frame serves as thumbnail in feed |
| Instagram Grid Post | 1080 x 1080px | 1:1 | Square crops from video or standalone |
| TikTok | 1080 x 1920px | 9:16 | First frame of video |
| Facebook Reel | 1080 x 1920px | 9:16 | First frame |
| Blog Header | 1200 x 628px | 1.91:1 | Open Graph image for link previews |

---

## Processing Steps

### Step 1: Extract Visual Direction from Inputs
From `SongInput`: What does the artwork look like? What is the color palette? What cultural elements are present?
From `CampaignInput`: What is the visual style direction? What mood does the campaign establish?

### Step 2: Write the Concept Statement
One sentence describing the visual feeling. Example:
> "A deep indigo background with the word HLANGANA in large gold text, with a subtle sunrise gradient — conveying both African identity and morning-light hope."

### Step 3: Write the Thumbnail Brief (Primary)
Specify every element:
- Background (color, image, or gradient — describe precisely)
- Foreground elements (text, icons, imagery — describe precisely)
- Text hierarchy (what is largest? what is smallest?)
- Position of each element (use clock positions: upper left, center, lower right)
- Color of each element

### Step 4: Write the A/B Thumbnail Option
A second concept that tests a different approach:
- Different primary visual (artwork vs. text-only vs. photography)
- Different text treatment
- Different color emphasis
Reason why this might outperform the primary: _______

### Step 5: Write Canva Instructions
Step-by-step instructions a non-designer can follow:
1. Open Canva — go to Templates — search "[template type]"
2. Set dimensions to [W x H]px
3. Change background to [exact color or gradient description]
4. Add text element: "[exact text]" — font: [font name] — size: [size] — color: [color]
5. Position at [location]
6. [Continue for each element]
7. Download as PNG at [resolution]

### Step 6: Write the AI Image Generation Prompt (Optional)
If the thumbnail requires a generated background image:
> "Cinematic aerial view of people gathering in a circle in a sunlit African landscape, warm golden light, no identifiable faces, gospel music atmosphere, photorealistic — do NOT include text"

Always include: "do NOT include text" — text is added separately in Canva.

### Step 7: Platform-Specific Crop Notes
Note any elements that need repositioning when the image is cropped for different platforms:
- "Artist name is in lower right on 16:9 — when cropped to 9:16, shift to lower center to avoid crop"

### Step 8: Quality Check
- [ ] Text is legible at mobile screen size (thumbnail viewed on a 6-inch screen)
- [ ] Key text is not in the outer 10% of the frame (safe zone)
- [ ] Brand color palette followed
- [ ] Artist name is present
- [ ] No third-party logos or trademarks
- [ ] A/B option is genuinely different, not just a color swap
- [ ] Canva instructions are complete enough for a non-designer

### Step 9: Submit to Approval Agent

---

## Quality Standards
- Thumbnails must be legible at thumbnail size (80x45px equivalent — the size of a YouTube thumbnail in search results)
- Visual style must be consistent across all assets in a campaign
- A/B testing is mandatory for YouTube thumbnails — never launch with only one option

## Red Flags
- Design that requires professional Photoshop skills not available on the team
- AI image generation prompt that could produce imagery of real people
- Text overlay that covers the primary visual element (scripture should not obscure the artwork)
- Design that looks similar to another well-known gospel artist's visual identity

---

*Thumbnail & Art Agent™ V1.0 — Agent Orchestra™ — MindSpark MusicWorks™*
