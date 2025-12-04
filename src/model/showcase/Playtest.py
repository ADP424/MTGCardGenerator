import re
from PIL import Image
from constants import (
    CARD_FRAME_LAYOUT_EXTRAS,
    CARD_MANA_COST,
    CARD_RULES_TEXT,
    LATO,
    LATO_BOLD,
    LATO_ITALICS,
    PLAYTEST_SYMBOL_PLACEHOLDER_KEY,
    SYMBOL_PLACEHOLDER_KEY,
)

from model.regular.RegularCard import RegularCard
from model.Layer import Layer
from log import log
from utils import add_drop_shadow, paste_image, str_to_int


class Playtest(RegularCard):
    """
    A layered image representing a playtest card and all the collection info on it,
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

        # Title Box
        self.TITLE_BOX_X = 208
        self.TITLE_BOX_Y = 152
        self.TITLE_BOX_WIDTH = 1080
        self.TITLE_BOX_HEIGHT = 128

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 70
        self.MANA_COST_SYMBOL_SPACING = 6
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_SYMBOL_OUTLINE_SIZE = 0

        # Title Text
        self.TITLE_X = 232
        self.TITLE_BOTTOM_Y = 261
        self.TITLE_WIDTH = 1182
        self.TITLE_MAX_FONT_SIZE = 67
        self.TITLE_FONT = LATO_BOLD

        # Type Box
        self.TYPE_BOX_Y = 1023
        self.TYPE_BOX_HEIGHT = 144

        # Type Text
        self.TYPE_X = 232 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 272
        self.TYPE_BOTTOM_Y = 1132
        self.TYPE_WIDTH = 1100 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 1129
        self.TYPE_MAX_FONT_SIZE = 67
        self.TYPE_MIN_FONT_SIZE = 6
        self.TYPE_FONT = LATO

        # Rules Text Box
        self.RULES_BOX_X = 201
        self.RULES_BOX_Y = 1173
        self.RULES_BOX_WIDTH = 1105
        self.RULES_BOX_HEIGHT = 648

        # Rules Text
        self.RULES_TEXT_X = 218
        self.RULES_TEXT_Y = 1157
        self.RULES_TEXT_WIDTH = 1084
        self.RULES_TEXT_HEIGHT = 664
        self.RULES_TEXT_FONT = LATO
        self.RULES_TEXT_FONT_ITALICS = LATO_ITALICS
        self.RULES_TEXT_MAX_FONT_SIZE = 78
        self.RULES_TEXT_MIN_FONT_SIZE = 6

        # Reminder Rules Text
        self.REMINDER_TEXT_X = 218
        self.REMINDER_TEXT_Y = 1819
        self.REMINDER_TEXT_WIDTH = 1084
        self.REMINDER_TEXT_HEIGHT = 113
        self.REMINDER_TEXT_MAX_FONT_SIZE = 55

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1079
        self.POWER_TOUGHNESS_Y = 1835
        self.POWER_TOUGHNESS_WIDTH = 238
        self.POWER_TOUGHNESS_HEIGHT = 97
        self.POWER_TOUGHNESS_FONT = LATO
        self.POWER_TOUGHNESS_FONT_SIZE = 70
        self.POWER_TOUGHNESS_FONT_COLOR = (0, 0, 0)

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1200
        self.SET_SYMBOL_Y = 1044
        self.SET_SYMBOL_WIDTH = 80

        # Footer
        # All RELATIVE values assume 0 degree rotation, the way the text would be read
        # This means width, height, tab length, etc. but NOT x or y coordinates
        self.FOOTER_X = 183
        self.FOOTER_Y = 1956
        self.FOOTER_WIDTH = 1135
        self.FOOTER_HEIGHT = 100

    def render_card(self, close_images: bool = True) -> Image.Image:
        """
        Merge all layers into one image.

        Returns
        -------
        Image
            The merged image.

        close_images: bool, default : True
            Whether to close the images used in the card layers or not.
            This means the card cannot be rendered again, but it frees memory.
        """

        art_image = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))
        art_image = paste_image(self.art_layer.image, art_image, (0, 0))

        composite_image = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))
        for layer in self.frame_layers + self.collector_layers + self.text_layers + self.overlay_layers:
            composite_image = paste_image(layer.image, composite_image, layer.position)
            if close_images and layer.image:
                layer.image.close()
                layer.image = None

        for extra in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS):
            if extra[:6] == "rotate":
                degrees = str_to_int(extra[6:], None)
                if degrees == None:
                    log("Unable to process rotation command in frame layout.")
                    break
                composite_image = composite_image.rotate(degrees)

        full_image = paste_image(composite_image, art_image, (0, 0))
        if close_images:
            art_image.close()
            composite_image.close()

        return full_image

    def _create_mana_cost_layer(self):
        """
        Process MTG mana cost in the playtest style, exchanging mana placeholders
        for symbols, and append it to `self.text_layers`.
        """

        text = self.get_metadata(CARD_MANA_COST)
        if len(text) == 0 or "{skip}" in text:
            return

        overlay = False
        if "{last}" in text:
            text = text.replace("{last}", "")
            overlay = True

        text = re.sub(r"{+|}+", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        image = Image.new("RGBA", (self.TITLE_BOX_WIDTH, self.TITLE_BOX_HEIGHT), (0, 0, 0, 0))

        if self.MANA_COST_SYMBOL_SPACING > 0:
            curr_x = self.TITLE_BOX_WIDTH - self.MANA_COST_SYMBOL_SPACING - self.MANA_COST_SYMBOL_OUTLINE_SIZE
        else:
            curr_x = self.TITLE_BOX_WIDTH - self.MANA_COST_SYMBOL_OUTLINE_SIZE
        for sym in reversed(text.split(" ")):
            symbol = PLAYTEST_SYMBOL_PLACEHOLDER_KEY.get(sym.strip().lower(), None)
            if symbol is None:
                log(f"Unknown placeholder for playtest card: '{{{sym.strip().lower()}}}'. Using regular symbol...")
                symbol = SYMBOL_PLACEHOLDER_KEY.get(sym.strip().lower(), None)
                if symbol is None:
                    log(f"STILL unknown placeholder: '{{{sym.strip().lower()}}}'.")
                    continue

            scale = self.MANA_COST_SYMBOL_SIZE / symbol.image.height
            width = int(symbol.image.width * scale)
            height = int(symbol.image.height * scale)
            symbol_image = add_drop_shadow(
                symbol.get_formatted_image(width, height, self.MANA_COST_SYMBOL_OUTLINE_SIZE),
                self.MANA_COST_SYMBOL_SHADOW_OFFSET,
            )

            curr_x -= symbol_image.width + self.MANA_COST_SYMBOL_SPACING
            if curr_x >= symbol_image.width:
                image.alpha_composite(symbol_image, (int(curr_x), (self.TITLE_BOX_HEIGHT - symbol_image.height) // 2))
            else:
                log("The mana cost is too long and has been cut off.")
                break

        self.mana_cost_x = self.TITLE_BOX_X + curr_x - self.MANA_COST_SYMBOL_SPACING

        layers = self.text_layers if not overlay else self.overlay_layers
        layers.append(Layer(image, (self.TITLE_BOX_X, self.TITLE_BOX_Y)))

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
            rules_texts[1].strip() if len(rules_texts) > 1 else "{bi}TEST CARD{/bi} {i}- Not for constructed play{/i}"
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
