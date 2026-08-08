from pathlib import Path
from datetime import datetime
import json

from app.daily.config import (
    CARDS_TEMPLATES,
)
from app.daily.renderer.render_html import render_html
from app.daily.renderer.render_png import render_png


ROOT = Path(__file__).resolve().parents[1]


def main():

    # ==================================================
    # Test date
    # ==================================================

    date = "2026-08-08"

    dt = datetime.strptime(
        date,
        "%Y-%m-%d",
    )

    today_text = (
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
            "curated.json을 찾을 수 없습니다.\n"
            f"Expected: {curated_path}"
        )


    data = json.loads(
        curated_path.read_text(
            encoding="utf-8"
        )
    )


    # ==================================================
    # Pages
    # ==================================================

    pages = data.get(
        "pages",
        data,
    )


    issues = pages.get(
        "issues",
        [],
    )


    if len(issues) != 5:

        raise RuntimeError(
            "Top 5 이슈가 필요합니다. "
            f"현재 생성된 이슈 수: "
            f"{len(issues)}"
        )


    # ==================================================
    # Output
    # ==================================================

    output_dir = (
        ROOT
        / "output"
        / "daily"
        / date
        / "card_test"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


    # ==================================================
    # Common
    # ==================================================

    common = {
        "today": today_text,
        "date_text": today_text,
        "total": 9,
    }


    # ==================================================
    # Renderer
    # ==================================================

    def render_card(
        *,
        template: str,
        output_name: str,
        page: int,
        context: dict,
    ):

        html = render_html(
            template,
            {
                **common,
                "page": page,
                **context,
            },
            CARDS_TEMPLATES,
        )


        html_path = (
            output_dir
            / f"{output_name}.html"
        )

        png_path = (
            output_dir
            / f"{output_name}.png"
        )


        html_path.write_text(
            html,
            encoding="utf-8",
        )


        render_png(
            html_path,
            png_path,
            width=1080,
            height=1350,
        )


        print(
            f"✅ {page}/9 "
            f"{png_path.name}"
        )


    # ==================================================
    # 1. Cover
    # ==================================================

    render_card(
        template="cover.html",
        output_name="cover",
        page=1,
        context=(
            pages.get(
                "cover",
                {},
            )
            or {}
        ),
    )


    # ==================================================
    # 2. Introduction
    # ==================================================

    render_card(
        template="introduction.html",
        output_name="introduction",
        page=2,
        context=(
            pages.get(
                "introduction",
                {},
            )
            or {}
        ),
    )


    # ==================================================
    # 3 ~ 7. Issues
    # ==================================================

    for issue_number, card in enumerate(
        issues,
        start=1,
    ):

        render_card(
            template="issue.html",
            output_name=(
                f"issue_{issue_number}"
            ),
            page=(
                issue_number + 2
            ),
            context={
                "card": card,
                "issue_number": issue_number,
            },
        )


    # ==================================================
    # 8. Insight
    # ==================================================

    render_card(
        template="insight.html",
        output_name="insight",
        page=8,
        context=(
            pages.get(
                "insight",
                {},
            )
            or {}
        ),
    )


    # ==================================================
    # 9. Ending
    # ==================================================

    render_card(
        template="ending.html",
        output_name="ending",
        page=9,
        context=(
            pages.get(
                "ending",
                {},
            )
            or {}
        ),
    )


    # ==================================================
    # Complete
    # ==================================================

    print()
    print("====================================")
    print("✅ Card render test complete")
    print("====================================")
    print()
    print(output_dir)
    print()


if __name__ == "__main__":
    main()