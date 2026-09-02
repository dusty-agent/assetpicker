import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

from .config import EUM_LIST_URL, EUM_DETAIL_URL
from .common import BaseCollector


class EumCollector(BaseCollector):
    source_name = "토지이음"

    @staticmethod
    def _extract_seq(href):
        if not href:
            return None
        try:
            qs = parse_qs(urlparse(href).query)
            if qs.get("seq"):
                return qs["seq"][0]
        except Exception:
            pass
        m = re.search(r"(?:seq=|seq['\"]?\s*[,=:]\s*['\"]?)(\d+)", href)
        return m.group(1) if m else None

    @staticmethod
    def _clean_title(title):
        title = title or ""
        title = re.sub(
            r"\s*-\s*고시번호,\s*담당기관,\s*고시일,\s*문의처,\s*열람장소,\s*첨부파일로\s*구성\s*$",
            "",
            title,
        )
        return title.strip()

    def fetch_list(self, max_items=60):
        soup = BeautifulSoup(self.get(EUM_LIST_URL).text, "lxml")
        items, seen = [], set()
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "gvGosiDet" not in href:
                continue
            seq = self._extract_seq(href)
            if not seq or seq in seen:
                continue
            items.append({
                "seq": seq,
                "title_hint": self._clean_title(self.clean(a.get_text(" ", strip=True))),
            })
            seen.add(seq)
            if len(items) >= max_items:
                break
        return items

    def fetch_detail(self, seq):
        soup = BeautifulSoup(self.get(EUM_DETAIL_URL, params={"seq": seq}).text, "lxml")
        full_text = self.clean(soup.get_text("\n", strip=True))

        title = ""
        for selector in ["h3", "h4", ".tit", ".title", "caption"]:
            node = soup.select_one(selector)
            if node:
                title = self._clean_title(self.clean(node.get_text(" ", strip=True)))
                if title and "고시정보" not in title:
                    break

        meta = {}
        for tr in soup.find_all("tr"):
            cells = [self.clean(x.get_text(" ", strip=True)) for x in tr.find_all(["th", "td"])]
            cells = [x for x in cells if x]
            if len(cells) >= 2:
                for i in range(0, len(cells) - 1, 2):
                    key = cells[i]
                    val = cells[i + 1]
                    if key in [
                        "고시번호", "담당기관", "고시일", "문의처", "열람장소",
                        "사업명", "사업의 명칭", "대지위치", "사업위치", "위치"
                    ]:
                        meta[key] = val

        # 페이지 본문에서 사업명/위치 힌트를 추가 추출.
        # 같은 '주택건설사업계획 승인' 고시가 여러 건일 때 카드 제목을 구분하기 위함.
        project_name = (
            meta.get("사업명")
            or meta.get("사업의 명칭")
            or ""
        )
        location = (
            meta.get("대지위치")
            or meta.get("사업위치")
            or meta.get("위치")
            or ""
        )

        if not project_name:
            patterns = [
                r"(?:사업명|사업의\s*명칭)\s*[:：]?\s*([^\n]{3,80})",
                r"(?:주택건설사업의\s*명칭)\s*[:：]?\s*([^\n]{3,80})",
            ]
            for pat in patterns:
                m = re.search(pat, full_text)
                if m:
                    candidate = self.clean(m.group(1))
                    candidate = re.split(
                        r"\s+(?:사업위치|대지위치|위치|사업주체|시행자|규모|세대수)\b",
                        candidate,
                        maxsplit=1,
                    )[0].strip(" -·")
                    if 3 <= len(candidate) <= 80:
                        project_name = candidate
                        break

        if not location:
            for pat in [
                r"(?:대지위치|사업위치|위치)\s*[:：]?\s*([^\n]{3,100})",
            ]:
                m = re.search(pat, full_text)
                if m:
                    candidate = self.clean(m.group(1))
                    candidate = re.split(
                        r"\s+(?:사업주체|시행자|규모|세대수|면적)\b",
                        candidate,
                        maxsplit=1,
                    )[0].strip(" -·")
                    if 3 <= len(candidate) <= 100:
                        location = candidate
                        break

        return {
            "source": self.source_name,
            "source_type": "official_notice",
            "category_hint": "정비사업/도시계획",
            "seq": str(seq),
            "title": title,
            "date": meta.get("고시일", ""),
            "agency": meta.get("담당기관", ""),
            "notice_no": meta.get("고시번호", ""),
            "project_name": project_name,
            "location": location,
            "url": f"{EUM_DETAIL_URL}?seq={seq}",
            "text": full_text,
        }

    def collect(self, max_items=60):
        out = []
        for item in self.fetch_list(max_items=max_items):
            try:
                detail = self.fetch_detail(item['seq'])
                if not detail.get('title'):
                    detail['title'] = item.get('title_hint', '')
                out.append(detail)
            except Exception as e:
                out.append({"source": self.source_name, "seq": item['seq'], "error": str(e)})
        return out
