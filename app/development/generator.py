from .prompts import SYSTEM_PROMPT, build_prompt


def _fallback(items, error_message: str):
    cards = []

    for item in items:
        row = dict(item)
        row["_ai_applied"] = False
        row["_ai_error"] = error_message
        cards.append(row)

    return {
        "cards": cards,
        "insight": {
            "keyword": "",
            "summary": "",
            "reason": "",
        },
    }


def generate_editorial(items, use_ai=True):
    """
    공식자료 후보 전체를 한 번의 LLM 호출로 편집합니다.

    반환:
    {
        "cards": [...원본 + display_*...],
        "insight": {
            "keyword": "...",
            "summary": "...",
            "reason": "..."
        }
    }
    """

    if not items:
        return {
            "cards": [],
            "insight": {},
        }

    if not use_ai:
        cards = []

        for item in items:
            row = dict(item)
            row["_ai_applied"] = False
            row["_ai_error"] = ""
            cards.append(row)

        return {
            "cards": cards,
            "insight": {},
        }

    try:
        from app.llm.client import LLMClient

        llm = LLMClient()

        result = llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_prompt(items),
        )

        if not isinstance(result, dict):
            raise RuntimeError(
                f"LLM 응답이 JSON object가 아닙니다: "
                f"{type(result).__name__}"
            )

        cards = result.get("cards")

        if not isinstance(cards, list):
            raise RuntimeError(
                "LLM 응답에 cards 배열이 없습니다."
            )

        if len(cards) != len(items):
            raise RuntimeError(
                "LLM cards 개수가 다릅니다. "
                f"expected={len(items)}, "
                f"actual={len(cards)}"
            )

        insight = (
            result.get("insight")
            or {}
        )

        if not isinstance(insight, dict):
            raise RuntimeError(
                "LLM insight가 object가 아닙니다."
            )

        by_index = {}

        for card in cards:
            if not isinstance(card, dict):
                raise RuntimeError(
                    "LLM cards 항목이 object가 아닙니다."
                )

            index = card.get("index")

            if not isinstance(index, int):
                raise RuntimeError(
                    "LLM card에 정수형 index가 없습니다."
                )

            by_index[index] = card

        merged_cards = []

        for index, raw in enumerate(
            items,
            start=1,
        ):
            ai = by_index.get(index)

            if ai is None:
                raise RuntimeError(
                    f"LLM 응답에서 index={index} 항목이 없습니다."
                )

            title = str(
                ai.get("title")
                or ""
            ).strip()

            summary = str(
                ai.get("summary")
                or ""
            ).strip()

            tags = ai.get("tags")

            if not title:
                raise RuntimeError(
                    f"index={index} title이 비어 있습니다."
                )

            if not summary:
                raise RuntimeError(
                    f"index={index} summary가 비어 있습니다."
                )

            if not isinstance(tags, list):
                tags = []

            tags = [
                str(tag).strip()
                for tag in tags
                if str(tag).strip()
            ][:3]

            merged = dict(raw)

            merged["display_title"] = title
            merged["display_summary"] = summary
            merged["display_tags"] = tags
            merged["_ai_applied"] = True
            merged["_ai_error"] = ""

            merged_cards.append(merged)

        cleaned_insight = {
            "keyword": str(
                insight.get("keyword")
                or ""
            ).strip(),
            "summary": str(
                insight.get("summary")
                or ""
            ).strip(),
            "reason": str(
                insight.get("reason")
                or ""
            ).strip(),
        }

        print(
            f"[AI OK] Development "
            f"{len(merged_cards)}건 + Insight 편집 완료"
        )

        return {
            "cards": merged_cards,
            "insight": cleaned_insight,
        }

    except Exception as e:
        message = (
            f"{type(e).__name__}: {e}"
        )

        print(
            f"[AI ERROR] {message}"
        )

        print(
            "[AI FALLBACK] 원본 선정 데이터를 사용합니다."
        )

        return _fallback(
            items,
            message,
        )


# 기존 코드 호환용
def polish_items(items, use_ai=True):
    return generate_editorial(
        items,
        use_ai=use_ai,
    )["cards"]
