from PIL import Image

from constants import CARD_ADDITIONAL_TITLES, CARD_DESCRIPTOR, CARD_TITLE
from model.dungeon.Dungeon import Dungeon
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from utils import get_card_key

OPPOSITE_DIRECTION = {"up": "down", "down": "up", "left": "right", "right": "left"}
EDGE_NAMES = frozenset(OPPOSITE_DIRECTION)


class ExpandedDungeon(Dungeon):
    """
    A shared abstract class for the different implementations of ExpandedDungeon.

    Attributes
    ----------
    metadata : dict[str, str | list], optional
        Information about the card (title, mana cost, rules text, frame, etc.)

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

    CARD_FACE_WIDTH = 1500
    CARD_FACE_HEIGHT = 2100
    FLOOR_INSET_X = 150  # 2 tiles, outermost card columns only
    FLOOR_INSET_Y = 300  # 4 tiles, title (top) and footer (bottom) card rows only
    EXPANDED_TILE_SIZE = 75

    def __init__(
        self,
        metadata: dict[str, str | list["RegularCard"]] = None,
        art_layer: Layer = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
        overlay_layers: list[Layer] = None,
    ):
        self._own_card_key = self._card_key_of(metadata)
        super().__init__(metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers)

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
        Same as `Dungeon.create_layers`, except the collector chrome only goes on the cards that
        have room for it: the footer on the bottom card row, and the title only on a titled card.
        """

        super().create_layers(
            create_art_layer,
            create_frame_layers,
            create_watermark_layer,
            create_rarity_symbol_layer,
            create_footer_layer and self._is_bottom_row(),
            create_mana_cost_layer,
            create_title_layer and self._is_titled(),
            create_type_layer,
            create_rules_text_layer,
            create_power_toughness_layer,
            create_overlay_layers,
            create_wall_layers,
            create_arrow_layers,
            create_room_name_layers,
        )

    def _card_key_of(self, metadata: dict[str, str | list["RegularCard"]] | None) -> str:
        """
        Return the key of a card from its metadata.
        """

        metadata = metadata or {}
        return get_card_key(
            metadata.get(CARD_TITLE, ""),
            metadata.get(CARD_ADDITIONAL_TITLES, ""),
            metadata.get(CARD_DESCRIPTOR, ""),
        )

    def _siblings_by_lower_key(self, sibling_cards: dict[str, "RegularCard"]) -> dict[str, "RegularCard"]:
        """
        Re-key a set's cards by lowercased card key.
        """

        return {key.lower(): card for key, card in sibling_cards.items()}

    def _band_name(self, index: int, count: int, low: str, high: str) -> str:
        """
        Name one axis of a card's position in the card grid, matching the outer-wall asset folders:
        `"closed"` when the dungeon is only one card along this axis, else `low` (e.g. "top"/"left"),
        `high` (e.g. "bottom"/"right"), or `"middle"`.
        """

        if count == 1:
            return "closed"
        if index == 0:
            return low
        if index == count - 1:
            return high
        return "middle"

    def _face_floor_bounds(self, row_band: str, column_position: str) -> tuple[int, int, int, int]:
        """
        Return the usable floor rectangle of one card face, in that face's own local coordinates, as
        `(x0, y0, x1, y1)`.

        Parameters
        ----------
        row_band : str
            The face's row band: `"closed"`, `"top"`, `"middle"`, or `"bottom"`.

        column_position : str
            The face's column position: `"closed"`, `"left"`, `"middle"`, or `"right"`.
        """

        return (
            self.FLOOR_INSET_X if column_position in ("closed", "left") else 0,
            self.FLOOR_INSET_Y if row_band in ("closed", "top") else 0,
            self.CARD_FACE_WIDTH - (self.FLOOR_INSET_X if column_position in ("closed", "right") else 0),
            self.CARD_FACE_HEIGHT - (self.FLOOR_INSET_Y if row_band in ("closed", "bottom") else 0),
        )

    def _init_rules_box(self, row_band: str, column_position: str):
        """
        Point `RULES_BOX_*` at one card face's own playfield cell, in that card's local coordinates,
        so the stock watermark renders once per physical card.
        """

        x0, y0, x1, y1 = self._face_floor_bounds(row_band, column_position)
        self.RULES_BOX_X = x0
        self.RULES_BOX_Y = y0
        self.RULES_BOX_WIDTH = x1 - x0
        self.RULES_BOX_HEIGHT = y1 - y0

    def _is_top_row(self) -> bool:
        """
        Whether this card sits in the dungeon's top card row (and so carries the title band).
        """

        return False

    def _is_bottom_row(self) -> bool:
        """
        Whether this card sits in the dungeon's bottom card row (and so carries the footer band).
        """

        return False

    def _is_titled(self) -> bool:
        """
        Whether this card actually draws a title.
        """

        return bool(self.has_title)

    def _floor_bounds(self) -> tuple[int, int, int, int]:
        """
        Return the rectangle the tile grid covers, as `(left, top, right, bottom)` pixels, in the
        coordinate space this subclass lays its rooms out in.
        """

        raise NotImplementedError

    def _init_grid_constants(self):
        """
        Override `Dungeon`'s tile grid with the expanded 75px grid over this dungeon's floor
        rectangle (see `_floor_bounds`).
        """

        self.TILE_SIZE = self.EXPANDED_TILE_SIZE
        left, top, right, bottom = self._floor_bounds()
        self.GRID_ORIGIN_X = left
        self.GRID_ORIGIN_Y = top
        self.GRID_COLUMNS = (right - left) // self.TILE_SIZE
        self.GRID_ROWS = (bottom - top) // self.TILE_SIZE

    def _init_wall_constants(self):
        """
        Same as `Dungeon._init_wall_constants`, except every asset path points at
        `images/frames/dungeon/expanded/wall`.
        """

        # Walls
        self.WALL_PATH = "dungeon/expanded/wall"
        self.WALL_SHAPE_FOLDER = "shape"
        self.WALL_EFFECT_FOLDER = "effect"
        self.WALL_TEXTURE_PREFIX = "dungeon/expanded/wall/texture/"
        self.WALL_OUTER_PIECE = "outer"

        # Doorways
        self.WALL_HORIZONTAL_DOORWAY_PIECE = "horizontal_doorway"
        self.WALL_VERTICAL_DOORWAY_PIECE = "vertical_doorway"
        self.DOOR_OPENING_COLUMNS = 2
        self.DOOR_OPENING_ROWS = 2
        self.DOORWAY_PIECE_WIDTH = 225
        self.DOORWAY_PIECE_HEIGHT = 150
        self.DOOR_MIN_SHARED_COLUMNS = self.DOOR_OPENING_COLUMNS + 2
        self.DOOR_MIN_SHARED_ROWS = self.DOOR_OPENING_ROWS + 2

        # Arrows
        self.ARROW_PATHS = {
            direction: f"{self.WALL_PATH}/arrow/{direction}"
            for direction in ("up", "down", "left", "right", "left_right", "up_down")
        }
        self.ARROW_WIDTH = 75
        self.ARROW_HEIGHT = 75
        self.ARROW_OFFSET_Y = 0
        self.ARROW_OFFSET_X = 0

    def _stamp_outer_wall_face(
        self,
        shape: Image.Image,
        effect: Image.Image,
        stamp_wall_piece,
        row_band: str,
        column_position: str,
        origin: tuple[int, int] = (0, 0),
    ):
        """
        Stamp one card face's outer wall border (`outer/{row_band}/{column_position}`) into a wall
        build, so the border shares the wall texture/effect seamlessly with the interior walls. A
        fully interior face has no border at all.

        Parameters
        ----------
        shape : Image
            The "L" silhouette `_create_wall_layers` is building, modified in place.

        effect : Image
            The RGBA effect image `_create_wall_layers` is building, modified in place.

        stamp_wall_piece : function
            `_create_wall_layers`'s own `stamp_wall_piece(...)` closure, passed in since it isn't
            a method.

        row_band : str
            The face's row band: `"closed"`, `"top"`, `"middle"`, or `"bottom"`.

        column_position : str
            The face's column position: `"closed"`, `"left"`, `"middle"`, or `"right"`.

        origin : tuple[int, int], default: (0, 0)
            Where this face's top left corner sits in the image being stamped into.
        """

        if row_band == "middle" and column_position == "middle":
            return
        stamp_wall_piece(
            shape,
            effect,
            f"{self.WALL_OUTER_PIECE}/{row_band}/{column_position}",
            origin,
            (self.CARD_FACE_WIDTH, self.CARD_FACE_HEIGHT),
        )

    def _parse_door_targets(self, value: str) -> list[str]:
        """
        Parse a `{to=...}` value the same way `Dungeon` does, except each comma-separated target may
        also have another card's key: `Card Key: Room Id`, optionally followed by `: direction` (one
        of `up`/`down`/`left`/`right`).
        """

        if value.lower().strip() in ("", "none", "-"):
            return []

        identifiers: list[str] = []
        for part in value.split(","):
            part = part.strip()
            if not part:
                continue
            card_key, room_id, direction = self._split_qualified_target(part)
            identifiers.append(
                room_id if card_key is None else self._qualified_door_target(card_key, room_id, direction)
            )
        return identifiers

    def _split_qualified_target(self, value: str) -> tuple[str | None, str, str | None]:
        """
        Split a `{to=...}` target into `(card_key, room_id, direction)`: `card_key` is `None` if
        the target is unqualified (or qualified with this card's own key, which names a room on
        this card just like an unqualified target would).

        Parameters
        ----------
        value : str
            One comma-separated target, already stripped of surrounding whitespace.
        """

        if ":" not in value:
            return None, value.lower(), None

        parts = [part.strip() for part in value.split(":")]
        direction = None
        if len(parts) > 1 and parts[-1].lower() in EDGE_NAMES:
            direction = parts.pop().lower()

        card_key, room_id = ":".join(parts[:-1]).strip(), parts[-1].strip().lower()
        if not card_key or card_key.lower() == self._own_card_key.lower():
            return None, room_id, direction
        return card_key, room_id, direction

    def _qualified_door_target(self, card_key: str, room_id: str, direction: str | None) -> str:
        """
        Turn a card-qualified `{to=...}` target into the identifier this card's rooms store, and
        record whatever the subclass needs to resolve it later. Defaults to ignoring the
        qualification entirely.

        Parameters
        ----------
        card_key : str
            The card key the target named.

        room_id : str
            The room id on that card, lowercased.

        direction : str | None
            The explicitly given edge the doorway sits on, if any.
        """

        return room_id

    def link_siblings(self, sibling_cards: dict[str, "RegularCard"]):
        """
        Connect this card up to the other cards of its dungeon, once every card in the set exists.

        Parameters
        ----------
        sibling_cards : dict[str, RegularCard]
            Every card in this card's set, keyed by `get_card_key()`-style card key -- the same
            dict `main.py` already builds per set (`card_sets[card_set]`).
        """
