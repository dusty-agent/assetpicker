from dataclasses import dataclass, field


@dataclass
class NewsCard:

    title: str

    summary: str

    source: str

    url: str = ""

    image: str = ""

    published_at: str = ""

    tags: list[str] = field(default_factory=list)


@dataclass
class MarketSummary:

    icon: str

    title: str

    description: str


@dataclass
class Insight:

    content: str


@dataclass
class DailyBriefing:

    today: str

    cards: list[NewsCard]

    # market: list[MarketSummary]

    insight: Insight