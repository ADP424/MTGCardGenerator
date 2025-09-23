import re
from PIL import Image, ImageDraw, ImageFont

from constants import (
    CARD_MANA_COST,
    CARD_RULES_TEXT,
    CARD_TITLE,
    CLASS_HEADER,
    MPLANTIN,
    SYMBOL_PLACEHOLDER_KEY,
)
from model.RegularCard import RegularCard
from model.Layer import Layer
from log import log


class RegularClass(RegularCard):
    """
    A layered image representing a regular enchantment class and all the collection info on it,
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

        # Title Text
        self.TITLE_Y = 105

        # Type Text
        self.TYPE_Y = 1782

        # Level Text
        self.LEVEL_FONT = MPLANTIN
        self.LEVEL_FONT_SIZE = 58

        # Rules Text Box
        self.RULES_BOX_X = 752
        self.RULES_BOX_Y = 238
        self.RULES_BOX_WIDTH = 633
        self.RULES_BOX_HEIGHT = 1522

        # Rules Text
        self.RULES_TEXT_X = 752
        self.RULES_TEXT_Y = 238
        self.RULES_TEXT_WIDTH = 633
        self.RULES_TEXT_HEIGHT = 1522

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1305
        self.SET_SYMBOL_Y = 1795
        self.SET_SYMBOL_WIDTH = 80

        # Extract level names from the card title
        titles = self.get_metadata(CARD_TITLE).split("{N}")
        self.level_titles = [level_title.strip() for level_title in titles[1:]]

        # Separate the card mana cost from the level mana costs
        costs = self.get_metadata(CARD_MANA_COST).split("\n")
        self.level_costs = [level_cost.strip() for level_cost in costs[1:]]
        self.set_metadata(CARD_MANA_COST, costs[0].strip())

        # Determine the heights and y-values of each subclass/level rules text
        full_rules_text = self.get_metadata(CARD_RULES_TEXT)
        full_rules_height = self.RULES_TEXT_HEIGHT

        self.RULES_TEXT_HEIGHT = 9999 * self.CARD_HEIGHT  # stop text shrinking to size while measuring
        self.level_rules_texts = [text.strip() for text in full_rules_text.split("{end}")]

        level_heights: list[int] = []
        total_height = 0
        for text in self.level_rules_texts:
            self.metadata[CARD_RULES_TEXT] = text
            _, _, _, content_height, _ = self._get_rules_text_layout(text)
            level_heights.append(content_height)
            total_height += content_height

        self.level_heights: list[int] = []
        self.level_header_y_axes: list[int] = []
        usable_height = full_rules_height - (len(self.level_rules_texts) - 1) * CLASS_HEADER.image.height
        for count, height in enumerate(level_heights):
            proportional_height = (height / total_height) * usable_height
            even_height = usable_height / len(level_heights)
            alpha = 0.5
            final_height = int(alpha * proportional_height + (1 - alpha) * even_height)
            self.level_heights.append(final_height)
            self.level_header_y_axes.append(sum(self.level_heights) + count * CLASS_HEADER.image.height)
        self.level_header_y_axes.pop()

        self.metadata[CARD_RULES_TEXT] = full_rules_text
        self.RULES_TEXT_HEIGHT = full_rules_height

    def create_layers(
        self,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_level_header_frame_layer: bool = True,
        create_watermark_layer: bool = True,
        create_rarity_symbol_layer: bool = True,
        create_footer_layer: bool = True,
        create_mana_cost_layer: bool = True,
        create_title_layer: bool = True,
        create_type_layer: bool = True,
        create_rules_text_layer: bool = True,
        create_power_toughness_layer: bool = True,
        create_level_headers_layers: bool = True,
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

        create_level_header_frame_layer: bool, default : True
            Whether to put the header frames for the level titles above the rules text or not.

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

        create_level_headers_layers: bool, default : True
            Whether to put the name and mana cost of each level on the class or not.

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

        if create_level_header_frame_layer:
            self._create_level_header_frame_layer()

        if create_level_headers_layers:
            self._create_level_headers_layers()

    def _create_watermark_layer(self):
        """
        Process a watermark image and append it to `self.collector_layers`.
        Assumes the image is in RGBA format.
        """

        full_rules_box_y = self.RULES_BOX_Y
        full_rules_box_height = self.RULES_BOX_HEIGHT

        target_y = self.RULES_BOX_Y + sum(self.level_heights[:(len(self.level_heights) - 1) // 2]) + CLASS_HEADER.image.height
        target_height = self.level_heights[(len(self.level_heights) - 1) // 2]
        self.RULES_BOX_Y = target_y
        self.RULES_BOX_HEIGHT = target_height
        super()._create_watermark_layer()

        self.RULES_BOX_Y = full_rules_box_y
        self.RULES_BOX_HEIGHT = full_rules_box_height


    def _create_level_header_frame_layer(self):
        """
        Create the header frames for each class level above the rules text area.
        """

        class_header = CLASS_HEADER.get_formatted_image()
        class_header_image = Image.new("RGBA", (self.RULES_BOX_WIDTH, self.RULES_BOX_HEIGHT), (0, 0, 0, 0))
        for header_y_axis in self.level_header_y_axes:
            class_header_image.alpha_composite(
                class_header,
                (
                    0,
                    header_y_axis,
                ),
            )
        self.frame_layers.append(Layer(class_header_image, (self.RULES_BOX_X, self.RULES_BOX_Y)))


    def _create_title_layer(self):
        """
        Process title text into the title and append it to `self.text_layers`.
        """

        full_card_title = self.get_metadata(CARD_TITLE)
        self.set_metadata(CARD_TITLE, full_card_title.split("{N}")[0])
        super()._create_title_layer()
        self.set_metadata(CARD_TITLE, full_card_title)

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`. Do this once for each level because this is a class.
        """

        full_rules_y = self.RULES_TEXT_Y
        full_rules_height = self.RULES_TEXT_HEIGHT
        full_rules_text = self.get_metadata(CARD_RULES_TEXT)

        curr_y = full_rules_y
        for idx, text in enumerate(self.level_rules_texts):
            self.RULES_TEXT_Y = curr_y
            self.RULES_TEXT_HEIGHT = self.level_heights[idx]
            self.metadata[CARD_RULES_TEXT] = text
            super()._create_rules_text_layer()

            curr_y += self.level_heights[idx]
            if idx < len(self.level_rules_texts) - 1:
                curr_y += CLASS_HEADER.image.height

        self.RULES_TEXT_Y = full_rules_y
        self.RULES_TEXT_HEIGHT = full_rules_height
        self.metadata[CARD_RULES_TEXT] = full_rules_text

    def _create_level_headers_layers(self):
        """
        Create the level mana costs and headers as text layers on top of the header frames.
        """

        level_font = ImageFont.truetype(self.LEVEL_FONT, self.LEVEL_FONT_SIZE)
        colon_font = ImageFont.truetype(self.LEVEL_FONT, int(self.RULES_TEXT_MANA_SYMBOL_SCALE * self.MANA_COST_SYMBOL_SIZE))

        for idx, level_y in enumerate(self.level_header_y_axes):
            image = Image.new("RGBA", (self.RULES_TEXT_WIDTH, CLASS_HEADER.image.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            # Draw the mana cost
            cost = re.sub(r"{+|}+", " ", self.level_costs[idx] if idx < len(self.level_costs) else "")
            cost = re.sub(r"\s+", " ", cost)
            cost = cost.strip()

            if len(cost) > 0:
                curr_x = self.LEVEL_FONT_SIZE // 4
                for sym in cost.split(" "):
                    symbol = SYMBOL_PLACEHOLDER_KEY.get(sym.strip().lower(), None)
                    if symbol is None:
                        log(f"Unknown placeholder '{{{sym}}}'")
                        continue

                    scale = self.LEVEL_FONT_SIZE * self.RULES_TEXT_MANA_SYMBOL_SCALE / symbol.image.height
                    width = int(symbol.image.width * scale)
                    height = int(symbol.image.height * scale)
                    symbol_image = symbol.get_formatted_image(width, height)

                    if curr_x < self.RULES_TEXT_WIDTH:
                        image.alpha_composite(
                            symbol_image, (curr_x, (CLASS_HEADER.image.height - symbol_image.height) // 2)
                        )
                    else:
                        log("The mana cost is too long and has been cut off.")
                        break
                    curr_x += symbol_image.width + self.MANA_COST_SYMBOL_SPACING

                colon_bounding_box = level_font.getbbox(":")
                colon_height = int(colon_bounding_box[3] - colon_bounding_box[1])
                draw.text((curr_x, (CLASS_HEADER.image.height - colon_height) // 2), ":", font=colon_font, fill="black", anchor="lt")

            # Draw the level title
            level_title = self.level_titles[idx] if idx < len(self.level_titles) else f"Level {idx + 1}"
            centered = len(cost) == 0
            title_length = level_font.getlength(level_title)
            if not centered:
                x_pos = self.RULES_TEXT_WIDTH - title_length - self.LEVEL_FONT_SIZE // 2
            else:
                x_pos = (self.RULES_TEXT_WIDTH - title_length) // 2

            ascent = level_font.getmetrics()[0]
            draw.text(
                (x_pos, (CLASS_HEADER.image.height - ascent) // 2),
                level_title,
                font=level_font,
                fill="black",
                anchor="lt",
                align="right" if not centered else "center",
            )

            self.text_layers.append(Layer(image, (self.RULES_TEXT_X, self.RULES_TEXT_Y + level_y)))
