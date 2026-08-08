from pathlib import Path
from datetime import datetime, timezone, timedelta
import json

from app.models.news import News


KST = timezone(
    timedelta(hours=9)
)


def save_raw_news(
    news: list[News],
    *,
    output_root: Path,
    rss_url: str | None = None,
):
    now = datetime.now(KST)
    date_text = now.strftime("%Y-%m-%d")

    output_dir = (
        output_root
        / date_text
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    articles = [
        item.model_dump(mode="json")
        for item in news
    ]

    payload = {
        "schema_version": "1.0",
        "date": date_text,
        "collected_at": now.isoformat(),
        "collector": "google_news_rss",
        "query": "부동산",
        "rss_url": rss_url,
        "count": len(articles),
        "articles": articles,
    }

    output_path = (
        output_dir
        / "raw.json"
    )

    output_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"✅ RAW data saved: {output_path}"
    )

    return output_path


def save_curated(
    pages: dict,
    *,
    output_root: Path,
):
    now = datetime.now(KST)
    date_text = now.strftime("%Y-%m-%d")

    output_dir = (
        output_root
        / date_text
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "schema_version": "1.0",
        "date": date_text,
        "generated_at": now.isoformat(),
        "pages": pages,
    }

    output_path = (
        output_dir
        / "curated.json"
    )

    output_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(
        f"✅ Curated data saved: {output_path}"
    )

    return output_path