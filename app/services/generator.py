from pathlib import Path

from app.analytics.reporter_analyzer import ReporterAnalyzer
from app.analytics.source_analyzer import SourceAnalyzer
from app.analytics.trend_analyzer import TrendAnalyzer

from app.collector.rss_collector import RSSCollector

from app.exporters.analysis_exporter import AnalysisExporter
from app.exporters.json_exporter import JsonExporter
from app.exporters.news_exporter import NewsExporter

from app.models.card import Card
from app.models.report import Report


class Generator:

    def run(self):
        print("🚀 AssetPicker Generator Started")

        news = self.collect_news()
        self.analyze_news(news)

        report = self.generate_report()

        JsonExporter().export(
            report=report,
            path=Path("public/latest.json")
        )

        print("✅ Generation Complete")

    def collect_news(self):

        news = RSSCollector().collect()

        print(f"📰 {len(news)}개의 뉴스를 수집했습니다.")

        NewsExporter().export(
            news,
            Path("public/latest_news.json")
        )

        return news

    def analyze_news(self, news):

        source_stats = SourceAnalyzer().analyze(news)
        reporter_stats = ReporterAnalyzer().analyze(news)
        trend_stats = TrendAnalyzer().analyze(news)

        AnalysisExporter().export(
            path=Path("public/daily_analysis.json"),
            sources=source_stats,
            reporters=reporter_stats,
            trends=trend_stats,
        )

        print(f"📊 언론사 {len(source_stats)}개")
        print(f"👨 기자 {len(reporter_stats)}명")
        print(f"🔥 키워드 {len(trend_stats)}개")

    def generate_report(self):

        cards = [
            Card(
                title="Hello AssetPicker",
                body="첫 번째 카드입니다."
            )
        ]

        return Report(
            title="AssetPicker",
            cards=cards
        )