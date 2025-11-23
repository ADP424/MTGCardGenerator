from PIL import Image, ImageDraw, ImageFont

from constants import BELEREN_BOLD_SMALL_CAPS, CARD_TRANSFORM_HINT
from model.regular.RegularCard import RegularCard
from model.Layer import Layer


class TransformFrontside(RegularCard):
    """
    A layered image representing a transform frontside and all the collection info on it,
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
        self.TITLE_BOX_X = 220
        self.TITLE_BOX_WIDTH = 1183

        # Title Text
        self.TITLE_X = 240
        self.TITLE_WIDTH = 1158

        # Reverse Power & Toughness Text
        self.REVERSE_POWER_TOUGHNESS_X = 1301
        self.REVERSE_POWER_TOUGHNESS_Y = 1767
        self.REVERSE_POWER_TOUGHNESS_WIDTH = 90
        self.REVERSE_POWER_TOUGHNESS_HEIGHT = 71
        self.REVERSE_POWER_TOUGHNESS_FONT_SIZE = 60
        self.REVERSE_POWER_TOUGHNESS_FONT_COLOR = (102, 102, 102)

    def create_layers(
        self,
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
        create_reverse_power_toughness_layer: bool = True,
        create_overlay_layers: bool = True,
    ):
        """
        Append every frame, text, and collector layer to the card based on `self.metadata`.

        Parameters
        ----------
        create_art_layer: bool, default: True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default: True
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

        create_reverse_power_toughness_layer: bool, default: True
            Whether to put the reverse power & toughness of the card on it or not.

        create_overlay_layers: bool, default: True
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

        if create_reverse_power_toughness_layer:
            self._create_reverse_power_toughness_layer()

    def _create_reverse_power_toughness_layer(self):
        """
        Process reverse power & toughness text for transform cards and append it to `self.text_layers`.
        """

        text = self.get_metadata(CARD_TRANSFORM_HINT).replace("*", "★")
        if len(text) == 0 or "{skip}" in text:
            return

        power_toughness_font = ImageFont.truetype(BELEREN_BOLD_SMALL_CAPS, self.REVERSE_POWER_TOUGHNESS_FONT_SIZE)
        symbol_backup_font = ImageFont.truetype(self.SYMBOL_FONT, self.FOOTER_FONT_SIZE)
        emoji_backup_font = ImageFont.truetype(self.EMOJI_FONT, self.FOOTER_FONT_SIZE)
        image = Image.new(
            "RGBA", (self.REVERSE_POWER_TOUGHNESS_WIDTH, self.REVERSE_POWER_TOUGHNESS_HEIGHT), (0, 0, 0, 0)
        )
        draw = ImageDraw.Draw(image)

        text_width = self._get_ucs_chunks_length(text, power_toughness_font, symbol_backup_font, emoji_backup_font)
        bounding_box = power_toughness_font.getbbox(text)
        text_height = int(bounding_box[3] - bounding_box[1])
        self._draw_ucs_chunks(
            draw,
            (
                (self.REVERSE_POWER_TOUGHNESS_WIDTH - text_width) // 2,
                (self.REVERSE_POWER_TOUGHNESS_HEIGHT - text_height) // 2,
            ),
            text,
            power_toughness_font,
            symbol_backup_font,
            emoji_backup_font,
            fill=self.REVERSE_POWER_TOUGHNESS_FONT_COLOR,
            anchor="lt",
        )

        self.text_layers.append(Layer(image, (self.REVERSE_POWER_TOUGHNESS_X, self.REVERSE_POWER_TOUGHNESS_Y)))
