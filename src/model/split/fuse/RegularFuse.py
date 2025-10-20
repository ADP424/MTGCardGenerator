from constants import (
    CARD_ADDITIONAL_TITLES,
    CARD_RULES_TEXT,
    CARD_TITLE,
)
from model.regular.RegularCard import RegularCard
from model.Layer import Layer
from model.split.RegularSplit import RegularSplit


class RegularFuse(RegularSplit):
    """
    A layered image representing a split fuse card and all the collection info on it,
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

        # First Rules Box
        self.FIRST_RULES_BOX_HEIGHT = 430

        # Second Rules Box
        self.SECOND_RULES_BOX_HEIGHT = 430

        # First Rules Text
        self.FIRST_RULES_TEXT_HEIGHT = 430

        # Second Rules Text
        self.SECOND_RULES_TEXT_HEIGHT = 430

        # Reminder Rules Text
        self.REMINDER_RULES_TEXT_X = 212
        self.REMINDER_RULES_TEXT_Y = 1337
        self.REMINDER_RULES_TEXT_WIDTH = 1782
        self.REMINDER_RULES_TEXT_HEIGHT = 107
        self.REMINDER_RULES_TEXT_MAX_FONT_SIZE = 60

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text boxes, exchanging placeholders for symbols and text formatting,
        and append them to `self.text_layers`.
        """

        full_rules_text = self.get_metadata(CARD_RULES_TEXT)

        rules_texts = full_rules_text.split("{end}")
        first_rules_text = rules_texts[0].strip()
        second_rules_text = rules_texts[1].strip() if len(rules_texts) > 1 else ""
        reminder_rules_text = (
            rules_texts[2].strip()
            if len(rules_texts) > 2
            else "Fuse {i}(You may cast one or both halves of this card from your hand.){/i}{center}"
        )

        # Do titles correctly so that {cardname} placeholder works as expected
        first_title = self.get_metadata(CARD_TITLE)
        second_title = self.get_metadata(CARD_ADDITIONAL_TITLES).split("\n")[0]

        self.RULES_TEXT_X = self.FIRST_RULES_TEXT_X
        self.RULES_TEXT_Y = self.FIRST_RULES_TEXT_Y
        self.RULES_TEXT_WIDTH = self.FIRST_RULES_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.FIRST_RULES_TEXT_HEIGHT
        self.set_metadata(CARD_RULES_TEXT, first_rules_text)
        self.set_metadata(CARD_TITLE, first_title)
        RegularCard._create_rules_text_layer(self)

        self.RULES_TEXT_X = self.SECOND_RULES_TEXT_X
        self.RULES_TEXT_Y = self.SECOND_RULES_TEXT_Y
        self.RULES_TEXT_WIDTH = self.SECOND_RULES_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.SECOND_RULES_TEXT_HEIGHT
        self.set_metadata(CARD_RULES_TEXT, second_rules_text)
        self.set_metadata(CARD_TITLE, second_title)
        RegularCard._create_rules_text_layer(self)

        rules_text_max_font_size = self.RULES_TEXT_MAX_FONT_SIZE

        self.RULES_TEXT_X = self.REMINDER_RULES_TEXT_X
        self.RULES_TEXT_Y = self.REMINDER_RULES_TEXT_Y
        self.RULES_TEXT_WIDTH = self.REMINDER_RULES_TEXT_WIDTH
        self.RULES_TEXT_HEIGHT = self.REMINDER_RULES_TEXT_HEIGHT
        self.RULES_TEXT_MAX_FONT_SIZE = self.REMINDER_RULES_TEXT_MAX_FONT_SIZE
        self.set_metadata(CARD_RULES_TEXT, reminder_rules_text)
        self.set_metadata(CARD_TITLE, f"{first_title} // {second_title}")
        RegularCard._create_rules_text_layer(self)

        self.RULES_TEXT_MAX_FONT_SIZE = rules_text_max_font_size

        self.set_metadata(CARD_RULES_TEXT, full_rules_text)
        self.set_metadata(CARD_TITLE, first_title)
