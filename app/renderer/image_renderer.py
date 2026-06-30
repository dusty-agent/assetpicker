from pathlib import Path

from playwright.sync_api import sync_playwright


class ImageRenderer:

    def render(
        self,
        html_dir: Path,
        output_dir: Path,
    ):

        output_dir.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:

            browser = p.chromium.launch()

            page = browser.new_page(
                viewport={
                    "width": 1080,
                    "height": 1350,
                }
            )

            for html_file in sorted(html_dir.glob("*.html")):

                page.goto(html_file.resolve().as_uri())

                # ⭐ Tailwind 등 모든 리소스가 로드될 때까지 대기
                page.wait_for_load_state("networkidle")

                page.screenshot(
                    path=str(output_dir / f"{html_file.stem}.png"),
                    full_page=True,
                )

            browser.close()