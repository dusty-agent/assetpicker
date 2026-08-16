from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.collector.rss_collector import RSSCollector

from app.daily.adapter import to_news_cards
from app.daily.archive import (
    save_raw_news,
    save_curated,
)
from app.daily.config import (
    OUTPUT,
    CARDS_TEMPLATES,
    SHORTS_TEMPLATES,
)
from app.daily.generator import DailyGenerator
from app.daily.renderer.render_html import render_html
from app.daily.renderer.render_png import render_png

from app.daily.shorts.builder import (
    build_daily_short,
)

from app.exporters.email import send_daily_email


# ==================================================
# Timezone
# ==================================================

KST = timezone(
    timedelta(hours=9)
)


# ==================================================
# Main
# ==================================================

def main():

    # ==================================================
    # Date
    # ==================================================

    today = datetime.now(KST)

    date = today.strftime(
        "%Y-%m-%d"
    )

    today_text = (
        f"{today.year}년 "
        f"{today.month}월 "
        f"{today.day}일"
    )

    print()
    print("====================================")
    print("AP Daily")
    print("====================================")
    print(f"DATE : {date}")
    print(f"TEXT : {today_text}")
    print()


    # ==================================================
    # 1. Collect
    # ==================================================

    print("📰 Collecting news...")

    collector = RSSCollector()

    raw_news = collector.collect()

    if not raw_news:

        raise RuntimeError(
            "수집된 뉴스가 없습니다."
        )

    print(
        f"✅ News collected: "
        f"{len(raw_news)}"
    )


    # ==================================================
    # 2. Save RAW
    # ==================================================

    save_raw_news(
        raw_news,
        output_root=Path(
            "data/daily"
        ),
        rss_url=collector.RSS_URL,
    )

    print(
        "✅ Raw news saved"
    )


    # ==================================================
    # 3. Adapter
    # ==================================================

    cards = to_news_cards(
        raw_news
    )


    # ==================================================
    # 4. Generate / Curate
    # ==================================================

    print()
    print(
        "🤖 Generating AP Daily..."
    )

    generator = DailyGenerator()

    pages = generator.generate(
        cards
    )


    # ==================================================
    # 5. Validate
    # ==================================================

    issues = pages.get(
        "issues",
        [],
    )

    if len(issues) != 5:

        raise RuntimeError(
            "AP Daily는 Top 5 이슈가 필요합니다. "
            f"현재 생성된 이슈 수: "
            f"{len(issues)}"
        )


    # ==================================================
    # 6. Save Curated
    # ==================================================

    save_curated(
        pages,
        output_root=Path(
            "data/daily"
        ),
    )

    print(
        "✅ Curated data saved"
    )


    # ==================================================
    # 7. Output directories
    # ==================================================

    OUTPUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    shorts_output = (
        OUTPUT
        / "shorts"
    )

    shorts_output.mkdir(
        parents=True,
        exist_ok=True,
    )


    # ==================================================
    # Common Context
    # ==================================================

    common = {
        "today": today_text,
        "date_text": today_text,
        "total": 9,
    }


    # ==================================================
    # Generic Renderer
    # ==================================================

    def render_page(
        *,
        template: str,
        output_name: str,
        page: int,
        context: dict,
        template_dir: Path,
        output_dir: Path,
        width: int,
        height: int,
    ):

        html = render_html(
            template,
            {
                **common,
                "page": page,
                **context,
            },
            template_dir,
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
            width=width,
            height=height,
        )

        return png_path


    # ==================================================
    # Card renderer
    # ==================================================

    def render_card(
        template: str,
        output_name: str,
        page: int,
        context: dict,
    ):

        png_path = render_page(
            template=template,
            output_name=output_name,
            page=page,
            context=context,
            template_dir=CARDS_TEMPLATES,
            output_dir=OUTPUT,
            width=1080,
            height=1350,
        )

        print(
            f"✅ CARD   "
            f"{page}/9  "
            f"{png_path.name}"
        )


    # ==================================================
    # Shorts renderer
    # ==================================================

    def render_short(
        template: str,
        output_name: str,
        page: int,
        context: dict,
    ):

        png_path = render_page(
            template=template,
            output_name=output_name,
            page=page,
            context=context,
            template_dir=SHORTS_TEMPLATES,
            output_dir=shorts_output,
            width=1080,
            height=1920,
        )

        print(
            f"✅ SHORTS "
            f"{page}/9  "
            f"{png_path.name}"
        )


    # ==================================================
    # Page definitions
    # ==================================================

    page_defs = []


    # --------------------------------------------------
    # PAGE 1
    # Cover
    # --------------------------------------------------

    page_defs.append(
        {
            "template": "cover.html",
            "output_name": "cover",
            "page": 1,
            "context": (
                pages.get(
                    "cover",
                    {},
                )
                or {}
            ),
        }
    )


    # --------------------------------------------------
    # PAGE 2
    # Introduction
    # --------------------------------------------------

    page_defs.append(
        {
            "template": "introduction.html",
            "output_name": "introduction",
            "page": 2,
            "context": (
                pages.get(
                    "introduction",
                    {},
                )
                or {}
            ),
        }
    )


    # --------------------------------------------------
    # PAGE 3 ~ 7
    # Issues
    # --------------------------------------------------

    for issue_number, card in enumerate(
        issues,
        start=1,
    ):

        page_number = (
            issue_number + 2
        )

        page_defs.append(
            {
                "template": "issue.html",
                "output_name": (
                    f"issue_"
                    f"{issue_number}"
                ),
                "page": page_number,
                "context": {
                    "card": card,
                    "issue_number": (
                        issue_number
                    ),
                },
            }
        )


    # --------------------------------------------------
    # PAGE 8
    # Insight
    # --------------------------------------------------

    insight_context = (
        pages.get(
            "insight",
            {},
        )
        or {}
    )

    page_defs.append(
        {
            "template": "insight.html",
            "output_name": "insight",
            "page": 8,
            "context": insight_context,
        }
    )


    # --------------------------------------------------
    # PAGE 9
    # Ending
    # --------------------------------------------------

    ending_context = (
        pages.get(
            "ending",
            {},
        )
        or {}
    )

    page_defs.append(
        {
            "template": "ending.html",
            "output_name": "ending",
            "page": 9,
            "context": ending_context,
        }
    )


    # ==================================================
    # 8. Render Cards
    # ==================================================

    print()
    print("====================================")
    print("Rendering Cards")
    print("1080 x 1350")
    print("====================================")
    print()

    for item in page_defs:

        render_card(
            template=item[
                "template"
            ],
            output_name=item[
                "output_name"
            ],
            page=item[
                "page"
            ],
            context=item[
                "context"
            ],
        )


    # ==================================================
    # 9. Render Shorts
    # ==================================================

    print()
    print("====================================")
    print("Rendering Shorts")
    print("1080 x 1920")
    print("====================================")
    print()

    for item in page_defs:

        render_short(
            template=item[
                "template"
            ],
            output_name=item[
                "output_name"
            ],
            page=item[
                "page"
            ],
            context=item[
                "context"
            ],
        )
        
    # ==================================================
    # 10. Build Shorts Video
    # ==================================================

    print()
    print("====================================")
    print("Building Shorts Video")
    print("====================================")
    print()


    short_video_path = (
        OUTPUT
        / f"ap_daily_short_{date}.mp4"
    )


    try:

        build_daily_short(
            date=date,
            source_dir=shorts_output,
            output_path=short_video_path,
        )

        print(
            "✅ Shorts video created"
        )

        print(
            short_video_path
        )


    except Exception as exc:

        print()
        print(
            "⚠️ Shorts video build failed."
        )

        print(
            exc
        )

        print(
            "AP Daily card/email pipeline will continue."
        )


    # ==================================================
    # 11. Email
    # ==================================================

    print(
        "📧 Sending email..."
    )

    send_daily_email()

    print(
        "✅ Email sent."
    )

    print()


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":
    main()