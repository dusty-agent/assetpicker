import re
from bs4 import BeautifulSoup

from .config import (
    MOLIT_PRESS_URL,
    INCLUDE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
)
from .common import BaseCollector


class MolitCollector(BaseCollector):
    source_name = "국토교통부"

    def _is_candidate(self, title, field):
        if not title:
            return False
        if title.startswith("[장관동정]") or title.startswith("[차관동정]"):
            return False
        if any(k in title for k in EXCLUDE_TITLE_KEYWORDS):
            return False

        # 주택토지/국토도시 분야를 우선 대상으로 보고,
        # 제목 자체에도 관련 키워드가 있는 경우만 채택
        if field not in {"주택토지", "국토도시", "일반"}:
            return False

        return any(k in title for k in INCLUDE_KEYWORDS)

    def collect(self, max_items=20):
        soup = BeautifulSoup(self.get(MOLIT_PRESS_URL).text, "lxml")
        out = []
        seen = set()

        date_re = re.compile(r"20\d{2}-\d{2}-\d{2}")

        for tr in soup.find_all("tr"):
            cells = [
                self.clean(td.get_text(" ", strip=True))
                for td in tr.find_all(["td", "th"])
            ]

            # 번호 | 제목 | 분야 | 등록일 | 조회
            if len(cells) < 4:
                continue

            date_idx = None
            for i, cell in enumerate(cells):
                if date_re.fullmatch(cell):
                    date_idx = i
                    break

            if date_idx is None or date_idx < 2:
                continue

            date = cells[date_idx]
            field = cells[date_idx - 1]
            title = cells[date_idx - 2]

            # 제목 셀 안에 링크가 있으면 상세 URL 보존
            links = tr.find_all("a", href=True)
            href = ""
            for a in links:
                if self.clean(a.get_text(" ", strip=True)) == title:
                    href = a.get("href", "")
                    break

            if not self._is_candidate(title, field):
                continue

            key = (title, date)
            if key in seen:
                continue
            seen.add(key)

            url = self.abs_url(MOLIT_PRESS_URL, href) if href else MOLIT_PRESS_URL

            out.append({
                "source": self.source_name,
                "source_type": "official_release",
                "category_hint": "주택정책/공급정책",
                "title": title,
                "date": date,
                "agency": "국토교통부",
                "notice_no": "",
                "field": field,
                "url": url,
                "text": title,
            })

            if len(out) >= max_items:
                break

        return out
