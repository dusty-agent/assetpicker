from collections import Counter

from app.models.news import News
from app.models.analytics import SourceStat


class SourceAnalyzer:

    def analyze(self, news: list[News]) -> list[SourceStat]:

        counter = Counter()

        for article in news:
            counter[article.source] += 1

        result = []

        for source, count in counter.items():
            result.append(
                SourceStat(
                    source=source,
                    article_count=count,
                    average_score=0,
                    duplicate_count=0,
                )
            )

        return sorted(
            result,
            key=lambda x: x.article_count,
            reverse=True,
        )