"""Asset Library — SQLite metadata + filesystem storage for all generated assets."""
import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from config import ASSETS_DIR, DB_PATH
from contracts.models import AssetRecord


class AssetLibrary:
    def __init__(self):
        self.db_path = DB_PATH
        self.assets_dir = ASSETS_DIR
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY,
                    version INTEGER DEFAULT 1,
                    campaign_id TEXT NOT NULL,
                    song_id TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    asset_description TEXT,
                    file_name TEXT,
                    file_path TEXT,
                    platform_targets TEXT,
                    status TEXT DEFAULT 'READY_FOR_REVIEW',
                    rendered_by TEXT DEFAULT 'claude_api',
                    created_at TEXT NOT NULL,
                    approved_at TEXT,
                    approval_decision TEXT,
                    revision_count INTEGER DEFAULT 0,
                    is_revision INTEGER DEFAULT 0,
                    revision_of_asset_id TEXT,
                    revision_notes TEXT,
                    metadata TEXT,
                    preview_text TEXT,
                    founder_notes TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS approval_log (
                    log_id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    decision_by TEXT DEFAULT 'founder',
                    decision_at TEXT NOT NULL,
                    founder_notes TEXT,
                    asset_version INTEGER DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_assets_campaign
                ON assets(campaign_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_assets_status
                ON assets(status)
            """)
            conn.commit()

    def _campaign_dir(self, campaign_id: str, asset_type: str) -> Path:
        d = self.assets_dir / campaign_id / asset_type
        d.mkdir(parents=True, exist_ok=True)
        return d

    def store_text_asset(
        self,
        campaign_id: str,
        song_id: str,
        asset_type: str,
        description: str,
        content: str,
        file_name: str,
        platform_targets: list = None,
        metadata: dict = None,
        requires_founder_input: bool = False,
    ) -> AssetRecord:
        """Store a text asset (caption, blog post, press release, etc.)."""
        asset_id = AssetRecord.new_id()
        subdir = self._category_for_type(asset_type)
        folder = self._campaign_dir(campaign_id, subdir)
        file_path = folder / file_name

        file_path.write_text(content, encoding="utf-8")

        meta = metadata or {}
        if requires_founder_input:
            meta["requires_founder_input"] = True

        record = AssetRecord(
            asset_id=asset_id,
            campaign_id=campaign_id,
            song_id=song_id,
            asset_type=asset_type,
            asset_description=description,
            file_name=file_name,
            file_path=str(file_path),
            platform_targets=platform_targets or [],
            rendered_by="claude_api",
            metadata=meta,
            preview_text=content,
        )
        self._insert(record)
        return record

    def store_json_asset(
        self,
        campaign_id: str,
        song_id: str,
        asset_type: str,
        description: str,
        data: dict,
        file_name: str,
        platform_targets: list = None,
        metadata: dict = None,
    ) -> AssetRecord:
        """Store a structured JSON asset (video package, thumbnail spec, etc.)."""
        content = json.dumps(data, indent=2, ensure_ascii=False)
        # Store the formatted JSON as markdown for readability
        readable = self._json_to_markdown(asset_type, data)
        asset_id = AssetRecord.new_id()
        subdir = self._category_for_type(asset_type)
        folder = self._campaign_dir(campaign_id, subdir)
        file_path = folder / file_name

        file_path.write_text(readable, encoding="utf-8")

        record = AssetRecord(
            asset_id=asset_id,
            campaign_id=campaign_id,
            song_id=song_id,
            asset_type=asset_type,
            asset_description=description,
            file_name=file_name,
            file_path=str(file_path),
            platform_targets=platform_targets or [],
            rendered_by="claude_api",
            metadata=metadata or {},
            preview_text=readable,
        )
        self._insert(record)
        return record

    def _insert(self, record: AssetRecord):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO assets VALUES
                   (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    record.asset_id,
                    1,
                    record.campaign_id,
                    record.song_id,
                    record.asset_type,
                    record.asset_description,
                    record.file_name,
                    record.file_path,
                    json.dumps(record.platform_targets),
                    record.status,
                    record.rendered_by,
                    record.created_at,
                    record.approved_at,
                    record.approval_decision,
                    record.revision_count,
                    int(record.is_revision),
                    record.revision_of_asset_id,
                    record.revision_notes,
                    json.dumps(record.metadata),
                    record.preview_text,
                    record.founder_notes,
                ),
            )
            conn.commit()

    def update_status(
        self,
        asset_id: str,
        status: str,
        decision_by: str = "founder",
        founder_notes: str = "",
    ):
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE assets SET status=?, approval_decision=?, approved_at=?, founder_notes=? WHERE asset_id=?",
                (status, status, now, founder_notes, asset_id),
            )
            log_id = f"log-{uuid.uuid4().hex[:8]}"
            conn.execute(
                "INSERT INTO approval_log VALUES (?,?,?,?,?,?,?,?)",
                (log_id, asset_id, self._get_campaign_id(asset_id, conn),
                 status, decision_by, now, founder_notes, 1),
            )
            conn.commit()

    def update_press_release_quote(self, asset_id: str, founder_quote: str):
        """Replace draft quote in press release with founder's actual words."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT file_path, preview_text FROM assets WHERE asset_id=?",
                (asset_id,)
            ).fetchone()

        if not row:
            return

        file_path, content = row
        if not content:
            return

        # Replace the draft quote marker
        updated = content.replace(
            "**⚠ DRAFT QUOTE — REPLACE WITH YOUR OWN WORDS:**",
            "**FOUNDER QUOTE (confirmed):**"
        )

        # Insert the founder's quote after the marker
        import re
        updated = re.sub(
            r'(FOUNDER QUOTE \(confirmed\):\*\*\n).*?(\n\n)',
            f"\\1> {founder_quote}\\2",
            updated,
            flags=re.DOTALL
        )

        Path(file_path).write_text(updated, encoding="utf-8")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE assets SET preview_text=?, metadata=? WHERE asset_id=?",
                (updated,
                 json.dumps({"requires_founder_input": False, "quote_confirmed": True}),
                 asset_id)
            )
            conn.commit()

    def get_assets_for_campaign(self, campaign_id: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM assets WHERE campaign_id=? ORDER BY created_at",
                (campaign_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_all_campaign_ids(self) -> list[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT DISTINCT campaign_id FROM assets ORDER BY campaign_id"
            ).fetchall()
        return [r[0] for r in rows]

    def get_campaign_stats(self, campaign_id: str) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) FROM assets WHERE campaign_id=? GROUP BY status",
                (campaign_id,)
            ).fetchall()
        counts = {r[0]: r[1] for r in rows}
        total = sum(counts.values())
        approved = counts.get("APPROVED", 0)
        return {
            "total": total,
            "approved": approved,
            "pending": total - approved - counts.get("REJECTED", 0),
            "rejected": counts.get("REJECTED", 0),
            "all_approved": approved == total and total > 0,
        }

    def get_approval_log(self, campaign_id: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT l.*, a.asset_description FROM approval_log l "
                "JOIN assets a ON l.asset_id = a.asset_id "
                "WHERE l.campaign_id=? ORDER BY l.decision_at",
                (campaign_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    def _get_campaign_id(self, asset_id: str, conn) -> str:
        row = conn.execute(
            "SELECT campaign_id FROM assets WHERE asset_id=?", (asset_id,)
        ).fetchone()
        return row[0] if row else ""

    @staticmethod
    def _category_for_type(asset_type: str) -> str:
        video_types = {"video_package", "veo_prompts", "storyboard"}
        image_types = {"thumbnail_concept", "thumbnail", "cover_art"}
        written_types = {"blog_post", "press_release", "church_blurb", "devotional"}
        caption_types = {
            "caption_instagram", "caption_tiktok",
            "caption_youtube", "caption_facebook", "social_captions"
        }
        if asset_type in video_types:
            return "video"
        if asset_type in image_types:
            return "thumbnails"
        if asset_type in written_types:
            return "written"
        if asset_type in caption_types:
            return "captions"
        return "misc"

    @staticmethod
    def _json_to_markdown(asset_type: str, data: dict) -> str:
        """Convert structured agent output to readable markdown."""
        lines = [f"# {asset_type.replace('_', ' ').title()}\n"]
        lines.append(f"*Generated by MusicWorks™ V2 — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*\n\n")

        def _render(obj, depth=0):
            if isinstance(obj, dict):
                out = []
                for k, v in obj.items():
                    prefix = "#" * (depth + 2) if isinstance(v, (dict, list)) else "**"
                    suffix = "" if isinstance(v, (dict, list)) else "**"
                    out.append(f"{prefix} {k.replace('_', ' ').title()}{suffix}\n")
                    out.append(_render(v, depth + 1))
                return "\n".join(out)
            elif isinstance(obj, list):
                return "\n".join(f"- {_render(item, depth)}" for item in obj) + "\n"
            else:
                return str(obj) + "\n"

        lines.append(_render(data))
        return "".join(lines)
