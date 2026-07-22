import re

from PIL import Image

from constants import CARD_FRAME_LAYOUT_EXTRAS, CARD_RULES_TEXT
from log import log
from model.dungeon.ExpandedDungeon import ExpandedDungeon
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from utils import alpha_composite_clipped

# {dungeon=Primary Card Key} and {cell=row,column} (1-based), stripped before Dungeon parses the rest
GLOBAL_DIRECTIVE_REGEX = re.compile(r"\{\s*(dungeon|cell)\s*[=:]\s*([^{}]*?)\s*\}", re.IGNORECASE)

# The "2x3" (rows x columns of cards) token in the primary's Frame Layout
CARD_GRID_SIZE_REGEX = re.compile(r"(\d+)\s*[x×]\s*(\d+)", re.IGNORECASE)

# The value of a {cell=row,column} directive
CELL_REGEX = re.compile(r"^\s*(\d+)\s*[,x]\s*(\d+)\s*$", re.IGNORECASE)


class ExpandedDungeonGlobal(ExpandedDungeon):
    """
    A dungeon spanning an R x C grid of cards, laid out as one single giant dungeon up front and
    only split into card faces at render time. One card row holds the dungeon's primary content,
    then the subsequent ones change styling details about the individual cards.
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
        metadata = dict(metadata) if metadata else {}
        self._own_card_key = self._card_key_of(metadata)

        self.card_grid_rows = 1
        self.card_grid_columns = 1
        self.has_title: bool | None = None  # only titles on title frames by default
        dims_given = False
        part_token = False
        for extra in metadata.get(CARD_FRAME_LAYOUT_EXTRAS, []):
            for word in str(extra).split():
                match = CARD_GRID_SIZE_REGEX.fullmatch(word)
                if match:
                    self.card_grid_rows = max(int(match.group(1)), 1)
                    self.card_grid_columns = max(int(match.group(2)), 1)
                    dims_given = True
                elif word.lower() == "part":
                    part_token = True
                elif word.lower() == "title":
                    self.has_title = True
                elif word.lower() in ("titleless", "no-title", "notitle", "untitled"):
                    self.has_title = False

        text = metadata.get(CARD_RULES_TEXT, "") or ""
        directives: dict[str, str] = {}

        def capture(match: re.Match) -> str:
            directives[match.group(1).lower()] = (match.group(2) or "").strip()
            return ""

        stripped = GLOBAL_DIRECTIVE_REGEX.sub(capture, text)

        self._primary_key = directives.get("dungeon", "").strip()
        self.is_primary = not self._primary_key and not part_token

        self.cell = (0, 0)
        if "cell" in directives:
            match = CELL_REGEX.match(directives["cell"])
            if match:
                self.cell = (int(match.group(1)) - 1, int(match.group(2)) - 1)
            else:
                log(
                    f"Can't parse '{directives['cell']}' as a global dungeon cell "
                    "(expected '{cell=row,column}', 1-based)."
                )

        if self.is_primary:
            if not dims_given:
                log(
                    f"'{self._own_card_key}' is a global dungeon with no recognized card-grid size in "
                    "its Frame Layout (e.g. 'Global Dungeon 2x3'). Assuming 1x1..."
                )
            row, column = self.cell
            if not (0 <= row < self.card_grid_rows and 0 <= column < self.card_grid_columns):
                log(
                    f"'{self._own_card_key}' claims cell {row + 1},{column + 1} of its own "
                    f"{self.card_grid_rows}x{self.card_grid_columns} card grid, which is out of range. "
                    "Using the top left cell..."
                )
                self.cell = (0, 0)
            metadata[CARD_RULES_TEXT] = stripped
        else:
            if not self._primary_key:
                log(
                    f"'{self._own_card_key}' is a global dungeon part with no {{dungeon=...}} directive "
                    "naming its primary card."
                )
            if stripped.strip():
                log(
                    f"'{self._own_card_key}' is a global dungeon part, but it has its own rules text. "
                    "A global dungeon's whole text belongs on its primary card. Ignoring it..."
                )
            metadata[CARD_RULES_TEXT] = "{skip}"  # Dungeon skips all room parsing/layout

        self.primary: "ExpandedDungeonGlobal | None" = self if self.is_primary else None
        self.parts: dict[tuple[int, int], "ExpandedDungeonGlobal"] = {}
        self._claimed_cells: set[tuple[int, int]] = {self.cell} if self.is_primary else set()
        self._cells_rendered: set[tuple[int, int]] = set()
        self._global_frame_content: Image.Image | None = None
        self._global_text_content: Image.Image | None = None

        super().__init__(metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers)

        # One watermark per physical card
        self._init_cell_rules_box()

        if not self.is_primary and self.wall_texture_frames:
            log(
                f"'{self._own_card_key}' is a global dungeon part, but its frames column lists wall "
                "textures. The primary card's textures cover the whole dungeon. Ignoring them..."
            )

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
        create_wall_layers: bool = True,
        create_arrow_layers: bool = True,
        create_room_name_layers: bool = True,
    ):
        """
        Same as `ExpandedDungeon.create_layers`, except it doesn't render the rules
        text, walls, arrows, or room names. Those come from the global render.
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
            False,  # room rules text comes from the global render
            create_power_toughness_layer,
            create_overlay_layers,
            False,  # walls come from the global render
            False,  # arrows come from the global render
            False,  # room names come from the global render
        )

        if self.primary is None:
            log(
                f"'{self._own_card_key}' was never linked to a global dungeon primary. "
                "Rendering its card chrome only..."
            )
            return
        if not (create_wall_layers or create_arrow_layers or create_rules_text_layer or create_room_name_layers):
            return

        frame_crop, text_crop = self.primary._take_global_crops(self)
        if create_wall_layers or create_arrow_layers:
            self.frame_layers.append(Layer(frame_crop))
        if create_rules_text_layer or create_room_name_layers:
            self.text_layers.append(Layer(text_crop))

    def _init_grid_constants(self):
        """
        Set the constants to lay the expanded tile grid out over the whole global canvas.
        """

        self.SUPER_WIDTH = self.card_grid_columns * self.CARD_FACE_WIDTH
        self.SUPER_HEIGHT = self.card_grid_rows * self.CARD_FACE_HEIGHT
        super()._init_grid_constants()

    def _floor_bounds(self) -> tuple[int, int, int, int]:
        return (
            self.FLOOR_INSET_X,
            self.FLOOR_INSET_Y,
            self.SUPER_WIDTH - self.FLOOR_INSET_X,
            self.SUPER_HEIGHT - self.FLOOR_INSET_Y,
        )

    def _cell_bands(self, cell: tuple[int, int]) -> tuple[str, str]:
        """
        The `(row_band, column_position)` of one card cell of this dungeon's card grid.
        """

        row, column = cell
        return (
            self._band_name(row, self.card_grid_rows, "top", "bottom"),
            self._band_name(column, self.card_grid_columns, "left", "right"),
        )

    def _init_cell_rules_box(self):
        """
        Point `RULES_BOX_*` at this card's own cell. Re-run by `_adopt_primary` once a
        part learns the real card-grid dimensions.
        """

        self._init_rules_box(*self._cell_bands(self.cell))

    def _is_top_row(self) -> bool:
        return self.primary is not None and self.cell[0] == 0

    def _is_bottom_row(self) -> bool:
        return self.primary is not None and self.cell[0] == self.primary.card_grid_rows - 1

    def _is_titled(self) -> bool:
        return self.has_title if self.has_title is not None else self._is_top_row()

    def _qualified_door_target(self, card_key: str, room_id: str, direction: str | None) -> str:
        """
        A deprecated `ExpandedDungeonLocal`-style qualified target is stripped down to its room id
        and resolved globally, with a warning to the user.
        """

        log(
            f"'{self._own_card_key}' uses the card-qualified doorway target '{card_key}: {room_id}'. A "
            f"global dungeon is one dungeon, so the room id alone is enough. Resolving '{room_id}' globally..."
        )
        return room_id

    def link_siblings(self, sibling_cards: dict[str, "RegularCard"]):
        """
        Pull every part in the set that names this card, adopt each into its cell, and
        validate coverage once.

        Parameters
        ----------
        sibling_cards : dict[str, RegularCard]
            Every card in this card's set, keyed by `get_card_key()`.
        """

        if not self.is_primary:
            if not self._primary_key:
                return
            primary = self._siblings_by_lower_key(sibling_cards).get(self._primary_key.lower())
            if primary is None:
                log(
                    f"'{self._own_card_key}' is part of the global dungeon '{self._primary_key}', "
                    "which isn't a card in this set."
                )
            elif not isinstance(primary, ExpandedDungeonGlobal) or not primary.is_primary:
                log(
                    f"'{self._own_card_key}' is part of '{self._primary_key}', which isn't a global "
                    "dungeon's primary card."
                )
            return

        # Pull every part that names this card
        claimed: dict[tuple[int, int], "ExpandedDungeonGlobal"] = {self.cell: self}
        for card in sibling_cards.values():
            if card is self or not isinstance(card, ExpandedDungeonGlobal) or card.is_primary:
                continue
            if card._primary_key.lower() != self._own_card_key.lower():
                continue
            row, column = card.cell
            label = f"{row + 1},{column + 1}"
            if not (0 <= row < self.card_grid_rows and 0 <= column < self.card_grid_columns):
                log(
                    f"'{card._own_card_key}' claims cell {label} of '{self._own_card_key}', which is "
                    f"outside its {self.card_grid_rows}x{self.card_grid_columns} card grid. Skipping it..."
                )
                continue
            if card.cell in claimed:
                log(
                    f"'{card._own_card_key}' claims cell {label} of '{self._own_card_key}', which "
                    f"'{claimed[card.cell]._own_card_key}' already claims. Skipping it..."
                )
                continue
            claimed[card.cell] = card
            card._adopt_primary(self)

        self.parts = {cell: card for cell, card in claimed.items() if card is not self}
        self._claimed_cells = set(claimed)
        for row in range(self.card_grid_rows):
            for column in range(self.card_grid_columns):
                if (row, column) not in claimed:
                    log(
                        f"No card in this set claims cell {row + 1},{column + 1} of "
                        f"'{self._own_card_key}'. That face of the dungeon won't be rendered."
                    )

    def _adopt_primary(self, primary: "ExpandedDungeonGlobal"):
        """
        Called on a part by its primary's `link_siblings` pass: learn the primary and the real
        card-grid dimensions, then recompute the watermark's rules box with them. A part's own grid
        constants stay at their 1x1 placeholders.
        """

        self.primary = primary
        self.card_grid_rows = primary.card_grid_rows
        self.card_grid_columns = primary.card_grid_columns
        self._init_cell_rules_box()

    def _seam_tile_columns(self) -> list[int]:
        """
        The tile columns where vertical card seams fall.
        """

        return [
            (column * self.CARD_FACE_WIDTH - self.GRID_ORIGIN_X) // self.TILE_SIZE
            for column in range(1, self.card_grid_columns)
        ]

    def _seam_tile_rows(self) -> list[int]:
        """
        The tile rows where horizontal card seams fall.
        """

        return [
            (row * self.CARD_FACE_HEIGHT - self.GRID_ORIGIN_Y) // self.TILE_SIZE
            for row in range(1, self.card_grid_rows)
        ]

    def _adjust_door_opening(
        self, tile_start: int, shared_start: int, shared_end: int, axis: str = "horizontal"
    ) -> int:
        """
        Nudge a doorway's opening off any physical card seam it straddles, so its arrow is never
        split between two physical cards.
        """

        opening = self.DOOR_OPENING_COLUMNS if axis == "horizontal" else self.DOOR_OPENING_ROWS
        seams = self._seam_tile_columns() if axis == "horizontal" else self._seam_tile_rows()
        if not seams:
            return tile_start

        def straddles(candidate: int) -> bool:
            return any(candidate < seam < candidate + opening for seam in seams)

        if not straddles(tile_start):
            return tile_start
        for delta in range(1, max(shared_end - shared_start, 1)):
            for candidate in (tile_start - delta, tile_start + delta):
                if shared_start <= candidate <= shared_end - opening and not straddles(candidate):
                    return candidate
        return tile_start

    def _stamp_outer_wall(self, shape: Image.Image, effect: Image.Image, stamp_wall_piece):
        """
        Stamp every card cell's outer wall border into the global wall build (each via the shared
        `_stamp_outer_wall_face`), so the border shares the wall texture/effect seamlessly with
        the interior walls.
        """

        for row in range(self.card_grid_rows):
            for column in range(self.card_grid_columns):
                self._stamp_outer_wall_face(
                    shape,
                    effect,
                    stamp_wall_piece,
                    *self._cell_bands((row, column)),
                    (column * self.CARD_FACE_WIDTH, row * self.CARD_FACE_HEIGHT),
                )

    def _create_wall_texture_image(self) -> Image.Image | None:
        """
        Build the single-card wall texture the normal way, then tile it across every card face of
        the super-canvas (preserving texture density rather than stretching it).
        """

        saved = (self.CARD_WIDTH, self.CARD_HEIGHT)
        self.CARD_WIDTH, self.CARD_HEIGHT = self.CARD_FACE_WIDTH, self.CARD_FACE_HEIGHT
        try:
            tile = super()._create_wall_texture_image()
        finally:
            self.CARD_WIDTH, self.CARD_HEIGHT = saved
        if tile is None:
            return None
        canvas = Image.new("RGBA", (self.SUPER_WIDTH, self.SUPER_HEIGHT), (0, 0, 0, 0))
        for row in range(self.card_grid_rows):
            for column in range(self.card_grid_columns):
                alpha_composite_clipped(canvas, tile, (column * self.CARD_FACE_WIDTH, row * self.CARD_FACE_HEIGHT))
        return canvas

    def _render_global_content(self) -> tuple[Image.Image, Image.Image]:
        """
        Build (and cache) the two super-canvas composites every card crops from: the frame-level
        content (walls + texture + arrows) and the text-level content (room names + rules text).
        """

        if self._global_frame_content is not None and self._global_text_content is not None:
            return self._global_frame_content, self._global_text_content

        size = (self.SUPER_WIDTH, self.SUPER_HEIGHT)
        frame_scratch: list[Layer] = []
        text_scratch: list[Layer] = []
        saved = (self.CARD_WIDTH, self.CARD_HEIGHT, self.frame_layers, self.text_layers)
        self.CARD_WIDTH, self.CARD_HEIGHT = size
        self.frame_layers, self.text_layers = frame_scratch, text_scratch
        try:
            self._create_wall_layers()
            self._create_arrow_layers()
            self._create_room_name_layers()
            self._create_rules_text_layer()
        finally:
            self.CARD_WIDTH, self.CARD_HEIGHT, self.frame_layers, self.text_layers = saved

        self._global_frame_content = self._composite_layers(frame_scratch, size)
        self._global_text_content = self._composite_layers(text_scratch, size)
        return self._global_frame_content, self._global_text_content

    def _composite_layers(layers: list[Layer], size: tuple[int, int]) -> Image.Image:
        """
        Flatten positioned layers onto one transparent canvas, in order, via `alpha_composite_clipped`
        (rather than `paste_image`) since the canvas may be a large super-canvas and each layer is
        typically small (a single room's text, or one arrow).
        """

        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        for layer in layers:
            image = layer.image
            if image is None:
                continue
            position = layer.position or (0, 0)
            alpha_composite_clipped(canvas, image.convert("RGBA"), position)
        return canvas

    def _cell_pixel_box(self, cell: tuple[int, int]) -> tuple[int, int, int, int]:
        """
        The super-canvas pixel rectangle of one card cell.
        """

        row, column = cell
        return (
            column * self.CARD_FACE_WIDTH,
            row * self.CARD_FACE_HEIGHT,
            (column + 1) * self.CARD_FACE_WIDTH,
            (row + 1) * self.CARD_FACE_HEIGHT,
        )

    def _take_global_crops(self, card: "ExpandedDungeonGlobal") -> tuple[Image.Image, Image.Image]:
        """
        Crop the (lazily built, cached) global content down to `card`'s cell. Once every claimed
        cell has taken its crops, the super-canvases are released.
        """

        frame_content, text_content = self._render_global_content()
        box = self._cell_pixel_box(card.cell)
        crops = (frame_content.crop(box), text_content.crop(box))
        self._cells_rendered.add(card.cell)
        if self._claimed_cells and self._claimed_cells <= self._cells_rendered:
            self._global_frame_content = None
            self._global_text_content = None
        return crops
