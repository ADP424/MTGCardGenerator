from constants import NEON_SYMBOL_PLACEHOLDER_KEY
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class Neon(RegularCard):
    """
    A layered image representing a card with a custom neon frame and all the collection info on
    it, with all relevant card metadata. Every text element is positioned exactly as it would be
    on a regular card, but rendered in white to match the frame's neon glow, and mana symbols are
    drawn from a dedicated neon symbol set.

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
        self.MANA_SYMBOL_KEY = NEON_SYMBOL_PLACEHOLDER_KEY

        # Mana Cost
        self.MANA_COST_TEXT_COLOR = (255, 255, 255)
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)

        # Title Text
        self.TITLE_FONT_COLOR = (255, 255, 255)

        # Type Text
        self.TYPE_FONT_COLOR = (255, 255, 255)

        # Rules Text
        self.RULES_TEXT_FONT_COLOR = (255, 255, 255)

        # Power & Toughness Text
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)
