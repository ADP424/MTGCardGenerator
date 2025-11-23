from constants import CARD_RULES_TEXT
from model.regular.RegularCard import RegularCard
from model.Layer import Layer


class RegularSplitRulesText(RegularCard):
    """
    A layered image representing a regular card but with its rules box split in half vertically,
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
        metadata: dict[str, str | list["RegularCard"]] = None,
        art_layer: Layer = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
        overlay_layers: list[Layer] = None,
    ):
        super().__init__(metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers)

        # First Rules Text Box
        self.FIRST_RULES_BOX_X = 112
        self.FIRST_RULES_BOX_WIDTH = 639

        # Second Rules Text Box
        self.SECOND_RULES_BOX_X = 751
        self.SECOND_RULES_BOX_WIDTH = 639

        # First Rules Text
        self.FIRST_RULES_TEXT_X = 112
        self.FIRST_RULES_TEXT_WIDTH = 636

        # Second Rules Text
        self.SECOND_RULES_TEXT_X = 751
        self.SECOND_RULES_TEXT_WIDTH = 636

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`. Do this once for each ability because this is a planeswalker.
        """

        full_rules_box_x = self.RULES_BOX_X
        full_rules_box_width = self.RULES_BOX_WIDTH
        full_rules_text_x = self.RULES_TEXT_X
        full_rules_text_width = self.RULES_TEXT_WIDTH
        full_rules_text = self.get_metadata(CARD_RULES_TEXT)

        rules_texts = full_rules_text.split("{end}")
        first_rules_text = rules_texts[0].strip()
        second_rules_text = rules_texts[1].strip() if len(rules_texts) > 1 else ""

        self.RULES_BOX_X = self.FIRST_RULES_BOX_X
        self.RULES_BOX_WIDTH = self.FIRST_RULES_BOX_WIDTH
        self.RULES_TEXT_X = self.FIRST_RULES_TEXT_X
        self.RULES_TEXT_WIDTH = self.FIRST_RULES_TEXT_WIDTH
        self.set_metadata(CARD_RULES_TEXT, first_rules_text)
        super()._create_rules_text_layer()

        self.RULES_BOX_X = self.SECOND_RULES_BOX_X
        self.RULES_BOX_WIDTH = self.SECOND_RULES_BOX_WIDTH
        self.RULES_TEXT_X = self.SECOND_RULES_TEXT_X
        self.RULES_TEXT_WIDTH = self.SECOND_RULES_TEXT_WIDTH
        self.set_metadata(CARD_RULES_TEXT, second_rules_text)
        super()._create_rules_text_layer()

        self.RULES_BOX_X = full_rules_box_x
        self.RULES_BOX_WIDTH = full_rules_box_width
        self.RULES_TEXT_X = full_rules_text_x
        self.RULES_TEXT_WIDTH = full_rules_text_width
        self.set_metadata(CARD_RULES_TEXT, full_rules_text)
