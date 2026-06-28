from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

PUBLIC_DIR = BASE_DIR / "public"
TEMPLATE_DIR = BASE_DIR / "templates"
PROMPT_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = PUBLIC_DIR / "cards"