import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.collector.development.eum import EumCollector
from app.collector.development.seoul_cleanup import SeoulCleanupCollector
from app.collector.development.molit import MolitCollector

from app.daily.renderer.render_html import render_html
from app.daily.renderer.render_png import render_png
from app.daily.shorts.tts import generate_tts
from app.development.shorts.builder import build_development_short

from .normalize import normalize_items
from .selector import select_top, dedupe_polished
from .generator import generate_editorial
from .storyboard import build_storyboard
from .config import (
    DATA_ROOT,
    OUTPUT_ROOT,
    MAX_ITEMS,
    TOP_N,
    MIN_SCORE,
    DAILY_ASSET_DIR,
    DEVELOPMENT_ASSET_DIR,
)

KST = timezone(timedelta(hours=9))

APP_DIR = Path(__file__).resolve().parents[1]
DEV_DIR = Path(__file__).resolve().parent

CARDS_TEMPLATES = DEV_DIR / "cards" / "templates"
SHORTS_TEMPLATES = DEV_DIR / "shorts" / "templates"

# ==================================================
# Development TTS Settings
# ==================================================

DEVELOPMENT_VOICE = "cedar"

DEVELOPMENT_TTS_SPEED = 1.15

DEVELOPMENT_TTS_INSTRUCTIONS = (
    "20~30대의 차분하고 자연스러운 "
    "한국어 남성 진행자처럼 읽는다. "
    "전문적이고 신뢰감 있는 느낌으로 전달한다. "
    "지나치게 무겁거나 권위적인 뉴스 앵커 톤은 피한다. "
    "부동산 개발과 정비사업 정보를 설명하는 "
    "세련된 브리핑 진행자처럼 읽는다. "
    "문장 사이의 쉼은 짧고 자연스럽게 한다. "
    "지역명과 사업명, 행정 용어를 또렷하게 발음한다."
)


def dump(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def clean_narration_text(text: str) -> str:
    text = (text or "").replace("\n", " ").replace("\r", " ").strip()
    return re.sub(r"\s+", " ", text)


def get_first_sentence(text: str) -> str:
    text = clean_narration_text(text)
    if not text:
        return ""
    match = re.match(r"^(.+?[.!?])(?:\s|$)", text)
    return match.group(1).strip() if match else text


def join_title_summary(title: str, summary: str) -> str:
    title = clean_narration_text(title)
    summary = clean_narration_text(summary)
    parts = []

    if title:
        if title[-1] not in ".!?":
            title += "."
        parts.append(title)

    if summary:
        if summary[-1] not in ".!?":
            summary += "."
        parts.append(summary)

    return " ".join(parts)


def run_collectors(max_items):
    collectors = [
        EumCollector(),
        SeoulCleanupCollector(),
        MolitCollector(),
    ]

    all_items = []
    status = []

    for col in collectors:
        try:
            items = col.collect(max_items=max_items)
            all_items.extend(items)
            status.append({
                "source": col.source_name,
                "count": len(items),
                "ok": True,
            })
        except Exception as e:
            status.append({
                "source": col.source_name,
                "count": 0,
                "ok": False,
                "error": str(e),
            })

    return all_items, status


def render_pages(*, storyboard, output_dir: Path, today_text: str):
    pages = storyboard.get("pages", [])
    total = len(pages)

    cards_output = output_dir / "cards"
    shorts_root = output_dir / "shorts"
    shorts_cards_output = shorts_root / "card_shorts"

    cards_output.mkdir(parents=True, exist_ok=True)
    shorts_cards_output.mkdir(parents=True, exist_ok=True)

    common = {
        "today": today_text,
        "date_text": today_text,
        "total": total,
    }

    issue_number = 0

    print()
    print("====================================")
    print("Rendering Development Cards")
    print("====================================")

    for page_obj in pages:
        kind = page_obj.get("kind", "")
        page_no = page_obj.get("page_number", 1)

        if kind == "issue":
            issue_number += 1

            summary = (
                page_obj.get(
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

            page_obj["summary_first"] = (
                summary_first
            )

            page_obj["summary_rest"] = (
                summary_rest
            )

        template_name = {
            "cover": "cover.html",
            "introduction": "introduction.html",
            "issue": "issue.html",
            "summary": "summary.html",
            "ending": "ending.html",
        }.get(kind)

        if not template_name:
            raise RuntimeError(f"지원하지 않는 page kind: {kind}")

        output_name = (
            f"issue_{issue_number}"
            if kind == "issue"
            else kind
        )

        context = {
            **common,
            "page": page_no,
            "card": page_obj,
            "issue_number": issue_number if kind == "issue" else None,
            "shared_asset_path": DAILY_ASSET_DIR.resolve().as_uri(),
            "development_asset_path": DEVELOPMENT_ASSET_DIR.resolve().as_uri(),
            **page_obj,
        }

        # 1080 x 1350 card
        html = render_html(
            template_name,
            context,
            CARDS_TEMPLATES,
        )
        html_path = cards_output / f"{output_name}.html"
        png_path = cards_output / f"{output_name}.png"
        html_path.write_text(html, encoding="utf-8")
        render_png(
            html_path,
            png_path,
            width=1080,
            height=1350,
        )
        print(f"✅ CARD   {page_no}/{total}  {png_path.name}")

        # 1080 x 1920 shorts card
        html = render_html(
            template_name,
            context,
            SHORTS_TEMPLATES,
        )
        html_path = shorts_cards_output / f"{output_name}.html"
        png_path = shorts_cards_output / f"{output_name}.png"
        html_path.write_text(html, encoding="utf-8")
        render_png(
            html_path,
            png_path,
            width=1080,
            height=1920,
        )
        print(f"✅ SHORTS {page_no}/{total}  {png_path.name}")

    return cards_output, shorts_root, shorts_cards_output


def build_narration_scripts(*, storyboard, today: datetime):
    pages = storyboard.get("pages", [])
    issues = [p for p in pages if p.get("kind") == "issue"]
    summary_page = next(
        (p for p in pages if p.get("kind") == "summary"),
        {},
    )

    scripts = {
        "opening": (
            f"{today.month}월 {today.day}일, "
            "오늘의 정비사업과 주택개발 공식 업데이트를 전해드립니다."
        )
    }

    for i, issue in enumerate(issues, start=1):
        title = issue.get("title", "")
        summary = issue.get("summary", "")
        scripts[f"issue_{i}"] = join_title_summary(
            title,
            get_first_sentence(summary),
        )

    summary_text = (
        summary_page.get("summary")
        or summary_page.get("body")
        or "오늘 확인된 주요 정비사업과 주택개발 변화를 정리했습니다."
    )
    scripts["summary"] = clean_narration_text(summary_text)

    scripts["ending"] = (
        "내일도 새로운 정비사업 변화를 전해드립니다. "
        "좋아요, 구독, 알림 설정 부탁드립니다."
    )
    for name, script in scripts.items():
        if not script.strip():
            raise RuntimeError(f"나레이션 대본이 비어 있습니다: {name}")

    return scripts


def generate_narration(*, scripts, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    print()
    print("====================================")
    print("Development Narration Scripts")
    print("====================================")

    for name, script in scripts.items():
        print(f"[{name}]")
        print(script)
        print()

    print("====================================")
    print("Generating TTS Narration")
    print("====================================")

    for name, script in scripts.items():
        generate_tts(
            script,
            output_dir / f"{name}.mp3",
            voice=DEVELOPMENT_VOICE,
            instructions=DEVELOPMENT_TTS_INSTRUCTIONS,
            speed=DEVELOPMENT_TTS_SPEED,
        )

    print("✅ TTS narration created")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-items", type=int, default=MAX_ITEMS)
    parser.add_argument("--top", type=int, default=TOP_N)
    parser.add_argument("--no-ai", action="store_true")
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--no-tts", action="store_true")
    parser.add_argument("--no-video", action="store_true")
    args = parser.parse_args()

    today = datetime.now(KST)
    run_date = today.strftime("%Y-%m-%d")
    today_text = f"{today.year}년 {today.month}월 {today.day}일"

    data_dir = DATA_ROOT / run_date
    output_dir = OUTPUT_ROOT / run_date

    raw, status = run_collectors(args.max_items)
    normalized, rejected = normalize_items(raw)
    # 중복 제거 후에도 최종 TOP N을 채울 수 있도록
    # 우선 후보를 넉넉하게 확보합니다.
    candidate_limit = max(
        args.top * 2,
        args.top,
    )

    candidates = select_top(
        normalized,
        max_items=candidate_limit,
        min_score=MIN_SCORE,
    )

    editorial = generate_editorial(
        candidates,
        use_ai=not args.no_ai,
    )

    polished_candidates = (
        editorial.get("cards")
        or []
    )

    # OpenAI 편집 결과까지 포함해 한 번 더 중복 제거 후
    # 최종 TOP N을 확정합니다.
    polished = (
        dedupe_polished(
            polished_candidates
        )
        [:args.top]
    )

    selected = polished

    development_insight = (
        editorial.get("insight")
        or {}
    )

    # 오늘 의미 있는 항목이 0개면 억지로 콘텐츠를 만들지 않음
    if not polished:
        dump(data_dir / "source_status.json", status)
        dump(data_dir / "raw.json", raw)
        dump(data_dir / "normalized.json", normalized)
        dump(data_dir / "rejected.json", rejected)
        dump(data_dir / "selected.json", selected)

        print("=" * 70)
        print("AssetPicker Development Update")
        print("=" * 70)
        print("오늘 선정할 의미 있는 공식 업데이트가 없습니다.")
        print("콘텐츠 생성을 건너뜁니다.")
        return

    storyboard = build_storyboard(
        polished,
        insight=development_insight,
        source_status=status,
    )

    dump(data_dir / "source_status.json", status)
    dump(data_dir / "raw.json", raw)
    dump(data_dir / "normalized.json", normalized)
    dump(data_dir / "rejected.json", rejected)
    dump(data_dir / "candidates.json", candidates)
    dump(data_dir / "selected.json", selected)
    dump(data_dir / "selected_polished.json", polished)
    dump(data_dir / "insight.json", development_insight)
    dump(output_dir / "storyboard.json", storyboard)

    print("=" * 70)
    print("AssetPicker Development Update")
    print("=" * 70)

    for s in status:
        msg = f"[{'OK' if s['ok'] else 'ER'}] {s['source']}: {s['count']}건"
        if not s["ok"]:
            msg += f" / {s.get('error', '')}"
        print(msg)

    print("-" * 70)
    print(f"수집 전체: {len(raw)}건")
    print(f"관련 판정: {len(normalized)}건")
    print(f"제외     : {len(rejected)}건")
    print(f"AI 후보  : {len(candidates)}건")
    print(f"최종 선정: {len(selected)}건")

    if args.no_ai:
        ai_label = "OFF"
    elif polished and all(x.get("_ai_applied") for x in polished):
        ai_label = "APPLIED"
    else:
        ai_label = "FALLBACK"

    print(f"OpenAI   : {ai_label}")
    print("-" * 70)

    for idx, item in enumerate(polished, 1):
        title = item.get("display_title") or item.get("title") or ""
        print(
            f"{idx}. [{item.get('source', '')}] "
            f"{title} | "
            f"{item.get('region', '')} | "
            f"{item.get('type', '')} | "
            f"{item.get('stage', '')} | "
            f"score={item.get('score', 0)}"
        )

    if not args.no_render:
        cards_output, shorts_root, shorts_cards_output = render_pages(
            storyboard=storyboard,
            output_dir=output_dir,
            today_text=today_text,
        )
    else:
        cards_output = output_dir / "cards"
        shorts_root = output_dir / "shorts"
        shorts_cards_output = shorts_root / "card_shorts"

    if not args.no_tts:
        narration_output = shorts_root / "narration"
        scripts = build_narration_scripts(
            storyboard=storyboard,
            today=today,
        )
        generate_narration(
            scripts=scripts,
            output_dir=narration_output,
        )
    else:
        narration_output = shorts_root / "narration"

    # ==================================================
    # Build Development Shorts MP4
    # ==================================================

    short_video_path = (
        shorts_root
        / f"development_update_{run_date}.mp4"
    )

    if not args.no_video:
        if args.no_render:
            print(
                "[VIDEO SKIP] --no-render 사용 시 "
                "새 쇼츠 PNG가 생성되지 않으므로 "
                "영상 합성을 건너뜁니다."
            )
        elif args.no_tts:
            print(
                "[VIDEO SKIP] --no-tts 사용 시 "
                "나레이션이 없으므로 "
                "영상 합성을 건너뜁니다."
            )
        else:
            print()
            print("====================================")
            print("Building Development Shorts Video")
            print("====================================")
            print()

            try:
                build_development_short(
                    date=run_date,
                    source_dir=shorts_cards_output,
                    output_path=short_video_path,
                    issue_count=len(polished),
                    scripts=scripts,
                )

                print(
                    "✅ Development Shorts video created"
                )
                print(
                    short_video_path
                )

            except Exception as exc:
                print()
                print(
                    "⚠️ Development Shorts video build failed."
                )
                print(
                    exc
                )
    else:
        print(
            "[VIDEO] OFF (--no-video)"
        )

    print()
    print("====================================")
    print("Development Update Complete")
    print("====================================")
    print(f"Data       : {data_dir}")
    print(f"Storyboard : {output_dir / 'storyboard.json'}")
    print(f"Cards      : {cards_output}")
    print(f"Short Cards: {shorts_cards_output}")
    print(f"Narration  : {narration_output}")
    print(f"Video      : {short_video_path}")


if __name__ == "__main__":
    main()
