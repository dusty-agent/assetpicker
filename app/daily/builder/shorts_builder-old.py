from pathlib import Path
from datetime import datetime
import asyncio

from playwright.async_api import async_playwright

from app.daily.renderer.render_html import render_html


ROOT = Path(__file__).resolve().parents[3]

OUTPUT_ROOT = (
    ROOT
    / "output"
    / "daily"
)


async def screenshot_html(
    html_path: Path,
    png_path: Path,
):
    """
    HTML 파일을 1080x1920 PNG로 캡처한다.
    """

    async with async_playwright() as p:

        browser = await p.chromium.launch()

        page = await browser.new_page(
            viewport={
                "width": 1080,
                "height": 1920,
            }
        )

        await page.goto(
            html_path.resolve().as_uri(),
            wait_until="networkidle",
        )

        await page.screenshot(
            path=str(png_path),
            full_page=False,
        )

        await browser.close()


def build_shorts_issue(
    *,
    date: str,
    issue_number: int,
    title: str,
    keywords: list[str],
    summary: str,
    source: str,
):
    """
    AP Daily Shorts 전용
    Issue 화면 1장을 생성한다.
    """

    output_dir = (
        OUTPUT_ROOT
        / date
        / "shorts"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ----------------------------------------------
    # 날짜
    # ----------------------------------------------

    dt = datetime.strptime(
        date,
        "%Y-%m-%d",
    )

    date_text = (
        f"{dt.year}년 "
        f"{dt.month}월 "
        f"{dt.day}일"
    )

    # ----------------------------------------------
    # Shorts template context
    # ----------------------------------------------

    context = {
        "date_text": date_text,
        "issue_number": issue_number,
        "title": title,
        "keywords": keywords,
        "summary": summary,
        "source": source,
    }

    # ----------------------------------------------
    # HTML 생성
    # ----------------------------------------------

    html = render_html(
        "shorts.html",
        context,
    )

    html_path = (
        output_dir
        / f"issue_{issue_number}.html"
    )

    png_path = (
        output_dir
        / f"issue_{issue_number}.png"
    )

    html_path.write_text(
        html,
        encoding="utf-8",
    )

    # ----------------------------------------------
    # PNG 캡처
    # ----------------------------------------------

    asyncio.run(
        screenshot_html(
            html_path,
            png_path,
        )
    )

    print()
    print(
        "Shorts issue generated:"
    )
    print(
        png_path
    )

    return png_path


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    build_shorts_issue(
        date="2026-08-08",

        issue_number=1,

        title=(
            "수도권 주택 공급 속도전"
        ),

        keywords=[
            "공급",
            "수도권",
            "정책",
        ],

        summary=(
            "정부가 수도권 주택 공급 확대를 위한 "
            "점검에 나섰습니다. 신속 공급과 후보지 "
            "검토가 주요 논의로 떠올랐습니다."
        ),

        source=(
            "연합뉴스 · KBS 뉴스"
        ),
    )