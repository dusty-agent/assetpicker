from datetime import datetime


def build_update_card(item):
    title = (
        item.get("display_title")
        or item.get("title", "")
    )

    summary = (
        item.get("display_summary")
        or item.get("title", "")
    )

    tags = (
        item.get("display_tags")
        or [
            x
            for x in [
                item.get("region") or "전국",
                item.get("type"),
                item.get("stage"),
            ]
            if x
        ]
    )

    source = (
        item.get("source_display")
        or item.get("source")
        or ""
    )

    return {
        "kind": "issue",
        "title": title,
        "tags": tags[:3],
        "summary": summary,
        "sources": [source] if source else [],
        "source": source,
        "agency": item.get("agency", ""),
        "notice_no": item.get("notice_no", ""),
        "source_url": item.get("url", ""),
        "project_name": item.get("project_name", ""),
        "location": item.get("location", ""),
        "score": item.get("score", 0),
    }


def build_storyboard(
    selected_items,
    *,
    insight=None,
    source_status=None,
):
    today = datetime.now().strftime(
        "%Y.%m.%d"
    )

    # ----------------------------------------------
    # Introduction source list
    # 실제 수집에 성공한 collector만 노출
    # ----------------------------------------------
    sources_used = []

    for row in (
        source_status
        or []
    ):
        if not row.get("ok"):
            continue

        source = (
            row.get("source")
            or ""
        ).strip()

        if (
            source
            and source not in sources_used
        ):
            sources_used.append(source)

    # source_status가 없는 과거 호출 호환
    if not sources_used:
        for item in selected_items:
            source = (
                item.get("source")
                or ""
            ).strip()

            if (
                source
                and source not in sources_used
            ):
                sources_used.append(source)

    updates = [
        build_update_card(x)
        for x in selected_items
    ]

    insight = insight or {}

    insight_keyword = (
        insight.get("keyword")
        or "오늘의 변화"
    )

    insight_summary = (
        insight.get("summary")
        or "오늘 선택된 공식자료의 공통 흐름을 확인합니다."
    )

    insight_reason = (
        insight.get("reason")
        or ""
    )

    total_pages = (
        len(updates)
        + 4
    )

    pages = [
        {
            "kind": "cover",
            "title": "오늘의 정비사업 업데이트",
            "subtitle": "재개발 · 재건축 · 신축 · 정책 변화",
            "date_label": today,
        },
        {
            "kind": "introduction",
            "title": "OFFICIAL DATA SOURCES",
            "subtitle": "오늘 확인한 공식 개발·정비사업 자료",
            "sources": sources_used,
            "note": (
                "공식기관의 신규 고시와 변경사항을 "
                "AssetPicker가 매일 선별합니다."
            ),
        },
        *updates,
        {
            "kind": "summary",
            "title": "TODAY'S DEVELOPMENT SUMMARY",
            "keyword": insight_keyword,
            "summary": insight_summary,
            "reason": insight_reason,
        },
        {
            "kind": "ending",
            "title": "전국 정비사업 변화",
            "subtitle": "내일도 빠르게 전해드립니다.",
            "closing": "AP Daily · Development Update",
        },
    ]

    for i, page in enumerate(
        pages,
        start=1,
    ):
        page["page_number"] = i
        page["total_pages"] = total_pages

    return {
        "report_type": "development_update",
        "skip_video": len(updates) == 0,
        "selected_count": len(updates),
        "sources_used": sources_used,
        "insight": insight,
        "pages": pages,
    }
