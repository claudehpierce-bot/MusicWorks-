"""Render Orchestrator — coordinates all agents and stores results in Asset Library."""
import json
from contracts.models import SongInput, CampaignPlan
from execution.asset_library import AssetLibrary
from brand_brain.brain_loader import load_context
import agents.social_media_agent as social_agent
import agents.blog_press_agent as blog_agent
import agents.video_production_agent as video_agent
import agents.thumbnail_agent as thumbnail_agent


class RenderOrchestrator:
    def __init__(self, library: AssetLibrary, mock_mode: bool = False):
        self.library = library
        self.mock_mode = mock_mode

    def _get_agent_outputs(self, song: SongInput, campaign: CampaignPlan) -> tuple:
        """Return (social, written, video, thumb) dicts from real agents or mock data."""
        if self.mock_mode:
            from agents.mock_data import (
                SOCIAL_MEDIA_OUTPUT,
                BLOG_PRESS_OUTPUT,
                VIDEO_PRODUCTION_OUTPUT,
                THUMBNAIL_OUTPUT,
            )
            return SOCIAL_MEDIA_OUTPUT, BLOG_PRESS_OUTPUT, VIDEO_PRODUCTION_OUTPUT, THUMBNAIL_OUTPUT
        return (
            social_agent.run(song, campaign),
            blog_agent.run(song, campaign),
            video_agent.run(song, campaign),
            thumbnail_agent.run(song, campaign),
        )

    def run_campaign(self, song: SongInput, campaign: CampaignPlan, printer=print) -> list:
        """
        Run all creative agents for a campaign.
        Returns a list of AssetRecord objects for every asset stored.
        """
        all_assets = []
        cid = campaign.campaign_id
        source = "[MOCK]" if self.mock_mode else ""

        # Load Brand Brain once — injected into every agent call
        brand_context = "" if self.mock_mode else load_context(song.artist_id)
        if brand_context:
            printer(f"  -> Brand Brain loaded: {song.artist_id}")
        elif not self.mock_mode and song.artist_id:
            printer(f"  -> [WARN] No Brand Brain found for artist_id={song.artist_id!r} -- proceeding without brand context")

        # ── 1. Social Media Agent ─────────────────────────────────────────────
        printer(f"  -> Social Media Agent running... {source}")
        if self.mock_mode:
            from agents.mock_data import SOCIAL_MEDIA_OUTPUT
            social = SOCIAL_MEDIA_OUTPUT
        else:
            social = social_agent.run(song, campaign, brand_context=brand_context)

        if not social.get("parse_error"):
            all_assets += self._store_social(song, campaign, social)
            printer(f"    [OK] {len(all_assets)} caption assets stored")
        else:
            printer("    [WARN] Social Media Agent returned unparseable output -- raw text saved")
            self.library.store_text_asset(
                cid, song.song_id, "social_captions_raw",
                "Social captions (parse error -- review manually)",
                social.get("raw_text", ""), "social_captions_raw.txt"
            )

        # ── 2. Blog & Press Agent ─────────────────────────────────────────────
        printer(f"  -> Blog & Press Agent running... {source}")
        if self.mock_mode:
            from agents.mock_data import BLOG_PRESS_OUTPUT
            written = BLOG_PRESS_OUTPUT
        else:
            written = blog_agent.run(song, campaign, brand_context=brand_context)

        if not written.get("parse_error"):
            before = len(all_assets)
            all_assets += self._store_written(song, campaign, written)
            printer(f"    [OK] {len(all_assets) - before} written assets stored")
        else:
            printer("    [WARN] Blog & Press Agent returned unparseable output -- raw text saved")
            self.library.store_text_asset(
                cid, song.song_id, "written_assets_raw",
                "Written assets (parse error -- review manually)",
                written.get("raw_text", ""), "written_assets_raw.txt"
            )

        # ── 3. Video Production Agent ─────────────────────────────────────────
        printer(f"  -> Video Production Agent running... {source}")
        if self.mock_mode:
            from agents.mock_data import VIDEO_PRODUCTION_OUTPUT
            video = VIDEO_PRODUCTION_OUTPUT
        else:
            video = video_agent.run(song, campaign, brand_context=brand_context)

        if not video.get("parse_error"):
            before = len(all_assets)
            all_assets += self._store_video(song, campaign, video)
            printer(f"    [OK] {len(all_assets) - before} video package assets stored (manual Veo run required)")
        else:
            printer("    [WARN] Video Production Agent returned unparseable output -- raw text saved")

        # ── 4. Thumbnail & Art Agent ──────────────────────────────────────────
        printer(f"  -> Thumbnail & Art Agent running... {source}")
        if self.mock_mode:
            from agents.mock_data import THUMBNAIL_OUTPUT
            thumb = THUMBNAIL_OUTPUT
        else:
            thumb = thumbnail_agent.run(song, campaign, brand_context=brand_context)

        if not thumb.get("parse_error"):
            before = len(all_assets)
            all_assets += self._store_thumbnails(song, campaign, thumb)
            printer(f"    [OK] {len(all_assets) - before} thumbnail assets stored")
        else:
            printer("    [WARN] Thumbnail Agent returned unparseable output -- raw text saved")

        return all_assets

    # ── Private storage methods ───────────────────────────────────────────────

    def _store_social(self, song: SongInput, campaign: CampaignPlan, data: dict) -> list:
        assets = []
        cid = campaign.campaign_id
        sid = song.song_id
        slug = song.title.lower()

        platform_map = {
            "instagram": ("caption_instagram", "Instagram Reel caption + hashtags + pinned comment", ["instagram_reels"]),
            "tiktok": ("caption_tiktok", "TikTok caption + hashtags + first comment", ["tiktok"]),
            "youtube": ("caption_youtube", "YouTube Shorts title + description + hashtags", ["youtube_shorts"]),
            "facebook": ("caption_facebook", "Facebook Reel caption + hashtags", ["facebook_reels"]),
        }

        for platform, (atype, desc, targets) in platform_map.items():
            pdata = data.get(platform, {})
            if not pdata:
                continue

            if platform == "youtube":
                content = self._format_youtube(pdata)
            else:
                content = self._format_caption(platform, pdata)

            assets.append(self.library.store_text_asset(
                cid, sid, atype, desc, content,
                f"{slug}_{platform}_caption_v1.md",
                platform_targets=targets,
                metadata={
                    "posting_time": pdata.get("posting_time_recommendation", ""),
                    "posting_rationale": pdata.get("posting_time_rationale", ""),
                    "hashtag_count": len(pdata.get("hashtags", [])),
                }
            ))
        return assets

    def _store_written(self, song: SongInput, campaign: CampaignPlan, data: dict) -> list:
        assets = []
        cid = campaign.campaign_id
        sid = song.song_id
        slug = song.title.lower()

        # Blog post
        bp = data.get("blog_post", {})
        if bp:
            content = self._format_blog_post(bp)
            assets.append(self.library.store_text_asset(
                cid, sid, "blog_post",
                f"Blog post — {bp.get('title', 'HLANGANA')}",
                content, f"{slug}_blog_post_v1.md",
                metadata={"word_count": bp.get("word_count", 0), "primary_keyword": bp.get("primary_keyword", "")}
            ))

        # Press release
        pr = data.get("press_release", {})
        if pr:
            content = self._format_press_release(pr)
            assets.append(self.library.store_text_asset(
                cid, sid, "press_release",
                "Press release — gospel media distribution",
                content, f"{slug}_press_release_v1.md",
                requires_founder_input=pr.get("quote_requires_founder_rewrite", True),
                metadata={"quote_requires_founder_rewrite": pr.get("quote_requires_founder_rewrite", True)}
            ))

        # Church blurb
        cb = data.get("church_blurb", {})
        if cb:
            content = cb.get("content", "")
            assets.append(self.library.store_text_asset(
                cid, sid, "church_blurb",
                "Church outreach blurb — pastoral distribution",
                content, f"{slug}_church_blurb_v1.txt",
            ))

        return assets

    def _store_video(self, song: SongInput, campaign: CampaignPlan, data: dict) -> list:
        cid = campaign.campaign_id
        sid = song.song_id
        slug = song.title.lower()
        content = self._format_video_package(data)

        record = self.library.store_text_asset(
            cid, sid, "video_package",
            "Video storyboard + Veo prompts (manual production required)",
            content, f"{slug}_video_package_v1.md",
            platform_targets=["instagram_reels", "youtube_shorts", "tiktok", "facebook_reels"],
            metadata={
                "veo_clips": len(data.get("veo_job_plan", [])),
                "requires_manual_veo_run": True,
                "estimated_production_time": data.get("estimated_production_time", "3-4 hours"),
            }
        )
        return [record]

    def _store_thumbnails(self, song: SongInput, campaign: CampaignPlan, data: dict) -> list:
        assets = []
        cid = campaign.campaign_id
        sid = song.song_id
        slug = song.title.lower()

        for option, label in [("concept_a", "A"), ("concept_b", "B")]:
            concept = data.get(option, {})
            if not concept:
                continue
            content = self._format_thumbnail_concept(label, concept)
            assets.append(self.library.store_text_asset(
                cid, sid, "thumbnail_concept",
                f"Thumbnail Concept {label} — {concept.get('label', '')}",
                content, f"{slug}_thumbnail_concept_{label.lower()}_v1.md",
                metadata={"option": label, "canva_time": data.get("estimated_canva_time", "30–45 min")}
            ))
        return assets

    # ── Formatting helpers ────────────────────────────────────────────────────

    @staticmethod
    def _format_caption(platform: str, data: dict) -> str:
        lines = [f"# {platform.title()} Caption\n"]
        lines.append(f"**Posting time:** {data.get('posting_time_recommendation', '')} — {data.get('posting_time_rationale', '')}\n\n")
        lines.append("---\n\n## Caption\n\n")
        lines.append(data.get("caption", "") + "\n\n")
        if data.get("pinned_comment"):
            lines.append("---\n\n## Pinned Comment\n\n")
            lines.append(data.get("pinned_comment") + "\n\n")
        if data.get("first_comment"):
            lines.append("---\n\n## First Comment\n\n")
            lines.append(data.get("first_comment") + "\n\n")
        return "".join(lines)

    @staticmethod
    def _format_youtube(data: dict) -> str:
        lines = ["# YouTube Shorts\n\n"]
        lines.append(f"**Posting time:** {data.get('posting_time_recommendation', '')} — {data.get('posting_time_rationale', '')}\n\n")
        lines.append(f"---\n\n## Title\n\n{data.get('title', '')}\n\n")
        lines.append(f"---\n\n## Description\n\n{data.get('description', '')}\n\n")
        tags = data.get("hashtags", [])
        if tags:
            lines.append(f"---\n\n## Hashtags\n\n{' '.join(tags)}\n\n")
        return "".join(lines)

    @staticmethod
    def _format_blog_post(data: dict) -> str:
        lines = [
            f"# {data.get('title', 'Blog Post')}\n\n",
            f"**Meta description:** {data.get('meta_description', '')}\n\n",
            f"**Primary keyword:** {data.get('primary_keyword', '')}\n\n",
            "---\n\n",
            data.get("content", ""),
        ]
        return "".join(lines)

    @staticmethod
    def _format_press_release(data: dict) -> str:
        quote_draft = data.get("founder_quote_draft", "")
        lines = [
            "# Press Release\n\n",
            "**FOR IMMEDIATE RELEASE**\n\n",
            f"## {data.get('headline', '')}\n\n",
            f"*{data.get('dateline', '')}*\n\n",
            data.get("body", ""),
            "\n\n---\n\n",
            "**⚠ DRAFT QUOTE — REPLACE WITH YOUR OWN WORDS:**\n\n",
            f'> "{quote_draft}"\n\n',
            "*(In the Approval Queue, type your own quote to replace this before approving.)*\n\n",
            "---\n\n",
            f"**About Fire & Flow Gospel:** {data.get('boilerplate_fire_and_flow', '')}\n\n",
            f"**About MindSpark MusicWorks™:** {data.get('boilerplate_musicworks', '')}\n\n",
            f"**Media Contact:** {data.get('contact_placeholder', '[NAME | EMAIL | PHONE]')}\n\n",
            "###\n",
        ]
        return "".join(lines)

    @staticmethod
    def _format_video_package(data: dict) -> str:
        lines = ["# Video Production Package\n\n"]
        lines.append(f"**Concept:** {data.get('concept_statement', '')}\n\n")
        lines.append(f"**Estimated production time:** {data.get('estimated_production_time', '')}\n\n")
        lines.append("---\n\n## Storyboard\n\n")
        for scene in data.get("storyboard", []):
            lines.append(f"### {scene.get('timecode', '')} — {scene.get('label', '')}\n\n")
            lines.append(f"**Visual:** {scene.get('visual', '')}\n\n")
            lines.append(f"**Audio:** {scene.get('audio', '')}\n\n")
            if scene.get("on_screen_text"):
                lines.append(f"**On-screen text:** {scene.get('on_screen_text')}\n\n")
            if scene.get("notes"):
                lines.append(f"**Notes:** {scene.get('notes')}\n\n")
        lines.append("---\n\n## Veo Job Plans (Run These Manually in V2)\n\n")
        for clip in data.get("veo_job_plan", []):
            lines.append(f"### Clip {clip.get('clip_number', '')} — {clip.get('label', '')}\n\n")
            lines.append(f"**Timecode in final video:** {clip.get('timecode_in_video', '')}\n\n")
            lines.append(f"**Duration:** {clip.get('duration_seconds', '')} seconds\n\n")
            lines.append(f"**Veo Prompt:**\n```\n{clip.get('veo_prompt', '')}\n```\n\n")
            lines.append(f"**Negative Prompt:**\n```\n{clip.get('negative_prompt', '')}\n```\n\n")
            if clip.get("style_notes"):
                lines.append(f"**Style Notes:** {clip.get('style_notes')}\n\n")
        lines.append("---\n\n## Production Notes (Human Assembly)\n\n")
        lines.append(data.get("production_notes_human", "") + "\n")
        return "".join(lines)

    @staticmethod
    def _format_thumbnail_concept(label: str, data: dict) -> str:
        lines = [f"# Thumbnail Concept {label} — {data.get('label', '')}\n\n"]
        lines.append(f"**Description:** {data.get('description', '')}\n\n")
        lines.append("---\n\n## Design Specification\n\n")
        for key, value in data.items():
            if key in ("label", "description", "canva_instructions"):
                continue
            if isinstance(value, list):
                lines.append(f"**{key.replace('_', ' ').title()}:** {', '.join(value)}\n\n")
            else:
                lines.append(f"**{key.replace('_', ' ').title()}:** {value}\n\n")
        lines.append("---\n\n## Canva Instructions\n\n")
        lines.append(data.get("canva_instructions", "") + "\n")
        return "".join(lines)
