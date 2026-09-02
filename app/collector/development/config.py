from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"

REQUEST_TIMEOUT = 20
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.7",
}

EUM_LIST_URL = "https://www.eum.go.kr/web/gs/gv/gvGosiList.jsp?silsi_yn=Y"
EUM_DETAIL_URL = "https://www.eum.go.kr/web/gs/gv/gvGosiDet.jsp"
SEOUL_CLEANUP_URL = "https://cleanup.seoul.go.kr/cleanup/mainPage.do"
MOLIT_EBOOK_URL = "https://molit.go.kr/ebook/"
MOLIT_PRESS_URL = "https://www.molit.go.kr/USR/NEWS/m_71/lst.jsp?cate=1"

# 제목 자체에 아래 내용이 있을 때만 우선 수집 대상으로 인정합니다.
# 사이트 메뉴/푸터의 단어가 본문 text에 섞여 오판하는 것을 막기 위해
# relevance 판정은 title 중심으로 수행합니다.
INCLUDE_KEYWORDS = [
    "재개발",
    "재건축",
    "재정비촉진",
    "정비구역",
    "정비계획",
    "가로주택정비",
    "소규모재건축",
    "소규모주택정비",
    "주택건설사업계획",
    "공공주택",
    "주택공급",
    "주택 공급",
    "노후계획도시",
    "도심 공공주택",
    "도심공공주택",
    "쪽방 정비사업",
    "청약",
    "분양",
]

SEOUL_EXACT_NAV_LABELS = {
    "민간재개발·재건축",
    "공공재개발·재건축",
    "재개발·재건축",
    "고시/공고",
    "조합입찰공고",
    "공지사항",
    "자료실",
    "이용안내",
}

MOLIT_LABELS = {
    "보도자료",
    "정책자료",
    "홍보자료",
    "보도자료 정책자료",
    "보도자료 홍보자료",
    "정책자료 홍보자료",
    "보도자료 정책자료 홍보자료",
}


# 콘텐츠성 낮은 운영/채용/단순 용역 공고는 데일리 핵심 업데이트에서 제외
EXCLUDE_TITLE_KEYWORDS = [
    "채용",
    "임시직원",
    "직원채용",
    "홍보요원",
    "선거인명부",
    "후보자 등록",
    "예비임원",
    "예비추진위원장",
    "예비감사",
    "교육",
    "아카데미",
    "원가자문",
    "홈페이지 이용",
]

# 시공자 선정은 사업 단계상 의미가 있으므로 입찰 중에서도 예외적으로 허용
ALLOW_TENDER_KEYWORDS = [
    "시공자 선정",
    "시공자선정",
    "시공자 입찰",
    "시공자입찰",
]
