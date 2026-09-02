from pathlib import Path
from datetime import datetime, timezone, timedelta
import os

from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


ROOT = Path(__file__).parent

ASSETS = ROOT / "assets"

CARDS_TEMPLATES = ROOT / "cards" / "templates"
SHORTS_TEMPLATES = ROOT / "shorts" / "templates"


KST = timezone(timedelta(hours=9))

TODAY = datetime.now(KST).strftime("%Y-%m-%d")

OUTPUT = Path("output/daily") / TODAY


DEBUG = True

WIDTH = 1080
HEIGHT = 1350

FONT = "Pretendard"

PRIMARY = "#F6D85B"
TEXT = "#FFFFFF"
TEXT_SUB = "#D1D5DB"

PADDING = 72