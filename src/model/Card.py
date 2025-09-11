import re
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont

from constants import (
    BELEREN_BOLD_SMALL_CAPS,
    CARD_FRAMES,
    CARD_TITLE,
    CARD_SUPERTYPES,
    CARD_TYPES,
    CARD_RARITY,
    CARD_SET,
    CARD_SUBTYPES,
    CARD_POWER_TOUGHNESS,
    CARD_MANA_COST,
    SET_SYMBOL_WIDTH,
    SET_SYMBOL_X,
    SET_SYMBOL_Y,
    SET_SYMBOLS_PATH,
    WATERMARK_COLORS,
    CARD_WATERMARK_COLOR,
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_RULES_TEXT,
    CARD_WATERMARK,
    WATERMARKS_PATH,
    MPLANTIN_ITALICS,
    FRAMES_PATH,
    LINE_HEIGHT_TO_GAP_RATIO,
    MANA_SYMBOL_RULES_TEXT_MARGIN,
    POWER_TOUGHNESS_FONT_SIZE,
    POWER_TOUGHNESS_HEIGHT,
    POWER_TOUGHNESS_WIDTH,
    POWER_TOUGHNESS_X,
    POWER_TOUGHNESS_Y,
    TITLE_BOX_HEIGHT,
    TITLE_BOX_WIDTH,
    TITLE_BOX_X,
    TITLE_BOX_Y,
    MANA_COST_SYMBOL_SHADOW_OFFSET,
    MANA_COST_SYMBOL_SIZE,
    MANA_COST_SYMBOL_SPACING,
    MANA_SYMBOL_RULES_TEXT_SCALE,
    SYMBOL_PLACEHOLDER_KEY,
    RULES_BOX_HEIGHT,
    RULES_BOX_MAX_FONT_SIZE,
    RULES_BOX_MIN_FONT_SIZE,
    RULES_BOX_WIDTH,
    RULES_BOX_X,
    RULES_BOX_Y,
    MPLANTIN,
    PLACEHOLDER_REGEX,
    BELEREN_BOLD,
    BELEREN_BOLD_SIZE,
    TITLE_MAX_WIDTH,
    TITLE_X,
    TITLE_Y,
    TYPE_BOX_HEIGHT,
    TYPE_FONT_SIZE,
    TYPE_MAX_WIDTH,
    TYPE_X,
    TYPE_Y,
    WATERMARK_OPACITY,
    WATERMARK_WIDTH,
)
from log import log
from model.Layer import Layer
from utils import open_image, replace_ticks


class Card:
    """
    A layered image representing a card and all the collection info on it, with all relevant card metadata.

    Attributes
    ----------
    base_width : int, default : `CARD_WIDTH`
        The width of the root image.

    base_height : int, default : `CARD_HEIGHT`
        The height of the root image.

    metadata : dict[str, str | list], default : {}
        Information about the card (title, mana cost, rules text, frame, etc.)

    frame_layers : list[Layer], default : []
        The layers of card frames. Lower-index layers are rendered first. Renders after art, before collector info.

    collector_layers : list[Layer], default : []
        The layers of collector info. Lower-index layers are rendered first. Renders after frames, before text.

    text_layers : list[Layer], default : []
        The layers of card text. Lower-index layers are rendered first. Renders after collector info and frames.
    """

    def __init__(
        self,
        base_width: int = CARD_WIDTH,
        base_height: int = CARD_HEIGHT,
        metadata: dict[str, str | list] = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
    ):
        self.base_width = base_width
        self.base_height = base_height
        self.metadata = metadata if metadata is not None else {}
        self.frame_layers = frame_layers if frame_layers is not None else []
        self.collector_layers = collector_layers if collector_layers is not None else []
        self.text_layers = text_layers if text_layers is not None else []

    def render_card(self) -> Image.Image:
        """
        Merge all layers into one image.

        Returns
        -------
        Image
            The merged image.
        """

        base_image = Image.new("RGBA", (self.base_width, self.base_height), (0, 0, 0, 0))
        composite_image = base_image.copy()

        for layer in self.frame_layers + self.collector_layers + self.text_layers:
            temp = Image.new("RGBA", composite_image.size, (0, 0, 0, 0))
            temp.paste(layer.image, layer.position)
            composite_image = Image.alpha_composite(composite_image, temp)

        return composite_image

    def create_frame_layers(self):
        """
        Append every frame layer to the card based on `self.metadata`.
        """

        card_frames = self.metadata.get(CARD_FRAMES, "")
        if len(card_frames) == 0:
            return

        pending_masks: list[Image.Image] = []

        for frame_path in card_frames.split("\n"):
            frame_path = frame_path.lower().strip()
            if len(frame_path) == 0:
                continue

            try:
                frame = open_image(f"{FRAMES_PATH}/{frame_path}.png")
            except Exception:
                log(f"Invalid frame path '{frame_path}'.")
                continue

            if "mask/" in frame_path.lower():
                pending_masks.append(frame)
                continue

            if len(pending_masks) > 0:
                combined_mask = Image.new("L", frame.size, 255)
                for mask in pending_masks:
                    base = mask.getchannel("A").resize(frame.size)
                    if base.getbbox() is None:
                        log(f"Warning: mask '{frame_path}' appears empty. Skipping one mask...")
                        continue

                    # combine masks multiplicatively so multiple masks narrow the kept area
                    combined_mask = ImageChops.multiply(combined_mask, base)

                new_frame = frame.copy()
                new_frame.putalpha(combined_mask)
                frame = new_frame

                pending_masks.clear()

            self.frame_layers.append(Layer(frame))

        if pending_masks:
            log(
                f"Warning: {len(pending_masks)} mask layer(s) at end of frame list with no following frame."
                "They were ignored."
            )

    def create_collector_layers(self):
        """
        Append every layer of additional "meta" info (rarity symbol, collector info, watermark, etc.)
        to `self.collector_layers`.
        """

        self._create_watermark_layer()
        self._create_rarity_symbol_layer()

    def _create_watermark_layer(
        self,
        watermark: Image.Image = None,
        watermark_color: tuple[int, int, int] | list[tuple[int, int, int]] = None,
        rules_box_x: int = RULES_BOX_X,
        rules_box_y: int = RULES_BOX_Y,
        rules_box_width: int = RULES_BOX_WIDTH,
        rules_box_height: int = RULES_BOX_HEIGHT,
        watermark_width: int = WATERMARK_WIDTH,
        watermark_opacity: float = WATERMARK_OPACITY,
    ):
        """
        Process a watermark image and append it to `self.collector_layers`.
        Assumes the image is in RGBA format.

        Parameters
        ----------
        watermark: Image, optional
            The watermark image to use. Uses the image from the card's metadata if not given.

        watermark_color: tuple[int, int, int] | list[tuple[int, int, int]], optional
            The watermark color(s) to use. Uses (or guesses) the color based on the card's metadata if not given.

        rules_box_x: int, default : `RULES_BOX_X`
            The leftmost x position of the rules text box bounding the watermark.

        rules_box_y: int, default : `RULES_BOX_Y`
            The topmost y position of the rules text box bounding the watermark.

        rules_box_width: int, default : `RULES_BOX_WIDTH`
            The width of the rules text box bounding the watermark.

        rules_box_height: int, default : `RULES_BOX_HEIGHT`
            The height of the rules text box bounding the watermark.

        watermark_width: int, default : `WATERMARK_WIDTH`
            The width of the watermark. Also determines the height, based on the relative scale of the image.

        watermark_opacity: int, default : `WATERMARK_OPACITY`
            The opacity of the watermark in the range [0.0, 1.0].
        """

        if watermark is None:
            watermark_path = f"{WATERMARKS_PATH}/{self.metadata.get(CARD_WATERMARK, "")}.png"
            watermark = open_image(watermark_path)
            if watermark is None:
                log(f"Could not find watermark at '{watermark_path}'.")
                return

        if watermark_color is None:
            colors = self.metadata.get(CARD_WATERMARK_COLOR, "").strip()
            if len(colors) > 0:
                watermark_color = []
                for color in colors.splitlines():
                    color = WATERMARK_COLORS.get(color.lower())
                    if color is not None:
                        watermark_color.append(color)
            else:
                # TODO: Figure out watermark color from color identity context
                pass

        if not watermark_color:
            watermark_color = (0, 0, 0)

        resized = watermark.resize((watermark_width, int((watermark_width / watermark.width) * watermark.height)))

        def recolor(image: Image.Image, color: tuple[int, int, int]) -> Image.Image:
            alpha = image.getchannel("A")
            solid = Image.new("RGBA", image.size, color)
            recolored_image = Image.new("RGBA", image.size)
            recolored_image.paste(solid, mask=alpha)
            return recolored_image

        recolored = resized
        if isinstance(watermark_color, tuple):
            recolored = recolor(recolored, watermark_color)
        elif isinstance(watermark_color, list):
            if len(watermark_color) == 1:
                recolored = recolor(recolored, watermark_color[0])
            else:
                left_color = recolor(resized, watermark_color[0]).convert("RGBA")
                right_color = recolor(resized, watermark_color[1]).convert("RGBA")
                mask = Image.open(f"{FRAMES_PATH}/mask/left.png").resize(resized.size).getchannel("A")
                recolored = Image.composite(left_color, right_color, mask)

        r, g, b, alpha = recolored.split()
        alpha = ImageEnhance.Brightness(alpha).enhance(watermark_opacity)
        made_translucent = Image.merge("RGBA", (r, g, b, alpha))

        self.collector_layers.append(
            Layer(
                made_translucent,
                (
                    rules_box_x + (rules_box_width - recolored.width) // 2,
                    rules_box_y + (rules_box_height - recolored.height) // 2,
                ),
            )
        )

    def _create_rarity_symbol_layer(
        self,
        card_set: str = None,
        rarity: str = None,
        set_symbol_x: int = SET_SYMBOL_X,
        set_symbol_y: int = SET_SYMBOL_Y,
        set_symbol_width: int = SET_SYMBOL_WIDTH,
    ):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.

        Parameters
        ----------
        card_set: str, optional
            The set whose symbol should be used. Uses the set from the card's metadata, if any, if not given.

        rarity: str, optional
            The rarity of the symbol that should be used. Uses the rarity from the card's metadata if not given.

        set_symbol_x: int, default : `SET_SYMBOL_X`
            The leftmost x position of the set symbol.

        set_symbol_y: int, default : `SET_SYMBOL_Y`
            The topmost y position of the set symbol.

        set_symbol_width: int, default : `SET_SYMBOL_WIDTH`
            The width of the set symbol.
        """

        if card_set is None:
            card_set = self.metadata.get(CARD_SET, "")
        if len(card_set) == 0:
            return
        
        if rarity is None:
            rarity = self.metadata.get(CARD_RARITY, "")
        if len(rarity) == 0:
            return
        
        symbol_path = f"{SET_SYMBOLS_PATH}/{card_set}/{rarity}.png"
        rarity_symbol = open_image(symbol_path)
        if rarity_symbol is None:
            log(f"Could not find rarity symbol at '{symbol_path}'.")
            return
        
        rarity_symbol = rarity_symbol.resize((set_symbol_width, int((set_symbol_width / rarity_symbol.width) * rarity_symbol.height)))
        self.collector_layers.append(Layer(rarity_symbol, (set_symbol_x, set_symbol_y)))


    def create_text_layers(self):
        """
        Append every layer of text of the card (rules text, mana cost, etc.) to `self.text_layers`.
        """

        self._create_mana_cost_layer()
        self._create_title_layer()
        self._create_type_layer()
        self._create_rules_text_layer()
        self._create_power_toughness_layer()

    def _create_mana_cost_layer(
        self,
        text: str = None,
        header_x: int = TITLE_BOX_X,
        header_y: int = TITLE_BOX_Y,
        header_width: int = TITLE_BOX_WIDTH,
        header_height: int = TITLE_BOX_HEIGHT,
    ):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The mana cost text to process. Uses the mana cost text in the card's metadata if not given.

        header_x: int, default : `TITLE_BOX_X`
            The leftmost x position of the mana cost header.

        header_y: int, default : `TITLE_BOX_Y`
            The topmost y position of the mana cost header.

        header_width: int, default : `TITLE_BOX_WIDTH`
            The width of the frame's mana cost header.

        header_height: int, default : `TITLE_BOX_HEIGHT`
            The height of the frame's mana cost header.
        """

        if text is None:
            text = self.metadata.get(CARD_MANA_COST, "")
        if len(text) == 0:
            return

        text = re.sub(r"{+|}+", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        def add_drop_shadow(
            symbol_image: Image.Image, offset: tuple[int, int] = MANA_COST_SYMBOL_SHADOW_OFFSET
        ) -> Image.Image:
            """
            Apply drop shadow to a mana symbol.

            Parameters
            ----------
            symbol_image: Image
                The image of the mana symbol.

            offset: tuple[float, float], default : `MANA_COST_SYMBOL_SHADOW_OFFSET`
                Offset of the shadow relative to the symbol in the form (x, y).

            Returns
            -------
            Image
                The mana symbol image provided, now with a drop shadow.
            """

            alpha = symbol_image.getchannel("A")
            shadow = Image.new("RGBA", symbol_image.size, (0, 0, 0, 0))
            black = Image.new("L", symbol_image.size)
            shadow.paste(black, mask=alpha)

            # Make a new image big enough for shadow to fit with the symbol
            total_width = int(symbol_image.width + abs(offset[0]))
            total_height = int(symbol_image.height + abs(offset[1]))
            result = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

            # Paste shadow first, then the symbol over it
            if offset[0] >= 0:
                symbol_x = 0
                shadow_x = offset[0]
            else:
                symbol_x = -offset[0]
                shadow_x = 0
            if offset[1] >= 0:
                symbol_y = 0
                shadow_y = offset[1]
            else:
                symbol_y = -offset[1]
                shadow_y = 0

            result.alpha_composite(shadow, (shadow_x, shadow_y))
            result.alpha_composite(symbol_image, (symbol_x, symbol_y))

            return result

        image = Image.new("RGBA", (header_width, header_height), (0, 0, 0, 0))

        curr_x = header_width + MANA_COST_SYMBOL_SPACING
        for sym in reversed(text.split(" ")):
            symbol = SYMBOL_PLACEHOLDER_KEY.get(sym.strip().lower(), None)
            if symbol is None:
                log(f"Unknown placeholder '{{{sym}}}'")
                continue

            scale = symbol.size_ratio * MANA_COST_SYMBOL_SIZE / symbol.image.height
            width = int(symbol.image.width * scale)
            height = int(symbol.image.height * scale)
            symbol_image = add_drop_shadow(symbol.image.resize((width, height), Image.LANCZOS))

            curr_x -= symbol_image.width + MANA_COST_SYMBOL_SPACING
            if curr_x >= symbol_image.width:
                image.alpha_composite(symbol_image, (int(curr_x), (header_height - symbol_image.height) // 2))
            else:
                log(f"The mana cost is too long and has been cut off.")
                break

        self.text_layers.append(Layer(image, (header_x, header_y)))

    def _create_title_layer(
        self,
        text: str = None,
        header_x: int = TITLE_X,
        header_y: int = TITLE_Y,
        header_width: int = TITLE_MAX_WIDTH,
        header_height: int = TITLE_BOX_HEIGHT,
    ):
        """
        Process title text into the title and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The title text to process. Uses the title in the card's metadata if not given.

        header_x: int, default : `TITLE_BOX_X`
            The leftmost x position of the title header.

        header_y: int, default : `TITLE_BOX_Y`
            The topmost y position of the title header.

        header_width: int, default : `TITLE_BOX_WIDTH`
            The width of the frame's title header.

        header_height: int, default : `TITLE_BOX_HEIGHT`
            The height of the frame's title header box.
        """

        if text is None:
            text = self.metadata.get(CARD_TITLE, "")
        if len(text) == 0:
            return

        title_font = ImageFont.truetype(BELEREN_BOLD, BELEREN_BOLD_SIZE)
        image = Image.new("RGBA", (header_width, header_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        bounding_box = title_font.getbbox(text)
        text_height = int(bounding_box[3] - bounding_box[1])
        draw.text((0, (header_height - text_height) // 4), text, font=title_font, fill="black")

        self.text_layers.append(Layer(image, (header_x, header_y)))

    def _create_type_layer(
        self,
        text: str = None,
        header_x: int = TYPE_X,
        header_y: int = TYPE_Y,
        header_width: int = TYPE_MAX_WIDTH,
        header_height: int = TYPE_BOX_HEIGHT,
    ):
        """
        Process type text into the type box and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The type text to process. Uses the type in the card's metadata if not given.

        header_x: int, default : `TYPE_BOX_X`
            The leftmost x position of the type header.

        header_y: int, default : `TYPE_BOX_Y`
            The topmost y position of the type header.

        header_width: int, default : `TYPE_BOX_WIDTH`
            The width of the frame's type header.

        header_height: int, default : `TYPE_BOX_HEIGHT`
            The height of the frame's type header box.
        """

        if text is None:
            first_part = (
                f"{self.metadata.get(CARD_SUPERTYPES, "").strip()} {self.metadata.get(CARD_TYPES, "").strip()}".strip()
            )
            second_part = self.metadata.get(CARD_SUBTYPES, "").strip()
            if len(second_part) > 0:
                text = " — ".join((first_part, second_part))
            else:
                text = first_part
        if len(text) == 0:
            return

        type_font = ImageFont.truetype(BELEREN_BOLD, TYPE_FONT_SIZE)
        image = Image.new("RGBA", (header_width, header_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        bounding_box = type_font.getbbox(text)
        text_height = int(bounding_box[3] - bounding_box[1])
        draw.text((0, (header_height - text_height) // 4), text, font=type_font, fill="black")

        self.text_layers.append(Layer(image, (header_x, header_y)))

    def _replace_text_placeholders(self, text: str) -> str:
        """
        Replace standard placeholders in the format `{PLACEHOLDER}` with what they represent.
        """

        new_text = text
        new_text = re.sub("{cardname}", self.metadata.get(CARD_TITLE, ""), new_text, flags=re.IGNORECASE)
        new_text = re.sub("{-}", "—", new_text)
        return new_text

    def _create_rules_text_layer(
        self,
        text: str = None,
        box_x: int = RULES_BOX_X,
        box_y: int = RULES_BOX_Y,
        box_width: int = RULES_BOX_WIDTH,
        box_height: int = RULES_BOX_HEIGHT,
    ):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The rules text to process. Uses the rules text in the card's metadata if not given.

        box_x: int, default : `RULES_BOX_X`
            The leftmost x position of the rules box.

        box_y: int, default : `RULES_BOX_Y`
            The topmost y position of the rules box.

        box_width: int, default : `RULES_BOX_WIDTH`
            The width of the frame's rules box.

        box_height: int, default : `RULES_BOX_HEIGHT`
            The height of the frame's rules box.
        """

        if text is None:
            text = self.metadata.get(CARD_RULES_TEXT, "")
        if len(text) == 0:
            return

        text = self._replace_text_placeholders(text)

        flavor_split: list[str] = re.split(r"\{flavor\}", text)
        raw_rules_text = flavor_split[0]
        raw_flavor_texts = flavor_split[1:] if len(flavor_split) > 1 else []

        for font_size in range(RULES_BOX_MAX_FONT_SIZE, RULES_BOX_MIN_FONT_SIZE - 1, -1):
            rules_font = ImageFont.truetype(MPLANTIN, font_size)
            flavor_font = ImageFont.truetype(MPLANTIN_ITALICS, font_size)

            line_height = font_size
            margin = int(font_size * 0.25)
            max_line_width = box_width - 2 * margin

            def parse_fragments(line: str) -> list[tuple[str, str]]:
                """
                Return [("text", str) | ("symbol", token), ...] for a single line.
                """

                fragments = []
                parts = PLACEHOLDER_REGEX.split(line)
                for i, part in enumerate(parts):

                    # Parts alternate like (text, symbol, text, symbol, etc.)
                    if i % 2 == 0:
                        if part:
                            fragments.append(("text", part))
                    else:
                        fragments.append(("symbol", part.strip()))
                return fragments

            def get_symbol_metrics(token: str) -> tuple[int, int, Image.Image | None]:
                """
                Return (width, height, Image | None) scaled to current font size.
                """

                symbol = SYMBOL_PLACEHOLDER_KEY.get(token.lower(), None)

                if symbol is None:
                    placeholder = f"[{token}]"
                    return int(rules_font.getlength(placeholder)), font_size, None

                scale = MANA_SYMBOL_RULES_TEXT_SCALE * symbol.size_ratio * font_size / symbol.image.height
                width = int(symbol.image.width * scale)
                height = int(symbol.image.height * scale)
                symbol = symbol.image.resize((width, height), Image.LANCZOS)
                return width, height, symbol

            def wrap_text_fragments(
                frags: list[tuple[str, str]], text_font: ImageFont.ImageFont
            ) -> list[list[tuple[str, str]]]:
                """
                Split the lines into individual words and symbols, then wrap them so that they fit within
                `max_line_width` (based on rules box size and margins).
                For example, `"Add {R}."` becomes `[[("text": "Add"), ("text": " "), ("symbol": "R"), ("text": ".")]]`
                """

                lines: list[list[tuple[str, str]]] = []
                curr_fragment: list[tuple[str, str]] = []
                curr_width = 0

                def go_to_newline():
                    """
                    Wrap the text to the next line.
                    """

                    nonlocal curr_fragment, curr_width
                    if curr_fragment:
                        lines.append(curr_fragment)
                    curr_fragment, curr_width = [], 0

                for kind, value in frags:

                    if kind == "symbol":
                        width, _, _ = get_symbol_metrics(value)
                        if curr_fragment and curr_width + width > max_line_width:
                            go_to_newline()
                        curr_fragment.append(("symbol", value))
                        curr_width += width + MANA_SYMBOL_RULES_TEXT_MARGIN

                    else:
                        for word in re.findall(r"\S+|\s+", value):
                            word = replace_ticks(word)
                            width = text_font.getlength(word)

                            if word.isspace():
                                if not curr_fragment:  # get rid of leading spaces
                                    continue
                                if curr_width + width > max_line_width:
                                    go_to_newline()
                                    continue
                                curr_fragment.append(("text", word))
                                curr_width += width
                            else:
                                if curr_fragment and curr_width + width > max_line_width:
                                    go_to_newline()

                                # If a single word is longer than a line by itself, split it up
                                if width > max_line_width:
                                    for char in word:
                                        char_width = text_font.getlength(char)
                                        if curr_fragment and curr_width + char_width > max_line_width:
                                            go_to_newline()
                                        curr_fragment.append(("text", char))
                                        curr_width += char_width
                                else:
                                    curr_fragment.append(("text", word))
                                    curr_width += width

                if curr_fragment:
                    lines.append(curr_fragment)
                return lines

            # Split the rules text into lines that fit the rules box horizontally
            rules_lines: list[list[tuple[str, str]]] = []
            for line in raw_rules_text.splitlines():
                rules_fragments = parse_fragments(line)
                rules_lines += wrap_text_fragments(rules_fragments, rules_font) if rules_fragments else [[("text", "")]]
                rules_lines.append([("newline", None)])
            rules_lines.pop()  # remove the ending newline

            # Split the flavor text into lines that fit the rules box horizontally
            flavor_lines: list[list[list[tuple[str, str]]]] = []
            for raw_flavor_text in raw_flavor_texts:
                flavor_lines.append([])
                for line in raw_flavor_text.splitlines():
                    flavor_fragments = parse_fragments(line)
                    flavor_lines[-1] += (
                        wrap_text_fragments(flavor_fragments, flavor_font) if flavor_fragments else [[("text", "")]]
                    )
                    flavor_lines[-1].append([("newline", None)])
                flavor_lines[-1].pop()  # remove the ending newline

            # If the lines of text are too tall, try the process again with a different font
            content_height = 0
            for line in rules_lines:
                if line[0][0] == "newline":
                    content_height += line_height // LINE_HEIGHT_TO_GAP_RATIO
                else:
                    content_height += line_height
            for lines in flavor_lines:
                for line in lines:
                    if line[0][0] == "newline":
                        content_height += line_height // LINE_HEIGHT_TO_GAP_RATIO
                    else:
                        content_height += line_height
                content_height += SYMBOL_PLACEHOLDER_KEY["flavor"].image.height + line_height
            usable_height = box_height - 2 * margin
            if content_height > usable_height:
                continue

            image = Image.new("RGBA", (box_width, box_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            curr_y = margin + (usable_height - content_height) // 2

            def draw_lines(lines: list[list[tuple[str, str]]], text_font: ImageFont.ImageFont):
                """
                Render lines of text as images.
                """

                nonlocal curr_y
                for line_fragments in lines:
                    if line_fragments and line_fragments[0][0] == "newline":
                        curr_y += (
                            line_height // LINE_HEIGHT_TO_GAP_RATIO
                        )  # add an extra gap for user-specified newlines
                        continue

                    curr_x = margin
                    for kind, value in line_fragments:
                        if kind == "text":
                            if value:
                                draw.text((curr_x, curr_y), value, font=text_font, fill="black")
                                curr_x += draw.textlength(value, font=text_font)
                        else:
                            width, _, symbol_image = get_symbol_metrics(value)
                            if symbol_image is not None:
                                image.alpha_composite(
                                    symbol_image, (int(curr_x), int(curr_y + MANA_SYMBOL_RULES_TEXT_MARGIN))
                                )
                            else:
                                placeholder = f"[{value}]"
                                draw.text((curr_x, curr_y), placeholder, font=text_font, fill="red")
                            curr_x += width + MANA_SYMBOL_RULES_TEXT_MARGIN
                    curr_y += line_height

            draw_lines(rules_lines, rules_font)
            for lines in flavor_lines:
                curr_y += line_height // 2
                image.alpha_composite(
                    SYMBOL_PLACEHOLDER_KEY["flavor"].image.resize(
                        (box_width - 2 * margin, SYMBOL_PLACEHOLDER_KEY["flavor"].image.height)
                    ),
                    (margin, curr_y),
                )
                curr_y += SYMBOL_PLACEHOLDER_KEY["flavor"].image.height + line_height // 2
                draw_lines(lines, flavor_font)

            self.text_layers.append(Layer(image, (box_x, box_y)))
            return

        raise ValueError("Text is too long to fit in box even at minimum font size.")

    def _create_power_toughness_layer(
        self,
        text: str = None,
        power_toughness_x: int = POWER_TOUGHNESS_X,
        power_toughness_y: int = POWER_TOUGHNESS_Y,
        power_toughness_width: int = POWER_TOUGHNESS_WIDTH,
        power_toughness_height: int = POWER_TOUGHNESS_HEIGHT,
    ):
        """
        Process power & toughness text into the power & toughness area and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The power & toughness text to process. Uses the power & toughness in the card's metadata if not given.

        power_toughness_x: int, default : `TYPE_BOX_X`
            The leftmost x position of the type header.

        power_toughness_y: int, default : `TYPE_BOX_Y`
            The topmost y position of the type header.

        power_toughness_width: int, default : `TYPE_BOX_WIDTH`
            The width of the frame's power & toughness area.

        power_toughness_height: int, default : `TYPE_BOX_HEIGHT`
            The height of the frame's type power & toughness area.
        """

        if text is None:
            text = self.metadata.get(CARD_POWER_TOUGHNESS, "").strip()
        if len(text) == 0:
            return

        power_toughness_font = ImageFont.truetype(BELEREN_BOLD_SMALL_CAPS, POWER_TOUGHNESS_FONT_SIZE)
        image = Image.new("RGBA", (power_toughness_width, power_toughness_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        text_width = power_toughness_font.getlength(text)
        bounding_box = power_toughness_font.getbbox(text)
        text_height = int(bounding_box[3] - bounding_box[1])
        draw.text(
            ((power_toughness_width - text_width) // 2, (power_toughness_height - text_height) // 4),
            text,
            font=power_toughness_font,
            fill="black",
        )

        self.text_layers.append(Layer(image, (power_toughness_x, power_toughness_y)))

    def create_layers(self):
        """
        Append every frame, text, and collector layer to the card based on `self.metadata`.
        """

        self.create_frame_layers()
        self.create_collector_layers()
        self.create_text_layers()

    def add_metadata(self, key: str, value: str, append: bool = False):
        """
        Add new metadata to the card. If `append = True`, try to append the value to the existing
        metadata entry instead.

        Parameters
        ----------
        key: str
            The metadata entry to add, replace, or append to.

        value: str
            The value to set the metadata entry to.

        append: bool, default : False
            Whether to append the value to the existing value of the metadata entry or not.
        """

        if not append:
            self.metadata[key] = value
        else:
            if isinstance(self.metadata[key], list):
                self.metadata[key].append(value)
            else:
                log(f"The value of '{key}' is not a list.")
