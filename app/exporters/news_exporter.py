import json
from pathlib import Path

from app.models.news import News


class NewsExporter:

    def export(self, news: list[News], path: Path):

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:

            json.dump(
                [n.model_dump(mode="json") for n in news],
                f,
                ensure_ascii=False,
                indent=2,
            )