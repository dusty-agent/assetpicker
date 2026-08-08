from pathlib import Path

from playwright.sync_api import sync_playwright


def render_png(
    html_path: Path,
    output_path: Path,
    width: int = 1080,
    height: int = 1350,
):
    """
    HTML 파일을 PNG로 렌더링한다.

    기본값:
        Card News = 1080 x 1350

    Shorts:
        width=1080,
        height=1920
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sync_playwright() as p:

        browser = p.chromium.launch()

        page = browser.new_page(
            viewport={
                "width": width,
                "height": height,
            }
        )

        page.goto(
            html_path.resolve().as_uri(),
            wait_until="networkidle",
        )

        page.screenshot(
            path=str(output_path),
            full_page=False,
        )

        browser.close()