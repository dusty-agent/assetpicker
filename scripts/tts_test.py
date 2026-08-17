from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import os
import re

from dotenv import load_dotenv


# ==================================================
# Helpers
# ==================================================

def get_first_sentence(text: str) -> str:
    """
    소수점(예: 4.3%) 중간에서 잘리지 않도록
    문장 끝으로 보이는 마침표/물음표/느낌표까지만 추출합니다.
    """
    text = text.strip()

    if not text:
        return ""

    match = re.match(
        r"^(.+?[.!?])(?:\s|$)",
        text,
    )

    if match:
        return match.group(1).strip()

    return text


# ==================================================
# Environment
# ==================================================

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        "OPENAI_API_KEY를 찾을 수 없습니다."
    )


# 환경변수 로드 후 import
from app.daily.shorts.tts import generate_tts


# ==================================================
# Settings
# ==================================================

KST = timezone(
    timedelta(hours=9)
)

today = datetime.now(KST)

date = today.strftime(
    "%Y-%m-%d"
)

CURATED_PATH = (
    Path("data")
    / "daily"
    / date
    / "curated.json"
)

OUTPUT_DIR = (
    Path("output")
    / "daily"
    / date
    / "shorts"
    / "narration"
)

# ==================================================
# Load Curated
# ==================================================

print()
print("====================================")
print("AP Daily TTS Test")
print("====================================")
print()

print(f"DATE    : {date}")
print(f"CURATED : {CURATED_PATH}")
print()


if not CURATED_PATH.exists():
    raise FileNotFoundError(
        f"curated.json을 찾을 수 없습니다: "
        f"{CURATED_PATH}"
    )


with CURATED_PATH.open(
    "r",
    encoding="utf-8",
) as f:
    curated = json.load(f)


pages = curated.get(
    "pages",
    {},
)

issues = pages.get(
    "issues",
    [],
)


if len(issues) != 5:
    raise RuntimeError(
        "이슈 5개가 필요합니다. "
        f"현재: {len(issues)}개"
    )


# ==================================================
# Narration Scripts
# ==================================================

narration_scripts = {}


# --------------------------------------------------
# Opening
# --------------------------------------------------

narration_scripts["opening"] = (
    f"{today.month}월 {today.day}일, "
    "오늘의 부동산 이슈를 전해드립니다."
)


# --------------------------------------------------
# Issue 1 ~ 5
# --------------------------------------------------

for i, issue in enumerate(
    issues,
    start=1,
):

    title = (
        issue.get(
            "title",
            "",
        )
        .strip()
    )

    summary = (
        issue.get(
            "summary",
            "",
        )
        .strip()
    )

    first_sentence = (
        get_first_sentence(
            summary
        )
    )

    narration_scripts[
        f"issue_{i}"
    ] = (
        f"{title}. "
        f"{first_sentence}"
    )


# --------------------------------------------------
# Insight
# --------------------------------------------------

insight_page = pages.get(
    "insight",
    {},
)

insight = insight_page.get(
    "insight",
    {},
)


keyword = (
    insight.get(
        "keyword",
        "",
    )
    .strip()
)

insight_summary = (
    insight.get(
        "summary",
        "",
    )
    .strip()
)


narration_scripts[
    "insight"
] = (
    f"오늘의 키워드는 "
    f"{keyword}입니다. "
    f"{insight_summary}"
)


# --------------------------------------------------
# Ending
# --------------------------------------------------

narration_scripts[
    "ending"
] = (
    "내일도 찾아옵니다. "
    "구독, 좋아요, 알림 설정 부탁드립니다."
)


# ==================================================
# Preview Scripts
# ==================================================

print("====================================")
print("Narration Scripts")
print("====================================")
print()


for name, script in narration_scripts.items():

    print(
        f"[{name}]"
    )

    print(
        script
    )

    print()


# ==================================================
# Generate TTS
# ==================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


print("====================================")
print("Generating TTS")
print("====================================")
print()


for name, script in narration_scripts.items():

    output_path = (
        OUTPUT_DIR
        / f"{name}.mp3"
    )

    generate_tts(
        script,
        output_path,
    )


print()
print("====================================")
print("DONE")
print("====================================")
print()

print(
    f"Output: "
    f"{OUTPUT_DIR.resolve()}"
)