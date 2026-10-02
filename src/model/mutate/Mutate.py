from constants import CARD_RULES_TEXT
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class Mutate(RegularCard):
    """
    A layered image representing a regular card but with its rules box split in half horizontally,
    the top half for the mutate ability and the bottom half for the rest of the rules text, and all
    the collection info on it, with all relevant card metadata.

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

        # Mutate Rules Text Box
        self.MUTATE_RULES_BOX_Y = self.RULES_BOX_Y
        self.MUTATE_RULES_BOX_HEIGHT = 358

        # Second Rules Text Box
        self.SECOND_RULES_BOX_Y = 2122
        self.SECOND_RULES_BOX_HEIGHT = 475

        # Mutate Rules Text
        self.MUTATE_RULES_TEXT_Y = self.RULES_TEXT_Y
        self.MUTATE_RULES_TEXT_HEIGHT = 358

        # Second Rules Text
        self.SECOND_RULES_TEXT_Y = 2126
        self.SECOND_RULES_TEXT_HEIGHT = 470

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`. The mutate ability goes in the top box, the rest of the rules
        text goes in the bottom box.
        """

        full_rules_box_y = self.RULES_BOX_Y
        full_rules_box_height = self.RULES_BOX_HEIGHT
        full_rules_text_y = self.RULES_TEXT_Y
        full_rules_text_height = self.RULES_TEXT_HEIGHT
        full_rules_text = self.get_metadata(CARD_RULES_TEXT)

        rules_texts = full_rules_text.split("{end}")
        mutate_rules_text = rules_texts[0].strip()
        second_rules_text = rules_texts[1].strip() if len(rules_texts) > 1 else ""

        self.RULES_BOX_Y = self.MUTATE_RULES_BOX_Y
        self.RULES_BOX_HEIGHT = self.MUTATE_RULES_BOX_HEIGHT
        self.RULES_TEXT_Y = self.MUTATE_RULES_TEXT_Y
        self.RULES_TEXT_HEIGHT = self.MUTATE_RULES_TEXT_HEIGHT
        self.set_metadata(CARD_RULES_TEXT, mutate_rules_text)
        super()._create_rules_text_layer()

        self.RULES_BOX_Y = self.SECOND_RULES_BOX_Y
        self.RULES_BOX_HEIGHT = self.SECOND_RULES_BOX_HEIGHT
        self.RULES_TEXT_Y = self.SECOND_RULES_TEXT_Y
        self.RULES_TEXT_HEIGHT = self.SECOND_RULES_TEXT_HEIGHT
        self.set_metadata(CARD_RULES_TEXT, second_rules_text)
        super()._create_rules_text_layer()

        self.RULES_BOX_Y = full_rules_box_y
        self.RULES_BOX_HEIGHT = full_rules_box_height
        self.RULES_TEXT_Y = full_rules_text_y
        self.RULES_TEXT_HEIGHT = full_rules_text_height
        self.set_metadata(CARD_RULES_TEXT, full_rules_text)
