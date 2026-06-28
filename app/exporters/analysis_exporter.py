import json
from pathlib import Path

from app.models.analytics import (
    SourceStat,
    ReporterStat,
)


class AnalysisExporter:

    def export(
        self,
        path: Path,
        sources: list[SourceStat],
        reporters: list[ReporterStat],
        trends: dict[str, int],
    ):

        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "sources": [s.model_dump() for s in sources],
            "reporters": [r.model_dump() for r in reporters],
            "trends": trends,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )