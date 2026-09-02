import re


# ==================================================
# Normalize helper
# ==================================================

def _norm(value) -> str:
    """
    중복 비교용 문자열 정리.
    실제 item 값은 변경하지 않습니다.
    """
    return re.sub(
        r"[^0-9A-Za-z가-힣]",
        "",
        str(value or ""),
    ).lower()


# ==================================================
# Raw / normalized item dedupe
# ==================================================

def dedupe(items):
    """
    기존 selector의 score/date 선택 로직은 건드리지 않고
    중복 제거만 강화합니다.

    1) source + notice_no + title 동일
    2) notice_no가 달라도
       source/date/region/type/stage/title이 같고
       project_name/location 구분 정보가 없으면 동일 이벤트로 처리
    3) project_name/location이 실제로 서로 다르면 별도 사건으로 유지
    """

    seen_exact = set()
    seen_event = set()

    out = []

    for item in items:

        source = _norm(
            item.get("source")
        )

        notice_no = _norm(
            item.get("notice_no")
        )

        title = _norm(
            item.get("title")
        )

        date = _norm(
            item.get("date")
        )

        region = _norm(
            item.get("region")
        )

        item_type = _norm(
            item.get("type")
        )

        stage = _norm(
            item.get("stage")
        )

        project_name = _norm(
            item.get("project_name")
        )

        location = _norm(
            item.get("location")
        )


        # ------------------------------------------
        # 1. 기존 방식 유지
        # ------------------------------------------

        exact_key = (
            source,
            notice_no,
            title,
        )

        if exact_key in seen_exact:
            continue


        # ------------------------------------------
        # 2. 실질적으로 동일한 이벤트
        # ------------------------------------------
        #
        # project_name/location이 있으면
        # 그 값까지 포함하여 서로 다른 사업을 살립니다.
        #
        # 둘 다 없으면
        # 동일 출처·날짜·지역·유형·단계·제목은
        # 카드뉴스 관점에서 같은 이벤트로 봅니다.
        # ------------------------------------------

        if project_name or location:

            event_key = (
                source,
                date,
                region,
                item_type,
                stage,
                title,
                project_name,
                location,
            )

        else:

            event_key = (
                source,
                date,
                region,
                item_type,
                stage,
                title,
                "",
                "",
            )


        if event_key in seen_event:
            continue


        seen_exact.add(
            exact_key
        )

        seen_event.add(
            event_key
        )

        out.append(
            item
        )


    return out


# ==================================================
# Selection
# ==================================================

def select_top(
    items,
    max_items=5,
    min_score=1,
):
    """
    기존 동작 보존.

    - score는 normalize 단계에서 이미 계산된 값을 그대로 사용
    - 날짜 확인되는 자료만 사용
    - 최신 날짜 우선
    - 동일 날짜면 score 높은 순
    """

    items = dedupe(
        items
    )

    selected = [

        x

        for x in items

        if (
            x.get(
                "score",
                0,
            )
            >= min_score
        )

        and x.get(
            "date"
        )
    ]


    selected.sort(

        key=lambda x: (

            x.get(
                "date",
                "",
            ),

            x.get(
                "score",
                0,
            ),
        ),

        reverse=True,
    )


    return selected[
        :max_items
    ]


# ==================================================
# Post-AI dedupe
# ==================================================

def dedupe_polished(items):
    """
    OpenAI 편집 뒤 최종 안전망.

    display_title + display_summary가 완전히 같으면
    한 장만 남깁니다.

    단, 제목만 같은 경우에는 삭제하지 않습니다.
    서로 다른 사업인데 제목이 우연히 같을 수 있기 때문입니다.
    """

    seen = set()
    out = []

    for item in items:

        title = _norm(
            item.get(
                "display_title"
            )
            or item.get(
                "title"
            )
        )

        summary = _norm(
            item.get(
                "display_summary"
            )
            or ""
        )


        # AI를 사용하지 않은 경우 summary가 비어 있을 수 있으므로
        # title만으로 공격적으로 제거하지 않습니다.
        if not summary:

            out.append(
                item
            )

            continue


        key = (
            title,
            summary,
        )


        if key in seen:
            continue


        seen.add(
            key
        )

        out.append(
            item
        )


    return out
