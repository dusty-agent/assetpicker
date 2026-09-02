"""
Development Shorts rendering adapter.

Expected final output:
    output/development/YYYY-MM-DD/shorts/card_shorts/

The existing AP Daily Shorts builder / renderer will be reused after its
actual callable signatures are connected.
"""

from pathlib import Path
from app.development.config import OUTPUT_ROOT, DAILY_ASSET_DIR


def shorts_cards_output_dir(run_date: str) -> Path:
    path = OUTPUT_ROOT / run_date / "shorts" / "card_shorts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def narration_output_dir(run_date: str) -> Path:
    path = OUTPUT_ROOT / run_date / "shorts" / "narration"
    path.mkdir(parents=True, exist_ok=True)
    return path


def shared_asset_dir() -> Path:
    return DAILY_ASSET_DIR
