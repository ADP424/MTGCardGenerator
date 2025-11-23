from PIL import Image, ImageDraw, ImageFont

from constants import (
    CARD_ADDITIONAL_TITLES,
    CARD_TRANSFORM_HINT,
    COLOR_TAG_PATTERN,
    COLOR_TAG_PATTERN_NO_BRACES,
    PLACEHOLDER_REGEX,
)
from log import log
from model.regular.RegularCard import RegularCard
from model.Layer import Layer
from utils import replace_ticks


class ModalFrontside(RegularCard):
    """
    A layered image representing the frontside of a modal DFC card and all the collection info on it,
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
    ):
        super().__init__(metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers)

        # Title Box
        self.TITLE_BOX_X = 220
        self.TITLE_BOX_WIDTH = 1183

        # Title Text
        self.TITLE_X = 240
        self.TITLE_WIDTH = 1158

        # Rules Text
        self.RULES_TEXT_HEIGHT = 552

        # Reminder Text/Box
        self.REMINDER_X = 102
        self.REMINDER_Y = 1866
        self.REMINDER_TEXT_MANA_BOTTOM_Y = 1931
        self.REMINDER_TEXT_BOTTOM_Y = 1942
        self.REMINDER_WIDTH = 548
        self.REMINDER_HEIGHT = 88
        self.REMINDER_MANA_FONT_SIZE = 55
        self.REMINDER_TYPE_MAX_FONT_SIZE = 50
        self.REMINDER_MANA_MIN_FONT_SIZE = 6
        self.REMINDER_TYPE_HINT_FONT_COLOR = (255, 255, 255)
        self.REMINDER_MANA_HINT_FONT_COLOR = (255, 255, 255)
        self.REMINDER_TYPE_MANA_GAP = 25

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
        create_reminder_mana_layer: bool = True,
        create_reminder_type_layer: bool = True,
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

        create_reminder_mana_layer: bool, default: True
            Whether to put the mana part of the reminder text at the bottom of the modal or not.

        create_reminder_type_layer: bool, default: True
            Whether to put the type part of the reminder text at the bottom of the modal or not.

        create_overlay_layers: bool, default: True
            Whether to put the overlays on top of the card after everything else or not.
        """

        super().create_layers(
            create_art_layer,
            create_frame_layers,
            create_watermark_layer,
            create_rarity_symbol_layer,
            create_footer_layer,
            create_mana_cost_layer,
            create_title_layer,
            create_type_layer,
            create_rules_text_layer,
            create_power_toughness_layer,
            create_overlay_layers,
        )

        if create_reminder_type_layer:
            self._create_reminder_type_layer()

        if create_reminder_mana_layer:
            self._create_reminder_mana_layer()

    def _create_reminder_type_layer(self):
        """
        Process reminder type text for modal cards and append it to `self.text_layers`.
        """

        type_hint = replace_ticks(self.get_metadata(CARD_ADDITIONAL_TITLES))
        if "{skip}" in type_hint:
            type_hint = ""

        centered = False
        if "{center}" in type_hint:
            centered = True
            type_hint = type_hint.replace("{center}", "")

        segments = []
        last_end = 0
        for match in COLOR_TAG_PATTERN.finditer(type_hint):
            r, g, b = map(int, match.groups()[:3])
            color = (r, g, b)
            segment_text = match.group(4)

            if match.start() > last_end:
                segments.append((type_hint[last_end : match.start()], self.REMINDER_TYPE_HINT_FONT_COLOR))

            segments.append((segment_text, color))
            last_end = match.end()

        if last_end < len(type_hint):
            segments.append((type_hint[last_end:], self.REMINDER_TYPE_HINT_FONT_COLOR))

        reminder_type_font = ImageFont.truetype(self.TITLE_FONT, self.REMINDER_TYPE_MAX_FONT_SIZE)
        symbol_backup_font = ImageFont.truetype(self.SYMBOL_FONT, self.REMINDER_TYPE_MAX_FONT_SIZE)
        emoji_backup_font = ImageFont.truetype(self.EMOJI_FONT, self.REMINDER_TYPE_MAX_FONT_SIZE)

        image = Image.new("RGBA", (self.REMINDER_WIDTH, self.REMINDER_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        x_pos = 0
        ascent = reminder_type_font.getmetrics()[0]
        y_pos = (self.REMINDER_TEXT_BOTTOM_Y - self.REMINDER_Y - ascent) // 2
        for seg_text, color in segments:
            self._draw_ucs_chunks(
                draw,
                (x_pos, y_pos),
                seg_text,
                reminder_type_font,
                symbol_backup_font,
                emoji_backup_font,
                fill=color,
                align="left" if not centered else "center",
            )
            x_pos += self._get_ucs_chunks_length(seg_text, reminder_type_font, symbol_backup_font, emoji_backup_font)

        self.reminder_type_x = x_pos + self.REMINDER_TYPE_MANA_GAP
        self.text_layers.append(Layer(image, (self.REMINDER_X, self.REMINDER_Y)))

    def _create_reminder_mana_layer(self):
        """
        Process reminder mana text for modal cards and append it to `self.text_layers`.
        """

        type_hint = self.get_metadata(CARD_ADDITIONAL_TITLES)
        mana_hint = self.get_metadata(CARD_TRANSFORM_HINT)
        if "{skip}" in type_hint:
            type_hint = ""
        if "{skip}" in mana_hint:
            mana_hint = ""

        fragments: list[tuple[str, str]] = []
        parts: list[str] = PLACEHOLDER_REGEX.split(mana_hint)
        for i, part in enumerate(parts):
            if i % 2 == 0:
                fragments.append(("text", part))
            else:
                token = part.strip().lower()
                if token == "i":
                    fragments.append(("format", "italic_on"))
                elif token in ("\\i", "/i"):
                    fragments.append(("format", "italic_off"))
                elif token == "ucs":
                    fragments.append(("format", "ucs_on"))
                elif token in ("\\ucs", "/ucs"):
                    fragments.append(("format", "ucs_off"))
                elif token == "emoji":
                    fragments.append(("format", "emoji_on"))
                elif token in ("\\emoji", "/emoji"):
                    fragments.append(("format", "emoji_off"))
                elif token[:5] == "color":
                    color_match = COLOR_TAG_PATTERN_NO_BRACES.findall(token)
                    if len(color_match) == 0:
                        continue
                    r, g, b = map(int, color_match[0][:3])
                    fragments.append(("color", (r, g, b)))
                elif token in ("\\color", "/color"):
                    fragments.append(("color", "end"))
                elif token == "space":
                    fragments.append(("spacing", "start"))
                elif token in ("\\space", "/space"):
                    fragments.append(("spacing", "end"))
                else:
                    fragments.append(("symbol", token))

        font_size = self.REMINDER_MANA_FONT_SIZE
        while font_size > self.REMINDER_MANA_MIN_FONT_SIZE:
            image = Image.new("RGBA", (self.REMINDER_WIDTH, self.REMINDER_HEIGHT), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            rules_font = ImageFont.truetype(self.RULES_TEXT_FONT, font_size)
            italics_font = ImageFont.truetype(self.RULES_TEXT_FONT_ITALICS, font_size)
            symbol_font = ImageFont.truetype(self.SYMBOL_FONT, font_size)
            emoji_font = ImageFont.truetype(self.EMOJI_FONT, font_size)

            curr_font_color = self.REMINDER_MANA_HINT_FONT_COLOR

            curr_x = 0
            for kind, value in fragments:
                curr_main_font = rules_font  # regular vs italics
                curr_font = rules_font  # regular vs italics vs symbol vs emoji

                if kind == "text":
                    bounding_box = curr_font.getbbox(value)
                    text_height = int(bounding_box[3] - bounding_box[1])
                    ascent = curr_font.getmetrics()[0]
                    if value:
                        draw.text(
                            (curr_x, self.REMINDER_TEXT_MANA_BOTTOM_Y - self.REMINDER_Y - min(text_height, ascent)),
                            value,
                            font=curr_font,
                            anchor="lt",
                            fill=curr_font_color,
                        )
                        curr_x += self._get_rules_text_fragment_length(value, curr_font)
                elif kind == "format":
                    if value == "italic_on":
                        curr_main_font = italics_font
                        curr_font = italics_font
                    elif value == "italic_off":
                        curr_main_font = rules_font
                        curr_font = rules_font
                    elif value == "ucs_on":
                        curr_font = symbol_font
                    elif value == "ucs_off":
                        curr_font = curr_main_font
                    elif value == "emoji_on":
                        curr_font = emoji_font
                    elif value == "emoji_off":
                        curr_font = curr_main_font
                    continue
                elif kind == "symbol":
                    width, height, symbol_image = self._get_symbol_metrics(value, curr_font, font_size)
                    if symbol_image is not None:
                        image.alpha_composite(
                            symbol_image,
                            (
                                int(curr_x),
                                (self.REMINDER_HEIGHT - height) // 2,
                            ),
                        )
                        curr_x += width + self.RULES_TEXT_MANA_SYMBOL_SPACING
                    else:
                        log(f"Unknown placeholder in reminder layer: '{value}'")
                elif kind == "color":
                    if value == "end":
                        curr_font_color = self.REMINDER_MANA_HINT_FONT_COLOR
                    else:
                        curr_font_color = value
                elif kind == "spacing":
                    if value:
                        curr_x += draw.textlength(value, curr_font)

            if curr_x < self.REMINDER_WIDTH - self.reminder_type_x:
                break
            font_size -= 1

        self.text_layers.append(Layer(image, (self.REMINDER_X + self.REMINDER_WIDTH - curr_x, self.REMINDER_Y)))
