from pathlib import Path
from datetime import datetime
import json

from app.daily.config import (
    CARDS_TEMPLATES,
    SHORTS_TEMPLATES,
)

from app.daily.renderer.render_html import render_html
from app.daily.renderer.render_png import render_png


ROOT = Path(__file__).resolve().parents[1]


def main():

    # ==================================================
    # Test
    # ==================================================

    date = "2026-08-08"
    issue_number = 1

    dt = datetime.strptime(
        date,
        "%Y-%m-%d",
    )

    date_text = (
        f"{dt.year}년 "
        f"{dt.month}월 "
        f"{dt.day}일"
    )

    # ==================================================
    # Load curated.json
    # ==================================================

    curated_path = (
        ROOT
        / "data"
        / "daily"
        / date
        / "curated.json"
    )

    if not curated_path.exists():
        raise FileNotFoundError(
            f"curated.json을 찾을 수 없습니다: {curated_path}"
        )

    data = json.loads(
        curated_path.read_text(
            encoding="utf-8"
        )
    )

    pages = data["pages"]
    issues = pages["issues"]

    if not issues:
        raise RuntimeError(
            "curated.json에 issues가 없습니다."
        )

    if issue_number < 1 or issue_number > len(issues):
        raise ValueError(
            f"issue_number 범위 오류: "
            f"1 ~ {len(issues)} 사이여야 합니다."
        )

    card = issues[issue_number - 1]

    # ==================================================
    # Output
    # ==================================================

    output_dir = (
        ROOT
        / "output"
        / "daily"
        / date
        / "compare"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ==================================================
    # 1. 카드뉴스 Issue
    # ==================================================
    #
    # 1 Cover
    # 2 Introduction
    # 3~7 Issue
    # 8 Insight
    # 9 Ending
    #
    # 따라서 Issue 1 = page 3
    # ==================================================

    card_page = issue_number + 2

    card_context = {
        "page": card_page,
        "total": 9,
        "today": date_text,
        "issue_number": issue_number,
        "card": card,

        # 기존 카드뉴스 배경 규칙 유지
        "bg": (
            "issue_odd.png"
            if card_page % 2 == 1
            else "issue_even.png"
        ),
    }

    card_html = render_html(
        "issue.html",
        card_context,
        CARDS_TEMPLATES,
    )

    card_html_path = (
        output_dir
        / f"issue_{issue_number}_card.html"
    )

    card_png_path = (
        output_dir
        / f"issue_{issue_number}_card.png"
    )

    card_html_path.write_text(
        card_html,
        encoding="utf-8",
    )

    render_png(
        card_html_path,
        card_png_path,
        width=1080,
        height=1350,
    )

    # ==================================================
    # 2. 쇼츠 Issue
    # ==================================================

    shorts_page = issue_number + 2

    shorts_context = {
        "page": shorts_page,
        "total": 9,
        "today": date_text,
        "date_text": date_text,
        "issue_number": issue_number,
        "card": card,
    }

    shorts_html = render_html(
        "issue.html",
        shorts_context,
        SHORTS_TEMPLATES,
    )

    shorts_html_path = (
        output_dir
        / f"issue_{issue_number}_shorts.html"
    )

    shorts_png_path = (
        output_dir
        / f"issue_{issue_number}_shorts.png"
    )

    shorts_html_path.write_text(
        shorts_html,
        encoding="utf-8",
    )

    render_png(
        shorts_html_path,
        shorts_png_path,
        width=1080,
        height=1920,
    )

    # ==================================================
    # Result
    # ==================================================

    print()
    print("====================================")
    print("AP Daily Issue Compare")
    print("====================================")

    print()
    print(f"DATE  : {date_text}")
    print(f"ISSUE : {issue_number}")
    print(f"PAGE  : {shorts_page} / 9")

    print()
    print("TITLE")
    print(card.get("title", ""))

    print()
    print("CARD")
    print(card_png_path)

    print()
    print("SHORTS")
    print(shorts_png_path)

    print()
    print("✅ Issue compare render complete")


if __name__ == "__main__":
    main()