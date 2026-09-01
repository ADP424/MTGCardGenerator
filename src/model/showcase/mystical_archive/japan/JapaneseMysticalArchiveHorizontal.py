from constants import (
    DF_MARU_GOTHIC,
    KLEE_ONE,
    MYSTICAL_ARCHIVE_SYMBOL_PLACEHOLDER_KEY,
    NUD_MOTOYA_EX_APORO,
)
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class JapaneseMysticalArchiveHorizontal(RegularCard):
    """
    A layered image representing a Japanese Mystical Archive frame with a horizontal
    title box (unlike JapaneseMysticalArchive's vertical, expanding title box).

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

        # Showcase-specific symbol art for mana cost + rules text.
        self.MANA_SYMBOL_KEY = MYSTICAL_ARCHIVE_SYMBOL_PLACEHOLDER_KEY

        # Fonts
        self.TITLE_FONT = NUD_MOTOYA_EX_APORO
        self.TYPE_FONT = NUD_MOTOYA_EX_APORO
        self.RULES_TEXT_FONT = DF_MARU_GOTHIC
        self.RULES_TEXT_FONT_ITALICS = KLEE_ONE

        # Title Box
        self.TITLE_BOX_X = 138
        self.TITLE_BOX_Y = 113
        self.TITLE_BOX_WIDTH = 1731
        self.TITLE_BOX_HEIGHT = 162

        # Mana Cost
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)

        # Title Text
        self.TITLE_X = 170
        self.TITLE_BOTTOM_Y = 256
        self.TITLE_WIDTH = 1688
        self.TITLE_FONT_COLOR = (255, 255, 255)

        # Type Box
        self.TYPE_BOX_Y = 1573
        self.TYPE_BOX_HEIGHT = 124

        # Type Text
        self.TYPE_X = 171
        self.TYPE_BOTTOM_Y = 1682
        self.TYPE_WIDTH = 1667

        # Rules Text Box
        self.RULES_BOX_X = 158
        self.RULES_BOX_Y = 1734
        self.RULES_BOX_WIDTH = 1696
        self.RULES_BOX_HEIGHT = 854

        # Rules Text
        self.RULES_TEXT_X = 170
        self.RULES_TEXT_Y = 1746
        self.RULES_TEXT_WIDTH = 1672
        self.RULES_TEXT_HEIGHT = 830

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1721
        self.SET_SYMBOL_Y = 1576
