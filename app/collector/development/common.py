import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .config import HEADERS, REQUEST_TIMEOUT


class BaseCollector:
    source_name = ""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get(self, url, params=None):
        r = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r

    @staticmethod
    def clean(text):
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def compact(text):
        return re.sub(r"[\s()·]", "", text or "")

    @staticmethod
    def abs_url(base_url, href):
        return urljoin(base_url, href)
