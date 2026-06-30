import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CANVA_API_TOKEN = os.getenv("CANVA_API_TOKEN", "")
CANVA_TEMPLATE_ID = os.getenv("CANVA_KINGDOM_WORDS_TEMPLATE_ID", "")

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "musicworks.db"

CLAUDE_MODEL = "claude-sonnet-4-6"

MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true" or not ANTHROPIC_API_KEY

ASSETS_DIR.mkdir(exist_ok=True)
