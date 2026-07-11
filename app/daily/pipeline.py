class DailyPipeline:

    def build_cover(
        self,
        result,
    ):
        return {}

    def build_introduction(
        self,
        result,
    ):
        return {}

    def build_issues(
        self,
        result,
    ):
        cards = result.get("cards", [])

        if not cards:
            raise RuntimeError(
                "LLM이 카드를 생성하지 않았습니다."
            )

        return cards

    def build_insight(
        self,
        result,
    ):
        return {
            "insight": result.get(
                "insight",
                {},
            ),
        }

    def build_ending(
        self,
        result,
    ):
        return {}

    def build(
        self,
        result,
    ):
        return {

            "cover": self.build_cover(
                result,
            ),

            "introduction": self.build_introduction(
                result,
            ),

            "issues": self.build_issues(
                result,
            ),

            "insight": self.build_insight(
                result,
            ),

            "ending": self.build_ending(
                result,
            ),

        }