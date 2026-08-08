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


# ==================================================
# Helpers
# ==================================================

def render_compare_page(
    *,
    template_name: str,
    output_name: str,
    card_context: dict,
    shorts_context: dict,
    output_dir: Path,
):
    """
    같은 페이지를
    - 카드뉴스 1080 x 1350
    - 쇼츠     1080 x 1920
    두 버전으로 렌더링한다.
    """

    # --------------------------------------------------
    # Card
    # --------------------------------------------------

    card_html = render_html(
        template_name,
        card_context,
        CARDS_TEMPLATES,
    )

    card_html_path = (
        output_dir
        / f"{output_name}_card.html"
    )

    card_png_path = (
        output_dir
        / f"{output_name}_card.png"
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

    # --------------------------------------------------
    # Shorts
    # --------------------------------------------------

    shorts_html = render_html(
        template_name,
        shorts_context,
        SHORTS_TEMPLATES,
    )

    shorts_html_path = (
        output_dir
        / f"{output_name}_shorts.html"
    )

    shorts_png_path = (
        output_dir
        / f"{output_name}_shorts.png"
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

    print(
        f"✅ {output_name:<18} "
        f"CARD + SHORTS"
    )


# ==================================================
# Main
# ==================================================

def main():

    # ==================================================
    # Test date
    # ==================================================

    date = "2026-08-08"

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
            f"curated.json을 찾을 수 없습니다: "
            f"{curated_path}"
        )

    data = json.loads(
        curated_path.read_text(
            encoding="utf-8"
        )
    )

    pages = data.get("pages")

    if not pages:
        raise RuntimeError(
            "curated.json에 pages 데이터가 없습니다."
        )

    # ==================================================
    # Data
    # ==================================================

    issues = pages.get(
        "issues",
        [],
    )

    insight = pages.get(
        "insight",
        {},
    )

    ending = pages.get(
        "ending",
        {},
    )

    if not issues:
        raise RuntimeError(
            "curated.json에 issues 데이터가 없습니다."
        )

    # --------------------------------------------------
    # insight 구조 보정
    #
    # 현재 데이터가
    #
    # "insight": {
    #     "insight": {
    #         "summary": "...",
    #         "reason": "..."
    #     }
    # }
    #
    # 형태인 경우 내부 insight를 사용한다.
    # --------------------------------------------------

    if (
        isinstance(insight, dict)
        and "insight" in insight
        and isinstance(
            insight["insight"],
            dict,
        )
    ):
        insight = insight["insight"]

    # ==================================================
    # Output
    # ==================================================

    output_dir = (
        ROOT
        / "output"
        / "daily"
        / date
        / "compare_all"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ==================================================
    # Common
    # ==================================================

    total = 9

    print()
    print("==========================================")
    print("AP Daily Full Page Compare")
    print("==========================================")
    print()
    print(f"DATE   : {date_text}")
    print(f"ISSUES : {len(issues)}")
    print(f"OUTPUT : {output_dir}")
    print()

    # ==================================================
    # PAGE 1
    # Cover
    # ==================================================

    render_compare_page(
        template_name="cover.html",
        output_name="01_cover",

        card_context={
            "page": 1,
            "total": total,
            "today": date_text,
        },

        shorts_context={
            "page": 1,
            "total": total,
            "today": date_text,
            "date_text": date_text,
        },

        output_dir=output_dir,
    )

    # ==================================================
    # PAGE 2
    # Introduction
    # ==================================================

    render_compare_page(
        template_name="introduction.html",
        output_name="02_introduction",

        card_context={
            "page": 2,
            "total": total,
            "today": date_text,
        },

        shorts_context={
            "page": 2,
            "total": total,
            "today": date_text,
            "date_text": date_text,
        },

        output_dir=output_dir,
    )

    # ==================================================
    # PAGE 3 ~ 7
    # Issues
    # ==================================================

    for issue_number, card in enumerate(
        issues[:5],
        start=1,
    ):

        page_number = issue_number + 2

        context = {
            "page": page_number,
            "total": total,
            "today": date_text,
            "date_text": date_text,
            "issue_number": issue_number,
            "card": card,
        }

        render_compare_page(
            template_name="issue.html",

            output_name=(
                f"{page_number:02d}_"
                f"issue_{issue_number}"
            ),

            card_context=context.copy(),
            shorts_context=context.copy(),

            output_dir=output_dir,
        )

    # ==================================================
    # PAGE 8
    # Insight
    # ==================================================

    render_compare_page(
        template_name="insight.html",
        output_name="08_insight",

        card_context={
            "page": 8,
            "total": total,
            "today": date_text,
            "date_text": date_text,
            "insight": insight,
        },

        shorts_context={
            "page": 8,
            "total": total,
            "today": date_text,
            "date_text": date_text,
            "insight": insight,
        },

        output_dir=output_dir,
    )

    # ==================================================
    # PAGE 9
    # Ending
    # ==================================================

    render_compare_page(
        template_name="ending.html",
        output_name="09_ending",

        card_context={
            "page": 9,
            "total": total,
            "today": date_text,
            "date_text": date_text,
            "ending": ending,
        },

        shorts_context={
            "page": 9,
            "total": total,
            "today": date_text,
            "date_text": date_text,
            "ending": ending,
        },

        output_dir=output_dir,
    )

    # ==================================================
    # Done
    # ==================================================

    print()
    print("==========================================")
    print("✅ AP Daily Full Compare Complete")
    print("==========================================")
    print()
    print("CARD   : 1080 x 1350")
    print("SHORTS : 1080 x 1920")
    print()
    print(f"OUTPUT : {output_dir}")
    print()


if __name__ == "__main__":
    main()
    