from pathlib import Path
from datetime import datetime

from app.daily.config import CARDS_TEMPLATES
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
    # Output
    # ==================================================

    output_dir = (
        ROOT
        / "output"
        / "daily"
        / date
        / "introduction_test"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


    # ==================================================
    # Render HTML
    # ==================================================

    html = render_html(
        "introduction.html",
        {
            "today": today_text,
            "page": 2,
            "total": 9,
        },
        CARDS_TEMPLATES,
    )


    html_path = (
        output_dir
        / "introduction.html"
    )

    png_path = (
        output_dir
        / "introduction.png"
    )


    html_path.write_text(
        html,
        encoding="utf-8",
    )


    # ==================================================
    # Render PNG
    # ==================================================

    render_png(
        html_path,
        png_path,
        width=1080,
        height=1350,
    )


    # ==================================================
    # Complete
    # ==================================================

    print()
    print("====================================")
    print("Introduction Render Test")
    print("====================================")
    print()
    print(f"✅ HTML : {html_path}")
    print(f"✅ PNG  : {png_path}")
    print()


if __name__ == "__main__":
    main()