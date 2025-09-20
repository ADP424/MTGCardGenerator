from PIL import Image

from constants import (
    BELEREN_BOLD_SMALL_CAPS,
    CARD_MANA_COST,
    CARD_RULES_TEXT,
    PLANESWALKER_ABILITY_BODY_EVEN,
    PLANESWALKER_ABILITY_BODY_ODD,
    PLANESWALKER_ABILITY_TOP_EVEN,
    PLANESWALKER_ABILITY_TOP_ODD,
)
from model.RegularCard import RegularCard
from model.Layer import Layer


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

        # Rules Text Box
        self.RULES_BOX_X = 180
        self.RULES_BOX_Y = 1315
        self.RULES_BOX_WIDTH = 1206
        self.RULES_BOX_HEIGHT = 608
        self.ABILITY_MARGIN = 20

        # Rules Text
        self.RULES_TEXT_X = 254
        self.RULES_TEXT_Y = 1315
        self.RULES_TEXT_WIDTH = 1132
        self.RULES_TEXT_HEIGHT = 608

        # Determine the heights and y-values of each ability rules text #
        full_rules_height = self.RULES_TEXT_HEIGHT
        full_rules_text = self.metadata[CARD_RULES_TEXT]

        self.ability_texts = [text.strip() for text in self.get_metadata(CARD_RULES_TEXT).split("{end}")]
        self.RULES_TEXT_HEIGHT = 9999 * self.CARD_HEIGHT
        ability_heights: list[int] = []
        total_height = 0
        for text in self.ability_texts:
            self.metadata[CARD_RULES_TEXT] = text
            _, _, _, _, content_height, _ = self._get_rules_text_layout(text)
            ability_heights.append(content_height)
            total_height += content_height

        self.ability_heights: list[int] = []
        curr_y = self.RULES_TEXT_Y
        for idx in range(len(ability_heights)):
            ability_height = int((ability_heights[idx] / total_height) * full_rules_height)
            self.ability_heights.append(ability_height)
            curr_y += ability_height

        self.RULES_TEXT_HEIGHT = full_rules_height
        self.metadata[CARD_RULES_TEXT] = full_rules_text

    def create_layers(
        self,
        create_ability_background: bool = True,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_watermark_layer: bool = True,
        create_rarity_symbol_layer: bool = True,
        create_footer_layer: bool = True,
        create_mana_cost_layer: bool = True,
        create_title_layer: bool = True,
        create_type_layer: bool = True,
        create_rules_text_layer: bool = True,
        create_power_toughness_layer: bool = True,
        create_overlay_layers: bool = True,
    ):
        """
        Append every frame, text, and collector layer to the card based on `self.metadata`.

        Parameters
        ----------
        create_ability_background: bool, default : True
            Whether to put the planeswalker's ability frames behind the text or not.

        create_art_layer: bool, default : True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default : True
            Whether to put the card's frames on or not.

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

        create_overlay_layers: bool, default : True
            Whether to put the overlays on top of the card after everything else or not.
        """

        if create_ability_background:
            self._create_ability_background()

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

    def _create_ability_background(self):
        """
        Create the planeswalker ability backgrounds behind the rest of the frame.
        """

        ability_background = Image.new("RGBA", (self.RULES_BOX_WIDTH, self.RULES_BOX_HEIGHT), (0, 0, 0, 0))

        def paste_image(image: Image.Image, position: tuple[int, int]):
            """
            Paste an image onto the ability background.
            """

            nonlocal ability_background
            if image is not None:
                temp = Image.new("RGBA", ability_background.size, (0, 0, 0, 0))
                temp.paste(image, position)
                ability_background = Image.alpha_composite(ability_background, temp)

        curr_y = 0
        for idx, height in enumerate(self.ability_heights):
            body_y = curr_y
            body_height = height
            if idx > 0:
                body_y += self.ABILITY_MARGIN // 2
                body_height -= self.ABILITY_MARGIN // 2
            if idx < len(self.ability_heights) - 1:
                body_height -= self.ABILITY_MARGIN // 2

            if idx == 0:
                ability_background_top = None
                ability_background_body = PLANESWALKER_ABILITY_BODY_EVEN.resize((self.RULES_BOX_WIDTH, body_height))
            elif idx % 2 == 0:
                ability_background_top = PLANESWALKER_ABILITY_TOP_EVEN.resize(
                    (self.RULES_BOX_WIDTH, self.ABILITY_MARGIN)
                )
                ability_background_body = PLANESWALKER_ABILITY_BODY_EVEN.resize((self.RULES_BOX_WIDTH, body_height))
            else:
                ability_background_top = PLANESWALKER_ABILITY_TOP_ODD.resize(
                    (self.RULES_BOX_WIDTH, self.ABILITY_MARGIN)
                )
                ability_background_body = PLANESWALKER_ABILITY_BODY_ODD.resize((self.RULES_BOX_WIDTH, body_height))

            paste_image(ability_background_top, (0, curr_y - self.ABILITY_MARGIN // 2))
            paste_image(ability_background_body, (0, body_y))

            curr_y += height

        self.frame_layers.append(Layer(ability_background, (self.RULES_BOX_X, self.RULES_BOX_Y)))

    def _create_mana_cost_layer(self):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`. Because this is a planeswalker, also process the
        ability costs.
        """

        mana_cost_lines = self.get_metadata(CARD_MANA_COST).splitlines()
        self.set_metadata(CARD_MANA_COST, mana_cost_lines[0].strip())
        super()._create_mana_cost_layer()

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`. Do this once for each ability because this is a planeswalker.
        """

        full_rules_y = self.RULES_TEXT_Y
        full_rules_height = self.RULES_TEXT_HEIGHT
        full_rules_text = self.metadata[CARD_RULES_TEXT]

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
