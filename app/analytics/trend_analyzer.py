from collections import Counter

from app.models.news import News


class TrendAnalyzer:

    def analyze(self, news: list[News]) -> dict[str, int]:

        counter = Counter()

        for article in news:

            words = article.title.split()

            for word in words:

                if len(word) >= 2:
                    counter[word] += 1

        return dict(counter.most_common(30))