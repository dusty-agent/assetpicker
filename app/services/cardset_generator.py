from app.models.card import Card
from app.models.card_set import CardSet
from app.models.card_type import CardType
from app.models.story import Story


class CardSetGenerator:

    def generate(self, story: Story) -> CardSet:

        cards = [
            self.build_cover(story),
            self.build_summary(story),
            self.build_why(story),
            self.build_buyer_view(story),
            self.build_assetpicker_view(story),
            self.build_brand(),
        ]

        return CardSet(
            title=story.headline,
            story=story,
            cards=cards,
        )

    def build_cover(self, story: Story) -> Card:

        return Card(
            type=CardType.COVER,
            title=story.headline,
            body=story.summary,
        )

    def build_summary(self, story: Story) -> Card:

        return Card(
            type=CardType.CONTENT,
            title="핵심 요약",
            body=story.summary,
        )

    def build_why(self, story: Story) -> Card:

        return Card(
            type=CardType.CONTENT,
            title="왜 중요할까요?",
            body=story.why,
        )

    def build_buyer_view(self, story: Story) -> Card:

        return Card(
            type=CardType.CONTENT,
            title="실수요자 관점",
            body=story.buyer_view,
        )

    def build_assetpicker_view(self, story: Story) -> Card:

        return Card(
            type=CardType.CONTENT,
            title="AssetPicker View",
            body=story.assetpicker_view,
        )

    def build_brand(self) -> Card:

        return Card(
            type=CardType.BRAND,
            title="AssetPicker",
            body="정보를 선별해, 자산이 되는 하루.\n\nassetpicker.dustydraft.com\n\nA DustyDraft Project.",
        )