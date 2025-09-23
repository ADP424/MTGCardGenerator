import re
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont

from constants import (
    ADD_TOTAL_TO_FOOTER,
    ARTIST_BRUSH,
    CARD_DESCRIPTOR,
    CARD_OVERLAYS,
    RULES_DIVIDING_LINE,
    INPUT_ART_PATH,
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
    GOTHAM_BOLD,
    OVERLAYS_PATH,
    RARITY_TO_INITIAL,
    SET_SYMBOLS_PATH,
    WATERMARK_COLORS,
    CARD_WATERMARK_COLOR,
    CARD_FRAME_LAYOUT,
    CARD_RULES_TEXT,
    CARD_WATERMARK,
    WATERMARKS_PATH,
    MPLANTIN_ITALICS,
    FRAMES_PATH,
    SYMBOL_PLACEHOLDER_KEY,
    MPLANTIN,
    PLACEHOLDER_REGEX,
    BELEREN_BOLD,
)
from log import log
from model.Layer import Layer
from utils import cardname_to_filename, open_image, paste_image, replace_ticks


class RegularCard:
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
        self.metadata = metadata if metadata is not None else {}
        self.art_layer = art_layer if art_layer is not None else Layer(None)
        self.frame_layers = frame_layers if frame_layers is not None else []
        self.collector_layers = collector_layers if collector_layers is not None else []
        self.text_layers = text_layers if text_layers is not None else []
        self.overlay_layers = overlay_layers if overlay_layers is not None else []
        self.footer_largest_index = footer_largest_index

        # Overall Card
        self.CARD_WIDTH = 1500
        self.CARD_HEIGHT = 2100

        # Title Box
        self.TITLE_BOX_X = 90
        self.TITLE_BOX_Y = 105
        self.TITLE_BOX_WIDTH = 1313
        self.TITLE_BOX_HEIGHT = 114

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 70
        self.MANA_COST_SYMBOL_SPACING = 6
        self.MANA_COST_SYMBOL_SHADOW_OFFSET = (-1, 6)

        # Title Text
        self.TITLE_X = 128
        self.TITLE_Y = 113
        self.TITLE_WIDTH = 1244
        self.TITLE_MAX_FONT_SIZE = 79
        self.TITLE_MIN_FONT_SIZE = 6
        self.TITLE_FONT = BELEREN_BOLD
        self.TITLE_FONT_COLOR = (0, 0, 0)
        self.TITLE_TEXT_ALIGN = "left"

        # Type Box
        self.TYPE_BOX_HEIGHT = 114

        # Type Text
        self.TYPE_X = 128
        self.TYPE_Y = 1190
        self.TYPE_WIDTH = 1244
        self.TYPE_MAX_FONT_SIZE = 67
        self.TYPE_MIN_FONT_SIZE = 6
        self.TYPE_FONT_COLOR = (0, 0, 0)

        # Rules Text Box
        self.RULES_BOX_X = 112
        self.RULES_BOX_Y = 1315
        self.RULES_BOX_WIDTH = 1278
        self.RULES_BOX_HEIGHT = 623
        self.RULES_BOX_MAX_FONT_SIZE = 78
        self.RULES_BOX_MIN_FONT_SIZE = 6

        # Rules Text
        self.RULES_TEXT_X = 112
        self.RULES_TEXT_Y = 1315
        self.RULES_TEXT_WIDTH = 1278
        self.RULES_TEXT_HEIGHT = 623
        self.RULES_TEXT_FONT = MPLANTIN
        self.RULES_TEXT_FONT_ITALICS = MPLANTIN_ITALICS
        self.RULES_TEXT_FONT_COLOR = (0, 0, 0)
        self.RULES_TEXT_MANA_SYMBOL_SCALE = 0.78
        self.RULES_TEXT_MANA_SYMBOL_SPACING = 5
        self.RULES_TEXT_LINE_HEIGHT_TO_GAP_RATIO = 4

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1166
        self.POWER_TOUGHNESS_Y = 1866
        self.POWER_TOUGHNESS_WIDTH = 252
        self.POWER_TOUGHNESS_HEIGHT = 124
        self.POWER_TOUGHNESS_FONT_SIZE = 80
        self.POWER_TOUGHNESS_FONT_COLOR = (0, 0, 0)

        # Watermark
        self.WATERMARK_HEIGHT_TO_RULES_TEXT_HEIGHT_SCALE = 0.77
        self.WATERMARK_OPACITY = 0.4

        # Set / Rarity Symbol
        self.SET_SYMBOL_X = 1296
        self.SET_SYMBOL_Y = 1198
        self.SET_SYMBOL_WIDTH = 90

        # Footer
        # All RELATIVE values assume 0 degree rotation, the way the text would be read
        # This means width, height, tab length, etc. but NOT x or y coordinates
        self.FOOTER_ROTATION = 0
        self.FOOTER_X = 96
        self.FOOTER_Y = 1968
        self.FOOTER_WIDTH = 1304
        self.FOOTER_HEIGHT = 152
        self.FOOTER_FONT_SIZE = 35
        self.FOOTER_FONT_OUTLINE_SIZE = 3
        self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO = 2
        self.FOOTER_TAB_LENGTH = 25
        self.FOOTER_ARTIST_GAP_LENGTH = 5

        # set when mana cost layer is made to help with title spacing
        self.mana_cost_x = float("inf")

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
        create_overlay_layers: bool = True,
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

        create_overlay_layers: bool, default: True
            Whether to put the overlays on top of the card after everything else or not.
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

        # overlay layers
        if create_overlay_layers:
            self._create_overlay_layers()

    def render_card(self) -> Image.Image:
        """
        Merge all layers into one image.

        Returns
        -------
        Image
            The merged image.
        """

        base_image = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))
        composite_image = base_image.copy()

        for layer in (
            [self.art_layer] + self.frame_layers + self.collector_layers + self.text_layers + self.overlay_layers
        ):
            composite_image = paste_image(layer.image, composite_image, layer.position)

        return composite_image

    def get_metadata(self, key: str, default: str | list["RegularCard"] = "") -> str | list["RegularCard"]:
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

    def set_metadata(self, key: str, value: str, append: bool = False):
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

        card_title = self.get_metadata(CARD_TITLE)
        card_descriptor = self.get_metadata(CARD_DESCRIPTOR)
        card_key = f"{card_title}{f" - {card_descriptor}" if len(card_descriptor) > 0 else ""}"
        art_path = f"{INPUT_ART_PATH}/{cardname_to_filename(card_key)}.png"
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
                    combined_mask = ImageChops.multiply(combined_mask, base)

                # This is the important part: preserving the r, g, b and alpha separation to prevent banding
                r, g, b, original_alpha = frame.split()
                new_alpha = ImageChops.multiply(original_alpha, combined_mask)
                new_frame = Image.merge("RGBA", (r, g, b, new_alpha))

                pending_masks.clear()
                frame = new_frame

            self.frame_layers.append(Layer(frame))

        if pending_masks:
            log(
                f"Warning: {len(pending_masks)} mask layer(s) at end of frame list with no following frame."
                " They were ignored."
            )

    def _create_watermark_layer(self):
        """
        Process a watermark image and append it to `self.collector_layers`.
        Assumes the image is in RGBA format.
        """

        watermark_name = self.get_metadata(CARD_WATERMARK)
        if len(watermark_name) == 0:
            return
        watermark_path = f"{WATERMARKS_PATH}/{watermark_name}.png"
        watermark = open_image(watermark_path)
        if watermark is None:
            log(f"Could not find watermark at '{watermark_path}'.")
            return

        colors = self.get_metadata(CARD_WATERMARK_COLOR)
        if len(colors) > 0:
            watermark_color = []
            for color in colors.splitlines():
                color = WATERMARK_COLORS.get(color.lower().strip())
                if color is not None:
                    watermark_color.append(color)

        if not watermark_color:
            watermark_color = (0, 0, 0)

        watermark_height = int(self.WATERMARK_HEIGHT_TO_RULES_TEXT_HEIGHT_SCALE * self.RULES_BOX_HEIGHT)
        resized = watermark.resize(
            (int((watermark_height / watermark.height) * watermark.width), watermark_height)
        )

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
        alpha = ImageEnhance.Brightness(alpha).enhance(self.WATERMARK_OPACITY)
        made_translucent = Image.merge("RGBA", (r, g, b, alpha))

        self.collector_layers.append(
            Layer(
                made_translucent,
                (
                    self.RULES_BOX_X + (self.RULES_BOX_WIDTH - recolored.width) // 2,
                    self.RULES_BOX_Y + (self.RULES_BOX_HEIGHT - recolored.height) // 2,
                ),
            )
        )

    def _create_rarity_symbol_layer(self):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.
        """

        card_set = self.get_metadata(CARD_SET).lower().replace(" ", "_")
        if len(card_set) == 0:
            return

        rarity = self.get_metadata(CARD_RARITY).lower()
        if rarity == "token":
            rarity = "common"
        if len(rarity) == 0:
            return

        symbol_path = f"{SET_SYMBOLS_PATH}/{card_set}/{rarity}.png"
        rarity_symbol = open_image(symbol_path)
        if rarity_symbol is None:
            log(f"Could not find rarity symbol at '{symbol_path}'.")
            return

        rarity_symbol = rarity_symbol.resize(
            (self.SET_SYMBOL_WIDTH, int((self.SET_SYMBOL_WIDTH / rarity_symbol.width) * rarity_symbol.height))
        )
        self.collector_layers.append(Layer(rarity_symbol, (self.SET_SYMBOL_X, self.SET_SYMBOL_Y)))

    def _create_footer_layer(self):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.
        """

        card_set = self.get_metadata(CARD_SET)
        rarity = self.get_metadata(CARD_RARITY)
        creation_date = self.get_metadata(CARD_CREATION_DATE)
        language = self.get_metadata(CARD_LANGUAGE)
        artist = self.get_metadata(CARD_ARTIST)

        footer_x = self.FOOTER_X
        footer_y = self.FOOTER_Y
        footer_width = self.FOOTER_WIDTH
        footer_height = self.FOOTER_HEIGHT
        footer_rotation = self.FOOTER_ROTATION

        index = self.get_metadata(CARD_INDEX).zfill(len(str(self.footer_largest_index)))
        rarity_initial = RARITY_TO_INITIAL.get(rarity.lower(), "")

        footer_font = ImageFont.truetype(GOTHAM_BOLD, self.FOOTER_FONT_SIZE)
        artist_font = ImageFont.truetype(BELEREN_BOLD_SMALL_CAPS, self.FOOTER_FONT_SIZE)
        legal_font = ImageFont.truetype(MPLANTIN, self.FOOTER_FONT_SIZE)

        image = Image.new("RGBA", (footer_width, footer_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        try:
            add_total_to_footer = int(self.get_metadata(ADD_TOTAL_TO_FOOTER)) > 0
        except ValueError:
            add_total_to_footer = False
        collector_number_text = f"{index}{f"/{self.footer_largest_index}" if add_total_to_footer else ""}"
        draw.text(
            (self.FOOTER_FONT_OUTLINE_SIZE, self.FOOTER_FONT_OUTLINE_SIZE),
            collector_number_text,
            font=footer_font,
            fill="white",
            stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
            stroke_fill="black",
        )

        top_left_bounding_box = footer_font.getbbox(collector_number_text)
        collector_number_text_height = (
            int(top_left_bounding_box[3] - top_left_bounding_box[1]) + self.FOOTER_FONT_OUTLINE_SIZE
        )
        set_info_y = collector_number_text_height + collector_number_text_height // self.FOOTER_LINE_HEIGHT_TO_GAP_RATIO

        set_info_text = f"{card_set}{" • " if len(card_set) > 0 else ""}{language}"
        draw.text(
            (self.FOOTER_FONT_OUTLINE_SIZE, set_info_y),
            set_info_text,
            font=footer_font,
            fill="white",
            stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
            stroke_fill="black",
        )

        rarity_artist_x = (
            max(
                int(footer_font.getlength(collector_number_text)) + self.FOOTER_FONT_OUTLINE_SIZE,
                int(footer_font.getlength(set_info_text)) + self.FOOTER_FONT_OUTLINE_SIZE,
            )
            + self.FOOTER_TAB_LENGTH
        )

        draw.text(
            (rarity_artist_x, self.FOOTER_FONT_OUTLINE_SIZE),
            rarity_initial,
            font=footer_font,
            fill="white",
            stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
            stroke_fill="black",
        )

        scale = self.FOOTER_FONT_SIZE / ARTIST_BRUSH.image.height
        artist_brush_width = int(ARTIST_BRUSH.image.width * scale)
        artist_brush_height = int(ARTIST_BRUSH.image.height * scale)
        artist_brush_image = ARTIST_BRUSH.get_formatted_image(
            artist_brush_width, artist_brush_height, self.FOOTER_FONT_OUTLINE_SIZE
        )

        if len(artist) > 0:
            image.alpha_composite(artist_brush_image, (rarity_artist_x, set_info_y - artist_brush_image.height // 4))
        draw.text(
            (
                rarity_artist_x + artist_brush_image.width + self.FOOTER_ARTIST_GAP_LENGTH,
                set_info_y,
            ),
            artist,
            font=artist_font,
            anchor="lt",
            fill="white",
            stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
            stroke_fill="black",
        )

        creation_date_width = int(legal_font.getlength(creation_date)) + self.FOOTER_FONT_OUTLINE_SIZE
        draw.text(
            (footer_width - creation_date_width, set_info_y),
            creation_date,
            font=legal_font,
            fill="white",
            stroke_width=self.FOOTER_FONT_OUTLINE_SIZE,
            stroke_fill="black",
        )

        if footer_rotation == 90:
            image = image.transpose(Image.Transpose.ROTATE_90)
        elif footer_rotation == 180:
            image = image.transpose(Image.Transpose.ROTATE_180)
        if footer_rotation == 270:
            image = image.transpose(Image.Transpose.ROTATE_270)
        self.text_layers.append(Layer(image, (footer_x, footer_y)))

    def _create_mana_cost_layer(self):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.
        """

        text = self.get_metadata(CARD_MANA_COST)
        if len(text) == 0:
            return

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

            offset: tuple[float, float]
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

        image = Image.new("RGBA", (self.TITLE_BOX_WIDTH, self.TITLE_BOX_HEIGHT), (0, 0, 0, 0))

        curr_x = self.TITLE_BOX_WIDTH - self.MANA_COST_SYMBOL_SPACING
        for sym in reversed(text.split(" ")):
            symbol = SYMBOL_PLACEHOLDER_KEY.get(sym.strip().lower(), None)
            if symbol is None:
                log(f"Unknown placeholder '{{{sym}}}'")
                continue

            scale = self.MANA_COST_SYMBOL_SIZE / symbol.image.height
            width = int(symbol.image.width * scale)
            height = int(symbol.image.height * scale)
            symbol_image = add_drop_shadow(
                symbol.get_formatted_image(width, height), self.MANA_COST_SYMBOL_SHADOW_OFFSET
            )

            curr_x -= symbol_image.width + self.MANA_COST_SYMBOL_SPACING
            if curr_x >= symbol_image.width:
                image.alpha_composite(symbol_image, (int(curr_x), (self.TITLE_BOX_HEIGHT - symbol_image.height) // 2))
            else:
                log("The mana cost is too long and has been cut off.")
                break

        self.mana_cost_x = self.TITLE_BOX_X + curr_x - self.MANA_COST_SYMBOL_SPACING
        self.text_layers.append(Layer(image, (self.TITLE_BOX_X, self.TITLE_BOX_Y)))

    def _create_title_layer(self):
        """
        Process title text into the title and append it to `self.text_layers`.
        """

        text = replace_ticks(self.get_metadata(CARD_TITLE))
        if len(text) == 0:
            return
        
        centered = False
        if "{center}" in text:
            centered = True
            text = text.replace("{center}", "")

        font_size = self.TITLE_MAX_FONT_SIZE
        title_font = ImageFont.truetype(self.TITLE_FONT, font_size)
        title_length = title_font.getlength(text)
        while (
            self.TITLE_X + title_length > min(self.mana_cost_x, self.TITLE_X + self.TITLE_WIDTH)
            and font_size >= self.TITLE_MIN_FONT_SIZE
        ):
            font_size -= 1
            title_font = ImageFont.truetype(BELEREN_BOLD, font_size)
            title_length = title_font.getlength(text)

        image = Image.new("RGBA", (self.TITLE_WIDTH, self.TITLE_BOX_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        text_align = self.TITLE_TEXT_ALIGN if not centered else "center"
        if text_align == "left":
            x_pos = 0
        elif text_align == "center":
            x_pos = (self.TITLE_WIDTH - title_length) // 2

        ascent = title_font.getmetrics()[0]
        draw.text(
            (x_pos, (self.TITLE_BOX_HEIGHT - ascent) // 2),
            text,
            font=title_font,
            fill=self.TITLE_FONT_COLOR,
            anchor="lt",
            align=text_align,
        )

        self.text_layers.append(Layer(image, (self.TITLE_X, self.TITLE_Y)))

    def _create_type_layer(self):
        """
        Process type text into the type box and append it to `self.text_layers`.
        """

        first_part = f"{self.get_metadata(CARD_SUPERTYPES)} {self.get_metadata(CARD_TYPES)}"
        second_part = self.get_metadata(CARD_SUBTYPES)
        if len(second_part) > 0:
            text = " — ".join((first_part, second_part)).strip()
        else:
            text = first_part.strip()
        text = replace_ticks(text)
        if len(text) == 0:
            return

        header_x = self.TYPE_X
        header_y = self.TYPE_Y
        header_width = self.TYPE_WIDTH
        header_height = self.TYPE_BOX_HEIGHT

        font_size = self.TYPE_MAX_FONT_SIZE
        type_font = ImageFont.truetype(BELEREN_BOLD, font_size)
        while header_x + type_font.getlength(text) > self.SET_SYMBOL_X and font_size >= self.TYPE_MIN_FONT_SIZE:
            font_size -= 1
            type_font = ImageFont.truetype(BELEREN_BOLD, font_size)

        image = Image.new("RGBA", (header_width, header_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        ascent = type_font.getmetrics()[0]
        draw.text(
            (0, (header_height - ascent) // 2),
            text,
            font=type_font,
            fill=self.TYPE_FONT_COLOR,
            anchor="lt",
        )

        self.text_layers.append(Layer(image, (header_x, header_y)))

    def _replace_text_placeholders(self, text: str) -> str:
        """
        Replace standard placeholders in the format `{PLACEHOLDER}` with what they represent.
        """

        new_text = text
        new_text = re.sub("{cardname}", self.get_metadata(CARD_TITLE).split("{N}")[0], new_text, flags=re.IGNORECASE)
        new_text = re.sub("{-}", "—", new_text)
        return new_text

    def _get_symbol_metrics(
        self, token: str, font: ImageFont.FreeTypeFont, font_size: int
    ) -> tuple[int, int, Image.Image | None]:
        """
        Return (width, height, Image | None) scaled to current font size.
        """

        symbol = SYMBOL_PLACEHOLDER_KEY.get(token.lower(), None)

        if symbol is None:
            placeholder = f"[{token}]"
            return int(font.getlength(placeholder)), font_size, None

        scale = self.RULES_TEXT_MANA_SYMBOL_SCALE * font_size / symbol.image.height
        width = int(symbol.image.width * scale)
        height = int(symbol.image.height * scale)
        symbol = symbol.get_formatted_image(width, height)
        return width, height, symbol

    def _get_rules_text_layout(self, text: str) -> tuple[
        list[list[list[tuple[str, str | int, ImageFont.FreeTypeFont]]]],
        int,
        int,
        int,
        int,
    ]:
        """
        Get all the rules text properly laid out into words, lines, and symbols.
        Helper function for `_create_rules_text_layer`.

        Returns
        -------
        tuple[
            list[list[list[tuple[str, str, ImageFont.FreeTypeFont]]]],
            int,
            int,
            int,
            int,
        ]
            The lines of rules/flavor text, the font size, the margin size,
            the height of the content, and the maximum usable height of the rules box
        """

        sections = re.split(r"(\{flavor\}|\{divider\})", text)
        rules_text_blocks: list[tuple[str, str]] = []
        current_type = "rules"
        for part in sections:
            if part == "{flavor}":
                current_type = "flavor"
                continue
            elif part == "{divider}":
                current_type = "rules"
                continue
            elif part.strip() == "":
                continue
            else:
                rules_text_blocks.append((current_type, part))
                current_type = "rules"  # reset to rules unless flavor continues

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
                    elif token == "\\I" or token == "/I":
                        fragments.append(("format", "italic_off"))
                    elif token == "bullet":
                        fragments.append(("bullet", "•"))
                    else:
                        fragments.append(("symbol", token))
            return fragments

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

            indent = 0

            def go_to_newline():
                nonlocal curr_fragment, curr_width
                if curr_fragment:
                    lines.append(curr_fragment)
                curr_fragment, curr_width = [], indent
                if indent > 0:
                    curr_fragment.append(("indent", indent, curr_font))

            for kind, value in frags:
                if kind == "format":
                    if value == "italic_on":
                        curr_font = italic_font
                    elif value == "italic_off":
                        curr_font = regular_font
                    continue
                elif kind == "symbol":
                    if value.lower() == "lns":
                        indent = 0
                        go_to_newline()
                        continue
                    width, _, _ = self._get_symbol_metrics(value, curr_font, font_size)
                    if curr_fragment and curr_width + width > max_line_width:
                        go_to_newline()
                    curr_fragment.append(("symbol", value, curr_font))
                    curr_width += width + self.RULES_TEXT_MANA_SYMBOL_SPACING
                elif kind == "bullet":
                    bullet_width = int(curr_font.getlength(f"{value} "))
                    curr_fragment.append(("text", f"{value} ", curr_font))
                    curr_width += bullet_width
                    indent = bullet_width
                else:
                    for word in re.findall(r"\S+|\s+", value):
                        word = replace_ticks(word)
                        width = int(curr_font.getlength(word))

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
                                    char_width = int(curr_font.getlength(char))
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

        for font_size in range(self.RULES_BOX_MAX_FONT_SIZE, self.RULES_BOX_MIN_FONT_SIZE - 1, -1):
            rules_font = ImageFont.truetype(self.RULES_TEXT_FONT, font_size)
            italics_font = ImageFont.truetype(self.RULES_TEXT_FONT_ITALICS, font_size)

            line_height = font_size
            margin = int(font_size * 0.25)
            max_line_width = self.RULES_TEXT_WIDTH - 2 * margin

            # Split the text into lines that fit the rules box horizontally
            rules_lines: list[list[list[tuple[str, str, ImageFont.FreeTypeFont]]]] = []
            for text_type, raw_text in rules_text_blocks:
                rules_lines.append([])
                if text_type == "flavor":
                    target_font = italics_font
                else:
                    target_font = rules_font
                for line in raw_text.splitlines():
                    flavor_fragments = parse_fragments(line)
                    rules_lines[-1] += (
                        wrap_text_fragments(flavor_fragments, target_font, italics_font)
                        if flavor_fragments
                        else [[("text", "", target_font)]]
                    )
                    rules_lines[-1].append([("newline", None)])
                rules_lines[-1].pop()  # remove the ending newline

            # If the lines of text are too tall, try the process again with a different font
            content_height = 0
            for idx, lines in enumerate(rules_lines):
                for line in lines:
                    if line[0][0] == "newline":
                        content_height += line_height // self.RULES_TEXT_LINE_HEIGHT_TO_GAP_RATIO
                    else:
                        content_height += line_height
                if idx < len(rules_lines) - 1:
                    content_height += RULES_DIVIDING_LINE.image.height + line_height
            usable_height = self.RULES_TEXT_HEIGHT - 2 * margin
            if content_height > usable_height:
                continue

            # check for power/toughness overlap
            if (
                len(self.get_metadata(CARD_POWER_TOUGHNESS)) > 0
                and self.RULES_TEXT_Y + usable_height >= self.POWER_TOUGHNESS_Y
            ):
                final_line = rules_lines[-1][-1]
                final_line_width = 0
                for kind, value, frag_font in final_line:
                    if kind == "text":
                        if value:
                            final_line_width += frag_font.getlength(value)
                    else:
                        width, _, _ = self._get_symbol_metrics(value, frag_font, font_size)
                        final_line_width += width + self.RULES_TEXT_MANA_SYMBOL_SPACING
                if self.RULES_TEXT_X + final_line_width >= self.POWER_TOUGHNESS_X:
                    continue
            break
        else:
            raise ValueError("Text is too long to fit in box even at minimum font size.")

        return rules_lines, font_size, margin, content_height, usable_height

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`.
        """

        text = self.get_metadata(CARD_RULES_TEXT)
        if len(text) == 0:
            return

        centered = False
        if "{center}" in text:
            centered = True
            text = text.replace("{center}", "")
        text = self._replace_text_placeholders(text)

        rules_lines, font_size, margin, content_height, usable_height = self._get_rules_text_layout(text)

        image = Image.new("RGBA", (self.RULES_TEXT_WIDTH, self.RULES_TEXT_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        line_height = font_size
        curr_y = margin + (usable_height - content_height) // 2

        def draw_lines(lines: list[list[tuple[str, str | int, ImageFont.FreeTypeFont]]]):
            """
            Render lines of text as images.
            """

            nonlocal curr_y
            for line_fragments in lines:
                if line_fragments and line_fragments[0][0] == "newline":
                    curr_y += (
                        line_height // self.RULES_TEXT_LINE_HEIGHT_TO_GAP_RATIO
                    )  # add an extra gap for user-specified newlines
                    continue

                if centered:
                    total_line_length = 0
                    for kind, value, frag_font in line_fragments:
                        if kind == "text":
                            if value:
                                total_line_length += draw.textlength(value, font=frag_font)
                        elif kind == "symbol":
                            width, _, _ = self._get_symbol_metrics(value, frag_font, font_size)
                            total_line_length += width + self.RULES_TEXT_MANA_SYMBOL_SPACING
                    curr_x = (self.RULES_TEXT_WIDTH - total_line_length) // 2
                else:
                    curr_x = margin

                for kind, value, frag_font in line_fragments:
                    if kind == "text":
                        if value:
                            draw.text((curr_x, curr_y), value, font=frag_font, fill=self.RULES_TEXT_FONT_COLOR)
                            curr_x += draw.textlength(value, font=frag_font)
                    elif kind == "symbol":
                        width, _, symbol_image = self._get_symbol_metrics(value, frag_font, font_size)
                        if symbol_image is not None:
                            image.alpha_composite(
                                symbol_image,
                                (
                                    int(curr_x),
                                    int(curr_y + self.RULES_TEXT_MANA_SYMBOL_SPACING),
                                ),
                            )
                        else:
                            placeholder = f"[{value}]"
                            draw.text((curr_x, curr_y), placeholder, font=frag_font, fill="red")
                        curr_x += width + self.RULES_TEXT_MANA_SYMBOL_SPACING
                    elif kind == "indent":
                        curr_x += value
                curr_y += line_height

        dividing_line = RULES_DIVIDING_LINE.get_formatted_image(self.RULES_TEXT_WIDTH, RULES_DIVIDING_LINE.image.height)
        for idx, lines in enumerate(rules_lines):
            if idx > 0:
                curr_y += line_height // 2
                image.alpha_composite(
                    dividing_line,
                    (0, curr_y),
                )
                curr_y += dividing_line.height + line_height // 2
            draw_lines(lines)

        self.text_layers.append(Layer(image, (self.RULES_TEXT_X, self.RULES_TEXT_Y)))

    def _create_power_toughness_layer(self):
        """
        Process power & toughness text into the power & toughness area and append it to `self.text_layers`.
        """

        text = self.get_metadata(CARD_POWER_TOUGHNESS).replace("*", "★")
        if len(text) == 0:
            return

        power_toughness_font = ImageFont.truetype(BELEREN_BOLD_SMALL_CAPS, self.POWER_TOUGHNESS_FONT_SIZE)
        image = Image.new("RGBA", (self.POWER_TOUGHNESS_WIDTH, self.POWER_TOUGHNESS_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        text_width = int(power_toughness_font.getlength(text))
        bounding_box = power_toughness_font.getbbox(text)
        text_height = int(bounding_box[3] - bounding_box[1])

        draw.text(
            ((self.POWER_TOUGHNESS_WIDTH - text_width) // 2, (self.POWER_TOUGHNESS_HEIGHT - text_height) // 2),
            text,
            font=power_toughness_font,
            fill=self.POWER_TOUGHNESS_FONT_COLOR,
            anchor="lt",
        )

        self.text_layers.append(Layer(image, (self.POWER_TOUGHNESS_X, self.POWER_TOUGHNESS_Y)))

    def _create_overlay_layers(self):
        """
        Create images from the filepaths in the overlays from `self.metadata` and append them to `self.overlay_layers`.
        """

        card_overlays = self.get_metadata(CARD_OVERLAYS)
        if len(card_overlays) == 0:
            return

        for image_path in card_overlays.split("\n"):
            image_path = image_path.lower().strip()
            if len(image_path) == 0:
                continue
            overlay = open_image(f"{OVERLAYS_PATH}/{image_path}.png")
            if overlay is None:
                log(f"Could not find overlay '{image_path}'.")
                continue
            self.overlay_layers.append(Layer(overlay))
