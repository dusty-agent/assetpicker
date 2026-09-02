from datetime import datetime, timezone, timedelta
from pathlib import Path
import re

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

from app.daily.shorts.tts import generate_tts

from app.daily.shorts.builder import (
    build_daily_short,
)


# ==================================================
# Timezone
# ==================================================

KST = timezone(
    timedelta(hours=9)
)


# ==================================================
# Helpers
# ==================================================

def get_first_sentence(
    text: str,
) -> str:

    """
    summary에서 첫 문장만 추출합니다.

    문장부호가 있으면 첫 문장까지만 사용하고,
    문장부호가 없으면 전체 문자열을 사용합니다.
    """

    text = (
        text
        .strip()
    )

    if not text:

        return ""

    match = re.match(
        r"^(.+?[.!?])(?:\s|$)",
        text,
    )

    if match:

        return (
            match
            .group(1)
            .strip()
        )

    return text


def clean_narration_text(
    text: str,
) -> str:

    """
    TTS용 문자열을 간단히 정리합니다.
    """

    text = (
        text
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def join_title_summary(
    title: str,
    summary: str,
) -> str:

    """
    제목 + 첫 문장을 자연스럽게 연결합니다.

    title 또는 summary 끝에 이미 문장부호가 있으면
    마침표를 중복해서 붙이지 않습니다.
    """

    title = clean_narration_text(
        title
    )

    summary = clean_narration_text(
        summary
    )

    parts = []

    if title:

        if title[-1] not in ".!?":

            title += "."

        parts.append(
            title
        )

    if summary:

        if summary[-1] not in ".!?":

            summary += "."

        parts.append(
            summary
        )

    return " ".join(
        parts
    )

def to_polite_narration(
    text: str,
) -> str:

    text = (
        text
        .strip()
    )

    replacements = [
        ("나왔다.", "나왔습니다."),
        ("이어졌다.", "이어졌습니다."),
        ("커졌다.", "커졌습니다."),
        ("확산됐다.", "확산됐습니다."),
        ("증가했다.", "증가했습니다."),
        ("감소했다.", "감소했습니다."),
        ("상승했다.", "상승했습니다."),
        ("하락했다.", "하락했습니다."),
        ("밝혔다.", "밝혔습니다."),
        ("발표했다.", "발표했습니다."),
        ("전망했다.", "전망했습니다."),
        ("지적했다.", "지적했습니다."),
        ("분석했다.", "분석했습니다."),
        ("보였다.", "보였습니다."),
        ("나타났다.", "나타났습니다."),
        ("확인됐다.", "확인됐습니다."),
        ("제기됐다.", "제기됐습니다."),
    ]

    for old, new in replacements:
        if text.endswith(old):
            return (
                text[
                    :-len(old)
                ]
                + new
            )

    return text

# ==================================================
# Narration Scripts
# ==================================================

def build_narration_scripts(
    *,
    today: datetime,
    pages: dict,
) -> dict[str, str]:

    """
    카드 생성에 사용한 동일한 pages 데이터를 이용해
    TTS 대본을 생성합니다.

    따라서 카드 issue_1과 narration issue_1이
    서로 다른 뉴스가 되는 것을 방지합니다.
    """

    narration_scripts = {}


    # ==================================================
    # Opening
    # ==================================================

    narration_scripts[
        "opening"
    ] = (
        f"{today.month}월 "
        f"{today.day}일, "
        "오늘의 부동산 이슈를 전해드립니다."
    )


    # ==================================================
    # Issues
    # ==================================================

    issues = pages.get(
        "issues",
        [],
    )

    if len(issues) != 5:

        raise RuntimeError(
            "TTS 생성을 위해서는 "
            "이슈 5개가 필요합니다. "
            f"현재: {len(issues)}개"
        )


    for i, issue in enumerate(
        issues,
        start=1,
    ):

        title = (
            issue.get(
                "title",
                "",
            )
            or ""
        )

        summary = (
            issue.get(
                "summary",
                "",
            )
            or ""
        )

        first_sentence = (
            get_first_sentence(
                summary
            )
        )
        
        first_sentence_narration = (
            to_polite_narration(
                first_sentence
            )
        )

        narration_scripts[
            f"issue_{i}"
        ] = (
            join_title_summary(
                title,
                first_sentence_narration,
            )
        )


    # ==================================================
    # Insight
    # ==================================================

    insight_page = (
        pages.get(
            "insight",
            {},
        )
        or {}
    )

    insight = (
        insight_page.get(
            "insight",
            {},
        )
        or {}
    )

    keyword = (
        insight.get(
            "keyword",
            "",
        )
        or ""
    )

    keyword = clean_narration_text(
        keyword
    )


    insight_summary = (
        insight.get(
            "summary",
            "",
        )
        or ""
    )

    insight_summary = (
        clean_narration_text(
            insight_summary
        )
    )


    insight_parts = []


    if keyword:

        insight_parts.append(
            f"오늘의 키워드는 "
            f"{keyword}입니다."
        )


    if insight_summary:

        if insight_summary[-1] not in ".!?":

            insight_summary += "."

        insight_parts.append(
            insight_summary
        )


    narration_scripts[
        "insight"
    ] = " ".join(
        insight_parts
    )


    # ==================================================
    # Ending
    # ==================================================

    narration_scripts[
        "ending"
    ] = (
        "내일도 찾아옵니다. "
        "구독, 좋아요, "
        "알림 설정 부탁드립니다."
    )


    # ==================================================
    # Validate
    # ==================================================

    required = [

        "opening",

        "issue_1",
        "issue_2",
        "issue_3",
        "issue_4",
        "issue_5",

        "insight",

        "ending",
    ]


    for name in required:

        script = (
            narration_scripts
            .get(
                name,
                "",
            )
            .strip()
        )

        if not script:

            raise RuntimeError(
                "나레이션 대본이 비어 있습니다.\n"
                f"Name: {name}"
            )


    return narration_scripts


# ==================================================
# Generate Narration
# ==================================================

def generate_narration(
    *,
    narration_scripts: dict[str, str],
    output_dir: Path,
):

    """
    narration_scripts를 실제 MP3로 생성합니다.
    """

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


    print()
    print("====================================")
    print("Narration Scripts")
    print("====================================")
    print()


    for name, script in (
        narration_scripts.items()
    ):

        print(
            f"[{name}]"
        )

        print(
            script
        )

        print()


    print("====================================")
    print("Generating TTS Narration")
    print("====================================")
    print()


    for name, script in (
        narration_scripts.items()
    ):

        output_path = (
            output_dir
            / f"{name}.mp3"
        )

        generate_tts(
            script,
            output_path,
        )


    print()
    print(
        "✅ TTS narration created"
    )
    print()


# ==================================================
# Main
# ==================================================

def main():

    # ==================================================
    # Date
    # ==================================================

    today = datetime.now(
        KST
    )

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
    print(
        f"DATE : {date}"
    )
    print(
        f"TEXT : {today_text}"
    )
    print()


    # ==================================================
    # 1. Collect
    # ==================================================

    print(
        "📰 Collecting news..."
    )

    collector = (
        RSSCollector()
    )

    raw_news = (
        collector.collect()
    )


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

        rss_url=(
            collector.RSS_URL
        ),
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


    generator = (
        DailyGenerator()
    )


    pages = (
        generator.generate(
            cards
        )
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
    # 7. Output Directories
    # ==================================================
    #
    # OUTPUT은 config.py에서 이미
    #
    # output/daily/YYYY-MM-DD
    #
    # 를 가리킵니다.
    #
    # 최종 구조:
    #
    # output/
    # └─ daily/
    #    └─ YYYY-MM-DD/
    #
    #       ├─ cards/
    #
    #       └─ shorts/
    #
    #          ├─ card_shorts/
    #
    #          ├─ narration/
    #
    #          └─
    #             ap_daily_short_YYYY-MM-DD.mp4
    #
    # ==================================================

    daily_output = OUTPUT


    cards_output = (
        daily_output
        / "cards"
    )


    shorts_root = (
        daily_output
        / "shorts"
    )


    shorts_cards_output = (
        shorts_root
        / "card_shorts"
    )


    narration_output = (
        shorts_root
        / "narration"
    )


    # ==================================================
    # Create Directories
    # ==================================================

    daily_output.mkdir(
        parents=True,
        exist_ok=True,
    )

    cards_output.mkdir(
        parents=True,
        exist_ok=True,
    )

    shorts_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    shorts_cards_output.mkdir(
        parents=True,
        exist_ok=True,
    )

    narration_output.mkdir(
        parents=True,
        exist_ok=True,
    )


    print()
    print("====================================")
    print("Output Directories")
    print("====================================")

    print(
        f"Daily       : "
        f"{daily_output}"
    )

    print(
        f"Cards       : "
        f"{cards_output}"
    )

    print(
        f"Short Cards : "
        f"{shorts_cards_output}"
    )

    print(
        f"Narration   : "
        f"{narration_output}"
    )

    print()


    # ==================================================
    # Common Context
    # ==================================================

    common = {

        "today":
            today_text,

        "date_text":
            today_text,

        "total":
            9,
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

                "page":
                    page,

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
    # Card Renderer
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

            template_dir=(
                CARDS_TEMPLATES
            ),

            output_dir=(
                cards_output
            ),

            width=1080,
            height=1350,
        )


        print(
            f"✅ CARD   "
            f"{page}/9  "
            f"{png_path.name}"
        )


    # ==================================================
    # Shorts Renderer
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

            template_dir=(
                SHORTS_TEMPLATES
            ),

            output_dir=(
                shorts_cards_output
            ),

            width=1080,
            height=1920,
        )


        print(
            f"✅ SHORTS "
            f"{page}/9  "
            f"{png_path.name}"
        )


    # ==================================================
    # Page Definitions
    # ==================================================

    page_defs = []


    # ==================================================
    # PAGE 1
    # Cover
    # ==================================================

    page_defs.append(
        {
            "template":
                "cover.html",

            "output_name":
                "cover",

            "page":
                1,

            "context":
                (
                    pages.get(
                        "cover",
                        {},
                    )
                    or {}
                ),
        }
    )


    # ==================================================
    # PAGE 2
    # Introduction
    # ==================================================

    page_defs.append(
        {
            "template":
                "introduction.html",

            "output_name":
                "introduction",

            "page":
                2,

            "context":
                (
                    pages.get(
                        "introduction",
                        {},
                    )
                    or {}
                ),
        }
    )


    # ==================================================
    # PAGE 3 ~ 7
    # Issues
    # ==================================================

    for issue_number, card in enumerate(
        issues,
        start=1,
    ):

        page_number = (
            issue_number
            + 2
        )


        # ==================================================
        # Summary
        #
        # TTS가 실제로 읽는 첫 문장과
        # 화면에만 보여주는 나머지 문장을 분리
        # ==================================================

        summary = (
            card.get(
                "summary",
                "",
            )
            or ""
        ).strip()


        summary_first = (
            get_first_sentence(
                summary
            )
        )


        summary_rest = (
            summary[
                len(summary_first):
            ]
            .strip()
        )


        # 기존 card 데이터는 그대로 유지하면서
        # 쇼츠 템플릿용 필드만 추가
        card["summary_first"] = (
            summary_first
        )

        card["summary_rest"] = (
            summary_rest
        )


        page_defs.append(
            {
                "template":
                    "issue.html",

                "output_name":
                    (
                        f"issue_"
                        f"{issue_number}"
                    ),

                "page":
                    page_number,

                "context":
                    {
                        "card":
                            card,

                        "issue_number":
                            issue_number,
                    },
            }
        )


    # ==================================================
    # PAGE 8
    # Insight
    # ==================================================

    insight_context = (
        pages.get(
            "insight",
            {},
        )
        or {}
    )


    page_defs.append(
        {
            "template":
                "insight.html",

            "output_name":
                "insight",

            "page":
                8,

            "context":
                insight_context,
        }
    )


    # ==================================================
    # PAGE 9
    # Ending
    # ==================================================

    ending_context = (
        pages.get(
            "ending",
            {},
        )
        or {}
    )


    page_defs.append(
        {
            "template":
                "ending.html",

            "output_name":
                "ending",

            "page":
                9,

            "context":
                ending_context,
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
    # 9. Render Shorts Cards
    # ==================================================

    print()
    print("====================================")
    print("Rendering Shorts Cards")
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
    # 10. Build Narration Scripts
    # ==================================================

    print()
    print("====================================")
    print("Preparing Narration")
    print("====================================")
    print()


    narration_scripts = (
        build_narration_scripts(
            today=today,
            pages=pages,
        )
    )


    # ==================================================
    # 11. Generate TTS
    # ==================================================

    generate_narration(
        narration_scripts=(
            narration_scripts
        ),

        output_dir=(
            narration_output
        ),
    )


    # ==================================================
    # 12. Build Shorts Video
    # ==================================================

    print()
    print("====================================")
    print("Building Shorts Video")
    print("====================================")
    print()


    short_video_path = (
        shorts_root
        / (
            f"ap_daily_short_"
            f"{date}.mp4"
        )
    )


    try:

        build_daily_short(
            date=date,

            source_dir=(
                shorts_cards_output
            ),

            output_path=(
                short_video_path
            ),

            scripts=(
                narration_scripts
            ),
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
            "AP Daily card/TTS "
            "pipeline will continue."
        )


    # ==================================================
    # Complete
    # ==================================================

    print()
    print("====================================")
    print("AP Daily Complete")
    print("====================================")
    print()


    print(
        f"Cards     : "
        f"{cards_output}"
    )


    print(
        f"Shorts    : "
        f"{shorts_root}"
    )


    print(
        f"Narration : "
        f"{narration_output}"
    )


    print(
        f"Video     : "
        f"{short_video_path}"
    )


    print()


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":
    main()