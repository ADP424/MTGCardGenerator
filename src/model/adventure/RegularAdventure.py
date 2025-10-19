from constants import (
    CARD_ADDITIONAL_TITLES,
    CARD_MANA_COST,
    CARD_RULES_TEXT,
    CARD_SUBTYPES,
    CARD_SUPERTYPES,
    CARD_TITLE,
    CARD_TYPES,
)
from model.regular.RegularCard import RegularCard
from model.Layer import Layer


class RegularAdventure(RegularCard):
    """
    A layered image representing an adventure card and all the collection info on it,
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

        # Adventure Title Box
        self.ADVENTURE_TITLE_BOX_X = 95
        self.ADVENTURE_TITLE_BOX_Y = 1325
        self.ADVENTURE_TITLE_BOX_WIDTH = 633
        self.ADVENTURE_TITLE_BOX_HEIGHT = 89

        # Adventure Mana Cost
        self.ADVENTURE_MANA_COST_SYMBOL_SIZE = 60
        self.ADVENTURE_MANA_COST_SYMBOL_SPACING = 5

        # Adventure Title Text
        self.ADVENTURE_TITLE_X = 120
        self.ADVENTURE_TITLE_BOTTOM_Y = 1400
        self.ADVENTURE_TITLE_WIDTH = 625
        self.ADVENTURE_TITLE_MAX_FONT_SIZE = 70
        self.ADVENTURE_TITLE_FONT_COLOR = (255, 255, 255)

        # Adventure Type Box
        self.ADVENTURE_TYPE_BOX_Y = 1435
        self.ADVENTURE_TYPE_BOX_HEIGHT = 71

        # Adventure Type Text
        self.ADVENTURE_TYPE_X = 123
        self.ADVENTURE_TYPE_BOTTOM_Y = 1476
        self.ADVENTURE_TYPE_WIDTH = 650
        self.ADVENTURE_TYPE_MAX_FONT_SIZE = 60
        self.ADVENTURE_TYPE_FONT_COLOR = (255, 255, 255)

        # Right Rules Text Box
        self.RULES_BOX_X = 756
        self.RULES_BOX_Y = 1320
        self.RULES_BOX_WIDTH = 652
        self.RULES_BOX_HEIGHT = 618

        # Adventure Rules Text Box
        self.ADVENTURE_RULES_BOX_X = 98
        self.ADVENTURE_RULES_BOX_Y = 1508
        self.ADVENTURE_RULES_BOX_WIDTH = 652
        self.ADVENTURE_RULES_BOX_HEIGHT = 430

        # Rules Text
        self.RULES_TEXT_MAX_FONT_SIZE = 70

        # Right Rules Text
        self.RULES_TEXT_X = 774
        self.RULES_TEXT_Y = 1320
        self.RULES_TEXT_WIDTH = 625
        self.RULES_TEXT_HEIGHT = 618

        # Adventure Rules Text
        self.ADVENTURE_RULES_TEXT_X = 112
        self.ADVENTURE_RULES_TEXT_Y = 1508
        self.ADVENTURE_RULES_TEXT_WIDTH = 625
        self.ADVENTURE_RULES_TEXT_HEIGHT = 430

        self.adventure_mana_cost_x = float("inf")

    def _create_mana_cost_layer(self):
        """
        Process MTG mana cost into the mana cost headers, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`, one for the main card and one for the adventure.
        """

        full_title_box_x = self.TITLE_BOX_X
        full_title_box_y = self.TITLE_BOX_Y
        full_title_box_width = self.TITLE_BOX_WIDTH
        full_title_box_height = self.TITLE_BOX_HEIGHT
        full_adventure_mana_cost_symbol_size = self.MANA_COST_SYMBOL_SIZE
        full_mana_cost_symbol_spacing = self.MANA_COST_SYMBOL_SPACING

        full_mana_cost = self.get_metadata(CARD_MANA_COST)

        mana_costs = full_mana_cost.split("\n")
        primary_mana_cost = mana_costs[0]
        adventure_mana_cost = mana_costs[1] if len(mana_costs) > 1 else ""

        self.set_metadata(CARD_MANA_COST, primary_mana_cost)
        super()._create_mana_cost_layer()
        primary_mana_cost_x = self.mana_cost_x

        self.TITLE_BOX_X = self.ADVENTURE_TITLE_BOX_X
        self.TITLE_BOX_Y = self.ADVENTURE_TITLE_BOX_Y
        self.TITLE_BOX_WIDTH = self.ADVENTURE_TITLE_BOX_WIDTH
        self.TITLE_BOX_HEIGHT = self.ADVENTURE_TITLE_BOX_HEIGHT
        self.MANA_COST_SYMBOL_SIZE = self.ADVENTURE_MANA_COST_SYMBOL_SIZE
        self.MANA_COST_SYMBOL_SPACING = self.ADVENTURE_MANA_COST_SYMBOL_SPACING
        self.set_metadata(CARD_MANA_COST, adventure_mana_cost)
        super()._create_mana_cost_layer()
        self.adventure_mana_cost_x = self.mana_cost_x

        self.mana_cost_x = primary_mana_cost_x
        self.set_metadata(CARD_MANA_COST, full_mana_cost)

        self.TITLE_BOX_X = full_title_box_x
        self.TITLE_BOX_Y = full_title_box_y
        self.TITLE_BOX_WIDTH = full_title_box_width
        self.TITLE_BOX_HEIGHT = full_title_box_height
        self.MANA_COST_SYMBOL_SIZE = full_adventure_mana_cost_symbol_size
        self.MANA_COST_SYMBOL_SPACING = full_mana_cost_symbol_spacing

    def _create_title_layer(self):
        """
        Process the regular and adventure title texts into their title boxes and append them to `self.text_layers`.
        """

        full_title_box_y = self.TITLE_BOX_Y
        full_title_x = self.TITLE_X
        full_title_bottom_y = self.TITLE_BOTTOM_Y
        full_title_width = self.TITLE_WIDTH
        full_title_box_height = self.TITLE_BOX_HEIGHT
        full_title_font_color = self.TITLE_FONT_COLOR
        main_title = self.get_metadata(CARD_TITLE)
        main_mana_cost_x = self.mana_cost_x

        super()._create_title_layer()

        adventure_title = self.get_metadata(CARD_ADDITIONAL_TITLES).split("\n")[0]

        self.TITLE_BOX_Y = self.ADVENTURE_TITLE_BOX_Y
        self.TITLE_X = self.ADVENTURE_TITLE_X
        self.TITLE_BOTTOM_Y = self.ADVENTURE_TITLE_BOTTOM_Y
        self.TITLE_WIDTH = self.ADVENTURE_TITLE_WIDTH
        self.TITLE_BOX_HEIGHT = self.ADVENTURE_TITLE_BOX_HEIGHT
        self.TITLE_FONT_COLOR = self.ADVENTURE_TITLE_FONT_COLOR
        self.set_metadata(CARD_TITLE, adventure_title)
        self.mana_cost_x = self.adventure_mana_cost_x
        super()._create_title_layer()

        self.TITLE_BOX_Y = full_title_box_y
        self.TITLE_X = full_title_x
        self.TITLE_BOTTOM_Y = full_title_bottom_y
        self.TITLE_WIDTH = full_title_width
        self.TITLE_BOX_HEIGHT = full_title_box_height
        self.TITLE_FONT_COLOR = full_title_font_color
        self.set_metadata(CARD_TITLE, main_title)
        self.mana_cost_x = main_mana_cost_x

    def _create_type_layer(self):
        """
        Process the regular and adventure type texts into their type boxes and append them to `self.text_layers`.
        """

        full_type_box_y = self.TYPE_BOX_Y
        full_type_x = self.TYPE_X
        full_type_bottom_y = self.TYPE_BOTTOM_Y
        full_type_width = self.TYPE_WIDTH
        full_type_box_height = self.TYPE_BOX_HEIGHT
        full_type_max_font_size = self.TYPE_MAX_FONT_SIZE
        full_type_font_color = self.TYPE_FONT_COLOR

        full_supertype = self.get_metadata(CARD_SUPERTYPES)
        full_type = self.get_metadata(CARD_TYPES)
        full_subtype = self.get_metadata(CARD_SUBTYPES)

        supertypes = full_supertype.split("\n")
        primary_supertype = supertypes[0].strip()
        adventure_supertype = supertypes[1].strip() if len(supertypes) > 1 else ""

        types = full_type.split("\n")
        primary_type = types[0].strip()
        adventure_type = types[1].strip() if len(types) > 1 else ""

        subtypes = full_subtype.split("\n")
        primary_subtype = subtypes[0].strip()
        adventure_subtype = subtypes[1].strip() if len(subtypes) > 1 else ""

        self.set_metadata(CARD_SUPERTYPES, primary_supertype)
        self.set_metadata(CARD_TYPES, primary_type)
        self.set_metadata(CARD_SUBTYPES, primary_subtype)
        super()._create_type_layer()

        self.TYPE_BOX_Y = self.ADVENTURE_TYPE_BOX_Y
        self.TYPE_X = self.ADVENTURE_TYPE_X
        self.TYPE_BOTTOM_Y = self.ADVENTURE_TYPE_BOTTOM_Y
        self.TYPE_WIDTH = self.ADVENTURE_TYPE_WIDTH
        self.TYPE_BOX_HEIGHT = self.ADVENTURE_TYPE_BOX_HEIGHT
        self.TYPE_MAX_FONT_SIZE = self.ADVENTURE_TYPE_MAX_FONT_SIZE
        self.TYPE_FONT_COLOR = self.ADVENTURE_TYPE_FONT_COLOR
        self.set_metadata(CARD_SUPERTYPES, adventure_supertype)
        self.set_metadata(CARD_TYPES, adventure_type)
        self.set_metadata(CARD_SUBTYPES, adventure_subtype)
        super()._create_type_layer()

        self.set_metadata(CARD_SUPERTYPES, full_supertype)
        self.set_metadata(CARD_TYPES, full_type)
        self.set_metadata(CARD_SUBTYPES, full_subtype)

        self.TYPE_BOX_Y = full_type_box_y
        self.TYPE_X = full_type_x
        self.TYPE_BOTTOM_Y = full_type_bottom_y
        self.TYPE_WIDTH = full_type_width
        self.TYPE_BOX_HEIGHT = full_type_box_height
        self.TYPE_MAX_FONT_SIZE = full_type_max_font_size
        self.TYPE_FONT_COLOR = full_type_font_color

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text boxes, exchanging placeholders for symbols and text formatting,
        and append them to `self.text_layers`.
        """

        full_rules_text = self.get_metadata(CARD_RULES_TEXT)
        full_title = self.get_metadata(CARD_TITLE)

        full_rules_text_x = self.RULES_TEXT_X
        full_rules_text_y = self.RULES_TEXT_Y
        full_rules_text_width = self.RULES_TEXT_WIDTH
        full_rules_text_height = self.RULES_TEXT_HEIGHT

        rules_texts = full_rules_text.split("{end}")
        primary_rules_text = rules_texts[0].strip()
        adventure_rules_text = rules_texts[1].strip() if len(rules_texts) > 1 else ""

        self.set_metadata(CARD_RULES_TEXT, primary_rules_text)
        super()._create_rules_text_layer()

        self.RULES_TEXT_X = self.ADVENTURE_RULES_TEXT_X
        self.RULES_TEXT_Y = self.ADVENTURE_RULES_TEXT_Y
        self.RULES_TEXT_WIDTH = self.ADVENTURE_RULES_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.ADVENTURE_RULES_TEXT_HEIGHT
        self.set_metadata(CARD_RULES_TEXT, adventure_rules_text)
        super()._create_rules_text_layer()

        self.set_metadata(CARD_RULES_TEXT, full_rules_text)
        self.set_metadata(CARD_TITLE, full_title)

        self.RULES_TEXT_X = full_rules_text_x
        self.RULES_TEXT_Y = full_rules_text_y
        self.RULES_TEXT_WIDTH = full_rules_text_width
        self.RULES_TEXT_HEIGHT = full_rules_text_height
