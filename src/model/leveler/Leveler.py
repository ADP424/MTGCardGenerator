from PIL import Image, ImageDraw

from constants import (
    BELEREN_BOLD,
    BELEREN_BOLD_SMALL_CAPS,
    CARD_MANA_COST,
    CARD_POWER_TOUGHNESS,
    CARD_RULES_TEXT,
)
from model.Layer import Layer
from model.regular.RegularCardSmall import RegularCardSmall
from utils import load_font


class Leveler(RegularCardSmall):
    """
    A layered image representing a leveler creature and all the collection info on it,
    with all relevant card metadata, at the legacy 1500x2100 resolution.

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

        # Rules Text Box heights (x, y, and width stay the same as the regular small card)
        self.FIRST_RULES_BOX_HEIGHT = 198
        self.SECOND_RULES_BOX_HEIGHT = 204
        self.THIRD_RULES_BOX_HEIGHT = 221

        # Rules text in the second and third sections is pushed right to clear the level arrows,
        # and any section stops short on the left to clear its power/toughness plate (if not empty)
        self.RULES_TEXT_LEVEL_ARROW_INDENT = 185
        self.RULES_TEXT_POWER_TOUGHNESS_INSET = 224

        # Power & Toughness Plates
        self.FIRST_POWER_TOUGHNESS_Y = 1355
        self.SECOND_POWER_TOUGHNESS_Y = 1553
        self.THIRD_POWER_TOUGHNESS_Y = 1761

        # Level Arrow Text
        self.LEVEL_LABEL_X = 108
        self.LEVEL_LABEL_WIDTH = 124
        self.SECOND_LEVEL_LABEL_Y = 1558
        self.THIRD_LEVEL_LABEL_Y = 1773
        self.LEVEL_LABEL_HEIGHT = 107
        self.LEVEL_LABEL_FONT = BELEREN_BOLD_SMALL_CAPS
        self.LEVEL_LABEL_FONT_SIZE = 30
        self.LEVEL_LABEL_TOP_Y = 13
        self.LEVEL_RANGE_FONT = BELEREN_BOLD
        self.LEVEL_RANGE_FONT_SIZE = 64
        self.LEVEL_RANGE_TOP_Y = 52
        self.LEVEL_LABEL_FONT_COLOR = (0, 0, 0)

        # Determine each section's rules text, and whether it has a corresponding power/toughness entry
        full_rules_text = self.get_metadata(CARD_RULES_TEXT)
        rules_texts = [text.strip() for text in full_rules_text.split("{end}")]
        self.first_rules_text = rules_texts[0] if len(rules_texts) > 0 else ""
        self.second_rules_text = rules_texts[1] if len(rules_texts) > 1 else ""
        self.third_rules_text = rules_texts[2] if len(rules_texts) > 2 else ""

        full_power_toughness = self.get_metadata(CARD_POWER_TOUGHNESS)
        power_toughnesses = [text.strip() for text in full_power_toughness.split("\n")]
        self.first_power_toughness = power_toughnesses[0] if len(power_toughnesses) > 0 else ""
        self.second_power_toughness = power_toughnesses[1] if len(power_toughnesses) > 1 else ""
        self.third_power_toughness = power_toughnesses[2] if len(power_toughnesses) > 2 else ""

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
        create_level_label_layers: bool = True,
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

        create_watermark_layer: bool, default: True
            Whether to put the watermark on the card or not.

        create_rarity_symbol_layer: bool, default: True
            Whether to put the rarity/set symbol on the card or not.

        create_footer_layer: bool, default: True
            Whether to put the footer collector info on the bottom of the card or not.

        create_mana_cost_layer: bool, default: True
            Whether to put the mana cost of the card on it or not.

        create_title_layer: bool, default: True
            Whether to put the title of the card on it or not.

        create_type_layer: bool, default: True
            Whether to put the type line of the card on it or not.

        create_rules_text_layer: bool, default: True
            Whether to put the rules text of the card on it or not.

        create_power_toughness_layer: bool, default: True
            Whether to put the power & toughness of the card on it or not.

        create_level_label_layers: bool, default: True
            Whether to put the level range labels next to the second and third rules text boxes or not.

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

        if create_level_label_layers:
            self._create_level_label_layers()

    def _create_mana_cost_layer(self):
        """
        Process MTG mana cost into the mana cost header, exchanging mana placeholders for symbols,
        and append it to `self.text_layers`.
        """

        full_mana_cost = self.get_metadata(CARD_MANA_COST)

        self.set_metadata(CARD_MANA_COST, full_mana_cost.split("\n")[0].strip())
        super()._create_mana_cost_layer()

        self.set_metadata(CARD_MANA_COST, full_mana_cost)

    def _create_rules_text_layer(self):
        """
        Process MTG rules text in the rules text box, exchanging placeholders for symbols and text formatting,
        and append it to `self.text_layers`. Do this once for each of the leveler's three rules text sections.
        """

        full_rules_box_y = self.RULES_BOX_Y
        full_rules_box_height = self.RULES_BOX_HEIGHT
        full_rules_text_x = self.RULES_TEXT_X
        full_rules_text_y = self.RULES_TEXT_Y
        full_rules_text_width = self.RULES_TEXT_WIDTH
        full_rules_text_height = self.RULES_TEXT_HEIGHT
        full_rules_text = self.get_metadata(CARD_RULES_TEXT)

        sections = (
            (self.first_rules_text, self.first_power_toughness, self.FIRST_RULES_BOX_HEIGHT, 0),
            (
                self.second_rules_text,
                self.second_power_toughness,
                self.SECOND_RULES_BOX_HEIGHT,
                self.RULES_TEXT_LEVEL_ARROW_INDENT,
            ),
            (
                self.third_rules_text,
                self.third_power_toughness,
                self.THIRD_RULES_BOX_HEIGHT,
                self.RULES_TEXT_LEVEL_ARROW_INDENT,
            ),
        )

        curr_y = full_rules_box_y
        for section_text, section_power_toughness, box_height, indent in sections:
            inset = self.RULES_TEXT_POWER_TOUGHNESS_INSET if len(section_power_toughness) > 0 else 0

            self.RULES_BOX_Y = curr_y
            self.RULES_BOX_HEIGHT = box_height
            self.RULES_TEXT_X = full_rules_text_x + indent
            self.RULES_TEXT_Y = curr_y
            self.RULES_TEXT_WIDTH = full_rules_text_width - indent - inset
            self.RULES_TEXT_HEIGHT = box_height
            self.set_metadata(CARD_RULES_TEXT, section_text)
            super()._create_rules_text_layer()

            curr_y += box_height

        self.RULES_BOX_Y = full_rules_box_y
        self.RULES_BOX_HEIGHT = full_rules_box_height
        self.RULES_TEXT_X = full_rules_text_x
        self.RULES_TEXT_Y = full_rules_text_y
        self.RULES_TEXT_WIDTH = full_rules_text_width
        self.RULES_TEXT_HEIGHT = full_rules_text_height
        self.set_metadata(CARD_RULES_TEXT, full_rules_text)

    def _create_power_toughness_layer(self):
        """
        Process power & toughness text into each of the three power & toughness plates
        and append them to `self.text_layers`.
        """

        full_power_toughness_y = self.POWER_TOUGHNESS_Y
        full_power_toughness = self.get_metadata(CARD_POWER_TOUGHNESS)

        power_toughnesses = (
            (self.first_power_toughness, self.FIRST_POWER_TOUGHNESS_Y),
            (self.second_power_toughness, self.SECOND_POWER_TOUGHNESS_Y),
            (self.third_power_toughness, self.THIRD_POWER_TOUGHNESS_Y),
        )

        for power_toughness_text, power_toughness_y in power_toughnesses:
            self.POWER_TOUGHNESS_Y = power_toughness_y
            self.set_metadata(CARD_POWER_TOUGHNESS, power_toughness_text)
            super()._create_power_toughness_layer()

        self.POWER_TOUGHNESS_Y = full_power_toughness_y
        self.set_metadata(CARD_POWER_TOUGHNESS, full_power_toughness)

    def _create_level_label_layers(self):
        """
        Process the level ranges from the mana cost column into the level arrow labels
        beside the second and third rules text boxes.
        """

        full_mana_cost = self.get_metadata(CARD_MANA_COST)
        mana_cost_parts = full_mana_cost.split("\n")
        level_entries = [part.strip() for part in mana_cost_parts[1:3]]

        label_font = load_font(self.LEVEL_LABEL_FONT, self.LEVEL_LABEL_FONT_SIZE)
        range_font = load_font(self.LEVEL_RANGE_FONT, self.LEVEL_RANGE_FONT_SIZE)
        label_fallback_fonts = self._load_fallback_fonts(self.LEVEL_LABEL_FONT, self.LEVEL_LABEL_FONT_SIZE)
        range_fallback_fonts = self._load_fallback_fonts(self.LEVEL_RANGE_FONT, self.LEVEL_RANGE_FONT_SIZE)

        for entry, box_y in zip(level_entries, (self.SECOND_LEVEL_LABEL_Y, self.THIRD_LEVEL_LABEL_Y)):
            if len(entry) == 0:
                continue

            lines = entry.split("\n")
            label_text = lines[0].strip() if len(lines) > 1 else "LEVEL"
            range_text = lines[1].strip() if len(lines) > 1 else lines[0].strip()

            image = Image.new("RGBA", (self.LEVEL_LABEL_WIDTH, self.LEVEL_LABEL_HEIGHT), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            label_length = self._get_ucs_chunks_length(label_text, label_font, label_fallback_fonts)
            label_top = label_font.getbbox(label_text)[1]
            self._draw_ucs_chunks(
                draw,
                ((self.LEVEL_LABEL_WIDTH - label_length) // 2, self.LEVEL_LABEL_TOP_Y - label_top),
                label_text,
                label_font,
                label_fallback_fonts,
                primary_font_path=self.LEVEL_LABEL_FONT,
                font_size=self.LEVEL_LABEL_FONT_SIZE,
                fill=self.LEVEL_LABEL_FONT_COLOR,
            )

            range_length = self._get_ucs_chunks_length(range_text, range_font, range_fallback_fonts)
            range_top = range_font.getbbox(range_text)[1]
            self._draw_ucs_chunks(
                draw,
                ((self.LEVEL_LABEL_WIDTH - range_length) // 2, self.LEVEL_RANGE_TOP_Y - range_top),
                range_text,
                range_font,
                range_fallback_fonts,
                primary_font_path=self.LEVEL_RANGE_FONT,
                font_size=self.LEVEL_RANGE_FONT_SIZE,
                fill=self.LEVEL_LABEL_FONT_COLOR,
            )

            self.text_layers.append(Layer(image, (self.LEVEL_LABEL_X, box_y)))
