from PIL import Image

from constants import (
    CARD_FRAME_LAYOUT_EXTRAS,
    CARD_RULES_TEXT,
    LATO,
    LATO_BOLD,
    LATO_ITALICS,
    PLAYTEST_SYMBOL_PLACEHOLDER_KEY,
)
from log import log
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from utils import paste_image, str_to_float


class Playtest(RegularCard):
    """
    A layered image representing a playtest card and all the collection info on it,
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

        # Symbols
        self.MANA_SYMBOL_KEY = PLAYTEST_SYMBOL_PLACEHOLDER_KEY

        # Title Box
        self.TITLE_BOX_X = 279
        self.TITLE_BOX_Y = 204
        self.TITLE_BOX_WIDTH = 1447
        self.TITLE_BOX_HEIGHT = 172

        # Mana Cost
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)

        # Title Text
        self.TITLE_X = 311
        self.TITLE_BOTTOM_Y = 350
        self.TITLE_WIDTH = 1584
        self.TITLE_MAX_FONT_SIZE = 90
        self.TITLE_FONT = LATO_BOLD

        # Type Box
        self.TYPE_BOX_Y = 1371
        self.TYPE_BOX_HEIGHT = 193

        # Type Text
        self.TYPE_X = 311 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 364
        self.TYPE_BOTTOM_Y = 1517
        self.TYPE_WIDTH = 1474 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 1513
        self.TYPE_MAX_FONT_SIZE = 90
        self.TYPE_MIN_FONT_SIZE = 8
        self.TYPE_FONT = LATO

        # Rules Text Box
        self.RULES_BOX_X = 269
        self.RULES_BOX_Y = 1572
        self.RULES_BOX_WIDTH = 1481
        self.RULES_BOX_HEIGHT = 868

        # Rules Text
        self.RULES_TEXT_X = 292
        self.RULES_TEXT_Y = 1550
        self.RULES_TEXT_WIDTH = 1453
        self.RULES_TEXT_HEIGHT = 890
        self.RULES_TEXT_FONT = LATO
        self.RULES_TEXT_FONT_ITALICS = LATO_ITALICS
        self.RULES_TEXT_MAX_FONT_SIZE = 105
        self.RULES_TEXT_MIN_FONT_SIZE = 8

        # Reminder Rules Text
        self.REMINDER_TEXT_X = 292
        self.REMINDER_TEXT_Y = 2437
        self.REMINDER_TEXT_WIDTH = 1453
        self.REMINDER_TEXT_HEIGHT = 151
        self.REMINDER_TEXT_MAX_FONT_SIZE = 74

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1446
        self.POWER_TOUGHNESS_Y = 2459
        self.POWER_TOUGHNESS_WIDTH = 319
        self.POWER_TOUGHNESS_HEIGHT = 130
        self.POWER_TOUGHNESS_FONT = LATO
        self.POWER_TOUGHNESS_FONT_SIZE = 94
        self.POWER_TOUGHNESS_FONT_COLOR = (0, 0, 0)

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1608
        self.SET_SYMBOL_Y = 1399
        self.SET_SYMBOL_WIDTH = 107

        # Footer
        # All RELATIVE values assume 0 degree rotation, the way the text would be read
        # This means width, height, tab length, etc. but NOT x or y coordinates
        self.FOOTER_X = 245
        self.FOOTER_Y = 2621
        self.FOOTER_WIDTH = 1521
        self.FOOTER_HEIGHT = 134

    def render_card(self, close_images: bool = True) -> Image.Image:
        """
        Merge all layers into one image.

        Returns
        -------
        Image
            The merged image.

        close_images: bool, default: True
            Whether to close the images used in the card layers or not.
            This means the card cannot be rendered again, but it frees memory.
        """

        art_image = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))
        art_image = self._paste_layer(self.art_layer, art_image, close_images)

        composite_image = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))
        for layer in self.frame_layers + self.collector_layers + self.text_layers + self.overlay_layers:
            composite_image = self._paste_layer(layer, composite_image, close_images)

        for extra in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS):
            if extra[:6] == "rotate":
                degrees = str_to_float(extra[6:], None)
                if degrees is None:
                    log("Unable to process rotation command in frame layout.")
                    break
                composite_image = composite_image.rotate(degrees)

        full_image = paste_image(composite_image, art_image, (0, 0))
        if close_images:
            art_image.close()
            composite_image.close()

        return full_image

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text boxes, exchanging placeholders for symbols and text formatting,
        and append them to `self.text_layers`.
        """

        rules_text_x = self.RULES_TEXT_X
        rules_text_y = self.RULES_TEXT_Y
        rules_text_width = self.RULES_TEXT_WIDTH
        rules_text_height = self.RULES_TEXT_HEIGHT
        rules_text_max_font_size = self.REMINDER_TEXT_MAX_FONT_SIZE

        full_rules_text = self.get_metadata(CARD_RULES_TEXT)

        rules_texts = full_rules_text.split("{end}")
        rules_text = rules_texts[0].strip()
        reminder_text = (
            rules_texts[1].strip() if len(rules_texts) > 1 else "{i}{bold}TEST CARD{/bold} - Not for constructed play"
        )

        self.set_metadata(CARD_RULES_TEXT, rules_text)
        super()._create_rules_text_layer()

        self.RULES_TEXT_X = self.REMINDER_TEXT_X
        self.RULES_TEXT_Y = self.REMINDER_TEXT_Y
        self.RULES_TEXT_WIDTH = self.REMINDER_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.REMINDER_TEXT_HEIGHT
        self.RULES_TEXT_MAX_FONT_SIZE = self.REMINDER_TEXT_MAX_FONT_SIZE
        self.set_metadata(CARD_RULES_TEXT, reminder_text)
        super()._create_rules_text_layer()

        self.RULES_TEXT_X = rules_text_x
        self.RULES_TEXT_Y = rules_text_y
        self.RULES_TEXT_WIDTH = rules_text_width
        self.RULES_TEXT_HEIGHT = rules_text_height
        self.RULES_TEXT_MAX_FONT_SIZE = rules_text_max_font_size

        self.set_metadata(CARD_RULES_TEXT, full_rules_text)
