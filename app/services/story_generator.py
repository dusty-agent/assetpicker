from app.models.story import Story


class StoryGenerator:

    def generate(self, news):

        return Story(
            news=news,

            headline=news.title,

            summary="핵심 요약 준비중",

            why="왜 중요한지 분석 준비중",

            buyer_view="실수요자 관점 준비중",

            assetpicker_view="AssetPicker 인사이트 준비중",

            keywords=[],

            score=None,
        )