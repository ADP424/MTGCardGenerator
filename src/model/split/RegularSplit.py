from constants import (
    CARD_ADDITIONAL_TITLES,
    CARD_MANA_COST,
    CARD_RULES_TEXT,
    CARD_SUBTYPES,
    CARD_SUPERTYPES,
    CARD_TITLE,
    CARD_TYPES,
    CARD_WATERMARK_COLOR,
)
from model.regular.RegularCard import RegularCard
from model.Layer import Layer


class RegularSplit(RegularCard):
    """
    A layered image representing a split card and all the collection info on it,
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
    ):
        super().__init__(metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers)

        # Overall Card
        self.CARD_WIDTH = 2100
        self.CARD_HEIGHT = 1500

        # First Title Box
        self.FIRST_TITLE_BOX_X = 193
        self.FIRST_TITLE_BOX_Y = self.TITLE_BOX_Y
        self.FIRST_TITLE_BOX_WIDTH = 840
        self.FIRST_TITLE_BOX_HEIGHT = self.TITLE_BOX_HEIGHT

        # Second Title Box
        self.SECOND_TITLE_BOX_X = 1151
        self.SECOND_TITLE_BOX_Y = self.TITLE_BOX_Y
        self.SECOND_TITLE_BOX_WIDTH = 840
        self.SECOND_TITLE_BOX_HEIGHT = self.TITLE_BOX_HEIGHT

        # First Title Text
        self.FIRST_TITLE_X = 223
        self.FIRST_TITLE_BOTTOM_Y = 198
        self.FIRST_TITLE_WIDTH = 859

        # Second Title Text
        self.SECOND_TITLE_X = 1181
        self.SECOND_TITLE_BOTTOM_Y = 198
        self.SECOND_TITLE_WIDTH = 859

        # Type Box
        self.TYPE_BOX_Y = 815
        self.TYPE_BOX_HEIGHT = 77

        # Type Text
        self.TYPE_MAX_FONT_SIZE = 60
        self.TYPE_MIN_FONT_SIZE = 6

        # First Type Text
        self.FIRST_TYPE_X = 222
        self.FIRST_TYPE_BOTTOM_Y = 872
        self.FIRST_TYPE_WIDTH = 853

        # Second Type Text
        self.SECOND_TYPE_X = 1179
        self.SECOND_TYPE_BOTTOM_Y = 872
        self.SECOND_TYPE_WIDTH = 853

        # First Rules Text Box
        self.FIRST_RULES_BOX_X = 212
        self.FIRST_RULES_BOX_Y = 907
        self.FIRST_RULES_BOX_WIDTH = 821
        self.FIRST_RULES_BOX_HEIGHT = 526

        # Second Rules Text Box
        self.SECOND_RULES_BOX_X = 1170
        self.SECOND_RULES_BOX_Y = 907
        self.SECOND_RULES_BOX_WIDTH = 821
        self.SECOND_RULES_BOX_HEIGHT = 526

        # First Rules Text
        self.FIRST_RULES_TEXT_X = 212
        self.FIRST_RULES_TEXT_Y = 907
        self.FIRST_RULES_TEXT_WIDTH = 821
        self.FIRST_RULES_TEXT_HEIGHT = 526

        # Second Rules Text
        self.SECOND_RULES_TEXT_X = 1170
        self.SECOND_RULES_TEXT_Y = 907
        self.SECOND_RULES_TEXT_WIDTH = 821
        self.SECOND_RULES_TEXT_HEIGHT = 526

        # First Set / Rarity Symbol
        self.FIRST_SET_SYMBOL_X = 970
        self.FIRST_SET_SYMBOL_Y = 823
        self.FIRST_SET_SYMBOL_WIDTH = 60

        # Second Set / Rarity Symbol
        self.SECOND_SET_SYMBOL_X = 1926
        self.SECOND_SET_SYMBOL_Y = 823
        self.SECOND_SET_SYMBOL_WIDTH = 60

        # Footer
        # All RELATIVE values assume 0 degree rotation, the way the text would be read
        # This means width, height, tab length, etc. but NOT x or y coordinates
        self.FOOTER_ROTATION = 270
        self.FOOTER_X = 0
        self.FOOTER_Y = 94
        self.FOOTER_WIDTH = 1304
        self.FOOTER_HEIGHT = 136

        # Other
        self.HOLO_STAMP_X = float("inf")
        self.HOLO_STAMP_Y = float("inf")

        self.first_mana_cost_x = float("inf")
        self.second_mana_cost_x = float("inf")

    def _create_watermark_layer(self):
        """
        Process two watermark images and append them to `self.collector_layers`
        (one for each rules text box because it's a room). Assumes the image is in RGBA format.
        """

        full_watermark_colors = self.get_metadata(CARD_WATERMARK_COLOR)

        watermark_colors = full_watermark_colors.split("{end}")
        first_watermark_colors = watermark_colors[0].strip()
        second_watermark_colors = watermark_colors[1].strip() if len(watermark_colors) > 1 else first_watermark_colors

        self.RULES_BOX_X = self.FIRST_RULES_BOX_X
        self.RULES_BOX_Y = self.FIRST_RULES_BOX_Y
        self.RULES_BOX_WIDTH = self.FIRST_RULES_BOX_WIDTH
        self.RULES_BOX_HEIGHT = self.FIRST_RULES_BOX_HEIGHT
        self.set_metadata(CARD_WATERMARK_COLOR, first_watermark_colors)
        super()._create_watermark_layer()

        self.RULES_BOX_X = self.SECOND_RULES_BOX_X
        self.RULES_BOX_Y = self.SECOND_RULES_BOX_Y
        self.RULES_BOX_WIDTH = self.SECOND_RULES_BOX_WIDTH
        self.RULES_BOX_HEIGHT = self.SECOND_RULES_BOX_HEIGHT
        self.set_metadata(CARD_WATERMARK_COLOR, second_watermark_colors)
        super()._create_watermark_layer()

        self.set_metadata(CARD_WATERMARK_COLOR, full_watermark_colors)

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

        first_title = self.get_metadata(CARD_TITLE)
        second_title = self.get_metadata(CARD_ADDITIONAL_TITLES).split("\n")[0]

        self.TITLE_X = self.FIRST_TITLE_X
        self.TITLE_BOTTOM_Y = self.FIRST_TITLE_BOTTOM_Y
        self.TITLE_WIDTH = self.FIRST_TITLE_WIDTH
        self.TITLE_BOX_HEIGHT = self.FIRST_TITLE_BOX_HEIGHT
        self.mana_cost_x = self.first_mana_cost_x
        super()._create_title_layer()

        self.TITLE_X = self.SECOND_TITLE_X
        self.TITLE_BOTTOM_Y = self.SECOND_TITLE_BOTTOM_Y
        self.TITLE_WIDTH = self.SECOND_TITLE_WIDTH
        self.TITLE_BOX_HEIGHT = self.SECOND_TITLE_BOX_HEIGHT
        self.set_metadata(CARD_TITLE, second_title)
        self.mana_cost_x = self.second_mana_cost_x
        super()._create_title_layer()

        self.set_metadata(CARD_TITLE, first_title)

    def _create_type_layer(self):
        """
        Process title text into the titles for each door of the room and append them to `self.text_layers`.
        """

        supertypes = self.get_metadata(CARD_SUPERTYPES)
        types = self.get_metadata(CARD_TYPES)
        subtypes = self.get_metadata(CARD_SUBTYPES)

        first_supertype = supertypes.split("\n")[0]
        first_type = types.split("\n")[0]
        first_subtype = subtypes.split("\n")[0]

        second_supertype = supertypes.split("\n")[1] if len(supertypes) > 0 else first_supertype
        second_type = types.split("\n")[1] if len(supertypes) > 0 else first_type
        second_subtype = subtypes.split("\n")[1] if len(supertypes) > 0 else first_subtype

        self.TYPE_X = self.FIRST_TYPE_X
        self.TYPE_BOTTOM_Y = self.FIRST_TYPE_BOTTOM_Y
        self.TYPE_WIDTH = self.FIRST_TYPE_WIDTH
        self.SET_SYMBOL_X = self.FIRST_SET_SYMBOL_X
        self.set_metadata(CARD_SUPERTYPES, first_supertype)
        self.set_metadata(CARD_TYPES, first_type)
        self.set_metadata(CARD_SUBTYPES, first_subtype)
        super()._create_type_layer()

        self.TYPE_X = self.SECOND_TYPE_X
        self.TYPE_BOTTOM_Y = self.SECOND_TYPE_BOTTOM_Y
        self.TYPE_WIDTH = self.SECOND_TYPE_WIDTH
        self.SET_SYMBOL_X = self.SECOND_SET_SYMBOL_X
        self.set_metadata(CARD_SUPERTYPES, second_supertype)
        self.set_metadata(CARD_TYPES, second_type)
        self.set_metadata(CARD_SUBTYPES, second_subtype)
        super()._create_type_layer()

        self.set_metadata(CARD_SUPERTYPES, supertypes)
        self.set_metadata(CARD_TYPES, types)
        self.set_metadata(CARD_SUBTYPES, subtypes)

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text boxes, exchanging placeholders for symbols and text formatting,
        and append them to `self.text_layers`.
        """

        full_rules_text = self.get_metadata(CARD_RULES_TEXT)

        rules_texts = full_rules_text.split("{end}")
        first_rules_text = rules_texts[0].strip()
        second_rules_text = rules_texts[1].strip() if len(rules_texts) > 1 else ""

        # Do titles correctly so that {cardname} placeholder works as expected
        first_title = self.get_metadata(CARD_TITLE)
        second_title = self.get_metadata(CARD_ADDITIONAL_TITLES).split("\n")[0]

        self.RULES_TEXT_X = self.FIRST_RULES_TEXT_X
        self.RULES_TEXT_Y = self.FIRST_RULES_TEXT_Y
        self.RULES_TEXT_WIDTH = self.FIRST_RULES_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.FIRST_RULES_TEXT_HEIGHT
        self.set_metadata(CARD_RULES_TEXT, first_rules_text)
        self.set_metadata(CARD_TITLE, first_title)
        super()._create_rules_text_layer()

        self.RULES_TEXT_X = self.SECOND_RULES_TEXT_X
        self.RULES_TEXT_Y = self.SECOND_RULES_TEXT_Y
        self.RULES_TEXT_WIDTH = self.SECOND_RULES_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.SECOND_RULES_TEXT_HEIGHT
        self.set_metadata(CARD_RULES_TEXT, second_rules_text)
        self.set_metadata(CARD_TITLE, second_title)
        super()._create_rules_text_layer()

        self.set_metadata(CARD_RULES_TEXT, full_rules_text)
        self.set_metadata(CARD_TITLE, first_title)

    def _create_rarity_symbol_layer(self):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.
        """

        self.SET_SYMBOL_X = self.FIRST_SET_SYMBOL_X
        self.SET_SYMBOL_Y = self.FIRST_SET_SYMBOL_Y
        self.SET_SYMBOL_WIDTH = self.FIRST_SET_SYMBOL_WIDTH
        super()._create_rarity_symbol_layer()

        self.SET_SYMBOL_X = self.SECOND_SET_SYMBOL_X
        self.SET_SYMBOL_Y = self.SECOND_SET_SYMBOL_Y
        self.SET_SYMBOL_WIDTH = self.SECOND_SET_SYMBOL_WIDTH
        super()._create_rarity_symbol_layer()
