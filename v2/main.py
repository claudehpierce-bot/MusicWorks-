"""
MindSpark MusicWorks™ V2 — Campaign Runner
Usage: python main.py [--song PATH] [--mode MODE] [--yes]
"""
import argparse
import json
import sys
from pathlib import Path

# ── Startup ───────────────────────────────────────────────────────────────────
BANNER = """
=========================================================
  MindSpark MusicWorks(tm)  V2
  Human-led. AI-assisted. Scripture-rooted.
=========================================================
"""

MODES = ["blitz", "standard", "growth", "ministry_push", "chart_push"]


def parse_args():
    parser = argparse.ArgumentParser(description="Run a MusicWorks V2 campaign")
    parser.add_argument(
        "--song",
        default="data/songs/hlangana.json",
        help="Path to song JSON file (default: data/songs/hlangana.json)",
    )
    parser.add_argument(
        "--mode",
        default="blitz",
        choices=MODES,
        help="Campaign mode (default: blitz)",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Auto-approve the campaign plan (skip the y/n prompt)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run with mock data — no Anthropic API key required",
    )
    return parser.parse_args()


def load_song(path: str):
    from contracts.models import SongInput
    p = Path(path)
    if not p.exists():
        print(f"\n✗ Song file not found: {path}")
        print("  Available songs:")
        for f in Path("data/songs").glob("*.json"):
            print(f"    {f}")
        sys.exit(1)

    data = json.loads(p.read_text(encoding="utf-8"))
    song = SongInput.from_dict(data)
    return song


def display_campaign_plan(plan) -> None:
    print(f"\n{'-' * 57}")
    print(f"  CAMPAIGN PLAN -- {plan.campaign_name}")
    print(f"{'-' * 57}")
    print(f"  Mode:     {plan.campaign_mode.upper()}")
    print(f"  Goal:     {plan.campaign_goal}")
    print(f"  Ministry: {plan.ministry_angle}")
    print()

    if plan.content_calendar:
        print("  CONTENT CALENDAR:")
        for item in plan.content_calendar[:8]:
            print(f"    {item.get('date', '')}  {item.get('time_est', ''):>8}  "
                  f"{item.get('platform', ''):20}  {item.get('asset_type', '')}")
        if len(plan.content_calendar) > 8:
            print(f"    ... and {len(plan.content_calendar) - 8} more items")
    print()

    open_risks = [r for r in plan.risk_log if r.get("status") == "open"]
    if open_risks:
        print("  OPEN RISKS (require your attention):")
        for risk in open_risks:
            sev = risk.get("severity", "?").upper()
            print(f"    [!] [{sev}] {risk.get('description', '')}")
            if risk.get("requires_founder_action"):
                print(f"       -> {risk.get('founder_action', '')}")
    else:
        print("  RISKS: None open.")
    print(f"{'-' * 57}")


def main():
    print(BANNER)
    args = parse_args()

    # ── Load song ─────────────────────────────────────────────────────────────
    from config import MOCK_MODE
    mock_mode = args.mock or MOCK_MODE
    if mock_mode:
        print("  [MOCK MODE] — no Anthropic API calls will be made\n")

    print(f"Loading song: {args.song}")
    song = load_song(args.song)

    print(f"\n  Song:   {song.title} ({song.title_meaning} — {song.title_language})")
    print(f"  Artist: {song.artist_name}")
    print(f"  Album:  {song.album_title}")
    print(f"  Mode:   {args.mode.upper()}")

    # Hard gate validation
    try:
        song.validate()
        print(f"\n  [OK] Theology Review: APPROVED")
        print(f"  [OK] Audio QC: APPROVED")
        print(f"  [OK] Hard gates cleared -- campaign can proceed")
    except ValueError as e:
        print(f"\n  [BLOCKED] {e}")
        sys.exit(1)

    # ── Campaign Agent ────────────────────────────────────────────────────────
    print(f"\nSTEP 1: Campaign Agent™ building campaign plan...")
    if mock_mode:
        from agents.mock_data import get_campaign_plan
        plan = get_campaign_plan(song, args.mode)
    else:
        from brand_brain.brain_loader import load_context
        brand_context = load_context(song.artist_id)
        if brand_context:
            print(f"  Brand Brain loaded: {song.artist_id}")
        import agents.campaign_agent as campaign_agent
        plan = campaign_agent.run(song, args.mode, brand_context=brand_context)
    display_campaign_plan(plan)

    # ── Founder approval of the plan ──────────────────────────────────────────
    if args.yes:
        print("\n  --yes flag set. Plan auto-approved.\n")
    else:
        answer = input("  Approve this campaign plan? (y/n): ").strip().lower()
        if answer != "y":
            print("\n  Campaign cancelled. Edit the song data or re-run with a different mode.")
            sys.exit(0)
        print()

    # ── Run all agents ────────────────────────────────────────────────────────
    print("STEP 2: Running Agent Orchestra™...")
    from execution.asset_library import AssetLibrary
    from execution.orchestrator import RenderOrchestrator

    library = AssetLibrary()
    orchestrator = RenderOrchestrator(library, mock_mode=mock_mode)

    assets = orchestrator.run_campaign(song, plan, printer=print)

    print(f"\n  [OK] {len(assets)} assets stored in Asset Library")
    print(f"  Campaign ID: {plan.campaign_id}")
    print(f"  Assets location: {library.assets_dir / plan.campaign_id}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 57}")
    print(f"  STEP 3: Review your assets in the Approval Queue")
    print()
    print(f"  Run this command:")
    print(f"    python -m streamlit run approval/app.py")
    print()
    print(f"  Then open: http://localhost:8501")
    print(f"{'=' * 57}\n")


if __name__ == "__main__":
    main()
