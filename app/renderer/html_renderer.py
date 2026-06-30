from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.models.card_set import CardSet

BASE_DIR = Path(__file__).parent

class HtmlRenderer:

    def render(
        self,
        cardset: CardSet,
        output_dir: Path,
    ):

        env = Environment(
            loader=FileSystemLoader(BASE_DIR / "templates")
        )

        output_dir.mkdir(parents=True, exist_ok=True)

        total = len(cardset.cards)

        for index, card in enumerate(cardset.cards, start=1):

            # CardType에 맞는 템플릿 선택
            template = env.get_template(
                f"{card.type.value}.html"
            )

            html = template.render(
                card=card,
                story=cardset.story,
                page=index,
                total=total,
            )

            (output_dir / f"card_{index}.html").write_text(
                html,
                encoding="utf-8"
            )