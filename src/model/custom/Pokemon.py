from PIL import Image, ImageDraw

from constants import (
    CARD_ADD_TOTAL_TO_FOOTER,
    CARD_ARTIST,
    CARD_CREATION_DATE,
    CARD_FOOTER_LARGEST_INDEX,
    CARD_INDEX,
    CARD_LANGUAGE,
    CARD_POWER_TOUGHNESS,
    CARD_RARITY,
    CARD_SET,
    GILL_SANS,
    GILL_SANS_BOLD,
    GILL_SANS_BOLD_ITALICS,
    GILL_SANS_ITALICS,
    POKEMON_SYMBOL_PLACEHOLDER_KEY,
    RARITY_TO_INITIAL,
)
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from utils import load_font


class Pokemon(RegularCard):
    """
    A layered image representing a card with a custom Pokemon frame and all the collection info
    on it, with all relevant card metadata.

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
        self.MANA_SYMBOL_KEY = POKEMON_SYMBOL_PLACEHOLDER_KEY

        # Title Box
        self.TITLE_BOX_X = 99
        self.TITLE_BOX_Y = 102
        self.TITLE_BOX_WIDTH = 1812
        self.TITLE_BOX_HEIGHT = 215

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 140
        self.MANA_COST_SYMBOL_SPACING = 10
        self.MANA_COST_ALIGN = "right"
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_TEXT_FONT = GILL_SANS_BOLD

        # Title Text
        self.TITLE_X = 150
        self.TITLE_BOTTOM_Y = 300
        self.TITLE_WIDTH = 1300
        self.TITLE_MAX_FONT_SIZE = 132
        self.TITLE_FONT = GILL_SANS_BOLD
        self.TITLE_FONT_COLOR = (0, 0, 0)

        # Type Box
        self.TYPE_BOX_Y = 1500
        self.TYPE_BOX_HEIGHT = 64

        # Type Text
        self.TYPE_X = 403
        self.TYPE_BOTTOM_Y = 1553
        self.TYPE_WIDTH = 1205
        self.TYPE_MAX_FONT_SIZE = 55
        self.TYPE_FONT = GILL_SANS_BOLD_ITALICS
        self.TYPE_FONT_COLOR = (0, 0, 0)
        self.TYPE_TEXT_ALIGN = "center"

        # Rules Text Box
        self.RULES_BOX_X = 100
        self.RULES_BOX_Y = 1588
        self.RULES_BOX_WIDTH = 1815
        self.RULES_BOX_HEIGHT = 1052

        # Rules Text
        self.RULES_TEXT_X = 190
        self.RULES_TEXT_Y = 1600
        self.RULES_TEXT_WIDTH = 1635
        self.RULES_TEXT_HEIGHT = 1025 if len(self.get_metadata(CARD_POWER_TOUGHNESS)) == 0 else 820
        self.RULES_TEXT_FONT = GILL_SANS
        self.RULES_TEXT_FONT_ITALICS = GILL_SANS_ITALICS
        self.RULES_TEXT_FONT_COLOR = (0, 0, 0)
        self.RULES_TEXT_DIVIDER = None

        # Power & Toughness
        self.POWER_LABEL_X = 845
        self.POWER_LABEL_Y = 2445
        self.POWER_LABEL_WIDTH = 306
        self.POWER_LABEL_HEIGHT = 58
        self.TOUGHNESS_LABEL_X = 1522
        self.TOUGHNESS_LABEL_Y = 2445
        self.TOUGHNESS_LABEL_WIDTH = 306
        self.TOUGHNESS_LABEL_HEIGHT = 58
        self.POWER_TOUGHNESS_LABEL_FONT = GILL_SANS_BOLD
        self.POWER_TOUGHNESS_LABEL_FONT_SIZE = 58

        self.POWER_TOUGHNESS_X = 784
        self.POWER_TOUGHNESS_Y = 2500
        self.POWER_TOUGHNESS_WIDTH = 1089
        self.POWER_TOUGHNESS_HEIGHT = 137
        self.TOUGHNESS_X = 1471
        self.POWER_TOUGHNESS_VALUE_WIDTH = 402
        self.POWER_TOUGHNESS_FONT = GILL_SANS_BOLD
        self.POWER_TOUGHNESS_FONT_SIZE = 135
        self.POWER_TOUGHNESS_FONT_COLOR = (0, 0, 0)

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1735
        self.SET_SYMBOL_Y = 1488
        self.SET_SYMBOL_WIDTH = 82

        # Footer
        self.FOOTER_X = 113
        self.FOOTER_Y = 2635
        self.FOOTER_WIDTH = 1790
        self.FOOTER_HEIGHT = 176
        self.FOOTER_FONT = GILL_SANS_BOLD
        self.LEGAL_FONT = GILL_SANS_BOLD
        self.FOOTER_FONT_SIZE = 48
        self.FOOTER_FONT_COLOR = (0, 0, 0)
        self.FOOTER_TAB_LENGTH = 24

    def _create_power_toughness_layer(self):
        """
        Draw "power"/"toughness" labels above their respective values, splitting the card's
        combined "Power/Toughness" metadata (e.g. "5/4") into its two halves.
        """

        text = self.get_metadata(CARD_POWER_TOUGHNESS).strip()
        if len(text) == 0 or "{skip}" in text:
            return

        power, _, toughness = text.partition("/")
        power = power.strip()
        toughness = toughness.strip()

        label_font = load_font(self.POWER_TOUGHNESS_LABEL_FONT, self.POWER_TOUGHNESS_LABEL_FONT_SIZE)
        value_font = load_font(self.POWER_TOUGHNESS_FONT, self.POWER_TOUGHNESS_FONT_SIZE)

        def draw_centered(position, width, height, value, font):
            image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            bbox = font.getbbox(value)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x_pos = (width - text_width) // 2 - bbox[0]
            y_pos = (height - text_height) // 2 - bbox[1]
            draw.text((x_pos, y_pos), value, font=font, fill=self.POWER_TOUGHNESS_FONT_COLOR)
            self.text_layers.append(Layer(image, position))

        draw_centered(
            (self.POWER_LABEL_X, self.POWER_LABEL_Y),
            self.POWER_LABEL_WIDTH,
            self.POWER_LABEL_HEIGHT,
            "power",
            label_font,
        )
        draw_centered(
            (self.TOUGHNESS_LABEL_X, self.TOUGHNESS_LABEL_Y),
            self.TOUGHNESS_LABEL_WIDTH,
            self.TOUGHNESS_LABEL_HEIGHT,
            "toughness",
            label_font,
        )
        draw_centered(
            (self.POWER_TOUGHNESS_X, self.POWER_TOUGHNESS_Y),
            self.POWER_TOUGHNESS_VALUE_WIDTH,
            self.POWER_TOUGHNESS_HEIGHT,
            power,
            value_font,
        )
        draw_centered(
            (self.TOUGHNESS_X, self.POWER_TOUGHNESS_Y),
            self.POWER_TOUGHNESS_VALUE_WIDTH,
            self.POWER_TOUGHNESS_HEIGHT,
            toughness,
            value_font,
        )

    def _create_footer_layer(self):
        """
        Draw "Illus. <artist>" on the left (omitted entirely if no artist is given) and the
        creation date on the right, on the top line. Below those, on the yellow border, draw the
        set name on the left and the index, rarity initial, and language (bullet-separated,
        right-justified) on the right.
        """

        card_set = self.get_metadata(CARD_SET)
        rarity, _ = self._extract_directives(self.get_metadata(CARD_RARITY).lower())
        creation_date = self.get_metadata(CARD_CREATION_DATE)
        language = self.get_metadata(CARD_LANGUAGE)
        artist = self.get_metadata(CARD_ARTIST)

        try:
            add_total_to_footer = int(self.get_metadata(CARD_ADD_TOTAL_TO_FOOTER)) > 0
        except ValueError:
            add_total_to_footer = False
        index = self.get_metadata(CARD_INDEX).zfill(len(str(self.get_metadata(CARD_FOOTER_LARGEST_INDEX))))
        index_text = f"{index}{f"/{self.get_metadata(CARD_FOOTER_LARGEST_INDEX)}" if add_total_to_footer else ""}"
        rarity_initial = RARITY_TO_INITIAL.get(rarity.strip().lower(), "")

        footer_font = load_font(self.FOOTER_FONT, self.FOOTER_FONT_SIZE)
        footer_fallback_fonts = self._load_fallback_fonts(self.FOOTER_FONT, self.FOOTER_FONT_SIZE)

        image = Image.new("RGBA", (self.FOOTER_WIDTH, self.FOOTER_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        ascent, descent = footer_font.getmetrics()
        line_height = ascent + descent
        gap = line_height + line_height // self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO

        if len(artist) > 0:
            self._draw_ucs_chunks(
                draw,
                (0, 0),
                f"Illus. {artist}",
                footer_font,
                footer_fallback_fonts,
                primary_font_path=self.FOOTER_FONT,
                font_size=self.FOOTER_FONT_SIZE,
                fill=self.FOOTER_FONT_COLOR,
            )

        if len(creation_date) > 0:
            creation_date_width = self._get_ucs_chunks_length(creation_date, footer_font, footer_fallback_fonts)
            self._draw_ucs_chunks(
                draw,
                (self.FOOTER_WIDTH - creation_date_width, 0),
                creation_date,
                footer_font,
                footer_fallback_fonts,
                primary_font_path=self.FOOTER_FONT,
                font_size=self.FOOTER_FONT_SIZE,
                fill=self.FOOTER_FONT_COLOR,
            )

        second_line_y = gap
        if len(card_set) > 0:
            self._draw_ucs_chunks(
                draw,
                (0, second_line_y),
                card_set,
                footer_font,
                footer_fallback_fonts,
                primary_font_path=self.FOOTER_FONT,
                font_size=self.FOOTER_FONT_SIZE,
                fill=self.FOOTER_FONT_COLOR,
            )

        language_part = f"{rarity_initial}{" • " if len(rarity_initial) > 0 else ""}{language}"
        parts = [part for part in (index_text, language_part) if len(part) > 0]
        part_widths = [self._get_ucs_chunks_length(part, footer_font, footer_fallback_fonts) for part in parts]
        total_width = sum(part_widths) + self.FOOTER_TAB_LENGTH * max(len(parts) - 1, 0)
        x_pos = self.FOOTER_WIDTH - total_width
        for i, part in enumerate(parts):
            self._draw_ucs_chunks(
                draw,
                (x_pos, second_line_y),
                part,
                footer_font,
                footer_fallback_fonts,
                primary_font_path=self.FOOTER_FONT,
                font_size=self.FOOTER_FONT_SIZE,
                fill=self.FOOTER_FONT_COLOR,
            )
            x_pos += part_widths[i] + self.FOOTER_TAB_LENGTH

        self.text_layers.append(Layer(image, (self.FOOTER_X, self.FOOTER_Y)))
