from datetime import datetime, timezone
import calendar

import feedparser

from app.models.news import News


class RSSCollector:

    RSS_URL = (
        "https://news.google.com/rss/search?"
        "q=부동산&hl=ko&gl=KR&ceid=KR:ko"
    )

    def collect(self) -> list[News]:

        feed = feedparser.parse(
            self.RSS_URL
        )

        news = []

        for entry in feed.entries:

            published = getattr(
                entry,
                "published_parsed",
                None,
            )

            if published:
                published_at = (
                    datetime.fromtimestamp(
                        calendar.timegm(published),
                        tz=timezone.utc,
                    )
                )
            else:
                published_at = (
                    datetime.now(timezone.utc)
                )

            news.append(
                News(
                    title=entry.title,
                    summary="",
                    source=(
                        getattr(
                            entry,
                            "source",
                            {},
                        ).get(
                            "title",
                            "",
                        )
                    ),
                    url=entry.link,
                    published_at=published_at,
                )
            )

        return news