import io
import re
from PIL import Image, ImageDraw, ImageFont

from constants import (
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_RULES_TEXT,
    FLAVOR_TEXT_FONT,
    LINE_HEIGHT_TO_GAP_RATIO,
    MANA_SYMBOL_FONT,
    MANA_SYMBOL_RULES_TEXT_SCALE,
    PLACEHOLDER_KEY,
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

    def add_layer(
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

    def remove_layer(self, index: int):
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

    def render_rules_text(self, text: str = None, box_width: int = RULES_BOX_WIDTH, box_height: int = RULES_BOX_HEIGHT):
        """
        Render MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The rules text to render. Uses the rules text in the card's metadata if not given.

        box_width: int, default : `RULES_BOX_WIDTH`
            The width of the frame's rules box.

        box_height: int, default : `RULES_BOX_HEIGHT`
            The height of the frame's rules box.
        """

        if text is None:
            text = self.metadata.get(CARD_RULES_TEXT, "")

        flavor_split: list[str] = re.split(r"\{flavor\}", text)
        raw_rules_text = flavor_split[0]
        raw_flavor_texts = flavor_split[1:] if len(flavor_split) > 1 else []

        for font_size in range(RULES_BOX_MAX_FONT_SIZE, RULES_BOX_MIN_FONT_SIZE - 1, -1):
            rules_font = ImageFont.truetype(RULES_TEXT_FONT, font_size)
            flavor_font = ImageFont.truetype(FLAVOR_TEXT_FONT, font_size)
            mana_symbol_font = ImageFont.truetype(MANA_SYMBOL_FONT, font_size)
            
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

                symbol = PLACEHOLDER_KEY.get(token, None)

                if symbol is None:
                    placeholder = f"[{token}]"
                    return int(rules_font.getlength(placeholder)), font_size, None

                if isinstance(symbol, Image.Image):
                    scale = font_size / symbol.height
                    width, height = int(symbol.width * scale * MANA_SYMBOL_RULES_TEXT_SCALE), int(symbol.height * scale * MANA_SYMBOL_RULES_TEXT_SCALE)
                    symbol = symbol.resize((width, height), Image.LANCZOS)
                    return width, height, symbol

                return 0, 0, None

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
                            if word.isspace():
                                if not curr_fragment:  # get rid of leading spaces
                                    continue
                                width = text_font.getlength(word)
                                if curr_width + width > max_line_width:
                                    go_to_newline()
                                    continue
                                curr_fragment.append(("text", word))
                                curr_width += width
                            else:
                                width = text_font.getlength(word)
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
            rules_lines.pop() # remove the ending newline

            # Split the flavor text into lines that fit the rules box horizontally
            flavor_lines: list[list[list[tuple[str, str]]]] = []
            for raw_flavor_text in raw_flavor_texts:
                flavor_lines.append([])
                for line in raw_flavor_text.splitlines():
                    flavor_fragments = parse_fragments(line)
                    flavor_lines[-1] += (
                        wrap_text_fragments(flavor_fragments, flavor_font) if flavor_fragments else [["text", ""]]
                    )
                    flavor_lines[-1].append([("newline", None)])
                flavor_lines[-1].pop() # remove the ending newline

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
                content_height += PLACEHOLDER_KEY["flavor"].height + line_height
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
                        curr_y += line_height // LINE_HEIGHT_TO_GAP_RATIO # add an extra gap for user-specified newlines
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
                    PLACEHOLDER_KEY["flavor"].resize((box_width - 2 * margin, PLACEHOLDER_KEY["flavor"].height)),
                    (int(margin), int(curr_y)),
                )
                curr_y += PLACEHOLDER_KEY["flavor"].height + line_height // 2
                draw_lines(lines, flavor_font)

            self.frame_layers.append(Layer(image, (RULES_BOX_X, RULES_BOX_Y)))
            return image

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
