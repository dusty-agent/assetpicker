from datetime import date

from app.collector.rss_collector import RSSCollector

from app.daily.adapter import to_news_cards
from app.daily.config import ASSETS
from app.daily.config import OUTPUT
from app.daily.generator import DailyGenerator
from app.daily.renderer.render_html import render_html
from app.daily.renderer.render_png import render_png
from app.exporters.email import send_daily_email

collector = RSSCollector()

cards = to_news_cards(
    collector.collect(),
)

generator = DailyGenerator()

pages = generator.generate(
    cards,
)


asset_path = ASSETS.resolve().as_uri()

today = date.today()

common = {

    "asset_path": asset_path,

    "today": f"{today.year}년 {today.month}월 {today.day}일", #date.today().strftime("%Y.%m.%d"),

    "total": 9,

}

OUTPUT.mkdir(

    parents=True,

    exist_ok=True,

)


def render_page(

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

    )

    html_path = OUTPUT / f"{output_name}.html"

    html_path.write_text(

        html,

        encoding="utf-8",

    )

    render_png(

        html_path,

        OUTPUT / f"{output_name}.png",

    )

# --------------------------------------------------
# Static Pages
# --------------------------------------------------

render_page(
    "cover.html",
    "cover",
    1,
    pages["cover"],
)

render_page(
    "introduction.html",
    "introduction",
    2,
    pages["introduction"],
)


# --------------------------------------------------
# Issues (Top5)
# --------------------------------------------------

for idx, card in enumerate(pages["issues"], start=3):

    render_page(

        "issue.html",

        f"issue_{idx-2}",

        idx,

        {

            "card": card,

            # 홀수는 issue 배경
            "bg": "issue_odd.png" if idx % 2 == 1 else "issue_even.png",

        },

    )


# --------------------------------------------------
# Insight
# --------------------------------------------------

render_page(

    "insight.html",

    "insight",

    8,

    pages["insight"],

)


# --------------------------------------------------
# Ending
# --------------------------------------------------

render_page(

    "ending.html",

    "ending",

    9,

    pages["ending"],

)

print("✅ AP Daily Complete.")

send_daily_email()