from collections import Counter

from app.models.news import News
from app.models.analytics import ReporterStat


class ReporterAnalyzer:

    def analyze(self, news: list[News]) -> list[ReporterStat]:

        counter = Counter()

        for article in news:

            if article.reporter:
                counter[article.reporter] += 1

        result = []

        for reporter, count in counter.items():

            result.append(
                ReporterStat(
                    reporter=reporter,
                    article_count=count,
                    average_score=0,
                )
            )

        return sorted(
            result,
            key=lambda x: x.article_count,
            reverse=True,
        )