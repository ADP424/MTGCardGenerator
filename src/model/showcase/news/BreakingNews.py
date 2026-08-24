from PIL import Image, ImageDraw, ImageFont

from constants import (
    ARIAL_BLACK,
    CARD_RARITY,
    CARD_RULES_TEXT,
    CARD_SET,
    CARD_SUBTYPES,
    CARD_SUPERTYPES,
    CARD_TITLE,
    CARD_TYPES,
    HELVETICA_NEUE_ITALICS,
    HELVETICA_NEUE_MEDIUM,
    SET_SYMBOLS_PATH,
)
from log import log
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from utils import add_drop_shadow, load_font, open_image, replace_ticks


class BreakingNews(RegularCard):
    """
    A layered image representing a "breaking news" broadcast-styled showcase card and all the
    collection info on it, with all relevant card metadata.

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
        self.CARD_WIDTH = 2100
        self.CARD_HEIGHT = 1500

        # Mana Cost Box
        self.TITLE_BOX_X = 1363
        self.TITLE_BOX_Y = 62
        self.TITLE_BOX_WIDTH = 636
        self.TITLE_BOX_HEIGHT = 206
        self.MANA_COST_ALIGN = "center"
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_SYMBOL_OUTLINE_SIZE = 6
        self.MANA_COST_SYMBOL_SIZE = 100

        # Set / Rarity Symbol Box
        self.SET_SYMBOL_X = 101
        self.SET_SYMBOL_Y = 823
        self.SET_SYMBOL_WIDTH = 446
        self.SET_SYMBOL_HEIGHT = 347
        self.SET_SYMBOL_SCALE = 0.8

        # Title/Type Box
        self.TITLE_TYPE_BOX_X = 587
        self.TITLE_TYPE_BOX_Y = 823
        self.TITLE_TYPE_BOX_WIDTH = 1412
        self.TITLE_TYPE_BOX_HEIGHT = 116
        self.TITLE_TYPE_BOX_MARGIN = 40
        self.TITLE_TYPE_BULLET_GAP = 24

        self.TITLE_FONT = ARIAL_BLACK
        self.TITLE_FONT_COLOR = (255, 255, 255)
        self.TITLE_MAX_FONT_SIZE = 80
        self.TITLE_MIN_FONT_SIZE = 6

        self.TYPE_FONT = ARIAL_BLACK
        self.TYPE_FONT_COLOR = (255, 255, 255)
        # The type line's max font size relative to the title's current font size
        self.TYPE_TO_TITLE_FONT_SIZE_RATIO = 0.75
        self.TYPE_MIN_FONT_SIZE = 6

        # Rules Text Box
        self.RULES_BOX_X = 587
        self.RULES_BOX_Y = 947
        self.RULES_BOX_WIDTH = 1412
        self.RULES_BOX_HEIGHT = 322

        # Rules Text
        self.RULES_TEXT_X = 587
        self.RULES_TEXT_Y = 947
        self.RULES_TEXT_WIDTH = 1412
        self.RULES_TEXT_HEIGHT = 322
        self.RULES_TEXT_FONT = HELVETICA_NEUE_MEDIUM
        self.RULES_TEXT_FONT_ITALICS = HELVETICA_NEUE_ITALICS
        self.RULES_TEXT_FONT_COLOR = (0, 0, 0)
        self.RULES_TEXT_MAX_FONT_SIZE = 70

        # Second Rules Text Box
        self.SECOND_RULES_BOX_X = 101
        self.SECOND_RULES_BOX_Y = 1178
        self.SECOND_RULES_BOX_WIDTH = 446
        self.SECOND_RULES_BOX_HEIGHT = 91

        # Second Rules Text
        self.SECOND_RULES_TEXT_X = 101
        self.SECOND_RULES_TEXT_Y = 1178
        self.SECOND_RULES_TEXT_WIDTH = 446
        self.SECOND_RULES_TEXT_HEIGHT = 91
        self.SECOND_RULES_TEXT_FONT_COLOR = (255, 255, 255)
        self.SECOND_RULES_TEXT_MAX_FONT_SIZE = 48

        # Footer
        self.FOOTER_ROTATION = 0
        self.FOOTER_X = 101
        self.FOOTER_Y = 1420
        self.FOOTER_WIDTH = self.CARD_WIDTH - 2 * 101
        self.FOOTER_HEIGHT = 95
        self.FOOTER_FONT_SIZE = 24
        self.FOOTER_FONT_OUTLINE_SIZE = 2
        self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO = 2
        self.FOOTER_TAB_LENGTH = 18
        self.FOOTER_ARTIST_GAP_LENGTH = 4

    def _create_type_layer(self):
        """
        Do nothing. On breaking news cards the type line shares the title/type bar with the
        title and is rendered by `_create_title_layer` instead, since the two need to shrink
        together as a single unit.
        """

        return

    def _get_type_line_text(self) -> str:
        """
        Build the plain type line text (supertypes + types [+ em-dash + subtypes]), directive-free.

        Returns
        -------
        str
            The type line text, with directives already stripped.
        """

        supertypes, _ = self._extract_directives(self.get_metadata(CARD_SUPERTYPES))
        types, _ = self._extract_directives(self.get_metadata(CARD_TYPES))
        subtypes, _ = self._extract_directives(self.get_metadata(CARD_SUBTYPES))

        first_part = f"{replace_ticks(supertypes)} {replace_ticks(types)}"
        second_part = replace_ticks(subtypes)
        if len(second_part) > 0:
            text = " — ".join((first_part, second_part)).strip()
        else:
            text = first_part.strip()
        return text

    def _create_title_layer(self):
        """
        Process the title and type line into the shared title/type bar, separated by a bullet.
        Both shrink together (keeping the title strictly bigger than the type line) until the
        combined text fits the box, then append the result to `self.text_layers`.
        """

        title_text, directives = self._extract_directives(self.get_metadata(CARD_TITLE))
        title_text = replace_ticks(title_text)
        title_text = title_text.replace("{skip}", "")
        offset_x, offset_y = self._get_directive_offset(directives)

        type_text = replace_ticks(self._get_type_line_text())

        if len(title_text) == 0 and len(type_text) == 0:
            return

        max_width = self.TITLE_TYPE_BOX_WIDTH - 2 * self.TITLE_TYPE_BOX_MARGIN

        def measure(
            title_font_size: int, type_font_size: int
        ) -> tuple[int, ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
            title_font = load_font(self.TITLE_FONT, title_font_size)
            type_font = load_font(self.TYPE_FONT, type_font_size)
            title_fallback_fonts = self._load_fallback_fonts(self.TITLE_FONT, title_font_size)
            type_fallback_fonts = self._load_fallback_fonts(self.TYPE_FONT, type_font_size)

            width = 0
            if len(title_text) > 0:
                width += self._get_ucs_chunks_length(title_text, title_font, title_fallback_fonts)
            if len(title_text) > 0 and len(type_text) > 0:
                width += self.TITLE_TYPE_BULLET_GAP + title_font.getlength("•") + self.TITLE_TYPE_BULLET_GAP
            if len(type_text) > 0:
                width += self._get_ucs_chunks_length(type_text, type_font, type_fallback_fonts)
            return int(width), title_font, type_font

        title_font_size = self.TITLE_MAX_FONT_SIZE
        type_font_size = max(int(title_font_size * self.TYPE_TO_TITLE_FONT_SIZE_RATIO), self.TYPE_MIN_FONT_SIZE)
        total_width, title_font, type_font = measure(title_font_size, type_font_size)

        while (
            total_width > max_width
            and title_font_size > self.TITLE_MIN_FONT_SIZE
            and type_font_size > self.TYPE_MIN_FONT_SIZE
        ):
            title_font_size -= 1
            type_font_size = max(int(title_font_size * self.TYPE_TO_TITLE_FONT_SIZE_RATIO), self.TYPE_MIN_FONT_SIZE)
            total_width, title_font, type_font = measure(title_font_size, type_font_size)

        title_fallback_fonts = self._load_fallback_fonts(self.TITLE_FONT, title_font_size)
        type_fallback_fonts = self._load_fallback_fonts(self.TYPE_FONT, type_font_size)

        image = Image.new("RGBA", (self.TITLE_TYPE_BOX_WIDTH, self.TITLE_TYPE_BOX_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        title_ascent, title_descent = title_font.getmetrics()
        type_ascent, type_descent = type_font.getmetrics()
        title_y = (self.TITLE_TYPE_BOX_HEIGHT - (title_ascent + title_descent)) // 2
        type_y = (self.TITLE_TYPE_BOX_HEIGHT - (type_ascent + type_descent)) // 2

        curr_x = self.TITLE_TYPE_BOX_MARGIN
        if len(title_text) > 0:
            self._draw_ucs_chunks(
                draw,
                (curr_x, title_y),
                title_text,
                title_font,
                title_fallback_fonts,
                primary_font_path=self.TITLE_FONT,
                font_size=title_font_size,
                fill=self.TITLE_FONT_COLOR,
            )
            curr_x += self._get_ucs_chunks_length(title_text, title_font, title_fallback_fonts)

        if len(title_text) > 0 and len(type_text) > 0:
            curr_x += self.TITLE_TYPE_BULLET_GAP
            bullet_y = title_y
            draw.text((curr_x, bullet_y), "•", font=title_font, fill=self.TITLE_FONT_COLOR)
            curr_x += int(title_font.getlength("•")) + self.TITLE_TYPE_BULLET_GAP

        if len(type_text) > 0:
            self._draw_ucs_chunks(
                draw,
                (curr_x, type_y),
                type_text,
                type_font,
                type_fallback_fonts,
                primary_font_path=self.TYPE_FONT,
                font_size=type_font_size,
                fill=self.TYPE_FONT_COLOR,
            )

        image = add_drop_shadow(image, self.TITLE_TEXT_DROP_SHADOW_RELATIVE_OFFSET)

        self.text_layers.append(Layer(image, (self.TITLE_TYPE_BOX_X + offset_x, self.TITLE_TYPE_BOX_Y + offset_y)))

    def _create_rarity_symbol_layer(self):
        """
        Process the rarity/set symbol and append it to `self.collector_layers`, scaled to fill
        (but not exceed) the left blue box, and centered within it.
        """

        card_set = self.get_metadata(CARD_SET).lower().replace(" ", "_")
        if len(card_set) == 0:
            return

        rarity = self.get_metadata(CARD_RARITY).lower()
        if rarity in ("token", "land"):
            rarity = "common"
        if len(rarity) == 0 or "{skip}" in rarity:
            return

        overlay = False
        if "{last}" in rarity:
            rarity = rarity.replace("{last}", "")
            overlay = True

        symbol_path = f"{SET_SYMBOLS_PATH}/{card_set}/{rarity}.png"
        rarity_symbol = open_image(symbol_path)
        if rarity_symbol is None:
            log(f"Could not find rarity symbol at '{symbol_path}'.")
            return

        scale = (
            min(self.SET_SYMBOL_WIDTH / rarity_symbol.width, self.SET_SYMBOL_HEIGHT / rarity_symbol.height)
            * self.SET_SYMBOL_SCALE
        )
        width = max(int(rarity_symbol.width * scale), 1)
        height = max(int(rarity_symbol.height * scale), 1)
        rarity_symbol = rarity_symbol.resize((width, height))

        position = (
            self.SET_SYMBOL_X + (self.SET_SYMBOL_WIDTH - width) // 2,
            self.SET_SYMBOL_Y + (self.SET_SYMBOL_HEIGHT - height) // 2,
        )

        layers = self.collector_layers if not overlay else self.overlay_layers
        layers.append(Layer(rarity_symbol, position))

    def _create_rules_text_layer(self):
        """
        Process MTG rules text into the gray rules text box, and optionally a short second rules
        text (after "{end}") into the red box below the rarity symbol - meant for a land's mana
        ability. Exchanges placeholders for symbols and text formatting as usual.
        """

        full_rules_text = self.get_metadata(CARD_RULES_TEXT)
        rules_texts = full_rules_text.split("{end}")
        main_rules_text = rules_texts[0].strip()
        second_rules_text = rules_texts[1].strip() if len(rules_texts) > 1 else ""

        main_rules_box = (self.RULES_BOX_X, self.RULES_BOX_Y, self.RULES_BOX_WIDTH, self.RULES_BOX_HEIGHT)
        main_rules_text_box = (self.RULES_TEXT_X, self.RULES_TEXT_Y, self.RULES_TEXT_WIDTH, self.RULES_TEXT_HEIGHT)
        main_font_color = self.RULES_TEXT_FONT_COLOR
        main_max_font_size = self.RULES_TEXT_MAX_FONT_SIZE

        self.set_metadata(CARD_RULES_TEXT, main_rules_text)
        super()._create_rules_text_layer()

        if len(second_rules_text) > 0:
            self.RULES_BOX_X, self.RULES_BOX_Y, self.RULES_BOX_WIDTH, self.RULES_BOX_HEIGHT = (
                self.SECOND_RULES_BOX_X,
                self.SECOND_RULES_BOX_Y,
                self.SECOND_RULES_BOX_WIDTH,
                self.SECOND_RULES_BOX_HEIGHT,
            )
            self.RULES_TEXT_X, self.RULES_TEXT_Y, self.RULES_TEXT_WIDTH, self.RULES_TEXT_HEIGHT = (
                self.SECOND_RULES_TEXT_X,
                self.SECOND_RULES_TEXT_Y,
                self.SECOND_RULES_TEXT_WIDTH,
                self.SECOND_RULES_TEXT_HEIGHT,
            )
            self.RULES_TEXT_FONT_COLOR = self.SECOND_RULES_TEXT_FONT_COLOR
            self.RULES_TEXT_MAX_FONT_SIZE = self.SECOND_RULES_TEXT_MAX_FONT_SIZE

            self.set_metadata(CARD_RULES_TEXT, f"{{center}}{second_rules_text}")
            super()._create_rules_text_layer()

            self.RULES_BOX_X, self.RULES_BOX_Y, self.RULES_BOX_WIDTH, self.RULES_BOX_HEIGHT = main_rules_box
            self.RULES_TEXT_X, self.RULES_TEXT_Y, self.RULES_TEXT_WIDTH, self.RULES_TEXT_HEIGHT = main_rules_text_box
            self.RULES_TEXT_FONT_COLOR = main_font_color
            self.RULES_TEXT_MAX_FONT_SIZE = main_max_font_size

        self.set_metadata(CARD_RULES_TEXT, full_rules_text)
