import re

from PIL import Image, ImageDraw

from constants import (
    BARLOW,
    BARLOW_ITALICS,
    CARD_ADDITIONAL_TITLES,
    CARD_RULES_TEXT,
    CARD_SUBTYPES,
    CARD_SUPERTYPES,
    CARD_TITLE,
    CARD_TYPES,
    CARD_WATERMARK_COLOR,
    COLOR_TAG_PATTERN,
    FRAMES_PATH,
    VERAMONO_BOLD,
    WATERMARK_COLORS,
)
from log import log
from model.Layer import Layer
from model.regular.RegularCardSmall import RegularCardSmall
from utils import load_font, open_image, replace_ticks


class Chat(RegularCardSmall):
    """
    A layered image representing a showcase card in the style of a Chat messenger app,
    and all the collection info on it, with all relevant card metadata.

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

    CHAT_TITLE_TOKEN_PATTERN = re.compile(r"chattitle(\d+)", re.IGNORECASE)

    def __init__(
        self,
        metadata: dict[str, str | list["RegularCardSmall"]] = None,
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

        # Chat Window
        # The coordinates are all relative to if a chat window frame was placed at (0, 0)
        # Users position each window and its text with {offset:(x, y)} directives
        self.CHAT_WINDOW_WIDTH = 1350
        self.CHAT_WINDOW_HEIGHT = 475
        self.CHAT_WINDOW_TITLE_BOX_X = 36
        self.CHAT_WINDOW_TITLE_BOX_Y = 9
        self.CHAT_WINDOW_TITLE_BOX_WIDTH = 1334
        self.CHAT_WINDOW_TITLE_BOX_HEIGHT = 67
        self.CHAT_WINDOW_TITLE_BOX_MARGIN = 12
        self.CHAT_WINDOW_RULES_BOX_X = 425
        self.CHAT_WINDOW_RULES_BOX_Y = 84
        self.CHAT_WINDOW_RULES_BOX_WIDTH = 945
        self.CHAT_WINDOW_RULES_BOX_HEIGHT = 384

        self.CHAT_TITLE_FONT_SCALE = 1.0
        self.CHAT_TITLE_SEPARATOR = "~"
        self.CHAT_TITLE_SEPARATOR_COLOR = (255, 255, 255)
        self.CHAT_TITLE_SEPARATOR_GAP = self.RULES_TEXT_MANA_SYMBOL_SPACING

        # Mana Cost
        self.TITLE_BOX_X = 87
        self.TITLE_BOX_Y = 45
        self.TITLE_BOX_WIDTH = self.CARD_WIDTH - self.TITLE_BOX_X - 40
        self.TITLE_BOX_HEIGHT = 114
        self.MANA_COST_SYMBOL_SIZE = 80
        self.MANA_COST_SYMBOL_OUTLINE_SIZE = 8
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (0, 0)
        self.MANA_COST_TEXT_FONT = VERAMONO_BOLD
        self.MANA_COST_TEXT_COLOR = (255, 255, 255)

        # Type Box
        self.TYPE_BOX_Y = self.CHAT_WINDOW_TITLE_BOX_Y
        self.TYPE_BOX_HEIGHT = self.CHAT_WINDOW_TITLE_BOX_HEIGHT
        self.TYPE_X = self.CHAT_WINDOW_TITLE_BOX_X + self.CHAT_WINDOW_TITLE_BOX_MARGIN
        self.TYPE_BOTTOM_Y = self.CHAT_WINDOW_TITLE_BOX_Y + self.CHAT_WINDOW_TITLE_BOX_HEIGHT - 14
        self.TYPE_WIDTH = self.CHAT_WINDOW_TITLE_BOX_WIDTH - 2 * self.CHAT_WINDOW_TITLE_BOX_MARGIN
        self.TYPE_MAX_FONT_SIZE = 52
        self.TYPE_FONT = VERAMONO_BOLD
        self.TYPE_FONT_COLOR = (255, 255, 255)

        # Set / Rarity Symbol
        self.SET_SYMBOL_WIDTH = 56
        self.SET_SYMBOL_X = (
            self.CHAT_WINDOW_TITLE_BOX_X
            + self.CHAT_WINDOW_TITLE_BOX_WIDTH
            - self.SET_SYMBOL_WIDTH
            - self.CHAT_WINDOW_TITLE_BOX_MARGIN
        )
        self.SET_SYMBOL_Y = (
            self.CHAT_WINDOW_TITLE_BOX_Y + (self.CHAT_WINDOW_TITLE_BOX_HEIGHT - self.SET_SYMBOL_WIDTH) // 2
        )

        # Rules Text Box
        self.RULES_BOX_X = self.CHAT_WINDOW_RULES_BOX_X
        self.RULES_BOX_Y = self.CHAT_WINDOW_RULES_BOX_Y
        self.RULES_BOX_WIDTH = self.CHAT_WINDOW_RULES_BOX_WIDTH
        self.RULES_BOX_HEIGHT = self.CHAT_WINDOW_RULES_BOX_HEIGHT

        # Rules Text
        self.RULES_TEXT_X = self.CHAT_WINDOW_RULES_BOX_X
        self.RULES_TEXT_Y = self.CHAT_WINDOW_RULES_BOX_Y
        self.RULES_TEXT_WIDTH = self.CHAT_WINDOW_RULES_BOX_WIDTH
        self.RULES_TEXT_HEIGHT = self.CHAT_WINDOW_RULES_BOX_HEIGHT
        self.RULES_TEXT_FONT = BARLOW
        self.RULES_TEXT_FONT_ITALICS = BARLOW_ITALICS
        self.RULES_TEXT_MAX_FONT_SIZE = 60
        self.RULES_TEXT_FONT_COLOR = (255, 255, 255)

        # Power & Toughness Text
        self.POWER_TOUGHNESS_FONT = VERAMONO_BOLD
        self.POWER_TOUGHNESS_FONT_SIZE = 120
        self.POWER_TOUGHNESS_FONT_COLOR = (255, 255, 255)
        self.POWER_TOUGHNESS_WIDTH = 378
        self.POWER_TOUGHNESS_HEIGHT = 186
        self.POWER_TOUGHNESS_X = 1070
        self.POWER_TOUGHNESS_Y = 1809

        # Footer
        self.FOOTER_X = 60
        self.FOOTER_Y = 1980
        self.FOOTER_WIDTH = self.CARD_WIDTH - 2 * 60
        self.ARTIST_FONT = VERAMONO_BOLD
        self.LEGAL_FONT = BARLOW

        # Determine the rules text sections (one per chat window) and the window titles
        full_rules_text = self.get_metadata(CARD_RULES_TEXT)
        self.window_rules_texts = [text.strip() for text in full_rules_text.split("{end}")]
        self.window_titles = [self.get_metadata(CARD_TITLE)] + [
            title.strip() for title in self.get_metadata(CARD_ADDITIONAL_TITLES).split("\n") if len(title.strip()) > 0
        ]

        # Rendered chat title images, keyed by (window index, rules text font size)
        self._chat_title_image_cache: dict[tuple[int, int], Image.Image] = {}

    def _create_title_layer(self):
        """
        Do nothing. On chat cards the title is rendered inline with the rules text (as the chat
        "username" beginning each paragraph). The window's title bar holds the type line.
        """

        return

    def _get_type_lines(self) -> list[tuple[str, str, str]]:
        """
        Split the type columns into their newline-separated lines, one per chat window.

        Returns
        -------
        list[tuple[str, str, str]]
            A list of (supertypes, types, subtypes) tuples, still containing any directives.
        """

        supertype_lines = self.get_metadata(CARD_SUPERTYPES).split("\n")
        type_lines = self.get_metadata(CARD_TYPES).split("\n")
        subtype_lines = self.get_metadata(CARD_SUBTYPES).split("\n")
        line_count = max(len(supertype_lines), len(type_lines), len(subtype_lines))
        return [
            (
                supertype_lines[idx].strip() if idx < len(supertype_lines) else "",
                type_lines[idx].strip() if idx < len(type_lines) else "",
                subtype_lines[idx].strip() if idx < len(subtype_lines) else "",
            )
            for idx in range(line_count)
        ]

    def _get_type_line_offsets(self) -> list[tuple[int, int]]:
        """
        Get the directive offset of every type line that actually renders, in order.

        Returns
        -------
        list[tuple[int, int]]
            One (x, y) offset per rendered type line.
        """

        offsets: list[tuple[int, int]] = []
        for supertypes, types, subtypes in self._get_type_lines():
            supertypes, supertype_directives = self._extract_directives(supertypes)
            types, type_directives = self._extract_directives(types)
            subtypes, subtype_directives = self._extract_directives(subtypes)
            combined = f"{supertypes}{types}{subtypes}"
            if len(combined.strip()) == 0 or "{skip}" in combined:
                continue
            offsets.append(
                self._get_directive_offset({**supertype_directives, **type_directives, **subtype_directives})
            )
        return offsets

    def _get_rules_section_offsets(self) -> list[tuple[int, int]]:
        """
        Get the directive offset of every rules text section that actually renders, in order.

        Returns
        -------
        list[tuple[int, int]]
            One (x, y) offset per rendered rules text section (i.e. per chat window).
        """

        offsets: list[tuple[int, int]] = []
        for section_text in self.window_rules_texts:
            cleaned, directives = self._extract_directives(section_text)
            if len(cleaned.strip()) == 0 or "{skip}" in cleaned:
                continue
            offsets.append(self._get_directive_offset(directives))
        return offsets

    def _create_type_layer(self):
        """
        Process each newline-separated type line into its own layer, one per chat window.
        Per-line directives in Supertype(s), Type(s), and Subtype(s) apply only to their own line.
        """

        full_supertypes = self.get_metadata(CARD_SUPERTYPES)
        full_types = self.get_metadata(CARD_TYPES)
        full_subtypes = self.get_metadata(CARD_SUBTYPES)

        for supertypes, types, subtypes in self._get_type_lines():
            self.metadata[CARD_SUPERTYPES] = supertypes
            self.metadata[CARD_TYPES] = types
            self.metadata[CARD_SUBTYPES] = subtypes
            super()._create_type_layer()

        self.metadata[CARD_SUPERTYPES] = full_supertypes
        self.metadata[CARD_TYPES] = full_types
        self.metadata[CARD_SUBTYPES] = full_subtypes

    def _create_rarity_symbol_layer(self):
        """
        Draw the rarity/set symbol once per type line, in line with it in that window's title bar.
        The symbol inherits its type line's offset directive.
        """

        full_set_symbol_x = self.SET_SYMBOL_X
        full_set_symbol_y = self.SET_SYMBOL_Y
        for offset_x, offset_y in self._get_type_line_offsets():
            self.SET_SYMBOL_X = full_set_symbol_x + offset_x
            self.SET_SYMBOL_Y = full_set_symbol_y + offset_y
            super()._create_rarity_symbol_layer()
        self.SET_SYMBOL_X = full_set_symbol_x
        self.SET_SYMBOL_Y = full_set_symbol_y

    def _create_watermark_layer(self):
        """
        Paste the watermark once per rules text section, centered in that window's rules box.
        The watermark inherits its section's offset directive.
        """

        full_rules_box_x = self.RULES_BOX_X
        full_rules_box_y = self.RULES_BOX_Y
        for offset_x, offset_y in self._get_rules_section_offsets():
            self.RULES_BOX_X = full_rules_box_x + offset_x
            self.RULES_BOX_Y = full_rules_box_y + offset_y
            super()._create_watermark_layer()
        self.RULES_BOX_X = full_rules_box_x
        self.RULES_BOX_Y = full_rules_box_y

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text
        formatting, and append it to `self.text_layers`.
        """

        full_rules_text = self.get_metadata(CARD_RULES_TEXT)
        for idx, section_text in enumerate(self.window_rules_texts):
            self.metadata[CARD_RULES_TEXT] = self._prefix_chat_titles(idx, section_text)
            super()._create_rules_text_layer()
        self.metadata[CARD_RULES_TEXT] = full_rules_text

    def _prefix_chat_titles(self, index: int, text: str) -> str:
        """
        Prefix every rules paragraph in the given section with an internal "{chattitleN}" token,
        which `_get_symbol_metrics` later swaps for the rendered chat title image. Flavor text
        blocks and "{lns}" soft line breaks are not prefixed.

        Parameters
        ----------
        index: int
            The chat window index this section belongs to.

        text: str
            The raw rules text section.

        Returns
        -------
        str
            The processed section text.
        """

        cleaned, directives = self._extract_directives(text)
        if len(cleaned.strip()) == 0 or "{skip}" in cleaned:
            return text
        if len(self._get_window_title_plain(index)) == 0:
            return text

        cleaned = re.sub(r"\{ln\}", "\n", cleaned, flags=re.IGNORECASE)

        token = f"{{chattitle{index}}}"
        sections = re.split(r"(\{flavor\}|\{divider\})", cleaned, flags=re.IGNORECASE)
        result = ""
        in_flavor = False
        for part in sections:
            lowered = part.lower()
            if lowered == "{flavor}":
                in_flavor = True
                result += part
                continue
            if lowered == "{divider}":
                in_flavor = False
                result += part
                continue
            if part == "":
                continue
            if in_flavor:
                result += part
                in_flavor = False
                continue

            lines = part.split("\n")
            prefixed_lines = []
            for line_index, line in enumerate(lines):
                at_line_start = line_index > 0 or len(result) == 0 or result.endswith("\n")
                if at_line_start and len(line.strip()) > 0:
                    prefixed_lines.append(token + line)
                else:
                    prefixed_lines.append(line)
            result += "\n".join(prefixed_lines)

        for key, value in directives.items():
            result += f"{{{key}:{value}}}"
        return result

    def _get_symbol_metrics(self, token, font, font_size, tint_color=None):
        """
        Return the width, height, and image scaled to the current font size for the given token.
        """

        match = Chat.CHAT_TITLE_TOKEN_PATTERN.fullmatch(token.strip())
        if match is not None:
            title_image = self._get_chat_title_image(int(match.group(1)), font_size)
            return title_image.width, title_image.height, title_image
        return super()._get_symbol_metrics(token, font, font_size, tint_color)

    def _get_window_title_text(self, index: int) -> str:
        """
        Fetch the (tick-replaced, directive/control-tag stripped) title text for the given window,
        color tags included.
        """

        raw_title = self.window_titles[index] if index < len(self.window_titles) else ""
        raw_title, _ = self._extract_directives(raw_title)
        for tag in ("{skip}", "{last}", "{center}"):
            raw_title = raw_title.replace(tag, "")
        return replace_ticks(raw_title.strip())

    def _get_window_title_plain(self, index: int) -> str:
        """
        Fetch the window title with color tags reduced to their inner text.
        """

        return COLOR_TAG_PATTERN.sub(lambda match: match.group(4), self._get_window_title_text(index)).strip()

    def _get_chat_title_colors(self) -> list[tuple[int, int, int]]:
        """
        Parse the Watermark Color(s) column into the default chat title color(s).
        Falls back to white if nothing valid is given.
        """

        colors = self.get_metadata(CARD_WATERMARK_COLOR)
        parsed: list[tuple[int, int, int]] = []
        if len(colors) > 0:
            for color in colors.split("\n"):
                color = WATERMARK_COLORS.get(color.lower().strip())
                if color is not None:
                    parsed.append(color)
        if len(parsed) == 0:
            parsed.append((255, 255, 255))
        return parsed

    def _recolor_chat_title(self, image: Image.Image, colors: list[tuple[int, int, int]]) -> Image.Image:
        """
        Recolor a title image with the given color(s). Two colors are split
        half and half, left to right, using the same mask the watermark uses.
        """

        def recolor(base: Image.Image, color: tuple[int, int, int]) -> Image.Image:
            alpha = base.getchannel("A")
            solid = Image.new("RGBA", base.size, color)
            recolored = Image.new("RGBA", base.size)
            recolored.paste(solid, mask=alpha)
            return recolored

        if len(colors) == 1:
            return recolor(image, colors[0])

        left_color = recolor(image, colors[0])
        right_color = recolor(image, colors[1])
        mask = open_image(f"{FRAMES_PATH}/regular/mask/left.png")
        if mask is None:
            log("Could not find the left color-split mask for the chat title. Using the first color only.")
            return recolor(image, colors[0])
        mask = mask.resize(image.size).getchannel("A")
        return Image.composite(left_color, right_color, mask)

    def _get_chat_title_image(self, index: int, rules_font_size: int) -> Image.Image:
        """
        Render (and cache) the "<title> ~" image for the given window.
        """

        cache_key = (index, rules_font_size)
        cached = self._chat_title_image_cache.get(cache_key)
        if cached is not None:
            return cached

        title_text_raw = self._get_window_title_text(index)
        title_font_size = max(int(rules_font_size * self.CHAT_TITLE_FONT_SCALE), 1)
        title_font = load_font(self.TITLE_FONT, title_font_size)
        title_fallback_fonts = self._load_fallback_fonts(self.TITLE_FONT, title_font_size)

        segments: list[tuple[str, tuple[int, int, int] | None]] = []
        last_end = 0
        for match in COLOR_TAG_PATTERN.finditer(title_text_raw):
            r, g, b = map(int, match.groups()[:3])
            if match.start() > last_end:
                segments.append((title_text_raw[last_end : match.start()], None))
            segments.append((match.group(4), (r, g, b)))
            last_end = match.end()
        if last_end < len(title_text_raw):
            segments.append((title_text_raw[last_end:], None))

        has_custom_color = any(color is not None for _, color in segments)
        title_text = "".join(segment_text for segment_text, _ in segments)
        if len(title_text.strip()) == 0:
            empty = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
            self._chat_title_image_cache[cache_key] = empty
            return empty

        watermark_colors = self._get_chat_title_colors()
        title_width = max(self._get_ucs_chunks_length(title_text, title_font, title_fallback_fonts), 1)
        separator_width = max(
            self._get_ucs_chunks_length(self.CHAT_TITLE_SEPARATOR, title_font, title_fallback_fonts),
            1,
        )

        rules_font = load_font(self.RULES_TEXT_FONT, rules_font_size)
        cap_bbox = rules_font.getbbox("H")
        rules_cap_center = (cap_bbox[1] + cap_bbox[3]) / 2
        rules_ascent = rules_font.getmetrics()[0]
        title_ascent, title_descent = title_font.getmetrics()
        natural_height = title_ascent + title_descent
        target_height = int(2 * (title_ascent + rules_cap_center - rules_ascent))
        image_height = max(natural_height, target_height, 1)

        image = Image.new(
            "RGBA",
            (title_width + self.CHAT_TITLE_SEPARATOR_GAP + separator_width, image_height),
            (0, 0, 0, 0),
        )

        title_image = Image.new("RGBA", (title_width, image_height), (0, 0, 0, 0))
        title_draw = ImageDraw.Draw(title_image)
        if has_custom_color:
            x_pos = 0
            default_color = watermark_colors[0]
            for segment_text, color in segments:
                self._draw_ucs_chunks(
                    title_draw,
                    (x_pos, 0),
                    segment_text,
                    title_font,
                    title_fallback_fonts,
                    primary_font_path=self.TITLE_FONT,
                    font_size=title_font_size,
                    fill=color if color is not None else default_color,
                )
                x_pos += self._get_ucs_chunks_length(segment_text, title_font, title_fallback_fonts)
        else:
            self._draw_ucs_chunks(
                title_draw,
                (0, 0),
                title_text,
                title_font,
                title_fallback_fonts,
                primary_font_path=self.TITLE_FONT,
                font_size=title_font_size,
                fill=(255, 255, 255),
            )
            title_image = self._recolor_chat_title(title_image, watermark_colors)
        image.alpha_composite(title_image, (0, 0))

        draw = ImageDraw.Draw(image)
        self._draw_ucs_chunks(
            draw,
            (title_width + self.CHAT_TITLE_SEPARATOR_GAP, 0),
            self.CHAT_TITLE_SEPARATOR,
            title_font,
            title_fallback_fonts,
            primary_font_path=self.TITLE_FONT,
            font_size=title_font_size,
            fill=self.CHAT_TITLE_SEPARATOR_COLOR,
        )

        self._chat_title_image_cache[cache_key] = image
        return image
