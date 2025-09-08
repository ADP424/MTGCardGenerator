import io
import re
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from constants import (
    CARD_TITLE,
    CARD_MANA_COST,
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_RULES_TEXT,
    FLAVOR_TEXT_FONT,
    LINE_HEIGHT_TO_GAP_RATIO,
    MANA_COST_HEADER_HEIGHT,
    MANA_COST_HEADER_WIDTH,
    MANA_COST_HEADER_X,
    MANA_COST_HEADER_Y,
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
    RULES_TEXT_FONT,
    PLACEHOLDER_REGEX,
)
from log import log
from model.Layer import Layer
from utils import replace_ticks


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
        The layers of card frames. Lower-index layers are rendered first. Renders after art, before text.

    text_layers : list[Layer], default : []
        The layers of card text. Lower-index layers are rendered first. Renders after art and frames.
    """

    def __init__(
        self,
        base_width: int = CARD_WIDTH,
        base_height: int = CARD_HEIGHT,
        metadata: dict[str, str | list] = None,
        frame_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
    ):
        self.base_width = base_width
        self.base_height = base_height
        self.metadata = metadata if metadata is not None else {}
        self.frame_layers = frame_layers if frame_layers is not None else []
        self.text_layers = text_layers if text_layers is not None else []

    def _image_is_valid(self, image: Image.Image):
        try:
            with io.BytesIO() as buffer:
                image.save(buffer, format="PNG")
                buffer.seek(0)
                with Image.open(buffer) as temp:
                    temp.verify()
            return True
        except Exception as e:
            log(f"Image invalid: {e}")
            return False

    def add_frame_layer(
        self,
        image: Image.Image | str,
        index: int = None,
        position: tuple[int, int] = (0, 0),
    ):
        """
        Add a layer with the image at the given path before the given index.

        Parameters
        ----------
        image: Image.Image | str
            The Image, or the path to the image, to set the layer to.

        index: int, optional
            The index to add the layer before. Adds to the top if not given.

        position: tuple[int, int], default : (0, 0)
            The position of the layer relative to the top left corner of the image.
        """

        if isinstance(image, str):
            image = Image.open(image)

        if not self._image_is_valid(image):
            raise AttributeError

        if index is None:
            self.frame_layers.append(Layer(image, position))
        else:
            self.frame_layers.insert(index, Layer(image, position))

    def remove_frame_layer(self, index: int):
        """
        Remove the layer at the given index.

        Parameters
        ----------
        index: int
            The index of the layer to remove.
        """

        self.frame_layers.pop(index)

    def merge_layers(self) -> Image.Image:
        """
        Merge all layers into one image.

        Returns
        -------
        Image
            The merged image. Returns None if the Card has no layers.
        """

        if len(self.frame_layers) == 0:
            return None

        base_image = Image.new("RGBA", (self.base_width, self.base_height), (0, 0, 0, 0))
        composite_image = base_image.copy()

        for layer in self.frame_layers:
            composite_image.paste(layer.image, layer.position, mask=layer.image)
        for layer in self.text_layers:
            composite_image.paste(layer.image, layer.position, mask=layer.image)

        return composite_image
    
    def render_text(self):
        """
        Append every layer of text of the card (rules text, mana cost, etc.) to `self.text_layers`.
        """

        self.render_mana_cost()
        self.render_rules_text()

    def render_mana_cost(
        self,
        text: str = None,
        header_x: int = MANA_COST_HEADER_X,
        header_y: int = MANA_COST_HEADER_Y,
        header_width: int = MANA_COST_HEADER_WIDTH,
        header_height: int = MANA_COST_HEADER_HEIGHT,
    ):
        """
        Render MTG mana cost in the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The mana cost text to render. Uses the mana cost text in the card's metadata if not given.

        header_x: int, default : `MANA_COST_HEADER_X`
            The leftmost x position of the mana cost header.

        header_y: int, default : `MANA_COST_HEADER_Y`
            The topmost y position of the mana cost header.

        header_width: int, default : `MANA_COST_HEADER_WIDTH`
            The width of the frame's mana cost header.

        header_height: int, default : `MANA_COST_HEADER_HEIGHT`
            The height of the frame's mana cost header.
        """

        if text is None:
            text = self.metadata.get(CARD_MANA_COST, "")
        text = re.sub(r"{+|}+", " ", text) # remove braces
        text = re.sub(r"\s+", " ", text) # remove strings of whitespace longer than 1
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

            # Create shadow by using the alpha channel
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

            curr_x -= (symbol_image.width + MANA_COST_SYMBOL_SPACING)
            if curr_x >= symbol_image.width:
                image.alpha_composite(
                    symbol_image, (int(curr_x), (header_height - symbol_image.height) // 2)
                )
            else:
                log(f"The mana cost is too long on '{self.metadata.get(CARD_TITLE, "Unknown Card")}'.")
                break

        self.text_layers.append(Layer(image, (header_x, header_y)))

    def _replace_text_placeholders(self, text: str) -> str:
        """
        Replace standard placeholders in the format `{PLACEHOLDER}` with what they represent.
        """

        new_text = re.sub("{cardname}", self.metadata.get(CARD_TITLE, ""), text, flags=re.IGNORECASE)
        return new_text

    def render_rules_text(
        self,
        text: str = None,
        box_x: int = RULES_BOX_X,
        box_y: int = RULES_BOX_Y,
        box_width: int = RULES_BOX_WIDTH,
        box_height: int = RULES_BOX_HEIGHT,
    ):
        """
        Render MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The rules text to render. Uses the rules text in the card's metadata if not given.

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

        text = self._replace_text_placeholders(text)

        flavor_split: list[str] = re.split(r"\{flavor\}", text)
        raw_rules_text = flavor_split[0]
        raw_flavor_texts = flavor_split[1:] if len(flavor_split) > 1 else []

        for font_size in range(RULES_BOX_MAX_FONT_SIZE, RULES_BOX_MIN_FONT_SIZE - 1, -1):
            rules_font = ImageFont.truetype(RULES_TEXT_FONT, font_size)
            flavor_font = ImageFont.truetype(FLAVOR_TEXT_FONT, font_size)

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
                        curr_width += width

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
                                image.alpha_composite(symbol_image, (int(curr_x), int(curr_y)))
                            else:
                                placeholder = f"[{value}]"
                                draw.text((curr_x, curr_y), placeholder, font=text_font, fill="red")
                            curr_x += width
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
