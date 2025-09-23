from PIL import Image, ImageDraw, ImageFont

from constants import (
    BELEREN_BOLD_SMALL_CAPS,
    CARD_MANA_COST,
    CARD_RULES_TEXT,
    PLANESWALKER_ABILITY_BODY_EVEN,
    PLANESWALKER_ABILITY_BODY_ODD,
    PLANESWALKER_ABILITY_TOP_EVEN,
    PLANESWALKER_ABILITY_TOP_ODD,
    PLANESWALKER_ABILITY_COST_BORDER_NEGATIVE,
    PLANESWALKER_ABILITY_COST_BORDER_NEUTRAL,
    PLANESWALKER_ABILITY_COST_BORDER_POSITIVE,
)
from model.RegularCard import RegularCard
from model.Layer import Layer
from utils import paste_image
from log import log


class RegularPlaneswalker(RegularCard):
    """
    A layered image representing a regular planeswalker and all the collection info on it,
    with all relevant card metadata.

    Attributes
    ----------
    metadata : dict[str, str | list], default : {}
        Information about the card (title, mana cost, rules text, frame, etc.)

    base_width : int, default : None
        The width of the root image. Determined by the frame layout in the metadata if not given.

    base_height : int, default : None
        The height of the root image. Determined by the frame layout in the metadata if not given.

    art_layer : Layer, optional
        The art to use in the art slot of the frame. Renders first, before the frame layers.

    frame_layers : list[Layer], default : []
        The layers of card frames. Lower-index layers are rendered first. Renders after art, before collector info.

    collector_layers : list[Layer], default : []
        The layers of collector info. Lower-index layers are rendered first. Renders after frames, before text.

    text_layers : list[Layer], default : []
        The layers of card text. Lower-index layers are rendered first. Renders after collector info and frames.

    overlay_layers : list[Layer], default : []
        Any additional layers to render above everything else on the card. Rendered absolutely last.
    """

    def __init__(
        self,
        metadata: dict[str, str | list["RegularCard"]] = None,
        art_layer: Layer = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
        overlay_layers: list[Layer] = None,
        footer_largest_index: int = 999,
    ):
        super().__init__(
            metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers, footer_largest_index
        )

        # Title Box
        self.TITLE_BOX_X = 90
        self.TITLE_BOX_Y = 76
        self.TITLE_BOX_WIDTH = 1313

        # Title Text
        self.TITLE_X = 130
        self.TITLE_Y = 78
        self.TITLE_WIDTH = 1244

        # Type Text
        self.TYPE_X = 130
        self.TYPE_Y = 1181
        self.TYPE_WIDTH = 1240

        # Rules Text Box
        self.RULES_BOX_X = 180
        self.RULES_BOX_Y = 1315
        self.RULES_BOX_WIDTH = 1206
        self.RULES_BOX_HEIGHT = 608

        # Planeswalker Ability Cost Frame
        self.ABILITY_COST_FRAME_X = 42
        self.ABILITY_COST_FRAME_WIDTH = 212

        # Rules Text
        self.RULES_TEXT_X = 254
        self.RULES_TEXT_Y = 1315
        self.RULES_TEXT_WIDTH = 1132
        self.RULES_TEXT_HEIGHT = 580

        # Planeswalker Ability Cost Text
        self.ABILITY_COST_TEXT_X = 80
        self.ABILITY_COST_TEXT_WIDTH = 135
        self.ABILITY_COST_TEXT_HEIGHT = 76
        self.ABILITY_TEXT_MARGIN = 20
        self.ABILITY_COST_FONT_SIZE = 60
        self.ABILITY_COST_FONT_COLOR = (255, 255, 255)

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1201
        self.POWER_TOUGHNESS_Y = 1848
        self.POWER_TOUGHNESS_WIDTH = 228
        self.POWER_TOUGHNESS_HEIGHT = 158
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1304
        self.SET_SYMBOL_Y = 1197
        self.SET_SYMBOL_WIDTH = 80

        # Separate mana and ability costs
        costs = self.get_metadata(CARD_MANA_COST).splitlines()
        self.ability_costs = [ability_cost.strip() for ability_cost in costs[1:]]
        self.set_metadata(CARD_MANA_COST, costs[0].strip())

        # Determine the heights and y-values of each ability rules text
        full_rules_text = self.get_metadata(CARD_RULES_TEXT)
        full_rules_height = self.RULES_TEXT_HEIGHT

        self.RULES_TEXT_HEIGHT = 9999 * self.CARD_HEIGHT  # stop text shrinking to size while measuring

        self.ability_texts = [text.strip() for text in full_rules_text.split("{end}")]
        ability_heights: list[int] = []
        total_height = 0
        for text in self.ability_texts:
            self.metadata[CARD_RULES_TEXT] = text
            _, _, _, content_height, _ = self._get_rules_text_layout(text)
            ability_heights.append(content_height)
            total_height += content_height

        self.ability_heights: list[int] = []
        for height in ability_heights:
            proportional_height = (height / total_height) * full_rules_height
            even_height = full_rules_height / len(ability_heights)
            alpha = 0.5
            final_height = int(alpha * proportional_height + (1 - alpha) * even_height)
            self.ability_heights.append(final_height)

        self.metadata[CARD_RULES_TEXT] = full_rules_text
        self.RULES_TEXT_HEIGHT = full_rules_height

    def create_layers(
        self,
        create_ability_background_layer: bool = True,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_ability_cost_frame_layers: bool = True,
        create_watermark_layer: bool = True,
        create_rarity_symbol_layer: bool = True,
        create_footer_layer: bool = True,
        create_mana_cost_layer: bool = True,
        create_title_layer: bool = True,
        create_type_layer: bool = True,
        create_rules_text_layer: bool = True,
        create_power_toughness_layer: bool = True,
        create_ability_cost_layers: bool = True,
        create_overlay_layers: bool = True,
    ):
        """
        Append every frame, text, and collector layer to the card based on `self.metadata`.

        Parameters
        ----------
        create_ability_background_layer: bool, default : True
            Whether to put the planeswalker's ability frames behind the text or not.

        create_art_layer: bool, default : True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default : True
            Whether to put the card's frames on or not.

        create_ability_cost_frame_layers: bool, default : True
            Whether to put the planeswalker's ability cost frames on or not.

        create_watermark_layer: bool, default : True
            Whether to put the watermark on the card or not.

        create_rarity_symbol_layer: bool, default : True
            Whether to put the rarity/set symbol on the card or not.

        create_footer_layer: bool, default : True
            Whether to put the footer collector info on the bottom of the card or not.

        create_mana_cost_layer: bool, default : True
            Whether to put the mana cost of the card on it or not.

        create_title_layer: bool, default : True
            Whether to put the title of the card on it or not.

        create_type_layer: bool, default : True
            Whether to put the type line of the card on it or not.

        create_rules_text_layer: bool, default : True
            Whether to put the rules text of the card on it or not.

        create_power_toughness_layer: bool, default : True
            Whether to put the power & toughness of the card on it or not.

        create_ability_cost_layers: bool, default : True
            Whether to put the cost of each planeswalker ability on the planeswalker or not.

        create_overlay_layers: bool, default : True
            Whether to put the overlays on top of the card after everything else or not.
        """

        if create_ability_background_layer:
            self._create_ability_background_layer()

        super().create_layers(
            create_art_layer,
            create_frame_layers,
            create_watermark_layer,
            create_rarity_symbol_layer,
            create_footer_layer,
            create_mana_cost_layer,
            create_title_layer,
            create_type_layer,
            create_rules_text_layer,
            create_power_toughness_layer,
            create_overlay_layers,
        )

        if create_ability_cost_frame_layers:
            self._create_ability_cost_frame_layers()

        if create_ability_cost_layers:
            self._create_ability_cost_layers()

    def _create_ability_background_layer(self):
        """
        Create the planeswalker ability backgrounds behind the rest of the frame.
        """

        ability_background = Image.new("RGBA", (self.RULES_BOX_WIDTH, self.RULES_BOX_HEIGHT), (0, 0, 0, 0))

        curr_y = 0
        for idx, height in enumerate(self.ability_heights):
            body_y = curr_y
            body_height = height
            if idx > 0:
                body_y += self.ABILITY_TEXT_MARGIN // 2
                body_height -= self.ABILITY_TEXT_MARGIN // 2
            if idx < len(self.ability_heights) - 1:
                body_height -= self.ABILITY_TEXT_MARGIN // 2
            else:
                body_height += self.RULES_BOX_HEIGHT - body_height

            if idx == 0:
                ability_background_top = None
                ability_background_body = PLANESWALKER_ABILITY_BODY_EVEN.get_formatted_image(
                    self.RULES_BOX_WIDTH, body_height
                )
            elif idx % 2 == 0:
                ability_background_top = PLANESWALKER_ABILITY_TOP_EVEN.get_formatted_image(
                    self.RULES_BOX_WIDTH, self.ABILITY_TEXT_MARGIN
                )
                ability_background_body = PLANESWALKER_ABILITY_BODY_EVEN.get_formatted_image(
                    self.RULES_BOX_WIDTH, body_height
                )
            else:
                ability_background_top = PLANESWALKER_ABILITY_TOP_ODD.get_formatted_image(
                    self.RULES_BOX_WIDTH, self.ABILITY_TEXT_MARGIN
                )
                ability_background_body = PLANESWALKER_ABILITY_BODY_ODD.get_formatted_image(
                    self.RULES_BOX_WIDTH, body_height
                )

            ability_background = paste_image(
                ability_background_top, ability_background, (0, curr_y - self.ABILITY_TEXT_MARGIN // 2)
            )
            ability_background = paste_image(ability_background_body, ability_background, (0, body_y))

            curr_y += height

        self.frame_layers.append(Layer(ability_background, (self.RULES_BOX_X, self.RULES_BOX_Y)))

    def _create_ability_cost_frame_layers(self):
        """
        Create the frames for the costs of each planeswalker abilities, above the rest of the frame.
        """

        ability_costs_image = Image.new(
            "RGBA",
            (self.RULES_BOX_WIDTH + (self.RULES_BOX_X - self.ABILITY_COST_FRAME_X), self.RULES_BOX_HEIGHT),
            (0, 0, 0, 0),
        )
        curr_y = 0

        self.ability_text_y_axes: list[int] = []
        for idx, height in enumerate(self.ability_heights):
            try:
                ability_cost = int(self.ability_costs[idx])
            except ValueError:
                log(f"Can't parse '{self.ability_costs[idx]}' as an ability cost.")
                continue

            if ability_cost > 0:
                ability_border = PLANESWALKER_ABILITY_COST_BORDER_POSITIVE.get_formatted_image()
            elif ability_cost < 0:
                ability_border = PLANESWALKER_ABILITY_COST_BORDER_NEGATIVE.get_formatted_image()
            else:
                ability_border = PLANESWALKER_ABILITY_COST_BORDER_NEUTRAL.get_formatted_image()
            ability_border = ability_border.resize(
                (
                    self.ABILITY_COST_FRAME_WIDTH,
                    int((self.ABILITY_COST_FRAME_WIDTH / ability_border.width) * ability_border.height),
                )
            )

            paste_y = max(curr_y + (height - ability_border.height) // 2, curr_y)
            ability_costs_image = paste_image(ability_border, ability_costs_image, (0, paste_y))
            curr_y += height

            # Text is centered around negative borders by default
            if ability_cost > 0:
                paste_y += int(0.11 * ability_border.height)  # recoil from the jank 0_0
            elif ability_cost == 0:
                paste_y += int(0.065 * ability_border.height)
            self.ability_text_y_axes.append(self.RULES_BOX_Y + paste_y + ability_border.height // 2)

        self.frame_layers.append(Layer(ability_costs_image, (self.ABILITY_COST_FRAME_X, self.RULES_BOX_Y)))

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`. Do this once for each ability because this is a planeswalker.
        """

        full_rules_y = self.RULES_TEXT_Y
        full_rules_height = self.RULES_TEXT_HEIGHT
        full_rules_text = self.get_metadata(CARD_RULES_TEXT)

        curr_y = full_rules_y
        for idx, text in enumerate(self.ability_texts):
            self.RULES_TEXT_Y = curr_y
            self.RULES_TEXT_HEIGHT = self.ability_heights[idx]
            self.metadata[CARD_RULES_TEXT] = text
            super()._create_rules_text_layer()
            curr_y += self.RULES_TEXT_HEIGHT

        self.RULES_TEXT_Y = full_rules_y
        self.RULES_TEXT_HEIGHT = full_rules_height
        self.metadata[CARD_RULES_TEXT] = full_rules_text

    def _create_ability_cost_layers(self):
        """
        Create the ability cost numbers over each ability cost frame.
        Depends on the ability frames being rendered first (to know the frame positions).
        """

        ability_cost_font = ImageFont.truetype(BELEREN_BOLD_SMALL_CAPS, self.ABILITY_COST_FONT_SIZE)

        for idx, cost in enumerate(self.ability_costs):
            image = Image.new("RGBA", (self.ABILITY_COST_TEXT_WIDTH, self.ABILITY_COST_TEXT_HEIGHT), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            text_width = int(ability_cost_font.getlength(cost))
            bounding_box = ability_cost_font.getbbox(cost)
            text_height = int(bounding_box[3] - bounding_box[1])

            draw.text(
                ((self.ABILITY_COST_TEXT_WIDTH - text_width) // 2, 0),
                cost,
                font=ability_cost_font,
                fill=self.ABILITY_COST_FONT_COLOR,
            )

            self.text_layers.append(
                Layer(
                    image,
                    (
                        self.ABILITY_COST_TEXT_X,
                        self.ability_text_y_axes[idx] - self.ABILITY_COST_TEXT_HEIGHT // 2 - text_height // 2,
                    ),
                )
            )
