from PIL import Image

from constants import CARD_FRAMES, FRAMES_PATH
from log import log
from model.Layer import Layer
from model.regular.RegularCardSmall import RegularCardSmall
from utils import open_image, paste_image


class Poker(RegularCardSmall):
    """
    A layered image representing a poker-card-styled showcase card and all the collection info on it,
    with all relevant card metadata.

    Attributes
    ----------
    metadata : dict[str, str | list], optional
        Information about the card (title, mana cost, rules text, frame, etc.)

    base_width : int, optional
        The width of the root image. Determined by the frame layout in the metadata if not given.

    base_height : int, optional
        The height of the root image. Determined by the frame layout in the metadata if not given.

    art_layer : Layer, optional
        The art to use in the art slot of the frame. Renders after the frame layers, since on
        poker frames the art must sit above the border/side text before the base overlay
        (title/type/rules box outlines) is drawn on top of it. See `render_card`.

    frame_layers : list[Layer], optional
        The layers of card frames (the border and side text). Lower-index layers are rendered
        first. Renders before art on poker frames, unlike the base `RegularCard` ordering.

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

        # Title Box
        self.TITLE_BOX_X = 258
        self.TITLE_BOX_Y = 55
        self.TITLE_BOX_WIDTH = 1173
        self.TITLE_BOX_HEIGHT = 204

        # Mana Cost
        self.MANA_COST_SYMBOL_SIZE = 90

        # Title Text
        self.TITLE_X = self.TITLE_BOX_X + 40
        self.TITLE_BOTTOM_Y = self.TITLE_BOX_Y + 190
        self.TITLE_WIDTH = self.TITLE_BOX_WIDTH - 80
        self.TITLE_MAX_FONT_SIZE = 100

        # Type Box
        self.TYPE_BOX_Y = 1019
        self.TYPE_BOX_HEIGHT = 145

        # Type Text
        self.TYPE_X = 88
        self.TYPE_BOTTOM_Y = self.TYPE_BOX_Y + 125
        self.TYPE_WIDTH = 1220
        self.TYPE_MAX_FONT_SIZE = 80

        # Set / Rarity Symbol
        self.SET_SYMBOL_WIDTH = 100
        self.SET_SYMBOL_X = 1308 - 40 - self.SET_SYMBOL_WIDTH
        self.SET_SYMBOL_Y = self.TYPE_BOX_Y + (self.TYPE_BOX_HEIGHT - self.SET_SYMBOL_WIDTH) // 2

        # Rules Text Box
        self.RULES_BOX_X = 48
        self.RULES_BOX_Y = 1196
        self.RULES_BOX_WIDTH = 1260
        self.RULES_BOX_HEIGHT = 702

        # Rules Text
        self.RULES_TEXT_X = self.RULES_BOX_X + 40
        self.RULES_TEXT_Y = self.RULES_BOX_Y + 30
        self.RULES_TEXT_WIDTH = self.RULES_BOX_WIDTH - 80
        self.RULES_TEXT_HEIGHT = self.RULES_BOX_HEIGHT - 60
        self.RULES_TEXT_MAX_FONT_SIZE = 68

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = 1033
        self.POWER_TOUGHNESS_Y = 1834
        self.POWER_TOUGHNESS_WIDTH = 260
        self.POWER_TOUGHNESS_HEIGHT = 143
        self.POWER_TOUGHNESS_FONT_SIZE = 85

        # Footer
        self.FOOTER_WIDTH = 1200

        # Base Overlay
        # Drawn on top of the art (the art is drawn on top of the bottom frame)
        self.POKER_BASE_PATH = f"{FRAMES_PATH}/the_one_set/showcase/poker/base.png"

        # Power & Toughness box layer(s), pulled out of `frame_layers` in `_create_frame_layers`.
        # Must render above the base overlay but below the power/toughness text. See `render_card`.
        self.power_toughness_frame_layers: list[Layer] = []

    def _create_frame_layers(self):
        """
        Append every frame layer to the card based on `self.metadata`, same as `RegularCard`, except
        any "power_toughness/" frame (before the "{end}" marker, if present) is diverted into
        `self.power_toughness_frame_layers` instead of `self.frame_layers`, so `render_card` can
        draw it above the art/base overlay instead of underneath the art with the rest of the frame.
        """

        card_frames = self.get_metadata(CARD_FRAMES)

        before = True
        for frame_line in card_frames.split("\n"):
            cleaned_line, directives = self._extract_directives(frame_line)
            offset = self._get_directive_offset(directives)
            frame_path = cleaned_line.lower().strip()

            if frame_path == "{end}":
                before = False
                continue
            if not before or "power_toughness/" not in frame_path or len(frame_path) == 0:
                continue

            frame = open_image(f"{FRAMES_PATH}/{frame_path}.png")
            if frame is None:
                log(f"Invalid frame path '{frame_path}'.")
                continue

            self.power_toughness_frame_layers.append(Layer(frame, offset))

        # Remove the power/toughness line(s) so the base implementation doesn't also add them to
        # `self.frame_layers` (which renders underneath the art on poker frames).
        filtered_frames = "\n".join(line for line in card_frames.split("\n") if "power_toughness/" not in line.lower())
        original_frames = self.metadata.get(CARD_FRAMES, "")
        self.metadata[CARD_FRAMES] = filtered_frames
        super()._create_frame_layers()
        self.metadata[CARD_FRAMES] = original_frames

    def render_card(self, close_images: bool = True) -> Image.Image:
        """
        Merge all layers into one image, in poker-specific order: the border frame first, then art,
        then the base overlay (title/type/rules box outlines), then any power/toughness box frame(s),
        and finally collector info, text, and overlay layers as usual.

        Returns
        -------
        Image
            The merged image.

        close_images: bool, default: True
            Whether to close the images used in the card layers or not.
            This means the card cannot be rendered again, but it frees memory.
        """

        composite_image = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))

        for layer in self.frame_layers:
            composite_image = paste_image(layer.image, composite_image, layer.position)
            if close_images and layer.image:
                layer.image.close()
                layer.image = None

        composite_image = paste_image(self.art_layer.image, composite_image, self.art_layer.position)
        if close_images and self.art_layer.image:
            self.art_layer.image.close()
            self.art_layer.image = None

        base_overlay = open_image(self.POKER_BASE_PATH)
        if base_overlay is None:
            log(f"Could not find the poker base overlay at '{self.POKER_BASE_PATH}'.")
        else:
            composite_image = paste_image(base_overlay, composite_image, (0, 0))
            base_overlay.close()

        for layer in self.power_toughness_frame_layers:
            composite_image = paste_image(layer.image, composite_image, layer.position)
            if close_images and layer.image:
                layer.image.close()
                layer.image = None

        for layer in self.collector_layers + self.text_layers + self.overlay_layers:
            composite_image = paste_image(layer.image, composite_image, layer.position)
            if close_images and layer.image:
                layer.image.close()
                layer.image = None

        return composite_image
