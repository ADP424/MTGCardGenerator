import re
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont

from constants import (
    ART_PATH,
    ARTIST_GAP_LENGTH,
    BELEREN_BOLD_SMALL_CAPS,
    CARD_CREATION_DATE,
    CARD_FRAMES,
    CARD_INDEX,
    CARD_TITLE,
    CARD_SUPERTYPES,
    CARD_TYPES,
    CARD_RARITY,
    CARD_SET,
    CARD_SUBTYPES,
    CARD_POWER_TOUGHNESS,
    CARD_MANA_COST,
    CARD_LANGUAGE,
    CARD_ARTIST,
    FOOTER_FONT_OUTLINE_SIZE,
    FOOTER_FONT_SIZE,
    FOOTER_HEIGHT,
    FOOTER_LINE_HEIGHT_TO_GAP_RATIO,
    FOOTER_TAB_LENGTH,
    FOOTER_WIDTH,
    FOOTER_X,
    FOOTER_Y,
    GOTHAM_BOLD,
    POWER_TOUGHNESS_FONT_COLOR,
    RARITY_TO_INITIAL,
    REVERSE_POWER_TOUGHNESS_FONT_COLOR,
    REVERSE_POWER_TOUGHNESS_FONT_SIZE,
    SET_SYMBOL_WIDTH,
    SET_SYMBOL_X,
    SET_SYMBOL_Y,
    SET_SYMBOLS_PATH,
    TITLE_FONT_COLOR,
    TITLE_MIN_FONT_SIZE,
    TYPE_FONT_COLOR,
    TYPE_MIN_FONT_SIZE,
    WATERMARK_COLORS,
    CARD_WATERMARK_COLOR,
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_FRAME_LAYOUT,
    CARD_RULES_TEXT,
    CARD_WATERMARK,
    WATERMARKS_PATH,
    MPLANTIN_ITALICS,
    FRAMES_PATH,
    RULES_TEXT_LINE_HEIGHT_TO_GAP_RATIO,
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
    TITLE_MAX_FONT_SIZE,
    TITLE_WIDTH,
    TITLE_X,
    TITLE_Y,
    TYPE_BOX_HEIGHT,
    TYPE_MAX_FONT_SIZE,
    TYPE_MAX_WIDTH,
    TYPE_X,
    TYPE_Y,
    WATERMARK_OPACITY,
    WATERMARK_WIDTH,
    CARD_REVERSE_POWER_TOUGHNESS,
    REVERSE_POWER_TOUGHNESS_WIDTH,
    REVERSE_POWER_TOUGHNESS_HEIGHT,
    REVERSE_POWER_TOUGHNESS_X,
    REVERSE_POWER_TOUGHNESS_Y,
)
from log import log
from model.Layer import Layer
from utils import cardname_to_filename, open_image, replace_ticks


class Card:
    """
    A layered image representing a card and all the collection info on it, with all relevant card metadata.

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
    """

    def __init__(
        self,
        metadata: dict[str, str | list["Card"]] = None,
        base_width: int = None,
        base_height: int = None,
        art_layer: Layer = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
    ):
        self.metadata = metadata if metadata is not None else {}
        self.base_width = base_width if base_width is not None else CARD_WIDTH[self.get_frame_layout()]
        self.base_height = base_height if base_height is not None else CARD_HEIGHT[self.get_frame_layout()]
        self.art_layer = art_layer
        self.frame_layers = frame_layers if frame_layers is not None else []
        self.collector_layers = collector_layers if collector_layers is not None else []
        self.text_layers = text_layers if text_layers is not None else []

    def create_layers(
        self,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_watermark_layer: bool = True,
        create_rarity_symbol_layer: bool = True,
        create_footer_layer: bool = True,
        create_mana_cost_layer: bool = True,
        create_title_layer: bool = True,
        create_type_layer: bool = True,
        create_rules_text_layer: bool = True,
        create_power_toughness_layer: bool = True,
        create_reverse_power_toughness_layer: bool = True,
    ):
        """
        Append every frame, text, and collector layer to the card based on `self.metadata`.

        Parameters
        ----------
        create_art_layer: bool, default: True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default: True
            Whether to put the card's frames on or not.

        create_watermark_layer: bool, default : True
            Whether to put the watermark on the card or not.

        create_rarity_symbol_layer: bool, default : True
            Whether to put the rarity/set symbol on the card or not.

        create_footer_layer: bool, default : True
            Whether to put the footer collector info on the bottom of the card or not.

        create_mana_cost_layer: bool, default : True
            Whether to put the mana cost of the card on it or not.

        create_title_layer: bool, default : True
            Whether to put the title of the card on it or not.

        create_type_layer: bool, default : True
            Whether to put the type line of the card on it or not.

        create_rules_text_layer: bool, default : True
            Whether to put the rules text of the card on it or not.

        create_power_toughness_layer: bool, default : True
            Whether to put the power & toughness of the card on it or not.

        create_reverse_power_toughness_layer: bool, default: True
            Whether to put the reverse power & toughness of the card on it or not.
        """

        # art layer
        if create_art_layer:
            self._create_art_layer()

        # frame layers
        if create_frame_layers:
            self._create_frame_layers()

        # collector info layers
        if create_watermark_layer:
            self._create_watermark_layer()
        if create_rarity_symbol_layer:
            self._create_rarity_symbol_layer()
        if create_footer_layer:
            self._create_footer_layer()

        # text layers
        if create_mana_cost_layer:
            self._create_mana_cost_layer()
        if create_title_layer:
            self._create_title_layer()
        if create_type_layer:
            self._create_type_layer()
        if create_rules_text_layer:
            self._create_rules_text_layer()
        if create_power_toughness_layer:
            self._create_power_toughness_layer()
        if create_reverse_power_toughness_layer:
            self._create_reverse_power_toughness_layer()

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

        for layer in [self.art_layer] + self.frame_layers + self.collector_layers + self.text_layers:
            temp = Image.new("RGBA", composite_image.size, (0, 0, 0, 0))
            if layer.image is not None:
                temp.paste(layer.image, layer.position)
                composite_image = Image.alpha_composite(composite_image, temp)

        return composite_image

    def get_metadata(self, key: str, default: str | list["Card"] = "") -> str | list["Card"]:
        """
        Fetch an entry from the card's metadata.

        Parameters
        ----------
        key: str
            The metadata entry to fetch the value of.

        default: any, default : ""
            The default value to return if the metadata entry isn't found.

        Returns
        -------

        """

        return self.metadata.get(key, default)

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
            if not self.get_metadata(key, False):
                self.metadata[key] = []
            if isinstance(self.metadata[key], list):
                self.metadata[key].append(value)
            else:
                log(f"The value of '{key}' is not a list.")

    def get_frame_layout(self) -> str:
        return self.get_metadata(CARD_FRAME_LAYOUT).lower()

    def _create_art_layer(self):
        """
        Create the art layer of the card from the art folder.
        """

        art_path = f"{ART_PATH}/{cardname_to_filename(self.get_metadata(CARD_TITLE))}.png"
        self.art_layer = Layer(open_image(art_path))

    def _create_frame_layers(self):
        """
        Append every frame layer to the card based on `self.metadata`.
        """

        card_frames = self.get_metadata(CARD_FRAMES)
        if len(card_frames) == 0:
            return

        pending_masks: list[Image.Image] = []

        for frame_path in card_frames.split("\n"):
            frame_path = frame_path.lower().strip()
            if len(frame_path) == 0:
                continue

            frame = open_image(f"{FRAMES_PATH}/{frame_path}.png")
            if frame is None:
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

    def _create_watermark_layer(
        self,
        watermark: Image.Image = None,
        watermark_color: tuple[int, int, int] | list[tuple[int, int, int]] = None,
        rules_box_x: int = None,
        rules_box_y: int = None,
        rules_box_width: int = None,
        rules_box_height: int = None,
        watermark_width: int = None,
        watermark_opacity: float = None,
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

        rules_box_x: int, optional
            The leftmost x position of the rules text box bounding the watermark.
            Determined by the frame layout in the metadata if not given.

        rules_box_y: int, optional
            The topmost y position of the rules text box bounding the watermark.
            Determined by the frame layout in the metadata if not given.

        rules_box_width: int, optional
            The width of the rules text box bounding the watermark.
            Determined by the frame layout in the metadata if not given.

        rules_box_height: int, optional
            The height of the rules text box bounding the watermark. Determined by the frame layout in the
            metadata if not given.

        watermark_width: int, optional
            The width of the watermark. Also determines the height, based on the relative scale of the image.
            Determined by the frame layout in the metadata if not given.

        watermark_opacity: int, optional
            The opacity of the watermark in the range [0.0, 1.0].
            Determined by the frame layout in the metadata if not given.
        """

        if watermark is None:
            watermark_path = f"{WATERMARKS_PATH}/{self.get_metadata(CARD_WATERMARK)}.png"
            watermark = open_image(watermark_path)
            if watermark is None:
                log(f"Could not find watermark at '{watermark_path}'.")
                return

        if watermark_color is None:
            colors = self.get_metadata(CARD_WATERMARK_COLOR)
            if len(colors) > 0:
                watermark_color = []
                for color in colors.splitlines():
                    color = WATERMARK_COLORS.get(color.lower().strip())
                    if color is not None:
                        watermark_color.append(color)
            else:
                # TODO: Figure out watermark color from color identity context
                pass

        if not watermark_color:
            watermark_color = (0, 0, 0)

        rules_box_x = RULES_BOX_X[self.get_frame_layout()] if rules_box_x is None else rules_box_x
        rules_box_y = RULES_BOX_Y[self.get_frame_layout()] if rules_box_y is None else rules_box_y
        rules_box_width = RULES_BOX_WIDTH[self.get_frame_layout()] if rules_box_width is None else rules_box_width
        rules_box_height = RULES_BOX_HEIGHT[self.get_frame_layout()] if rules_box_height is None else rules_box_height
        watermark_width = WATERMARK_WIDTH[self.get_frame_layout()] if watermark_width is None else watermark_width
        watermark_opacity = (
            WATERMARK_OPACITY[self.get_frame_layout()] if watermark_opacity is None else watermark_opacity
        )

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
        set_symbol_x: int = None,
        set_symbol_y: int = None,
        set_symbol_width: int = None,
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

        set_symbol_x: int, optional
            The leftmost x position of the set symbol. Determined by the frame layout in the metadata if not given.

        set_symbol_y: int, optional
            The topmost y position of the set symbol. Determined by the frame layout in the metadata if not given.

        set_symbol_width: int, optional
            The width of the set symbol. Determined by the frame layout in the metadata if not given.
        """

        if card_set is None:
            card_set = self.get_metadata(CARD_SET).lower().replace(" ", "_")
        if len(card_set) == 0:
            return

        if rarity is None:
            rarity = self.get_metadata(CARD_RARITY).lower()
        if len(rarity) == 0:
            return

        set_symbol_x = SET_SYMBOL_X[self.get_frame_layout()] if set_symbol_x is None else set_symbol_x
        set_symbol_y = SET_SYMBOL_Y[self.get_frame_layout()] if set_symbol_y is None else set_symbol_y
        set_symbol_width = SET_SYMBOL_WIDTH[self.get_frame_layout()] if set_symbol_width is None else set_symbol_width

        symbol_path = f"{SET_SYMBOLS_PATH}/{card_set}/{rarity}.png"
        rarity_symbol = open_image(symbol_path)
        if rarity_symbol is None:
            log(f"Could not find rarity symbol at '{symbol_path}'.")
            return

        rarity_symbol = rarity_symbol.resize(
            (set_symbol_width, int((set_symbol_width / rarity_symbol.width) * rarity_symbol.height))
        )
        self.collector_layers.append(Layer(rarity_symbol, (set_symbol_x, set_symbol_y)))

    def _create_footer_layer(
        self,
        card_set: str = None,
        rarity: str = None,
        creation_date: str = None,
        language: str = None,
        artist: str = None,
        largest_index: str = "999",
        add_total_card_count: bool = False,
        footer_x: int = None,
        footer_y: int = None,
        footer_width: int = None,
        footer_height: int = None,
    ):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.

        Parameters
        ----------
        card_set: str, optional
            The set of the card. Uses the set from the card's metadata, if any, if not given.

        rarity: str, optional
            The rarity of the card. Uses the rarity from the card's metadata if not given.

        creation_date: str, optional
            The date the card was created. Uses the creation date from the card's metadata if not given.

        language: str, optional
            The language to display next to the set name. Uses the language from the card's metadata if not given.

        artist: str, default : ""
            The artist to display on the footer. Uses the artist from the card's metadata if not given.

        largest_index: str, default : "999"
            The largest index among cards in this set, for the purposes of the collector number.

        add_total_card_count: bool, default : False
            Whether to include the card total in the collector number (i.e. "012 / 999").

        footer_x: int, optional
            The leftmost x position of the footer. Determined by the frame layout in the metadata if not given.

        footer_y: int, optional
            The topmost y position of the footer. Determined by the frame layout in the metadata if not given.

        footer_width: int, optional
            The width of the footer. Determined by the frame layout in the metadata if not given.

        footer_height: int, optional
            The height of the footer. Determined by the frame layout in the metadata if not given.
        """

        if card_set is None:
            card_set = self.get_metadata(CARD_SET)

        if rarity is None:
            rarity = self.get_metadata(CARD_RARITY)

        if creation_date is None:
            creation_date = self.get_metadata(CARD_CREATION_DATE)

        if language is None:
            language = self.get_metadata(CARD_LANGUAGE)

        if artist is None:
            artist = self.get_metadata(CARD_ARTIST)

        footer_x = FOOTER_X[self.get_frame_layout()] if footer_x is None else footer_x
        footer_y = FOOTER_Y[self.get_frame_layout()] if footer_y is None else footer_y
        footer_width = FOOTER_WIDTH[self.get_frame_layout()] if footer_width is None else footer_width
        footer_height = FOOTER_HEIGHT[self.get_frame_layout()] if footer_height is None else footer_height

        index = self.get_metadata(CARD_INDEX).zfill(len(largest_index))
        rarity_initial = RARITY_TO_INITIAL.get(rarity.lower(), "")

        footer_font = ImageFont.truetype(GOTHAM_BOLD, FOOTER_FONT_SIZE[self.get_frame_layout()])
        artist_font = ImageFont.truetype(BELEREN_BOLD_SMALL_CAPS, FOOTER_FONT_SIZE[self.get_frame_layout()])
        legal_font = ImageFont.truetype(MPLANTIN, FOOTER_FONT_SIZE[self.get_frame_layout()])

        image = Image.new("RGBA", (footer_width, footer_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        collector_number_text = f"{index}{f"/{largest_index}" if add_total_card_count else ""}"
        draw.text(
            (FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()], FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()]),
            collector_number_text,
            font=footer_font,
            fill="white",
            stroke_width=FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()],
            stroke_fill="black",
        )

        top_left_bounding_box = footer_font.getbbox(collector_number_text)
        collector_number_text_height = (
            int(top_left_bounding_box[3] - top_left_bounding_box[1]) + FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()]
        )
        set_info_y = (
            collector_number_text_height
            + collector_number_text_height // FOOTER_LINE_HEIGHT_TO_GAP_RATIO[self.get_frame_layout()]
        )

        set_info_text = f"{card_set}{" • " if len(card_set) > 0 else ""}{language}"
        draw.text(
            (FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()], set_info_y),
            set_info_text,
            font=footer_font,
            fill="white",
            stroke_width=FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()],
            stroke_fill="black",
        )

        rarity_artist_x = (
            max(
                int(footer_font.getlength(collector_number_text)) + FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()],
                int(footer_font.getlength(set_info_text)) + FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()],
            )
            + FOOTER_TAB_LENGTH[self.get_frame_layout()]
        )

        draw.text(
            (rarity_artist_x, FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()]),
            rarity_initial,
            font=footer_font,
            fill="white",
            stroke_width=FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()],
            stroke_fill="black",
        )

        artist_brush = SYMBOL_PLACEHOLDER_KEY.get("artist_brush")
        scale = FOOTER_FONT_SIZE[self.get_frame_layout()] / artist_brush.image.height
        artist_brush_width = int(artist_brush.image.width * scale)
        artist_brush_height = int(artist_brush.image.height * scale)
        artist_brush_image = artist_brush.get_formatted_image(
            artist_brush_width, artist_brush_height, FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()]
        )

        if len(artist) > 0:
            image.alpha_composite(artist_brush_image, (rarity_artist_x, set_info_y - artist_brush_image.height // 4))
        draw.text(
            (
                rarity_artist_x + artist_brush_image.width + ARTIST_GAP_LENGTH[self.get_frame_layout()],
                set_info_y,
            ),
            artist,
            font=artist_font,
            anchor="lt",
            fill="white",
            stroke_width=FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()],
            stroke_fill="black",
        )

        creation_date_width = (
            int(legal_font.getlength(creation_date)) + FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()]
        )
        draw.text(
            (footer_width - creation_date_width, set_info_y),
            creation_date,
            font=legal_font,
            fill="white",
            stroke_width=FOOTER_FONT_OUTLINE_SIZE[self.get_frame_layout()],
            stroke_fill="black",
        )

        self.text_layers.append(Layer(image, (footer_x, footer_y)))

    def _create_mana_cost_layer(
        self,
        text: str = None,
        header_x: int = None,
        header_y: int = None,
        header_width: int = None,
        header_height: int = None,
    ):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The mana cost text to process. Uses the mana cost text in the card's metadata if not given.

        header_x: int, optional
            The leftmost x position of the mana cost header.
            Determined by the frame layout in the metadata if not given.

        header_y: int, optional
            The topmost y position of the mana cost header. Determined by the frame layout in the metadata if not given.

        header_width: int, optional
            The width of the frame's mana cost header. Determined by the frame layout in the metadata if not given.

        header_height: int, optional
            The height of the frame's mana cost header. Determined by the frame layout in the metadata if not given.
        """

        if text is None:
            text = self.get_metadata(CARD_MANA_COST)
        if len(text) == 0:
            return

        header_x = TITLE_BOX_X[self.get_frame_layout()] if header_x is None else header_x
        header_y = TITLE_BOX_Y[self.get_frame_layout()] if header_y is None else header_y
        header_width = TITLE_BOX_WIDTH[self.get_frame_layout()] if header_width is None else header_width
        header_height = TITLE_BOX_HEIGHT[self.get_frame_layout()] if header_height is None else header_height

        text = re.sub(r"{+|}+", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        def add_drop_shadow(symbol_image: Image.Image, offset: tuple[int, int]) -> Image.Image:
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

        curr_x = header_width - MANA_COST_SYMBOL_SPACING[self.get_frame_layout()]
        for sym in reversed(text.split(" ")):
            symbol = SYMBOL_PLACEHOLDER_KEY.get(sym.strip().lower(), None)
            if symbol is None:
                log(f"Unknown placeholder '{{{sym}}}'")
                continue

            scale = MANA_COST_SYMBOL_SIZE[self.get_frame_layout()] / symbol.image.height
            width = int(symbol.image.width * scale)
            height = int(symbol.image.height * scale)
            symbol_image = add_drop_shadow(
                symbol.get_formatted_image(width, height), MANA_COST_SYMBOL_SHADOW_OFFSET[self.get_frame_layout()]
            )

            curr_x -= symbol_image.width + MANA_COST_SYMBOL_SPACING[self.get_frame_layout()]
            if curr_x >= symbol_image.width:
                image.alpha_composite(symbol_image, (int(curr_x), (header_height - symbol_image.height) // 2))
            else:
                log("The mana cost is too long and has been cut off.")
                break

        self.text_layers.append(Layer(image, (header_x, header_y)))

    def _create_title_layer(
        self,
        text: str = None,
        header_x: int = None,
        header_y: int = None,
        header_width: int = None,
        header_height: int = None,
    ):
        """
        Process title text into the title and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The title text to process. Uses the title in the card's metadata if not given.

        header_x: int, optional
            The leftmost x position of the title header. Determined by the frame layout in the metadata if not given.

        header_y: int, optional
            The topmost y position of the title header. Determined by the frame layout in the metadata if not given.

        header_width: int, optional
            The width of the frame's title header. Determined by the frame layout in the metadata if not given.

        header_height: int, optional
            The height of the frame's title header box. Determined by the frame layout in the metadata if not given.
        """

        if text is None:
            text = self.get_metadata(CARD_TITLE)
        if len(text) == 0:
            return

        header_x = TITLE_X[self.get_frame_layout()] if header_x is None else header_x
        header_y = TITLE_Y[self.get_frame_layout()] if header_y is None else header_y
        header_width = TITLE_WIDTH[self.get_frame_layout()] if header_width is None else header_width
        header_height = TITLE_BOX_HEIGHT[self.get_frame_layout()] if header_height is None else header_height

        font_size = TITLE_MAX_FONT_SIZE[self.get_frame_layout()]
        title_font = ImageFont.truetype(BELEREN_BOLD, font_size)
        while (
            header_x + title_font.getlength(text) > SET_SYMBOL_X[self.get_frame_layout()]
            and font_size >= TITLE_MIN_FONT_SIZE[self.get_frame_layout()]
        ):
            font_size -= 1
            title_font = ImageFont.truetype(BELEREN_BOLD, font_size)

        image = Image.new("RGBA", (header_width, header_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        ascent = title_font.getmetrics()[0]
        draw.text(
            (0, (header_height - ascent) // 2),
            text,
            font=title_font,
            fill=TITLE_FONT_COLOR[self.get_frame_layout()],
            anchor="lt",
        )

        self.text_layers.append(Layer(image, (header_x, header_y)))

    def _create_type_layer(
        self,
        text: str = None,
        header_x: int = None,
        header_y: int = None,
        header_width: int = None,
        header_height: int = None,
    ):
        """
        Process type text into the type box and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The type text to process. Uses the type in the card's metadata if not given.

        header_x: int, optional
            The leftmost x position of the type header. Determined by the frame layout in the metadata if not given.

        header_y: int, optional
            The topmost y position of the type header. Determined by the frame layout in the metadata if not given.

        header_width: int, optional
            The width of the frame's type header. Determined by the frame layout in the metadata if not given.

        header_height: int, optional
            The height of the frame's type header box. Determined by the frame layout in the metadata if not given.
        """

        if text is None:
            first_part = f"{self.get_metadata(CARD_SUPERTYPES)} {self.get_metadata(CARD_TYPES)}"
            second_part = self.get_metadata(CARD_SUBTYPES)
            if len(second_part) > 0:
                text = " — ".join((first_part, second_part)).strip()
            else:
                text = first_part.strip()
        if len(text) == 0:
            return

        header_x = TYPE_X[self.get_frame_layout()] if header_x is None else header_x
        header_y = TYPE_Y[self.get_frame_layout()] if header_y is None else header_y
        header_width = TYPE_MAX_WIDTH[self.get_frame_layout()] if header_width is None else header_width
        header_height = TYPE_BOX_HEIGHT[self.get_frame_layout()] if header_height is None else header_height

        font_size = TYPE_MAX_FONT_SIZE[self.get_frame_layout()]
        type_font = ImageFont.truetype(BELEREN_BOLD, font_size)
        while (
            header_x + type_font.getlength(text) > SET_SYMBOL_X[self.get_frame_layout()]
            and font_size >= TYPE_MIN_FONT_SIZE[self.get_frame_layout()]
        ):
            font_size -= 1
            type_font = ImageFont.truetype(BELEREN_BOLD, font_size)

        image = Image.new("RGBA", (header_width, header_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        ascent = type_font.getmetrics()[0]
        draw.text(
            (0, (header_height - ascent) // 2),
            text,
            font=type_font,
            fill=TYPE_FONT_COLOR[self.get_frame_layout()],
            anchor="lt",
        )

        self.text_layers.append(Layer(image, (header_x, header_y)))

    def _replace_text_placeholders(self, text: str) -> str:
        """
        Replace standard placeholders in the format `{PLACEHOLDER}` with what they represent.
        """

        new_text = text
        new_text = re.sub("{cardname}", self.get_metadata(CARD_TITLE), new_text, flags=re.IGNORECASE)
        new_text = re.sub("{-}", "—", new_text)
        return new_text

    def _create_rules_text_layer(
        self,
        text: str = None,
        box_x: int = None,
        box_y: int = None,
        box_width: int = None,
        box_height: int = None,
    ):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The rules text to process. Uses the rules text in the card's metadata if not given.

        box_x: int, optional
            The leftmost x position of the rules box. Determined by the frame layout in the metadata if not given.

        box_y: int, optional
            The topmost y position of the rules box. Determined by the frame layout in the metadata if not given.

        box_width: int, optional
            The width of the frame's rules box. Determined by the frame layout in the metadata if not given.

        box_height: int, optional
            The height of the frame's rules box. Determined by the frame layout in the metadata if not given.
        """

        if text is None:
            text = self.get_metadata(CARD_RULES_TEXT)
        if len(text) == 0:
            return

        box_x = RULES_BOX_X[self.get_frame_layout()] if box_x is None else box_x
        box_y = RULES_BOX_Y[self.get_frame_layout()] if box_y is None else box_y
        box_width = RULES_BOX_WIDTH[self.get_frame_layout()] if box_width is None else box_width
        box_height = RULES_BOX_HEIGHT[self.get_frame_layout()] if box_height is None else box_height

        text = self._replace_text_placeholders(text)

        flavor_split: list[str] = re.split(r"\{flavor\}", text)
        raw_rules_text = flavor_split[0]
        raw_flavor_texts = flavor_split[1:] if len(flavor_split) > 1 else []

        for font_size in range(
            RULES_BOX_MAX_FONT_SIZE[self.get_frame_layout()], RULES_BOX_MIN_FONT_SIZE[self.get_frame_layout()] - 1, -1
        ):
            rules_font = ImageFont.truetype(MPLANTIN, font_size)
            italics_font = ImageFont.truetype(MPLANTIN_ITALICS, font_size)

            line_height = font_size
            margin = int(font_size * 0.25)
            max_line_width = box_width - 2 * margin

            def parse_fragments(line: str) -> list[tuple[str, str]]:
                """
                Return [("text", str), ("symbol", token), ("format", "italic_on"/"italic_off"), ...]
                """
                fragments = []
                parts = PLACEHOLDER_REGEX.split(line)
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        if part:
                            fragments.append(("text", part))
                    else:
                        token = part.strip()
                        if token == "I":
                            fragments.append(("format", "italic_on"))
                        elif token == "\\I":
                            fragments.append(("format", "italic_off"))
                        else:
                            fragments.append(("symbol", token))
                return fragments

            def get_symbol_metrics(token: str) -> tuple[int, int, Image.Image | None]:
                """
                Return (width, height, Image | None) scaled to current font size.
                """

                symbol = SYMBOL_PLACEHOLDER_KEY.get(token.lower(), None)

                if symbol is None:
                    placeholder = f"[{token}]"
                    return int(rules_font.getlength(placeholder)), font_size, None

                scale = MANA_SYMBOL_RULES_TEXT_SCALE[self.get_frame_layout()] * font_size / symbol.image.height
                width = int(symbol.image.width * scale)
                height = int(symbol.image.height * scale)
                symbol = symbol.get_formatted_image(width, height)
                return width, height, symbol

            def wrap_text_fragments(
                frags: list[tuple[str, str]], regular_font: ImageFont.FreeTypeFont, italic_font: ImageFont.FreeTypeFont
            ) -> list[list[tuple[str, str, ImageFont.FreeTypeFont]]]:
                """
                Split the lines into individual words and symbols, then wrap them so that they fit within
                `max_line_width` (based on rules box size and margins).
                """

                lines = []
                curr_fragment = []
                curr_width = 0
                curr_font = regular_font

                def go_to_newline():
                    nonlocal curr_fragment, curr_width
                    if curr_fragment:
                        lines.append(curr_fragment)
                    curr_fragment, curr_width = [], 0

                for kind, value in frags:
                    if kind == "format":
                        if value == "italic_on":
                            curr_font = italic_font
                        elif value == "italic_off":
                            curr_font = regular_font
                        continue
                    elif kind == "symbol":
                        if value.lower() == "lns":
                            go_to_newline()
                            continue
                        width, _, _ = get_symbol_metrics(value)
                        if curr_fragment and curr_width + width > max_line_width:
                            go_to_newline()
                        curr_fragment.append(("symbol", value, curr_font))
                        curr_width += width + MANA_SYMBOL_RULES_TEXT_MARGIN[self.get_frame_layout()]
                    else:
                        for word in re.findall(r"\S+|\s+", value):
                            word = replace_ticks(word)
                            width = curr_font.getlength(word)

                            if word.isspace():
                                if not curr_fragment:
                                    continue
                                if curr_width + width > max_line_width:
                                    go_to_newline()
                                    continue
                                curr_fragment.append(("text", word, curr_font))
                                curr_width += width
                            else:
                                if curr_fragment and curr_width + width > max_line_width:
                                    go_to_newline()
                                if width > max_line_width:
                                    for char in word:
                                        char_width = curr_font.getlength(char)
                                        if curr_fragment and curr_width + char_width > max_line_width:
                                            go_to_newline()
                                        curr_fragment.append(("text", char, curr_font))
                                        curr_width += char_width
                                else:
                                    curr_fragment.append(("text", word, curr_font))
                                    curr_width += width

                if curr_fragment:
                    lines.append(curr_fragment)
                return lines

            # Split the rules text into lines that fit the rules box horizontally
            rules_lines: list[list[tuple[str, str, ImageFont.FreeTypeFont]]] = []
            for line in raw_rules_text.splitlines():
                rules_fragments = parse_fragments(line)
                rules_lines += (
                    wrap_text_fragments(rules_fragments, rules_font, italics_font)
                    if rules_fragments
                    else [[("text", "")]]
                )
                rules_lines.append([("newline", None)])
            rules_lines.pop()  # remove the ending newline

            # Split the flavor text into lines that fit the rules box horizontally
            flavor_lines: list[list[list[tuple[str, str, ImageFont.FreeTypeFont]]]] = []
            for raw_flavor_text in raw_flavor_texts:
                flavor_lines.append([])
                for line in raw_flavor_text.splitlines():
                    flavor_fragments = parse_fragments(line)
                    flavor_lines[-1] += (
                        wrap_text_fragments(flavor_fragments, italics_font, italics_font)
                        if flavor_fragments
                        else [[("text", "")]]
                    )
                    flavor_lines[-1].append([("newline", None)])
                flavor_lines[-1].pop()  # remove the ending newline

            # If the lines of text are too tall, try the process again with a different font
            content_height = 0
            for line in rules_lines:
                if line[0][0] == "newline":
                    content_height += line_height // RULES_TEXT_LINE_HEIGHT_TO_GAP_RATIO[self.get_frame_layout()]
                else:
                    content_height += line_height
            for lines in flavor_lines:
                for line in lines:
                    if line[0][0] == "newline":
                        content_height += line_height // RULES_TEXT_LINE_HEIGHT_TO_GAP_RATIO[self.get_frame_layout()]
                    else:
                        content_height += line_height
                content_height += SYMBOL_PLACEHOLDER_KEY["flavor"].image.height + line_height
            usable_height = box_height - 2 * margin
            if content_height > usable_height:
                continue

            image = Image.new("RGBA", (box_width, box_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            # check for power/toughness overlap
            power_toughness_x = POWER_TOUGHNESS_X[self.get_frame_layout()]
            power_toughness_y = POWER_TOUGHNESS_Y[self.get_frame_layout()]
            if box_y + usable_height >= power_toughness_y:
                final_line = flavor_lines[-1][-1] if len(flavor_lines) > 0 else rules_lines[-1]
                final_line_width = 0
                for kind, value, frag_font in final_line:
                    if kind == "text":
                        if value:
                            final_line_width += draw.textlength(value, font=frag_font)
                    else:
                        width, _, _ = get_symbol_metrics(value)
                        final_line_width += width + MANA_SYMBOL_RULES_TEXT_MARGIN[self.get_frame_layout()]
                if box_x + final_line_width >= power_toughness_x:
                    continue

            curr_y = margin + (usable_height - content_height) // 2

            def draw_lines(lines: list[list[tuple[str, str, str]]], text_font: ImageFont.ImageFont):
                """
                Render lines of text as images.
                """

                nonlocal curr_y
                for line_fragments in lines:
                    if line_fragments and line_fragments[0][0] == "newline":
                        curr_y += (
                            line_height // RULES_TEXT_LINE_HEIGHT_TO_GAP_RATIO[self.get_frame_layout()]
                        )  # add an extra gap for user-specified newlines
                        continue

                    curr_x = margin
                    for kind, value, frag_font in line_fragments:
                        if kind == "text":
                            if value:
                                draw.text((curr_x, curr_y), value, font=frag_font, fill="black")
                                curr_x += draw.textlength(value, font=frag_font)
                        else:
                            width, _, symbol_image = get_symbol_metrics(value)
                            if symbol_image is not None:
                                image.alpha_composite(
                                    symbol_image,
                                    (
                                        int(curr_x),
                                        int(curr_y + MANA_SYMBOL_RULES_TEXT_MARGIN[self.get_frame_layout()]),
                                    ),
                                )
                            else:
                                placeholder = f"[{value}]"
                                draw.text((curr_x, curr_y), placeholder, font=text_font, fill="red")
                            curr_x += width + MANA_SYMBOL_RULES_TEXT_MARGIN[self.get_frame_layout()]
                    curr_y += line_height

            draw_lines(rules_lines, rules_font)
            for lines in flavor_lines:
                curr_y += line_height // 2
                image.alpha_composite(
                    SYMBOL_PLACEHOLDER_KEY["flavor"].image.resize(
                        (box_width, SYMBOL_PLACEHOLDER_KEY["flavor"].image.height)
                    ),
                    (0, curr_y),
                )
                curr_y += SYMBOL_PLACEHOLDER_KEY["flavor"].image.height + line_height // 2
                draw_lines(lines, italics_font)

            self.text_layers.append(Layer(image, (box_x, box_y)))
            return

        raise ValueError("Text is too long to fit in box even at minimum font size.")

    def _create_power_toughness_layer(
        self,
        text: str = None,
        power_toughness_x: int = None,
        power_toughness_y: int = None,
        power_toughness_width: int = None,
        power_toughness_height: int = None,
    ):
        """
        Process power & toughness text into the power & toughness area and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The power & toughness text to process. Uses the power & toughness in the card's metadata if not given.

        power_toughness_x: int, optional
            The leftmost x position of the power & touchness box.
            Determined by the frame layout in the metadata if not given.

        power_toughness_y: int, optional
            The topmost y position of the power & touchness box.
            Determined by the frame layout in the metadata if not given.

        power_toughness_width: int, optional
            The width of the frame's power & toughness area.
            Determined by the frame layout in the metadata if not given.

        power_toughness_height: int, optional
            The height of the frame's power & toughness area.
            Determined by the frame layout in the metadata if not given.
        """

        if text is None:
            text = self.get_metadata(CARD_POWER_TOUGHNESS).replace("*", "★")
        if len(text) == 0:
            return

        power_toughness_x = (
            POWER_TOUGHNESS_X[self.get_frame_layout()] if power_toughness_x is None else power_toughness_x
        )
        power_toughness_y = (
            POWER_TOUGHNESS_Y[self.get_frame_layout()] if power_toughness_y is None else power_toughness_y
        )
        power_toughness_width = (
            POWER_TOUGHNESS_WIDTH[self.get_frame_layout()] if power_toughness_width is None else power_toughness_width
        )
        power_toughness_height = (
            POWER_TOUGHNESS_HEIGHT[self.get_frame_layout()]
            if power_toughness_height is None
            else power_toughness_height
        )

        power_toughness_font = ImageFont.truetype(
            BELEREN_BOLD_SMALL_CAPS, POWER_TOUGHNESS_FONT_SIZE[self.get_frame_layout()]
        )
        image = Image.new("RGBA", (power_toughness_width, power_toughness_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        text_width = int(power_toughness_font.getlength(text))
        bounding_box = power_toughness_font.getbbox(text)
        text_height = int(bounding_box[3] - bounding_box[1])

        draw.text(
            ((power_toughness_width - text_width) // 2, (power_toughness_height - text_height) // 2),
            text,
            font=power_toughness_font,
            fill=POWER_TOUGHNESS_FONT_COLOR[self.get_frame_layout()],
            anchor="lt"
        )

        self.text_layers.append(Layer(image, (power_toughness_x, power_toughness_y)))

    def _create_reverse_power_toughness_layer(
        self,
        text: str = None,
        power_toughness_x: int = None,
        power_toughness_y: int = None,
        power_toughness_width: int = None,
        power_toughness_height: int = None,
    ):
        """
        Process reverse power & toughness text for transform cards and append it to `self.text_layers`.

        Parameters
        ----------
        text: str, optional
            The reverse power & toughness text to process.
            Uses the power & toughness in the card's metadata if not given.

        power_toughness_x: int, optional
            The leftmost x position of the reverse power & toughness area.
            Determined by the frame layout in the metadata if not given.

        power_toughness_y: int, optional
            The topmost y position of the reverse power & toughness area.
            Determined by the frame layout in the metadata if not given.

        power_toughness_width: int, optional
            The width of the frame's reverse power & toughness area.
            Determined by the frame layout in the metadata if not given.

        power_toughness_height: int, optional
            The height of the frame's reverse power & toughness area.
            Determined by the frame layout in the metadata if not given.
        """

        if text is None:
            text = self.get_metadata(CARD_REVERSE_POWER_TOUGHNESS)
        if len(text) == 0:
            return

        power_toughness_x = (
            REVERSE_POWER_TOUGHNESS_X[self.get_frame_layout()] if power_toughness_x is None else power_toughness_x
        )
        power_toughness_y = (
            REVERSE_POWER_TOUGHNESS_Y[self.get_frame_layout()] if power_toughness_y is None else power_toughness_y
        )
        power_toughness_width = (
            REVERSE_POWER_TOUGHNESS_WIDTH[self.get_frame_layout()]
            if power_toughness_width is None
            else power_toughness_width
        )
        power_toughness_height = (
            REVERSE_POWER_TOUGHNESS_HEIGHT[self.get_frame_layout()]
            if power_toughness_height is None
            else power_toughness_height
        )

        power_toughness_font = ImageFont.truetype(
            BELEREN_BOLD_SMALL_CAPS, REVERSE_POWER_TOUGHNESS_FONT_SIZE[self.get_frame_layout()]
        )
        image = Image.new("RGBA", (power_toughness_width, power_toughness_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        text_width = power_toughness_font.getlength(text)
        bounding_box = power_toughness_font.getbbox(text)
        text_height = int(bounding_box[3] - bounding_box[1])
        draw.text(
            ((power_toughness_width - text_width) // 2, (power_toughness_height - text_height) // 4),
            text,
            font=power_toughness_font,
            fill=REVERSE_POWER_TOUGHNESS_FONT_COLOR[self.get_frame_layout()],
        )

        self.text_layers.append(Layer(image, (power_toughness_x, power_toughness_y)))
