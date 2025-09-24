from constants import CARD_MANA_COST, CARD_RULES_TEXT, CARD_TITLE
from model.RegularCard import RegularCard
from model.Layer import Layer


class RegularRoom(RegularCard):
    """
    A layered image representing an enchantment room card and all the collection info on it,
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

        # Overall Card
        self.CARD_WIDTH = 2814
        self.CARD_HEIGHT = 2010

        # First Title Box
        self.FIRST_TITLE_BOX_X = 249
        self.FIRST_TITLE_BOX_Y = 101
        self.FIRST_TITLE_BOX_WIDTH = 1134
        self.FIRST_TITLE_BOX_HEIGHT = 145

        # Second Title Box
        self.SECOND_TITLE_BOX_X = 1535
        self.SECOND_TITLE_BOX_Y = 101
        self.SECOND_TITLE_BOX_WIDTH = 1134
        self.SECOND_TITLE_BOX_HEIGHT = 145

        # Title Text
        self.TITLE_MAX_FONT_SIZE = 106
        self.TITLE_MIN_FONT_SIZE = 8

        # First Title Text
        self.FIRST_TITLE_X = 297
        self.FIRST_TITLE_Y = 102
        self.FIRST_TITLE_WIDTH = 1097

        # Second Title Text
        self.SECOND_TITLE_X = 1580
        self.SECOND_TITLE_Y = 102
        self.SECOND_TITLE_WIDTH = 1097

        # Type Box
        self.TYPE_BOX_HEIGHT = 153

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 94
        self.MANA_COST_SYMBOL_SPACING = 8
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (-1, 8)

        # Type Text
        self.TYPE_X = 299
        self.TYPE_Y = 1068
        self.TYPE_WIDTH = 2369
        self.TYPE_MAX_FONT_SIZE = 80
        self.TYPE_MIN_FONT_SIZE = 8
        self.TYPE_FONT_COLOR = (255, 255, 255)

        # Rules Text Box
        self.RULES_BOX_MAX_FONT_SIZE = 104
        self.RULES_BOX_MIN_FONT_SIZE = 8

        # Shared Rules Text Box
        self.SHARED_RULES_BOX_X = 277
        self.SHARED_RULES_BOX_Y = 1104
        self.SHARED_RULES_BOX_WIDTH = 2380
        self.SHARED_RULES_BOX_HEIGHT = 180
        self.SHARED_RULES_TEXT_FONT_COLOR = (255, 255, 255)

        # First Rules Text Box
        self.FIRST_RULES_BOX_X = 277
        self.FIRST_RULES_BOX_Y = 1405
        self.FIRST_RULES_BOX_WIDTH = 1095
        self.FIRST_RULES_BOX_HEIGHT = 506
        self.FIRST_RULES_TEXT_FONT_COLOR = (0, 0, 0)

        # Second Rules Text Box
        self.SECOND_RULES_BOX_X = 1563
        self.SECOND_RULES_BOX_Y = 1405
        self.SECOND_RULES_BOX_WIDTH = 1095
        self.SECOND_RULES_BOX_HEIGHT = 506
        self.SECOND_RULES_TEXT_FONT_COLOR = (0, 0, 0)

        # Rules Text
        self.RULES_TEXT_MANA_SYMBOL_SPACING = 7

        # Shared Rules Text
        self.SHARED_RULES_TEXT_X = 277
        self.SHARED_RULES_TEXT_Y = 1213
        self.SHARED_RULES_TEXT_WIDTH = 2380
        self.SHARED_RULES_TEXT_HEIGHT = 180

        # First Rules Text
        self.FIRST_RULES_TEXT_X = 277
        self.FIRST_RULES_TEXT_Y = 1405
        self.FIRST_RULES_TEXT_WIDTH = 1095
        self.FIRST_RULES_TEXT_HEIGHT = 506

        # Second Rules Text
        self.SECOND_RULES_TEXT_X = 1563
        self.SECOND_RULES_TEXT_Y = 1405
        self.SECOND_RULES_TEXT_WIDTH = 1095
        self.SECOND_RULES_TEXT_HEIGHT = 506

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 2588
        self.SET_SYMBOL_Y = 1105
        self.SET_SYMBOL_WIDTH = 70

        # Footer
        # All RELATIVE values assume 0 degree rotation, the way the text would be read
        # This means width, height, tab length, etc. but NOT x or y coordinates
        self.FOOTER_ROTATION = 270
        self.FOOTER_X = 0
        self.FOOTER_Y = 129
        self.FOOTER_WIDTH = 1760
        self.FOOTER_HEIGHT = 181
        self.FOOTER_FONT_SIZE = 47
        self.FOOTER_FONT_OUTLINE_SIZE = 4
        self.FOOTER_TAB_LENGTH = 33
        self.FOOTER_ARTIST_GAP_LENGTH = 7

        self.first_mana_cost_x = float("inf")
        self.second_mana_cost_x = float("inf")

    def _create_watermark_layer(self):
        """
        Process two watermark images and append them to `self.collector_layers`
        (one for each rules text box because it's a room). Assumes the image is in RGBA format.
        """

        self.RULES_BOX_X = self.FIRST_RULES_BOX_X
        self.RULES_BOX_Y = self.FIRST_RULES_BOX_Y
        self.RULES_BOX_WIDTH = self.FIRST_RULES_BOX_WIDTH
        self.RULES_BOX_HEIGHT = self.FIRST_RULES_BOX_HEIGHT
        super()._create_watermark_layer()

        self.RULES_BOX_X = self.SECOND_RULES_BOX_X
        self.RULES_BOX_Y = self.SECOND_RULES_BOX_Y
        self.RULES_BOX_WIDTH = self.SECOND_RULES_BOX_WIDTH
        self.RULES_BOX_HEIGHT = self.SECOND_RULES_BOX_HEIGHT
        super()._create_watermark_layer()

    def _create_mana_cost_layer(self):
        """
        Process MTG mana cost into the mana cost headers, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`, one for each door of the room.
        """

        full_mana_cost = self.get_metadata(CARD_MANA_COST)

        mana_costs = full_mana_cost.split("\n")
        first_mana_cost = mana_costs[0]
        second_mana_cost = mana_costs[1] if len(mana_costs) > 1 else ""

        self.TITLE_BOX_X = self.FIRST_TITLE_BOX_X
        self.TITLE_BOX_Y = self.FIRST_TITLE_BOX_Y
        self.TITLE_BOX_WIDTH = self.FIRST_TITLE_BOX_WIDTH
        self.TITLE_BOX_HEIGHT = self.FIRST_TITLE_BOX_HEIGHT
        self.set_metadata(CARD_MANA_COST, first_mana_cost)
        super()._create_mana_cost_layer()
        self.first_mana_cost_x = self.mana_cost_x

        self.TITLE_BOX_X = self.SECOND_TITLE_BOX_X
        self.TITLE_BOX_Y = self.SECOND_TITLE_BOX_Y
        self.TITLE_BOX_WIDTH = self.SECOND_TITLE_BOX_WIDTH
        self.TITLE_BOX_HEIGHT = self.SECOND_TITLE_BOX_HEIGHT
        self.set_metadata(CARD_MANA_COST, second_mana_cost)
        super()._create_mana_cost_layer()
        self.second_mana_cost_x = self.mana_cost_x

        self.set_metadata(CARD_MANA_COST, full_mana_cost)

    def _create_title_layer(self):
        """
        Process title text into the titles for each door of the room and append them to `self.text_layers`.
        """

        full_title = self.get_metadata(CARD_TITLE)

        titles = full_title.split("{N}")
        first_title = titles[0].strip()
        second_title = titles[1].strip() if len(titles) > 1 else ""

        self.TITLE_X = self.FIRST_TITLE_X
        self.TITLE_Y = self.FIRST_TITLE_Y
        self.TITLE_WIDTH = self.FIRST_TITLE_WIDTH
        self.TITLE_BOX_HEIGHT = self.FIRST_TITLE_BOX_HEIGHT
        self.set_metadata(CARD_TITLE, first_title)
        self.mana_cost_x = self.first_mana_cost_x
        super()._create_title_layer()

        self.TITLE_X = self.SECOND_TITLE_X
        self.TITLE_Y = self.SECOND_TITLE_Y
        self.TITLE_WIDTH = self.SECOND_TITLE_WIDTH
        self.TITLE_BOX_HEIGHT = self.SECOND_TITLE_BOX_HEIGHT
        self.set_metadata(CARD_TITLE, second_title)
        self.mana_cost_x = self.second_mana_cost_x
        super()._create_title_layer()

        self.set_metadata(CARD_TITLE, full_title)

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text boxes, exchanging placeholders for symbols and text formatting,
        and append them to `self.text_layers`.
        """

        full_rules_text = self.get_metadata(CARD_RULES_TEXT)
        full_title = self.get_metadata(CARD_TITLE)

        titles = full_rules_text.split("{end}")
        shared_rules_text = titles[0].strip()
        first_rules_text = titles[1].strip() if len(titles) > 1 else ""
        second_rules_text = titles[2].strip() if len(titles) > 2 else ""

        # Do titles correctly so that {cardname} placeholder works as expected
        titles = full_title.split("{N}")
        first_title = titles[0].strip()
        second_title = titles[1].strip() if len(titles) > 1 else ""

        self.RULES_TEXT_X = self.SHARED_RULES_TEXT_X
        self.RULES_TEXT_Y = self.SHARED_RULES_TEXT_Y
        self.RULES_TEXT_WIDTH = self.SHARED_RULES_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.SHARED_RULES_TEXT_HEIGHT
        self.RULES_TEXT_FONT_COLOR = self.SHARED_RULES_TEXT_FONT_COLOR
        self.set_metadata(CARD_RULES_TEXT, shared_rules_text)
        self.set_metadata(CARD_TITLE, f"{first_title} // {second_title}")
        super()._create_rules_text_layer()

        self.RULES_TEXT_X = self.FIRST_RULES_TEXT_X
        self.RULES_TEXT_Y = self.FIRST_RULES_TEXT_Y
        self.RULES_TEXT_WIDTH = self.FIRST_RULES_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.FIRST_RULES_TEXT_HEIGHT
        self.RULES_TEXT_FONT_COLOR = self.FIRST_RULES_TEXT_FONT_COLOR
        self.set_metadata(CARD_RULES_TEXT, first_rules_text)
        self.set_metadata(CARD_TITLE, first_title)
        super()._create_rules_text_layer()

        self.RULES_TEXT_X = self.SECOND_RULES_TEXT_X
        self.RULES_TEXT_Y = self.SECOND_RULES_TEXT_Y
        self.RULES_TEXT_WIDTH = self.SECOND_RULES_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.SECOND_RULES_TEXT_HEIGHT
        self.RULES_TEXT_FONT_COLOR = self.SECOND_RULES_TEXT_FONT_COLOR
        self.set_metadata(CARD_RULES_TEXT, second_rules_text)
        self.set_metadata(CARD_TITLE, second_title)
        super()._create_rules_text_layer()

        self.set_metadata(CARD_RULES_TEXT, full_rules_text)
        self.set_metadata(CARD_TITLE, full_title)
