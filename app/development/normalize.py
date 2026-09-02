import re
from app.collector.development.config import (
    INCLUDE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
    ALLOW_TENDER_KEYWORDS,
)

REGION_PATTERNS = [
    ("서울특별시", "서울"),
    ("부산광역시", "부산"),
    ("대구광역시", "대구"),
    ("인천광역시", "인천"),
    ("광주광역시", "광주"),
    ("전남광주통합특별시", "광주"),
    ("대전광역시", "대전"),
    ("울산광역시", "울산"),
    ("세종특별자치시", "세종"),
    ("경기도", "경기"),
    ("강원특별자치도", "강원"),
    ("충청북도", "충북"),
    ("충청남도", "충남"),
    ("전북특별자치도", "전북"),
    ("전라남도", "전남"),
    ("경상북도", "경북"),
    ("경상남도", "경남"),
    ("제주특별자치도", "제주"),
]

SHORT_REGION_PATTERNS = [
    ("서울", "서울"), ("부산", "부산"), ("대구", "대구"), ("인천", "인천"),
    ("광주", "광주"), ("대전", "대전"), ("울산", "울산"), ("세종", "세종"),
    ("경기", "경기"), ("강원", "강원"), ("충북", "충북"), ("충남", "충남"),
    ("전북", "전북"), ("전남", "전남"), ("경북", "경북"), ("경남", "경남"),
    ("제주", "제주"),
]


def compact(text):
    return re.sub(r"[\s()·:/\-]", "", text or "")


def classification_text(item):
    # 중요: 사이트 전체 text를 분류에 사용하지 않습니다.
    # 메뉴, 푸터, 지역 선택 박스 때문에 오탐이 발생하기 때문입니다.
    return " ".join(
        str(item.get(k, "") or "")
        for k in ["title", "agency", "notice_no"]
    )


def detect_region(item):
    agency = str(item.get("agency", "") or "")
    title = str(item.get("title", "") or "")

    # 기관명을 가장 신뢰
    for needle, region in REGION_PATTERNS:
        if needle in agency:
            return region

    for needle, region in SHORT_REGION_PATTERNS:
        if needle in agency:
            return region

    # 기관명에서 못 찾았을 때 제목만 보조적으로 사용
    for needle, region in REGION_PATTERNS:
        if needle in title:
            return region

    if item.get("source") == "국토교통부":
        return "전국"

    if item.get("source") == "서울시 정비사업 정보몽땅":
        return "서울"

    return ""


def detect_type(item):
    title = compact(item.get("title", ""))

    if "재건축" in title:
        return "재건축"
    if "재개발" in title or "재정비촉진" in title:
        return "재개발"
    if "가로주택정비" in title or "소규모주택정비" in title:
        return "소규모정비"
    if "주택건설사업계획" in title:
        return "신축/주택건설"
    if "청약" in title or "분양" in title:
        return "분양/청약"
    if (
        "주택공급" in title
        or "공공주택" in title
        or "노후계획도시" in title
        or "쪽방정비사업" in title
    ):
        return "주택정책"
    return "정비사업"


def detect_stage(item):
    title = compact(item.get("title", ""))

    if "관리처분" in title and "인가" in title:
        return "관리처분인가"
    if "사업시행계획인가" in title or "사업시행인가" in title:
        return "사업시행인가"
    if "조합설립인가" in title:
        return "조합설립인가"
    if "정비구역" in title and ("지정" in title or "결정" in title):
        return "정비구역 지정"
    if "주택건설사업계획" in title and "승인" in title:
        return "사업계획 승인"
    if "분양" in title or "청약" in title:
        return "분양/청약"
    if (
        "주택공급" in title
        or "공공주택" in title
        or "노후계획도시" in title
        or "쪽방정비사업" in title
    ):
        return "정책 변화"
    if "시공자" in title and "선정" in title:
        return "시공자 선정"
    if "조합설립" in title:
        return "조합설립 단계"
    return "사업 업데이트"


def is_relevant(item):
    title = str(item.get("title", "") or "")

    if any(keyword in title for keyword in EXCLUDE_TITLE_KEYWORDS):
        return False

    if ("입찰" in title or "용역" in title) and not any(
        keyword in title for keyword in ALLOW_TENDER_KEYWORDS
    ):
        return False

    return any(keyword in title for keyword in INCLUDE_KEYWORDS)


def score(item):
    title = compact(item.get("title", ""))
    s = 0
    reasons = []

    if "관리처분" in title and "인가" in title:
        s += 7
        reasons.append("관리처분인가 +7")
    elif "사업시행계획인가" in title or "사업시행인가" in title:
        s += 6
        reasons.append("사업시행인가 +6")
    elif "정비구역" in title and ("지정" in title or "결정" in title):
        s += 6
        reasons.append("정비구역 지정 +6")
    elif "조합설립인가" in title:
        s += 5
        reasons.append("조합설립인가 +5")
    elif "주택건설사업계획" in title and "승인" in title:
        s += 4
        reasons.append("주택건설사업계획 승인 +4")
    elif "시공자" in title and "선정" in title:
        s += 4
        reasons.append("시공자 선정 +4")
    elif (
        "주택공급" in title
        or "공공주택" in title
        or "노후계획도시" in title
        or "쪽방정비사업" in title
    ):
        s += 4
        reasons.append("주택정책/공급 변화 +4")
    elif "재개발" in title or "재건축" in title or "재정비촉진" in title:
        s += 3
        reasons.append("정비사업 직접 관련 +3")
    else:
        s += 1
        reasons.append("관련 공식자료 +1")

    # 변경 자체를 과도하게 깎지 않되 신규보다 우선순위는 낮춤
    if "변경" in title:
        s -= 1
        reasons.append("변경 -1")

    if item.get("source") == "국토교통부":
        s += 1
        reasons.append("중앙정부 정책 +1")

    return s, reasons


def normalize_items(items):
    out = []
    rejected = []

    for item in items:
        if item.get("error"):
            rejected.append({**item, "reject_reason": "collector_error"})
            continue

        if not is_relevant(item):
            rejected.append({**item, "reject_reason": "title_not_relevant"})
            continue

        sc, reasons = score(item)

        normalized = {
            **item,
            "region": detect_region(item),
            "type": detect_type(item),
            "stage": detect_stage(item),
            "score": sc,
            "score_reasons": reasons,
            "source_display": " · ".join(
                x for x in [item.get("source", ""), item.get("agency", "")]
                if x
            ),
        }
        out.append(normalized)

    out.sort(key=lambda x: (x.get("score", 0), x.get("date", "")), reverse=True)
    return out, rejected
