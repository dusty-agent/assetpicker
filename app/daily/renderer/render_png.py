from pathlib import Path

from playwright.sync_api import sync_playwright


def render_png(
    html_path: Path,
    output_path: Path,
):

    with sync_playwright() as p:

        browser = p.chromium.launch()

        page = browser.new_page(
            viewport={
                "width": 1080,
                "height": 1350,
            }
        )

        page.goto(html_path.resolve().as_uri())

        page.screenshot(
            path=str(output_path),
        )

        browser.close()