from PIL import Image, ImageDraw, ImageFont

from constants import (
    CARD_RULES_TEXT,
    MPLANTIN,
    MPLANTIN_BOLD,
    SAGA_BANNER_STRIPE,
    SAGA_CHAPTER_DIVIDING_LINE,
    SAGA_CHAPTER_FRAME,
)
from model.RegularCard import RegularCard
from model.Layer import Layer
from utils import int_to_roman_numeral, paste_image


class RegularSaga(RegularCard):
    """
    A layered image representing a regular saga and all the collection info on it,
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

        # Rules Text Box
        self.RULES_BOX_X = 116
        self.RULES_BOX_Y = 238
        self.RULES_BOX_WIDTH = 633
        self.RULES_BOX_HEIGHT = 1522

        # Saga Ability Text
        self.CHAPTER_TEXT_INDENT = 62

        # Rules Text
        self.RULES_TEXT_X = 116
        self.RULES_TEXT_Y = 238
        self.RULES_TEXT_WIDTH = 633
        self.RULES_TEXT_HEIGHT = 1522

        # Chapter Number Frame
        self.CHAPTER_NUMBER_X = 58
        self.CHAPTER_NUMBER_WIDTH = 118
        self.CHAPTER_NUMBER_HEIGHT = 132

        # Chapter Text
        self.STATIC_TEXT_HEIGHT = 339
        self.STATIC_CHAPTER_TEXT_GAP = 33
        self.CHAPTER_TEXT_START_Y = 620
        self.CHAPTER_NUMBER_FONT = MPLANTIN
        self.CHAPTER_NUMBER_FONT_SIZE = 70
        self.CHAPTER_NUMBER_FONT_COLOR = (0, 0, 0)

        # Banner
        self.BANNER_STRIPE_X = 110
        self.BANNER_STRIPE_Y = 644
        self.BANNER_STRIPE_WIDTH = 12
        self.BANNER_STRIPE_HEIGHT = 1000

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1305
        self.SET_SYMBOL_Y = 1795
        self.SET_SYMBOL_WIDTH = 80

        # Determine the heights and y-values of each ability rules text #
        full_rules_text = self.metadata[CARD_RULES_TEXT]
        full_rules_height = self.RULES_TEXT_HEIGHT

        self.RULES_TEXT_HEIGHT = 9999 * self.CARD_HEIGHT # stop text shrinking to size while measuring

        texts = self.get_metadata(CARD_RULES_TEXT).split("{end}")
        self.static_text = texts[0].strip()
        self.chapter_texts = [text.strip() for text in texts[1:]]

        chapter_heights: list[int] = []
        total_height = 0
        for idx, text in enumerate(self.chapter_texts):
            if idx > 0 and text == self.chapter_texts[idx - 1]:
                chapter_heights.append(chapter_heights[idx - 1])
                chapter_heights[idx - 1] = 0
                continue
            self.metadata[CARD_RULES_TEXT] = text
            _, _, _, _, content_height, _ = self._get_rules_text_layout(text)
            chapter_heights.append(content_height)
            total_height += content_height

        self.chapter_heights: list[int] = []
        for height in chapter_heights:
            if height == 0:
                self.chapter_heights.append(0)
                continue

            proportional_height = (height / total_height) * (
                full_rules_height - (self.STATIC_TEXT_HEIGHT + self.STATIC_CHAPTER_TEXT_GAP)
            )
            even_height = (full_rules_height - (self.STATIC_TEXT_HEIGHT + self.STATIC_CHAPTER_TEXT_GAP)) / ( len(chapter_heights) - chapter_heights.count(0))
            alpha = 0.5
            final_height = int(alpha * proportional_height + (1 - alpha) * even_height)
            self.chapter_heights.append(final_height)

        self.metadata[CARD_RULES_TEXT] = full_rules_text
        self.RULES_TEXT_HEIGHT = full_rules_height

    def create_layers(
        self,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_banner_stripe_layer: bool = True,
        create_chapter_frame_layers: bool = True,
        create_watermark_layer: bool = True,
        create_rarity_symbol_layer: bool = True,
        create_footer_layer: bool = True,
        create_mana_cost_layer: bool = True,
        create_title_layer: bool = True,
        create_type_layer: bool = True,
        create_rules_text_layer: bool = True,
        create_power_toughness_layer: bool = True,
        create_chapter_number_layers: bool = True,
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

        create_banner_stripe_layer: bool, default : True
            Whether to put the stripe over the saga's banners on the left or not.

        create_chapter_frame_layers: bool, default : True
            Whether to put the saga's chapter number frames on or not.

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

        create_chapter_number_layers: bool, default : True
            Whether to put the number of each saga chapter on the saga or not.

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

        if create_banner_stripe_layer:
            self._create_banner_stripe_layer()

        if create_chapter_frame_layers:
            self._create_chapter_frame_layers()

        if create_chapter_number_layers:
            self._create_chapter_number_layers()

    def _create_banner_stripe_layer(self):
        """
        Create the stripe over the banner on the left of the saga, above the rest of the frame, below the chapter frames.
        """

        banner_stripe = SAGA_BANNER_STRIPE.get_formatted_image(self.BANNER_STRIPE_WIDTH, self.BANNER_STRIPE_HEIGHT)
        self.frame_layers.append(Layer(banner_stripe, (self.BANNER_STRIPE_X, self.BANNER_STRIPE_Y)))

    def _create_chapter_frame_layers(self):
        """
        Create the frames for the costs of each chapter number, above the rest of the frame.
        """

        chapter_frame_image = Image.new(
            "RGBA",
            (
                self.RULES_BOX_WIDTH + (self.RULES_BOX_X - self.CHAPTER_NUMBER_X - self.CHAPTER_TEXT_INDENT),
                self.RULES_BOX_HEIGHT - (self.STATIC_TEXT_HEIGHT + self.STATIC_CHAPTER_TEXT_GAP),
            ),
            (0, 0, 0, 0),
        )
        curr_y = 0

        self.chapter_number_y_axes: list[int] = []
        pending_frames = 1
        for height in self.chapter_heights:

            # if this chapter text is the same as the following one, hold the frame
            if height == 0:
                pending_frames += 1
                continue

            chapter_frame = SAGA_CHAPTER_FRAME.get_formatted_image(
                self.CHAPTER_NUMBER_WIDTH,
                int((self.CHAPTER_NUMBER_WIDTH / SAGA_CHAPTER_FRAME.image.width) * SAGA_CHAPTER_FRAME.image.height),
            )

            curr_segment_y = curr_y
            for _ in range(1, pending_frames + 1):
                segment_height = height // pending_frames

                paste_y = max(curr_segment_y + (segment_height - chapter_frame.height) // 2, curr_segment_y)
                chapter_frame_image = paste_image(chapter_frame, chapter_frame_image, (0, paste_y))

                self.chapter_number_y_axes.append(
                    self.RULES_BOX_Y
                    + self.STATIC_TEXT_HEIGHT
                    + self.STATIC_CHAPTER_TEXT_GAP
                    + paste_y
                    + chapter_frame.height // 2
                )

                curr_segment_y += segment_height

            pending_frames = 1
            curr_y += height

        self.frame_layers.append(
            Layer(
                chapter_frame_image,
                (self.CHAPTER_NUMBER_X, self.RULES_BOX_Y + self.STATIC_TEXT_HEIGHT + self.STATIC_CHAPTER_TEXT_GAP),
            )
        )

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`. Do this once for each ability because this is a saga.
        """

        full_rules_x = self.RULES_TEXT_X
        full_rules_y = self.RULES_TEXT_Y
        full_rules_width = self.RULES_TEXT_WIDTH
        full_rules_height = self.RULES_TEXT_HEIGHT
        full_rules_text = self.metadata[CARD_RULES_TEXT]

        saga_chapter_dividing_line = SAGA_CHAPTER_DIVIDING_LINE.get_formatted_image()
        dividing_lines_image = Image.new("RGBA", (self.RULES_BOX_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))

        self.RULES_TEXT_Y = full_rules_y
        self.RULES_TEXT_HEIGHT = self.STATIC_TEXT_HEIGHT
        self.metadata[CARD_RULES_TEXT] = self.static_text
        super()._create_rules_text_layer()

        self.RULES_TEXT_X = full_rules_x + self.CHAPTER_TEXT_INDENT
        self.RULES_TEXT_WIDTH = full_rules_width - self.CHAPTER_TEXT_INDENT
        curr_y = full_rules_y
        for idx, text in enumerate(self.chapter_texts):
            if self.chapter_heights[idx] == 0:
                continue

            self.RULES_TEXT_Y = curr_y + (self.STATIC_TEXT_HEIGHT + self.STATIC_CHAPTER_TEXT_GAP)
            self.RULES_TEXT_HEIGHT = self.chapter_heights[idx]
            self.metadata[CARD_RULES_TEXT] = text
            super()._create_rules_text_layer()

            dividing_lines_image.alpha_composite(
                saga_chapter_dividing_line,
                (
                    self.CHAPTER_TEXT_INDENT // 2,
                    self.CHAPTER_TEXT_START_Y + curr_y - full_rules_y - saga_chapter_dividing_line.height,
                ),
            )

            curr_y += self.chapter_heights[idx]

        self.RULES_TEXT_X = full_rules_x
        self.RULES_TEXT_Y = full_rules_y
        self.RULES_TEXT_WIDTH = full_rules_width
        self.RULES_TEXT_HEIGHT = full_rules_height
        self.metadata[CARD_RULES_TEXT] = full_rules_text

        self.text_layers.append(Layer(dividing_lines_image, (self.RULES_BOX_X, 0)))

    def _create_chapter_number_layers(self):
        """
        Create the chapter numbers over each chapter number frame.
        Depends on the chapter frames being rendered first (to know the frame positions).
        """

        chapter_number_font = ImageFont.truetype(self.CHAPTER_NUMBER_FONT, self.CHAPTER_NUMBER_FONT_SIZE)

        for num in range(len(self.chapter_texts)):
            image = Image.new("RGBA", (self.CHAPTER_NUMBER_WIDTH, self.CHAPTER_NUMBER_HEIGHT), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            numeral = int_to_roman_numeral(num + 1)

            text_width = int(chapter_number_font.getlength(numeral))
            bounding_box = chapter_number_font.getbbox(numeral)
            text_height = int(bounding_box[3] - bounding_box[1])

            draw.text(
                ((self.CHAPTER_NUMBER_WIDTH - text_width) // 2, 0),
                numeral,
                font=chapter_number_font,
                fill=self.CHAPTER_NUMBER_FONT_COLOR,
            )

            y_offset = -bounding_box[1]  # Pillow and it's text metrics...
            self.text_layers.append(
                Layer(
                    image,
                    (
                        self.CHAPTER_NUMBER_X,
                        self.chapter_number_y_axes[num] - text_height // 2 + y_offset,
                    ),
                )
            )
