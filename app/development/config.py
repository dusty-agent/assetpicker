from pathlib import Path

# .../<project>/app/development/config.py
APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent

DATA_ROOT = PROJECT_ROOT / "data" / "development"
OUTPUT_ROOT = PROJECT_ROOT / "output" / "development"

# Existing AP Daily design assets are reused.
DAILY_ASSET_DIR = APP_DIR / "daily" / "assets"

MAX_ITEMS = 40
TOP_N = 5
MIN_SCORE = 1

SOURCE_DESCRIPTIONS = {
    "토지이음": "정비구역 지정·변경, 사업승인 등 전국 고시",
    "서울시 정비사업 정보몽땅": "서울 재개발·재건축 진행상황",
    "국토교통부": "주택공급·정비사업·제도 변화",
}

DEVELOPMENT_ASSET_DIR = Path(__file__).resolve().parent / "assets"
