from pathlib import Path
from datetime import datetime

from app.daily.config import SHORTS_TEMPLATES
from app.daily.renderer.render_html import render_html
from app.daily.renderer.render_png import render_png


ROOT = Path(__file__).resolve().parents[1]


def main():

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


    insight = {
        "summary": (
            "오늘 부동산 시장의 핵심은 공급을 "
            "더 빨리 늘리려는 정부 움직임과 "
            "세제·대출을 둘러싼 불확실성입니다."
        ),

        "reason": (
            "대통령 주재 장시간 회의와 공급대책 임박 보도가 "
            "가장 큰 정책 신호였습니다. 동시에 세제개편 후폭풍, "
            "대출 규제 재점검, 용산 부지 논쟁이 맞물리며 "
            "시장은 정책 방향을 확인하려는 관망세가 커지고 있습니다."
        ),

        "sources": [],
    }


    output_dir = (
        ROOT
        / "output"
        / "daily"
        / date
        / "shorts"
        / "insight_test"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


    html = render_html(
        "insight.html",
        {
            "today": today_text,
            "page": 8,
            "total": 9,
            "insight": insight,
        },
        SHORTS_TEMPLATES,
    )


    html_path = (
        output_dir
        / "insight.html"
    )

    png_path = (
        output_dir
        / "insight.png"
    )


    html_path.write_text(
        html,
        encoding="utf-8",
    )


    render_png(
        html_path,
        png_path,
        width=1080,
        height=1920,
    )


    print()
    print("====================================")
    print("Shorts Insight Render Test")
    print("====================================")
    print()
    print(f"✅ HTML : {html_path}")
    print(f"✅ PNG  : {png_path}")
    print()


if __name__ == "__main__":
    main()