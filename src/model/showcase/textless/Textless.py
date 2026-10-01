from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class Textless(RegularCard):
    """
    A layered image representing a card with a textless showcase frame and all the collection info on it,
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

        # Title Text
        self.TITLE_FONT_COLOR = (255, 255, 255)
        self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.03, 0.03)

        # Type Box
        self.TYPE_BOX_Y += 2302

        # Type Text
        self.TYPE_FONT_COLOR = (255, 255, 255)
        self.TYPE_BOTTOM_Y = 2426
        self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET = (0.03, 0.03)

        # Set / Rarity Symbol
        self.SET_SYMBOL_Y = 2316

        # Power / Toughness
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)

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

        create_watermark_layer: bool, default: True
            Whether to put the watermark on the card or not. Ignored; a textless frame never has a watermark.

        create_rarity_symbol_layer: bool, default: True
            Whether to put the rarity/set symbol on the card or not.

        create_footer_layer: bool, default: True
            Whether to put the footer collector info on the bottom of the card or not.

        create_mana_cost_layer: bool, default: True
            Whether to put the mana cost of the card on it or not.

        create_title_layer: bool, default: True
            Whether to put the title of the card on it or not.

        create_type_layer: bool, default: True
            Whether to put the type line of the card on it or not.

        create_rules_text_layer: bool, default: True
            Whether to put the rules text of the card on it or not. Ignored; a textless frame never has rules text.

        create_power_toughness_layer: bool, default: True
            Whether to put the power & toughness of the card on it or not.

        create_overlay_layers: bool, default: True
            Whether to put the overlays on top of the card after everything else or not.
        """

        super().create_layers(
            create_art_layer,
            create_frame_layers,
            False,  # a textless frame never has a watermark
            create_rarity_symbol_layer,
            create_footer_layer,
            create_mana_cost_layer,
            create_title_layer,
            create_type_layer,
            False,  # a textless frame never has rules text
            create_power_toughness_layer,
            create_overlay_layers,
        )
