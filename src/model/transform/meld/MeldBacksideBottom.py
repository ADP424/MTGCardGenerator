from constants import CARD_FRAME_LAYOUT_EXTRAS
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class MeldBacksideBottom(RegularCard):
    """
    A layered image representing the bottom half of a meld backside (see `MeldBacksideTop` for the
    top half, and `MeldBacksideMiddle` for the plain art strip between them). Together, the three
    halves' physical cards line up to form one large landscape image.

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

        # Overall Card
        self.CARD_WIDTH = 2814
        self.CARD_HEIGHT = 2010

        # Type Box
        self.TYPE_BOX_Y = 260
        self.TYPE_BOX_HEIGHT = 218

        # Type Text
        self.TYPE_X = 241 if "pip" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, []) else 374
        self.TYPE_BOTTOM_Y = 446
        self.TYPE_WIDTH = 2462
        self.TYPE_MAX_FONT_SIZE = 128
        self.TYPE_FONT_COLOR = (255, 255, 255)

        # Rules Text Box
        self.RULES_BOX_X = 208
        self.RULES_BOX_Y = 507
        self.RULES_BOX_WIDTH = 2400
        self.RULES_BOX_HEIGHT = 1195

        # Rules Text
        self.RULES_TEXT_X = 208
        self.RULES_TEXT_Y = 507
        self.RULES_TEXT_WIDTH = 2400
        self.RULES_TEXT_HEIGHT = 1195
        self.RULES_TEXT_MAX_FONT_SIZE = 147

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 2190
        self.POWER_TOUGHNESS_Y = 1568
        self.POWER_TOUGHNESS_WIDTH = 466
        self.POWER_TOUGHNESS_HEIGHT = 223
        self.POWER_TOUGHNESS_FONT_SIZE = 154
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)

        # Set / Rarity Symbol (doesn't get used on backsides but just in case)
        self.SET_SYMBOL_X = 2431
        self.SET_SYMBOL_Y = 284
        self.SET_SYMBOL_WIDTH = 170

        # Footer
        self.FOOTER_ROTATION = 0
        self.FOOTER_X = 181
        self.FOOTER_Y = 1765
        self.FOOTER_WIDTH = 2455
        self.FOOTER_HEIGHT = 260
        self.FOOTER_FONT_SIZE = 66

        # Other
        self.HOLO_STAMP_X = float("inf")
        self.HOLO_STAMP_Y = float("inf")

    def create_layers(
        self,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_watermark_layer: bool = True,
        create_footer_layer: bool = True,
        create_type_layer: bool = True,
        create_rules_text_layer: bool = True,
        create_power_toughness_layer: bool = True,
        create_overlay_layers: bool = True,
    ):
        """
        Append every frame, text, and collector layer to the card based on `self.metadata`. Everything
        a normal card would show is drawn here except the title, which belongs on `MeldBacksideTop`.

        Parameters
        ----------
        create_art_layer: bool, default: True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default: True
            Whether to put the card's frames on or not.

        create_watermark_layer: bool, default: True
            Whether to put the watermark on the card or not.

        create_rarity_symbol_layer: bool, default: True
            Whether to put the rarity/set symbol on the card or not.

        create_footer_layer: bool, default: True
            Whether to put the footer collector info on the bottom of the card or not.

        create_type_layer: bool, default: True
            Whether to put the type line of the card on it or not.

        create_rules_text_layer: bool, default: True
            Whether to put the rules text of the card on it or not.

        create_power_toughness_layer: bool, default: True
            Whether to put the power & toughness of the card on it or not.

        create_overlay_layers: bool, default: True
            Whether to put the overlays on top of the card after everything else or not.
        """

        if create_art_layer:
            self._create_art_layer()

        if create_frame_layers:
            self._create_frame_layers()

        if create_watermark_layer:
            self._create_watermark_layer()

        if create_footer_layer:
            self._create_footer_layer()

        if create_type_layer:
            self._create_type_layer()

        if create_rules_text_layer:
            self._create_rules_text_layer()

        if create_power_toughness_layer:
            self._create_power_toughness_layer()

        if create_overlay_layers:
            self._create_overlay_layers()
