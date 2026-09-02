"""
Development card rendering adapter.

This module intentionally does NOT create another global renderer.
The existing AP Daily rendering stack should be reused.

Expected final output:
    output/development/YYYY-MM-DD/cards/

The concrete daily renderer call is connected after verifying the exact
function signatures in app.daily.builder.cards_builder and
app.daily.renderer.
"""

from pathlib import Path
from app.development.config import OUTPUT_ROOT, DAILY_ASSET_DIR


def cards_output_dir(run_date: str) -> Path:
    path = OUTPUT_ROOT / run_date / "cards"
    path.mkdir(parents=True, exist_ok=True)
    return path


def shared_asset_dir() -> Path:
    return DAILY_ASSET_DIR
