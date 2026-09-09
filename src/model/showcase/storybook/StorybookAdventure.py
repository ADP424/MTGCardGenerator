from constants import (
    CARD_ADDITIONAL_TITLES,
    CARD_SUBTYPES,
    CARD_SUPERTYPES,
    CARD_TITLE,
    CARD_TYPES,
)
from model.adventure.Adventure import Adventure
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class StorybookAdventure(Adventure):
    """
    A layered image representing a storybook showcase adventure card and all the collection info on it,
    with all relevant card metadata.

    Attributes
    ----------
    metadata : dict[str, str | list], optional
        Information about the card (title, mana cost, rules text, frame, etc.)

    base_width : int, optional
        The width of the root image. Determined by the frame layout in the metadata if not given.

    base_height : int, optional
        The height of the root image. Determined by the frame layout in the metadata if not given.

    art_layer : Layer, optional
        The art to use in the art slot of the frame. Renders first, before the frame layers.

    frame_layers : list[Layer], optional
        The layers of card frames. Lower-index layers are rendered first. Renders after art, before collector info.

    collector_layers : list[Layer], optional
        The layers of collector info. Lower-index layers are rendered first. Renders after frames, before text.

    text_layers : list[Layer], optional
        The layers of card text. Lower-index layers are rendered first. Renders after collector info and frames.

    overlay_layers : list[Layer], optional
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
        super().__init__(
            metadata,
            art_layer,
            frame_layers,
            collector_layers,
            text_layers,
            overlay_layers,
        )

        # Title Box
        self.TITLE_BOX_X = 248
        self.TITLE_BOX_Y = 137
        self.TITLE_BOX_WIDTH = 1631

        # Title Text
        self.TITLE_X = 292

        # Type Text
        self.TYPE_X = 424
        self.TYPE_WIDTH = 1180

        # Right Rules Text Box
        self.RULES_BOX_X = 1028
        self.RULES_BOX_Y = 1800
        self.RULES_BOX_WIDTH = 828
        self.RULES_BOX_HEIGHT = 690

        # Adventure Title Text
        self.ADVENTURE_TITLE_X = 165
        self.ADVENTURE_TITLE_BOTTOM_Y = 1876
        self.ADVENTURE_TITLE_WIDTH = 838
        self.ADVENTURE_TITLE_MAX_FONT_SIZE = 82
        self.ADVENTURE_TITLE_FONT_COLOR = (255, 255, 255)

        # Adventure Title & Type Drop Shadow (white text over the book's dark green header)
        self.ADVENTURE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.075, 0.075)

        # Adventure Rules Text Box
        self.ADVENTURE_RULES_BOX_X = 130
        self.ADVENTURE_RULES_BOX_Y = 2065
        self.ADVENTURE_RULES_BOX_WIDTH = 820
        self.ADVENTURE_RULES_BOX_HEIGHT = 435

        # Right Rules Text
        self.RULES_TEXT_X = 1036
        self.RULES_TEXT_Y = 1812
        self.RULES_TEXT_WIDTH = 820
        self.RULES_TEXT_HEIGHT = 690

        # Adventure Rules Text
        self.ADVENTURE_RULES_TEXT_X = 155
        self.ADVENTURE_RULES_TEXT_Y = 2068
        self.ADVENTURE_RULES_TEXT_WIDTH = 820
        self.ADVENTURE_RULES_TEXT_HEIGHT = 435

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1562
        self.POWER_TOUGHNESS_Y = 2500
        self.POWER_TOUGHNESS_WIDTH = 354
        self.POWER_TOUGHNESS_HEIGHT = 169

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1732
        self.SET_SYMBOL_Y = 1620
        self.SET_SYMBOL_WIDTH = 99

    def _create_type_layer(self):
        """
        Process the regular and adventure type texts into their type boxes and append them to
        `self.text_layers`.
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
        self.TYPE_TEXT_ALIGN = "center"
        RegularCard._create_type_layer(self)
        self.TYPE_TEXT_ALIGN = "left"

        full_type_drop_shadow_offset = self.TYPE_TEXT_DROP_SHADOW_RELATIVE_OFFSET

        self.TYPE_BOX_Y = self.ADVENTURE_TYPE_BOX_Y
        self.TYPE_X = self.ADVENTURE_TYPE_X
        self.TYPE_BOTTOM_Y = self.ADVENTURE_TYPE_BOTTOM_Y
        self.TYPE_WIDTH = self.ADVENTURE_TYPE_WIDTH
        self.TYPE_BOX_HEIGHT = self.ADVENTURE_TYPE_BOX_HEIGHT
        self.TYPE_MAX_FONT_SIZE = self.ADVENTURE_TYPE_MAX_FONT_SIZE
        self.TYPE_FONT_COLOR = self.ADVENTURE_TYPE_FONT_COLOR
        self.TYPE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = self.ADVENTURE_TEXT_DROP_SHADOW_RELATIVE_OFFSET
        self.set_metadata(CARD_SUPERTYPES, adventure_supertype)
        self.set_metadata(CARD_TYPES, adventure_type)
        self.set_metadata(CARD_SUBTYPES, adventure_subtype)
        RegularCard._create_type_layer(self)
        self.TYPE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = full_type_drop_shadow_offset

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

    def _create_title_layer(self):
        """
        Process the regular and adventure title texts into their title boxes and append them to
        `self.text_layers`. The adventure title on the book page gets a drop shadow to stay legible
        over the header's dark green background, matching the storybook frame's art.
        """

        full_title_box_y = self.TITLE_BOX_Y
        full_title_x = self.TITLE_X
        full_title_bottom_y = self.TITLE_BOTTOM_Y
        full_title_width = self.TITLE_WIDTH
        full_title_box_height = self.TITLE_BOX_HEIGHT
        full_title_max_font_size = self.TITLE_MAX_FONT_SIZE
        full_title_font_color = self.TITLE_FONT_COLOR
        full_title_drop_shadow_offset = self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET

        main_title = self.get_metadata(CARD_TITLE)
        main_mana_cost_x = self.mana_cost_x

        RegularCard._create_title_layer(self)

        adventure_title = self.get_metadata(CARD_ADDITIONAL_TITLES).split("\n")[0]

        self.TITLE_BOX_Y = self.ADVENTURE_TITLE_BOX_Y
        self.TITLE_X = self.ADVENTURE_TITLE_X
        self.TITLE_BOTTOM_Y = self.ADVENTURE_TITLE_BOTTOM_Y
        self.TITLE_WIDTH = self.ADVENTURE_TITLE_WIDTH
        self.TITLE_BOX_HEIGHT = self.ADVENTURE_TITLE_BOX_HEIGHT
        self.TITLE_MAX_FONT_SIZE = self.ADVENTURE_TITLE_MAX_FONT_SIZE
        self.TITLE_FONT_COLOR = self.ADVENTURE_TITLE_FONT_COLOR
        self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = self.ADVENTURE_TEXT_DROP_SHADOW_RELATIVE_OFFSET
        self.set_metadata(CARD_TITLE, adventure_title)
        self.mana_cost_x = self.adventure_mana_cost_x
        RegularCard._create_title_layer(self)

        self.TITLE_BOX_Y = full_title_box_y
        self.TITLE_X = full_title_x
        self.TITLE_BOTTOM_Y = full_title_bottom_y
        self.TITLE_WIDTH = full_title_width
        self.TITLE_BOX_HEIGHT = full_title_box_height
        self.TITLE_MAX_FONT_SIZE = full_title_max_font_size
        self.TITLE_FONT_COLOR = full_title_font_color
        self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = full_title_drop_shadow_offset

        self.set_metadata(CARD_TITLE, main_title)
        self.mana_cost_x = main_mana_cost_x
