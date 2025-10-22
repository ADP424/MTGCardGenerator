import re
from PIL import Image
from constants import (
    CARD_FRAME_LAYOUT_EXTRAS,
    CARD_MANA_COST,
    CARD_POWER_TOUGHNESS,
    CARD_TYPES,
    FUTURE_SHIFTED_SYMBOL_PLACEHOLDER_KEY,
    FUTURE_SHIFTED_TYPE_ICON_KEY,
)
from log import log
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class FutureShifted(RegularCard):
    """
    A layered image representing a card with a future shifted showcase frame
    and all the collection info on it, with all relevant card metadata.

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
        metadata: dict[str, str | list[RegularCard]] = None,
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
        self.TITLE_BOX_Y = 105
        self.TITLE_BOX_WIDTH = 1313
        self.TITLE_BOX_HEIGHT = 114

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 118
        self.MANA_COST_SYMBOL_X = {
            1: 185,
            2: 124,
            3: 94,
            4: 94,
            5: 120,
            6: 215,
        }
        self.MANA_COST_SYMBOL_Y = {
            1: 284,
            2: 420,
            3: 569,
            4: 721,
            5: 884,
            6: 1036,
        }

        # Title Text
        self.TITLE_X = 265
        self.TITLE_BOTTOM_Y = 218
        self.TITLE_WIDTH = 1100
        self.TITLE_FONT_COLOR = (255, 255, 255)

        # Type Box
        self.TYPE_BOX_Y = 1187
        self.TYPE_BOX_HEIGHT = 114

        # Type Text
        self.TYPE_X = 181 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 252
        self.TYPE_BOTTOM_Y = 1276
        self.TYPE_WIDTH = 1114 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 1043
        self.TYPE_FONT_COLOR = (255, 255, 255)

        # Rules Text Box
        self.RULES_BOX_X = 112
        self.RULES_BOX_Y = 1315
        self.RULES_BOX_WIDTH = 1278
        self.RULES_BOX_HEIGHT = 550

        # Rules Text
        self.RULES_TEXT_X = 134
        self.RULES_TEXT_WIDTH = 1235
        self.RULES_TEXT_HEIGHT = 550

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1144
        self.POWER_TOUGHNESS_Y = 1880
        self.POWER_TOUGHNESS_WIDTH = 252
        self.POWER_TOUGHNESS_HEIGHT = 120
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1334
        self.SET_SYMBOL_Y = 1215
        self.SET_SYMBOL_WIDTH = 70

        # Footer
        # All RELATIVE values assume 0 degree rotation, the way the text would be read
        # This means width, height, tab length, etc. but NOT x or y coordinates
        self.FOOTER_Y = 1929
        self.FOOTER_WIDTH = 1304 if len(self.get_metadata(CARD_POWER_TOUGHNESS)) == 0 else 1040

        # Type Icon
        self.TYPE_ICON_X = 102
        self.TYPE_ICON_Y = 100
        self.TYPE_ICON_SIZE = 59
        self.TYPE_ICON_COLOR = (
            (255, 255, 255)
            if "white" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            and "light" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            else (0, 0, 0)
        )

        # Other
        self.RULES_TEXT_DIVIDER = None

    def create_layers(
        self,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_type_icon_layer: bool = True,
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
        create_art_layer: bool, default : True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default : True
            Whether to put the card's frames on or not.

        create_type_icon_layer: bool, default : True
            Whether to put the future shifted card's type icon in the top left or not.

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

        if create_type_icon_layer:
            self._create_type_icon_layer()

    def _create_type_icon_layer(self):
        """
        Process the type icon for the top left of the future shifted frame, and append it to `self.frame_layers`.
        """

        card_type = self.get_metadata(CARD_TYPES).lower()
        type_icon = FUTURE_SHIFTED_TYPE_ICON_KEY.get(card_type, FUTURE_SHIFTED_TYPE_ICON_KEY["multitype"])
        scale = self.TYPE_ICON_SIZE / type_icon.image.height

        type_icon_image = type_icon.get_formatted_image(type_icon.image.width * scale, type_icon.image.height * scale)

        alpha = type_icon_image.getchannel("A")
        solid = Image.new("RGBA", type_icon_image.size, self.TYPE_ICON_COLOR)
        recolored_type_icon_image = Image.new("RGBA", type_icon_image.size)
        recolored_type_icon_image.paste(solid, mask=alpha)

        self.frame_layers.append(
            Layer(
                recolored_type_icon_image,
                (self.TYPE_ICON_X, self.TYPE_ICON_Y),
            )
        )

    def _create_mana_cost_layer(self):
        """
        Process MTG mana cost into the spots on the future shifted frame, exchanging
        mana placeholders for symbols, and append it to `self.text_layers`.
        """

        text = self.get_metadata(CARD_MANA_COST)
        if len(text) == 0 or "{skip}" in text:
            return

        text = re.sub(r"{+|}+", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        image = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))

        num = 1
        for sym in text.split(" "):
            if num > 6:
                log("Future shifted frames can only support up to six mana cost symbols. Skipping '{sym}'...")

            symbol = FUTURE_SHIFTED_SYMBOL_PLACEHOLDER_KEY.get(sym.strip().lower(), None)
            if symbol is None:
                log(f"Unknown placeholder for future shifted card: '{{{sym}}}'")
                continue

            scale = self.MANA_COST_SYMBOL_SIZE / symbol.image.height
            width = int(symbol.image.width * scale)
            height = int(symbol.image.height * scale)
            symbol_image = symbol.get_formatted_image(width, height)

            x_location = self.MANA_COST_SYMBOL_X.get(num, 0)
            y_location = self.MANA_COST_SYMBOL_Y.get(num, 0)

            image.alpha_composite(symbol_image, (x_location, y_location))

            num += 1

        self.text_layers.append(Layer(image, (0, 0)))
