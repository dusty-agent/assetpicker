from pathlib import Path
from datetime import date
import os

from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


ROOT = Path(__file__).parent

ASSETS = ROOT / "assets"
TEMPLATES = ROOT / "templates"

TODAY = date.today().isoformat()

OUTPUT = Path("output/daily") / TODAY

DEBUG = True

WIDTH = 1080
HEIGHT = 1350

FONT = "Pretendard"

PRIMARY = "#D4AF37"
TEXT = "#FFFFFF"
TEXT_SUB = "#D1D5DB"

PADDING = 72