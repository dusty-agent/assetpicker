from app.models.news import News

from app.daily.models import NewsCard


def to_news_cards(
    news: list[News],
) -> list[NewsCard]:

    cards = []

    for item in news:

        cards.append(

            NewsCard(

                title=item.title,

                summary=item.summary,

                source=item.source,

                url=item.url,

                published_at=str(item.published_at),

            )

        )

    return cards