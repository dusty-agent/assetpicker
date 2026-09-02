import re
from bs4 import BeautifulSoup

from .config import (
    SEOUL_CLEANUP_URL,
    INCLUDE_KEYWORDS,
    SEOUL_EXACT_NAV_LABELS,
    EXCLUDE_TITLE_KEYWORDS,
    ALLOW_TENDER_KEYWORDS,
)
from .common import BaseCollector


class SeoulCleanupCollector(BaseCollector):
    source_name = "서울시 정비사업 정보몽땅"

    def _is_candidate(self, title):
        if not title:
            return False

        title = self.clean(title)

        if title in SEOUL_EXACT_NAV_LABELS:
            return False

        if len(title) < 12:
            return False

        if any(k in title for k in EXCLUDE_TITLE_KEYWORDS):
            return False

        # 일반 입찰/용역은 제외하되 시공자 선정 관련은 허용
        if ("입찰" in title or "용역" in title) and not any(
            k in title for k in ALLOW_TENDER_KEYWORDS
        ):
            return False

        return any(k in title for k in INCLUDE_KEYWORDS)

    def _clean_notice_title(self, raw_title):
        raw_title = self.clean(raw_title)

        # 정보몽땅 홈에서는 제목 뒤에 사업장명/공고일자/입찰마감일이 이어질 수 있음
        business_name = ""
        m = re.search(
            r"사업장명\s*:\s*(.*?)\s*(?:공고일자|입찰마감일|20\d{2}[.\-/]\d{1,2}[.\-/]\d{1,2})",
            raw_title,
        )
        if m:
            business_name = self.clean(m.group(1)).strip(" -·:")

        headline = re.split(r"\s*사업장명\s*:", raw_title, maxsplit=1)[0].strip()

        # '시공자 선정 재입찰공고'처럼 제목이 너무 일반적이면 사업장명을 앞에 붙임
        generic_heads = {
            "시공자 선정 입찰 공고",
            "시공자 선정 재입찰공고",
            "시공자 선정 재공고",
            "시공자 선정 입찰 재공고",
            "시공자 선정",
        }
        if business_name and (
            headline in generic_heads
            or len(headline) < 18
        ):
            headline = f"{business_name} {headline}"

        return self.clean(headline), business_name

    def collect(self, max_items=20):
        soup = BeautifulSoup(self.get(SEOUL_CLEANUP_URL).text, "lxml")

        out = []
        seen = set()
        date_re = re.compile(r"20\d{2}[.\-/]\d{1,2}[.\-/]\d{1,2}")

        for a in soup.find_all("a"):
            raw_title = self.clean(a.get_text(" ", strip=True))
            title, business_name = self._clean_notice_title(raw_title)
            if not self._is_candidate(title):
                continue

            href = a.get("href") or ""
            onclick = a.get("onclick") or ""
            if not href and not onclick:
                continue

            parent = a
            parent_text = title
            date = ""

            # 링크 부모 몇 단계에서 날짜를 찾음
            for _ in range(5):
                if not parent:
                    break
                parent_text = self.clean(parent.get_text(" ", strip=True))
                m = date_re.search(parent_text)
                if m:
                    date = re.sub(r"[./]", "-", m.group(0))
                    break
                parent = parent.parent

            # 홈 화면의 상시 안내/배너 문구는 날짜가 없는 경우가 많음.
            # 데일리 업데이트에는 "실제 날짜가 확인되는 게시물"만 채택.
            if not date:
                continue

            key = (title, date)
            if key in seen:
                continue
            seen.add(key)

            url = (
                self.abs_url(SEOUL_CLEANUP_URL, href)
                if href and not href.lower().startswith("javascript")
                else SEOUL_CLEANUP_URL
            )

            out.append({
                "source": self.source_name,
                "source_type": "official_notice",
                "category_hint": "서울 정비사업",
                "board": "",
                "title": title,
                "project_name": business_name,
                "date": date,
                "agency": "서울특별시",
                "notice_no": "",
                "url": url,
                "text": parent_text,
            })

            if len(out) >= max_items:
                break

        return out
